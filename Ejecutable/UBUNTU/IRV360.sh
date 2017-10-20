#!/bin/bash
readonly virtualEnv="/home/$USER/.edm/envs/IRV360_ENV/bin"
readonly virtualEnvCanopy="/home/$USER/.local/share/canopy/edm/envs/User/bin"
readonly python_run="bin/python2.7"
readonly python_script="IRV360/Scripts/IRV360.py"
readonly DIR=`pwd`


export LC_ALL=en_US.UTF-8
export LANG=en_US.UTF-8
eval cd "$DIR/IRV360/Scripts"
source "$virtualEnv/activate"
"$virtualEnv/python2.7" "$DIR/$python_script"
