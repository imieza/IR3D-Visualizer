#!/bin/bash
DIR="Desktop/IRV360/IR3D-Visualizer/instalable"

edm_installer="edm_installer.sh"
$DIR"/edm/bin/edm" environments import IRV360_ENV -f $DIR"/boundled_env.json"
