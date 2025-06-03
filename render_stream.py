#!/usr/bin/env python3
"""
YouTube Live Stream for Render.com
"""
import os
import subprocess
import time
import logging

# 設置日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_ffmpeg():
    """檢查 FFmpeg 是否可用"""
    try:
        subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True)
        logger.info("FFmpeg is available")
        return True
    except:
        logger.error("FFmpeg not found, installing...")
        subprocess.run(['apt', 'update'], check=True)
        subprocess.run(['apt', 'install', '-y', 'ffmpeg'], check=True)
        return True

def start_stream():
    """啟動 YouTube 直播"""
    # YouTube 串流金鑰（從環境變數獲取）
    stream_key = os.environ.get('YOUTUBE_STREAM_KEY', 'f8bd-vduf-ycuf-s1ke-atbb')
    rtmp_url = f"rtmp://a.rtmp.youtube.com/live2/{stream_key}"
    
    # FFmpeg 命令 - 生成測試圖案
    cmd = [
        'ffmpeg',
        '-f', 'lavfi',
        '-i', 'testsrc=size=1920x1080:rate=30,format=yuv420p',
        '-f', 'lavfi', 
        '-i', 'sine=frequency=1000:sample_rate=44100',
        '-c:v', 'libx264',
        '-preset', 'fast',
        '-b:v', '3000k',
        '-maxrate', '3500k',
        '-bufsize', '6000k',
        '-pix_fmt', 'yuv420p',
        '-g', '60',
        '-c:a', 'aac',
        '-b:a', '128k',
        '-f', 'flv',
        rtmp_url
    ]
    
    logger.info(f"Starting stream to: {rtmp_url}")
    
    while True:
        try:
            # 啟動串流
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            stdout, stderr = process.communicate()
            
            if process.returncode != 0:
                logger.error(f"FFmpeg error: {stderr.decode()}")
                logger.info("Restarting in 10 seconds...")
                time.sleep(10)
            else:
                logger.info("Stream ended normally")
                break
                
        except KeyboardInterrupt:
            logger.info("Stream stopped by user")
            break
        except Exception as e:
            logger.error(f"Error: {e}")
            logger.info("Restarting in 10 seconds...")
            time.sleep(10)

if __name__ == "__main__":
    logger.info("YouTube Live Stream Starting...")
    check_ffmpeg()
    start_stream() 