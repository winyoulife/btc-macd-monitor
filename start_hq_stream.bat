@echo off
echo Starting HIGH QUALITY stream to YouTube...
ssh -i C:\Users\tracy\.ssh\ssh-key-2025-06-02.key ubuntu@193.123.161.19 "pkill ffmpeg"
echo Stopped existing streams...
ssh -i C:\Users\tracy\.ssh\ssh-key-2025-06-02.key ubuntu@193.123.161.19 "nohup ffmpeg -f lavfi -i 'testsrc=size=1920x1080:rate=30,format=yuv420p' -f lavfi -i 'sine=frequency=1000:sample_rate=44100' -c:v libx264 -preset medium -b:v 6800k -maxrate 8000k -bufsize 12000k -g 60 -c:a aac -b:a 128k -f flv rtmp://a.rtmp.youtube.com/live2/f8bd-vduf-ycuf-s1ke-atbb > ~/hq_stream.log 2>&1 &"
echo High quality stream started! Target bitrate: 6800k
pause 