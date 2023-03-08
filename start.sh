#!/bin/bash

# Enter the device name. Must be unique
read -p "Enter the device name: " deviceName

# Enter the group name. Must be unique
read -p "Enter the group name: " groupName

# Enter the role name
read -p "Enter the role name: " roleName

# Enter a role alias name
read -p "Enter the name for your role alias name: " roleAliasName

# Enter desired temporary credential duration, (3600 to 43200 seconds)
read -p "Enter maximum temporary credential duration between 3600 and 43200 seconds: " maxDuration

# Enter default region
read -p "Enter the AWS region in which this device will operate: " region

# Enter AWS Access Key, this will be deleted once all the scripts have been run
echo "This will be deleted after GG has been setup."
read -p "Enter the AWS Access Key ID: " accessKeyId

# Enter AWS Secret Access Key, this will be deleted once all the scripts have been run
echo "This will be deleted after GG has been setup."
read -p "Enter the AWS Secret Access Key: " secretAccessKey

# run the raspberry pi setup
sh ./scripts/RPiPrep.sh $deviceName $groupName $roleAliasName $roleName $maxDuration $region $accessKeyId $secretAccessKey

############################################################################
#                                                                               
#  USE ISENGARD STS CREDENTIALS BY CLICKING THE COPY ICON NEXT TO THE ROLE
#  NAME ON THE ISENGARD LANDING PAGE. SELECT BASH/ZSH AND PASTE IN THE SHELL
#
############################################################################



