#!/bin/bash
: "${CMD_PREFIX_BGW:='mpirun -np 2'}"
$CMD_PREFIX_BGW kgrid.x ./kgrid.inp ./kgrid.out ./kgrid.log
