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
