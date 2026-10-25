#!/usr/bin/env python3
"""DeePMD helper functions created by Mat3ra.com"""

def qe2dp(data_dir, ext):
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
