# do not run any of these scripts with sudo, ~ refers to /home/pi while
# sudo runs it as root and makes it refer to /

# change directory to /home/pi
cd /home/pi

# install GDK CLI
sudo python3 -m pip install -U git+https://github.com/aws-greengrass/aws-greengrass-gdk-cli.git@v1.1.0

# make root dir for greengrass component built via GDK CLI
mkdir /home/pi/greengrassv2
cd /home/pi/greengrassv2

# initialize GG template
gdk component init --template HelloWorld --language python

# move files where they need to be
yes | cp -i /home/pi/src/python/main.py /home/pi/greengrassv2/main.py
cp /home/pi/src/python/* /home/pi/greengrassv2/src
sudo rm /home/pi/greengrassv2/src/greeter.py








