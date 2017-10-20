#!/bin/bash
readonly virtualEnv="/Users/$USER/.edm/envs/IRV360_ENV"

activate="bin/activate"
python_run="bin/python2.7"
python_script="IRV360/Scripts/IRV360.py"
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

source "$virtualEnv/$activate"
export LC_ALL=en_US.UTF-8
export LANG=en_US.UTF-8
python "$DIR/$python_script"
