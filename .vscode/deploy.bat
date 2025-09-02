scp -r ./src/* kiosk@testbench:/home/kiosk/temp/
scp ./src/.env kiosk@testbench:/home/kiosk/temp/
ssh kiosk@testbench "cd ~/scripts && ./hotload.sh"