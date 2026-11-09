#!/bin/bash
set -e
# TODO: implement WAIT_FOR_COMPLETION for when the jobs are submitted via PBS
# See: deepmd/train_mlff_qe-cp-traj/run.sh

export OMP_NUM_THREADS=1
module load espresso

echo "<>------------- 1. DFT calculation using Quantum ESPRESSO -------------<>"
cd 1-mf-qe
bash link_files.sh

echo "<>------------------------ 1.1 SCF calculation ------------------------<>"
cd 1-scf
bash 1-calculate_scf.run
cd ..

echo "<>------------------------- 1.2 Mean-field WFN ------------------------<>"
cd 2-wfn
bash 1-calculate_wfn.run
bash 2-convert_wfn.run
cd ..

echo "<>------------------------ 1.3 Mean-field WFNq ------------------------<>"
cd 3-wfnq
bash 1-calculate_wfn.run
bash 2-convert_wfn.run
cd ..

echo "<>-------------------- 1.4 Mean-field bandstructure -------------------<>"
cd 4-bandstructure
bash 1-calculate_wfn.run
bash 2-convert_wfn.run
cd ../..

module load berkeleygw

echo "<>--------------------- 2. BerkeleyGW Calculation ---------------------<>"
cd 2-bgw-qe
bash link_files.sh

echo "<>-------------------- 2.1 BGW Epsilon calculation --------------------<>"
cd 1-epsilon
bash 1-run_epsilon.run
cd ..

echo "<>--------------------- 2.2 BGW Sigma calculation ---------------------<>"
cd 2-sigma
bash 1-run_sigma.run

echo "<>---------------- 2.2 Bandstructure using interqp code ---------------<>"
cd bandstructure
bash 1-run_inteqp.run
