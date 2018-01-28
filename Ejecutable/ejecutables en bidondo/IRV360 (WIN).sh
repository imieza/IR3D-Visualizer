#!/bin/bash
readonly virtualEnv="C:\Users\$USER\AppData\Local\Enthought\Canopy32\edm\envs\User"

activate="bin/activate"
python_run="bin/python2.7"
python_script="/Scripts/IRV360.py"
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

source "$virtualEnv$activate"
export LC_ALL=en_US.UTF-8
export LANG=en_US.UTF-8
"$virtualEnv$python_run" "$DIR$python_script"

