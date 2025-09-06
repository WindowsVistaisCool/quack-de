@echo off
set HOSTNAME=192.168.1.20

scp -r ./src/* kiosk@%HOSTNAME%:/home/kiosk/temp/
scp ./src/.env kiosk@%HOSTNAME%:/home/kiosk/temp/
ssh kiosk@%HOSTNAME% "cd ~/scripts && ./hotload.sh"