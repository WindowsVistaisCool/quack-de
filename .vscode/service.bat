@echo off
set HOSTNAME=192.168.1.20

scp ./service/* kiosk@%HOSTNAME%:/home/kiosk/service
scp ./service/themes/* kiosk@%HOSTNAME%:/home/kiosk/service/themes
ssh kiosk@%HOSTNAME% "cd ~/scripts && ./buildservice.sh"