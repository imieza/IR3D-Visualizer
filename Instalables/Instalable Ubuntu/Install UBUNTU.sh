#!/bin/bash
readonly virtualEnv="/home/$USER/.edm/envs/IRV360_ENV/bin"
readonly DIR=`pwd`
edm_installer=".edm/edm_installer.sh"
$DIR"/.edm/edm/bin/edm" environments import IRV360_ENV -f $DIR"/.edm/boundled_env.json"
source "$virtualEnv/activate"
pip install --upgrade virtualenvwrapper
