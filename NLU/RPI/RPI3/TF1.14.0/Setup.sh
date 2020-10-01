#!/bin/sh
echo "!! This program will set up everything you need to use the GeniSys NLU Engine !!"
echo " "
echo "-- Installing dependencies"
sudo apt install python3-pip
sudo apt install python3.7-dev
wget https://github.com/lhelontra/tensorflow-on-arm/releases/download/v1.14.0-buster/tensorflow-1.14.0-cp37-none-linux_armv7l.whl
pip3 install --user tensorflow-1.14.0-cp37-none-linux_armv7l.whl
sudo apt install cmake
sudo apt install mpg123
pip3 install --user flask
pip3 install --user gtts
pip3 install --user nltk
pip3 install --user pydbus
pip3 install --user paho-mqtt
pip3 install --user regex
pip3 install --user TFLearn
echo " "
echo "-- Installing MITIE"
git clone https://github.com/mit-nlp/MITIE.git
cd MITIE/mitielib
mkdir build && cd build
cmake ..
cmake --build . --config Release --target install
cd ../../
make MITIE-models
echo "-- GeniSysAI NLU installed"