#!/bin/bash -l

# This serial script links the epsmat and eqp files.

echo "Linking epsmat.h5 files"
for directory in *-*/; do
  # Ignore the "1-epsilon/" directory and things that are not directories
  if [[ ( $directory == 1-* ) || ! -d $directory ]]; then continue; fi
  echo " Working on directory $directory"

  cd $directory
  ln -sf ../1-epsilon/epsmat.h5 ./
  ln -sf ../1-epsilon/eps0mat.h5 ./
  cd ../
done

cd 2-sigma/bandstructure
ln -sf ../eqp1.dat ./eqp_co.dat

echo
echo "Done!"
