ssh kiosk@testbench "rm -rf ~/temp && mkdir ~/temp"
scp -r ./scripts kiosk@testbench:/home/kiosk/
ssh kiosk@testbench "cd ~/scripts && chmod +x *.sh && ./install.sh"