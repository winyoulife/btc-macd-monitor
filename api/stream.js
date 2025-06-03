import { spawn } from 'child_process';

export default async function handler(req, res) {
  const streamKey = process.env.YOUTUBE_STREAM_KEY || 'f8bd-vduf-ycuf-s1ke-atbb';
  const rtmpUrl = `rtmp://a.rtmp.youtube.com/live2/${streamKey}`;

  try {
    console.log('Starting YouTube stream via Vercel function...');
    
    // Vercel Edge 環境中的 FFmpeg 串流
    const ffmpegArgs = [
      '-f', 'lavfi',
      '-i', 'testsrc=size=1280x720:rate=30',
      '-f', 'lavfi',
      '-i', 'sine=frequency=1000:sample_rate=48000',
      '-c:v', 'libx264',
      '-preset', 'ultrafast',
      '-b:v', '1500k',
      '-maxrate', '1500k',
      '-bufsize', '3000k',
      '-pix_fmt', 'yuv420p',
      '-g', '30',
      '-c:a', 'aac',
      '-b:a', '128k',
      '-ar', '48000',
      '-f', 'flv',
      '-t', '240', // 限制 4 分鐘避免超時
      rtmpUrl
    ];

    const ffmpeg = spawn('ffmpeg', ffmpegArgs);
    
    let output = '';
    let error = '';

    ffmpeg.stdout.on('data', (data) => {
      output += data.toString();
    });

    ffmpeg.stderr.on('data', (data) => {
      error += data.toString();
      console.log('FFmpeg stderr:', data.toString());
    });

    // 設置超時
    const timeout = setTimeout(() => {
      ffmpeg.kill('SIGTERM');
      console.log('FFmpeg process terminated due to timeout');
    }, 240000); // 4 分鐘

    ffmpeg.on('close', (code) => {
      clearTimeout(timeout);
      console.log(`FFmpeg process exited with code ${code}`);
    });

    // 立即返回響應
    res.status(200).json({
      message: 'YouTube stream started',
      streamUrl: rtmpUrl,
      duration: '4 minutes',
      timestamp: new Date().toISOString(),
      note: 'Stream will run for 4 minutes due to Vercel function timeout limits'
    });

  } catch (err) {
    console.error('Error starting stream:', err);
    res.status(500).json({
      error: 'Failed to start stream',
      message: err.message,
      timestamp: new Date().toISOString()
    });
  }
} 