@echo off
echo Starting YouTube stream from Windows...
ffmpeg -f gdigrab -framerate 30 -i desktop -c:v libx264 -preset fast -b:v 3000k -maxrate 3500k -bufsize 6000k -pix_fmt yuv420p -g 60 -c:a aac -f flv rtmp://a.rtmp.youtube.com/live2/f8bd-vduf-ycuf-s1ke-atbb
pause 