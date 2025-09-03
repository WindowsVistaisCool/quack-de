scp -r ./service kiosk@testbench:/home/kiosk/
ssh kiosk@testbench "cd ~/scripts && ./buildservice.sh"