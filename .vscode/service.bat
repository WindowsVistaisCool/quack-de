scp ./service/* kiosk@testbench:/home/kiosk/service
scp ./service/themes/* kiosk@testbench:/home/kiosk/service/themes
ssh kiosk@testbench "cd ~/scripts && ./buildservice.sh"