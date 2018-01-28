#!/bin/bash
readonly virtualEnv="/home/$USER/.edm/envs/IRV360_ENV/bin"
readonly DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

echo $DIR
sudo installer -pkg "$DIR/.edm/edm_1.8.2.pkg" -target /

#edm_installer=".edm/edm_installer.sh"
edm environments remove IRV360_ENV
