export default function handler(req, res) {
  res.status(200).json({ 
    status: 'OK', 
    service: 'YouTube Stream Controller',
    timestamp: new Date().toISOString()
  });
} 