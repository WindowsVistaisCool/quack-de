echo "Creating necessary directories and files..."
mkdir ~/deploy # Directory for the main application
mkdir ~/led # Directory for LED service
mkdir ~/temp # Temporary directory for scripts

echo "Setting up environment [xinit]..."
cat > ~/.xinitrc <<- "EOF"
# xset s off
# xset s noblank
# xset -dpms s off

openbox-session
EOF

echo "Setting up environment [bash-profile]..."
cat > ~/.bash_profile <<- "EOF"
#!/bin/sh
source ~/.profile
if [[ -z $DISPLAY ]] && [[ $(tty) = /dev/tty1 ]]; then
    cd ~
    sudo ./led_svc &
    cd ~/deploy
    startx -- -nocursor
fi
EOF

echo "Setting up environment [openbox-autostart]..."
cat > ~/.config/openbox/autostart <<- "EOF"
#!/bin/sh
# Start the main application
cd ~/deploy
sudo python3 ./main.py &
EOF