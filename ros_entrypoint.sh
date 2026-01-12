#!/bin/bash
set -e

id -u ros &>/dev/null || adduser --quiet --disabled-password --gecos '' --uid ${UID:=1000} ros

if ! getent group i2c > /dev/null; then
    groupadd -g 988 i2c
    echo "Created i2c group"
fi
# groupadd -g ${I2C_GROUP_ID:=988} i2c
usermod -aG dialout,i2c ros

source /opt/ros/${ROS_DISTRO}/setup.bash
source /colcon_ws/install/setup.bash || true

exec "$@"