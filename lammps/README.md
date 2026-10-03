# LAMMPS

LAMMPS [^1] is a classical molecular dynamics simulation code focusing on
materials modeling. It was designed to run efficiently on parallel computers and
to be easy to extend and modify. Originally developed at Sandia National
Laboratories, a US Department of Energy facility, LAMMPS now includes
contributions from many research groups and individuals from many institutions.
Most of the funding for LAMMPS has come from the US Department of Energy (DOE).
LAMMPS is open-source software distributed under the terms of the GNU Public
License Version 2 (GPLv2).

## Examples

### Energy minimization
An example calculation of energy minimization of two dimensional Lennard-Jones
melt is available under [emin](./emin) directory.

### LAMMPS+M3GNet
The example under the [m3gnet](./m3gnet) directory uses M3GNet pair potential.

### NEB calculation
An example calculation of NEB is available under [neb](./neb) directory.
The example uses the SIVAC potential. The calculation is run on multiple nodes:
2 nodes with 44 cores each. Adapted from the original example in the LAMMPS
project: https://github.com/lammps/lammps/blob/develop/examples/neb/

## Links
[^1]: https://docs.lammps.org/Manual.html
