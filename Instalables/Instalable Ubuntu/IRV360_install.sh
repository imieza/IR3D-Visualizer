#!/bin/bash
DIR=`pwd`
edm_installer=".edm/edm_installer.sh"
$DIR"/.edm/edm/bin/edm" environments import IRV360_ENV -f $DIR"/.edm/boundled_env.json"
