#!/bin/bash

module load dials/latest

input_path=$1


dials.import $input_path/*.cbf
dials.import $input_path/*.img
dials.import $input_path/*.mccd

dials.find_spots imported.expt nproc=4
dials.python /dls/science/users/gwx73773/iolite/src/iolite/run_radial_average_bg.py imported.expt
