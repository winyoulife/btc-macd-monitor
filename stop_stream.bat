@echo off
echo Stopping YouTube stream...
ssh -i C:\Users\tracy\.ssh\ssh-key-2025-06-02.key ubuntu@193.123.161.19 "pkill ffmpeg && echo 'Stream stopped successfully'"
echo Stream has been stopped!
pause 