#!/bin/bash

# Example script for running statick with a custom configuration and custom
# profile

if [ ! -d src ]; then 
    mkdir src

    pushd src || exit
    git clone https://github.com/ros-planning/navigation.git
    popd || exit
fi

catkin_make -DCMAKE_BUILD_TYPE=RelWithDebInfo

. devel/setup.bash  # NOLINT

if [ ! -d statick_example4 ]; then
    mkdir statick_example4
fi

statick src/navigation/amcl --output-directory statick_example4/ --user-paths ./navigation_config --profile profile_objective.yaml
