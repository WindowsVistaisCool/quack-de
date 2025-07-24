echo "Creating necessary directories and files..."
mkdir ~/deploy
mkdir ~/temp

echo "Setting up environment [xinit]..."
cat > ~/.xinitrc <<- "EOF"
#!/bin/sh
xset s off
xset s noblank
xset -dpms s off

openbox-session
EOF

echo "Setting up environment [bash-profile]..."
cat > ~/.bash_profile <<- "EOF"
#!/bin/sh
source ~/.profile
if [[ -z $DISPLAY ]] && [[ $(tty) = /dev/tty1 ]]; then
    cd /home/kiosk/deploy
    startx # -- -nocursor
fi
EOF

echo "Setting up environment [openbox-autostart]..."
cat > ~/.config/openbox/autostart <<- "EOF"
#!/bin/sh
# Start the main application
cd ~/deploy
python3 ./main.py &
EOF