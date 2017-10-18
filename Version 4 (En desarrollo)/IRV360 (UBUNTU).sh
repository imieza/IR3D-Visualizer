#!/bin/bash
readonly virtualEnv="/home/nahuel/.edm/envs/NEW_ENV"
readonly virtualEnvCanopy="/home/$USER/.local/share/canopy/edm/envs/User/bin"

python_run="bin/python2.7"
python_script="Scripts/IRV360.py"
DIR=`pwd`
export LC_ALL=en_US.UTF-8
export LANG=en_US.UTF-8
source "$virtualEnvCanopy/activate"
"$virtualEnvCanopy/python2.7" "$DIR/$python_script"
