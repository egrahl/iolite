#!/bin/bash
module load dials/latest

id=$1
input1=$2
input2=$3


dials.python /dls/science/users/gwx73773/iolite/src/iolite/run_xia2.py --id=$id --inputpath1=$input1 --inputpath2=$input2
cd DEFAULT/NATIVE/SWEEP1/integrate
dials.python /dls/science/users/gwx73773/iolite/src/iolite/overlaps/extract.py 13_integrated.expt 13_integrated.refl
chmod +x /dls/science/users/gwx73773/iolite/src/iolite/command_line/run_overlaps_pixel.sh
qsub -q low.q /dls/science/users/gwx73773/iolite/src/iolite/command_line/run_overlaps_pixel.sh
chmod +x /dls/science/users/gwx73773/iolite/src/iolite/command_line/run_overlaps_reflection.sh
qsub -q low.q /dls/science/users/gwx73773/iolite/src/iolite/command_line/run_overlaps_reflection.sh
cd ..
cd ..
cd ..
cd ..