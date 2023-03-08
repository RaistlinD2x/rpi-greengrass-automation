#!/bin/bash

# change to /home/pi directory
cd /home/pi
mkdir /home/pi/certs

# update rpi packages and install Java required for greengrass
sudo apt-get update -y && sudo apt-get upgrade -y
sudo apt install default-jdk -y
java -version

# install Adafruit library for sensors
sudo apt-get install python3 python3-pip git cmake -y
pip3 install adafruit-circuitpython-dht
sudo apt-get install libgpiod2

# /etc/sysctl.conf enable ipv4 forwarding and enable hard and symlink protection
sudo sed -i 's/#net.ipv4.ip_forward=1/net.ipv4.ip_forward=1/' /etc/sysctl.conf

grep -qxF "fs.protected_hardlinks=1" /etc/sysctl.conf || echo "fs.protected_hardlinks=1" | sudo tee -a /etc/sysctl.conf
grep -qxF "fs.protected_symlinks=1" /etc/sysctl.conf || echo "fs.protected_symlinks=1" | sudo tee -a /etc/sysctl.conf

# back to home
cd /home/pi

# Manually create config file for later deletion
mkdir /home/pi/.aws
cat << EOF > /home/pi/.aws/config
[default]
aws_access_key_id=$7
aws_secret_access_key=$8
region=$6
EOF

# download the GGv2 stuff
curl -s https://d2s8p88vqu9w66.cloudfront.net/releases/greengrass-nucleus-latest.zip > \
    greengrass-nucleus-latest.zip && unzip greengrass-nucleus-latest.zip -d GreengrassCore

# install the GGv2 components, this will also add in your device name and
# assign it to the group you've chosen
sudo -E java -Droot="/greengrass/v2" -Dlog.store=FILE -jar ./GreengrassCore/lib/Greengrass.jar --aws-region $6 --thing-name $1 --thing-group-name $2 --component-default-user ggc_user:ggc_group --provision true --setup-system-service true --deploy-dev-tools true

# start using temporary credentials
python3 /home/pi/src/scripts/gg_setup.py $1 $2 $3 $4 $5 $6

# delete aws credentials
sudo rm -r /home/pi/.aws

# download GG HelloWorld template, replace files, and ready for component setup
cd /home/pi/src/scripts
sh addTemplateComponent.sh