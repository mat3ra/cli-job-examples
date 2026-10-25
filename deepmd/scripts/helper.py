#!/usr/bin/env python3
"""DeePMD helper functions created by Mat3ra.com"""

def qe2dp(data_dir, ext):
    """
    Convert Quantum ESPRESSO output files into a DeePMD-kit training dataset.

    Recursively searches `data_dir` for files matching `ext` (e.g. QE `pwscf.out`-style
    or XML output read via ASE), normalizes their line endings, concatenates every
    frame found into a single ASE trajectory, and converts that trajectory into
    DeePMD's raw and compressed npy formats using dpdata.

    Parameters
    ----------
    data_dir : str
        Path to the directory tree containing Quantum ESPRESSO output files to convert.
        The directory is copied (not modified in place) before processing.
    ext : str
        File extension (without the leading dot) identifying which files under
        `data_dir` to read as ASE-compatible structures (e.g. "out", "xml").

    Side Effects
    ------------
    - Creates and removes a temporary `./tmp` working copy of `data_dir`.
    - Writes and then deletes an intermediate `./deepmd.traj` ASE trajectory file.
    - Writes the final dataset to a `./deepmd` directory in both raw and npy formats.
    - Files that ASE fails to parse are skipped with a printed warning rather than
      aborting the conversion.
    """
    from ase.io import read, write
    from ase.io import Trajectory
    import dpdata
    import pathlib
    import os

    # Clean previous leftovers and copy to tmp
    os.system('rm -rf ./tmp deepmd.traj')
    os.system('cp -r ' + data_dir + ' ./tmp')

    # Convert all matching files in ./tmp from DOS to Unix
    os.system(f'find ./tmp -name "*.{ext}" -exec dos2unix {{}} + > /dev/null 2>&1')

    p = pathlib.Path('./tmp')
    traj = Trajectory('deepmd.traj', mode='a')

    for f in p.glob('**/*.' + str(ext)):
        try:
            cell = read(f, index=':')
            for atoms in cell:
                traj.write(atoms=atoms)
        except Exception as e:
            print(f"[WARNING] Could not read {f}: {e}")

    traj.close()
    d_ase = dpdata.MultiSystems.from_file(file_name='./deepmd.traj', fmt='ase/structure')
    d_ase.to_deepmd_raw('deepmd')
    d_ase.to_deepmd_npy('deepmd')
    os.system('rm deepmd.traj')
    os.system('rm -rf tmp')


def get_deepmd_list(data_dir="./deepmd"):
    """Get list of DeePMD system directories, ignoring hidden files."""
    return sorted(
        [
            d
            for d in os.listdir(data_dir)
            if os.path.isdir(os.path.join(data_dir, d)) and not d.startswith(".")
        ]
    )


def extract_symbols(folder_name):
    """Extract chemical element symbols from formula name (e.g. 'La24Li40Nb16O96')."""
    raw_splits = re.split(r"[0-9]", folder_name)
    return [s for s in raw_splits if s != ""]


def calculate_max_nbor_size(data_dir, symbols, rcut, scale):
    """Run dp neighbor-stat and apply buffer scale."""
    cmd = ["dp", "neighbor-stat", "-s", data_dir, "-r", str(rcut), "-t"] + symbols
    result = subprocess.run(cmd, capture_output=True, text=True)

    with open("neigh-stat.log", "w") as f:
        f.write(result.stdout)
        f.write(result.stderr)

    max_nbor_size = []
    for line in (result.stdout + result.stderr).splitlines():
        if "max_nbor_size:" in line:
            tmp = re.findall(r"\d+", line)
            max_nbor_size = [int(float(n) * scale) for n in tmp]
            break

    if not max_nbor_size:
        raise RuntimeError(
            "Could not parse 'max_nbor_size' from neighbor-stat output. Check 'neigh-stat.log'."
        )

    return max_nbor_size


def create_deepmd_json(data_dir, dp_list, rcut, num_steps, prec="low"):
    """Generate train.json."""
    scale_map = {"low": 1.0, "medium": 1.5, "high": 2.0}
    if prec not in scale_map:
        raise ValueError(
            f"Invalid prec '{prec}'. Must be 'low', 'medium', or 'high'."
        )
    scale = scale_map[prec]

    symbols = extract_symbols(dp_list[0])
    max_nbor_size = calculate_max_nbor_size(data_dir, symbols, rcut, scale)
    systems = [
        os.path.join(data_dir, l) + "/"
        for l in dp_list
    ]

    config = {
        "_comment": " model parameters",
        "model": {
            "type_map": symbols,
            "descriptor": {
                "type": "se_e2_a",
                "sel": max_nbor_size,
                "rcut_smth": 0.50,
                "rcut": rcut,
                "neuron": [25, 50, 100],
                "resnet_dt": False,
                "axis_neuron": 16,
                "seed": 1,
            },
            "fitting_net": {
                "neuron": [240, 240, 240],
                "resnet_dt": True,
                "seed": 1,
            },
        },
        "learning_rate": {
            "type": "exp",
            "decay_steps": 5000,
            "start_lr": 0.001,
            "stop_lr": 3.51e-8,
        },
        "loss": {
            "type": "ener",
            "start_pref_e": 0.02,
            "limit_pref_e": 1,
            "start_pref_f": 1000,
            "limit_pref_f": 1,
            "start_pref_v": 0,
            "limit_pref_v": 0,
        },
        "training": {
            "training_data": {
                "systems": systems,
                "batch_size": "auto",
            },
            "validation_data": {
                "systems": systems,
                "batch_size": 1,
                "numb_btch": 3,
            },
            "numb_steps": num_steps,
            "seed": 10,
            "disp_file": "lcurve.out",
            "disp_freq": 100,
            "save_freq": 1000,
        },
    }

    with open("./train.json", "w") as f:
        json.dump(config, f, indent=4)


def dptrain(fjson="train.json"):
    """Execute dp train with real-time logging to terminal and file."""
    cmd = f"dp train {fjson} 2>&1 | tee log_dp_train"
    os.system(cmd)


def dpfreeze(fpb="graph.pb"):
    """Freeze latest checkpoint into graph.pb."""
    cmd = f"dp freeze -o {fpb} 2>&1 | tee log_dp_freeze"
    os.system(cmd)
