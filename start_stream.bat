@echo off
echo Connecting to Oracle Cloud and starting YouTube stream...
ssh -i C:\Users\tracy\.ssh\ssh-key-2025-06-02.key ubuntu@193.123.161.19 "pkill ffmpeg; export DISPLAY=:99.0; nohup ffmpeg -f x11grab -video_size 1920x1080 -framerate 30 -i :99.0 -c:v libx264 -preset ultrafast -maxrate 2500k -bufsize 5000k -pix_fmt yuv420p -g 50 -f flv rtmp://a.rtmp.youtube.com/live2/f8bd-vduf-ycuf-s1ke-atbb > ~/stream.log 2>&1 & echo 'Stream started successfully'"
echo Stream should be starting on YouTube now!
pause 