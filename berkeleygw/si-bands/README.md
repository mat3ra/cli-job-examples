# Silicon Bandstructure with BerkeleyGW and Quantum ESPRESSO

Adapted from: https://workshop2023.berkeleygw.org

In this example we will calculate the quasiparticle band structure of silicon
using the LDA and GW approximations.

## 1. mf-qe

Perform DFT calculations using Quantum ESPRESSO and convert QE outputs to
BerkeleyGW input format.

### 1.1 SCF
In this directory we perform standard SCF calculation and obtain charge
densities which will be used to generate all the other WFNs with Quantum
ESPRESSO.

### 1.2 Mean-field wavefunction
In this directory we perform a non-self-consistent (NSCF) mean-field
calculation to generate all of the Bloch states needed for the subsequent GW
calculations.  The resulting wavefunction file will then be read as `WFN` by
the Epsilon code, and `WFN_inner` by the Sigma code.

1. Take a look at the input file (`kgrid.inp`) for `kgrid.x`, the executable
   that generates our k-grids for NSCF calculations. Compare with the
   documentation of `kgrid.x`. Note the line specifying the FFT grid. We take
   that from the SCF calculation, reported next to `FFT dimensions`.

2. Run `bash 0-get_kgrid.sh` to generate the k-grid. Take a look at the output
   output `kgrid.out` and the more verbose log `kgrid.log`.

3. Copy the k-points in the reduced BZ from `kgrid.out` and put them in the
   Quantum ESPRESSO input file (`bands.in`) in the specified location at the
   end of the file. Do not repeat the line starting with `K_POINTS crystal`.

4. Run `bash 1-calculate_wfn.run` to calculate the wavefunctions using Quantum
   ESPRESSO. This should take a few seconds. These wavefunctions will be
   written to files in Quantum ESPRESSO format, so they will need to be
   converted to BGW format in the next step using the utility `pw2bgw.x`.

5. Take a look at the input file (`pw2bgw.in`) for `pw2bgw.x`, our utility that
   converts wavefunctions in Quantum ESPRESSO format to BGW format. Compare
   this input file with the documentation available in the code.

6. Run `bash 2-convert_wfn.run` to convert the wavefunction file from Quantum
   ESPRESSO to the BerkeleyGW format.

7. Take a look at the output file. Use `wfn_rho_vxc_info.x` to inspect the
   k-points in the `WFN` file.

###  1.3 MF/Epsilon (WFNq)
In this directory we perform a non-self-consistent (NSCF) mean-field
calculation to generate all of the Bloch states needed for the subsequent GW
calculations. The resulting wavefunction file will then be read as `WFNq` by
the Epsilon code.

1. Take a look at the input file `kgrid.inp` for `kgrid.x`. Note the small
   q-shift.

2. Run `bash 0-get_kgrid.sh` to generate the k-grid. Take a look at the output
   output `kgrid.out` and the more verbose log `kgrid.log`.

3. Copy the k-points in the reduced BZ from `kgrid.out` and put them in the
   Quantum ESPRESSO input file (`bands.in`) in the specified location at the
   end of the file. Take a look ad the input file.

4. Run `bash 1-calculate_wfn.run` to calculate the wavefunctions using Quantum
   ESPRESSO. This should take a few seconds. These wavefunctions will be
   written to files in Quantum ESPRESSO format, so they will need to be
   converted to BGW format in the next step using the utility `pw2bgw.x`.

5. Take a look at the input file (`pw2bgw.in`) for `pw2bgw.x`, our utility that
   converts wavefunctions in Quantum ESPRESSO format to BGW format.

6. Run `bash 2-convert_wfn.run` to convert the wavefunction file from Quantum
   ESPRESSO to the BerkeleyGW format.

7. Take a look at the output file. Use `wfn_rho_vxc_info.x` to inspect the
   k-points in the `WFN` file.

### 1.4 MF/Bandstructure
In this directory we perform a non-self-consistent (NSCF) mean-field
calculation to generate all of the Bloch states needed for the subsequent GW
calculations.  The resulting wavefunction file will then be read as `WFN_co`
by the Inteqp code.


1. Run `bash 1-calculate_wfn.run` to calculate the wavefunctions using QE.

2. Look at the k-path specification in `bands.in` and the k-points generated in
   `bands.out` Identify what paths are being taken with respect to a diagram
   such as <http://www.iue.tuwien.ac.at/phd/dhar/node18.html>.

3. Run `bash 2-convert_wfn.run` to convert the wavefunction file from Quantum
   ESPRESSO to the BerkeleyGW format.

4. Take a look at the output file. Use `wfn_rho_vxc_info.x` to inspect the
k-points in the `WFN` file.

## 2. bgw-qe
Perform GW calculation using BerkeleyGW code.

### 2.1 BGW/Epsilon
In this step we calculate the RPA dielectric matrix of silicon using the
Epsilon code from BerkeleyGW.

### 2.2 BGW/Sigma
In this step we calculate the GW quasiparticle energies for silicon using
the Sigma code from BerkeleyGW.

Descend into the `bandstructure` directory to calculate an interpolated
quasiparticle bandstructure with the inteqp code.

## Instructions

1. Review and run `bash run-all.sh`.
2. Make bandstructure plot:

```
# create and activate python virtualenv
python3 -m venv .venv
source .venv/bin/activate

# install python packages
pip install numpy matplotlib

# run plot script
cd 2-bgw-qe/2-sigma/bandstructure
python3 2-plot_bandstructure.py
```

The plot is saved as `Si_bands.pdf`. It is wellknown that standard DFT under
estimates semiconductor bandgap. With GW approximation, the bandgap value is
more closer to the experimental value.

```
LDA gap: 0.483 eV
GW gap: 1.137 eV
```
