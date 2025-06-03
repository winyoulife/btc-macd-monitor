@echo off
echo Checking stream status...
ssh -i C:\Users\tracy\.ssh\ssh-key-2025-06-02.key ubuntu@193.123.161.19 "ps aux | grep ffmpeg"
echo.
echo Checking stream logs...
ssh -i C:\Users\tracy\.ssh\ssh-key-2025-06-02.key ubuntu@193.123.161.19 "tail -20 ~/stream.log"
pause 