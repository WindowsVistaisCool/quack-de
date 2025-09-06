#!/bin/bash

cd ~
sudo pkill led_svc
sudo rm led_svc
cd ~/service/build
cmake ..
make -j4
sudo mv ./service ~/led_svc
cd ~
sudo ./led_svc