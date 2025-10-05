import http from 'http';
import fs from 'fs';
import path from 'path';

const PORT = 3003;

const server = http.createServer((req, res) => {
  // Set CORS headers
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

  // Obsługa endpointu /api/current?city=warsaw
  if (req.url.startsWith('/api/current')) {
    const urlObj = new URL('http://localhost' + req.url);
    const city = urlObj.searchParams.get('city');
    // Lista miast i współrzędnych
    const LOCATIONS = {
      warsaw: { lat: 52.2297, lon: 21.0122, name: 'Warsaw' },
      krakow: { lat: 50.0647, lon: 19.945, name: 'Kraków' },
      gdansk: { lat: 54.352, lon: 18.6466, name: 'Gdańsk' },
      wroclaw: { lat: 51.1079, lon: 17.0385, name: 'Wrocław' },
      poznan: { lat: 52.4064, lon: 16.9252, name: 'Poznań' },
      lodz: { lat: 51.7592, lon: 19.456, name: 'Łódź' },
      katowice: { lat: 50.2649, lon: 19.0238, name: 'Katowice' },
      szczecin: { lat: 53.4285, lon: 14.5528, name: 'Szczecin' },
      bydgoszcz: { lat: 53.1235, lon: 18.0084, name: 'Bydgoszcz' },
      lublin: { lat: 51.2465, lon: 22.5684, name: 'Lublin' },
      bialystok: { lat: 53.1325, lon: 23.1688, name: 'Białystok' },
      czestochowa: { lat: 50.7964, lon: 19.1201, name: 'Częstochowa' },
      radom: { lat: 51.4027, lon: 21.1471, name: 'Radom' },
      torun: { lat: 53.0138, lon: 18.5984, name: 'Toruń' },
      rzeszow: { lat: 50.0412, lon: 21.9991, name: 'Rzeszów' },
      kielce: { lat: 50.8661, lon: 20.6286, name: 'Kielce' }
    };
    if (!city || !LOCATIONS[city]) {
      res.writeHead(400, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({ error: 'City parameter required or not found' }));
      return;
    }
    const { lat, lon, name } = LOCATIONS[city];
    // Proxy do Open-Meteo API
    fetch(`https://api.open-meteo.com/v1/forecast?latitude=${lat}&longitude=${lon}&current=temperature_2m,relative_humidity_2m,wind_speed_10m,precipitation&timezone=Europe/Warsaw`)
      .then(apiRes => apiRes.json())
      .then(data => {
        if (!data.current) {
          res.writeHead(500, { 'Content-Type': 'application/json' });
          res.end(JSON.stringify({ error: 'No current weather data available' }));
          return;
        }
        const current = data.current;
        const result = {
          name,
          slug: city,
          timestamp: current.time,
          temp_c: Math.round(current.temperature_2m * 10) / 10,
          wind_mps: current.wind_speed_10m,
          humidity_pct: current.relative_humidity_2m,
          precip_mm: current.precipitation
        };
        res.writeHead(200, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify(result));
      })
      .catch(() => {
        res.writeHead(500, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({ error: 'Failed to fetch weather data' }));
      });
    return;
  }

  // ...obsługa plików statycznych jak dotychczas...
  let filePath = '.' + req.url;
  if (filePath === './') {
    filePath = './pages-index.html';
  }

  const extname = String(path.extname(filePath)).toLowerCase();
  const mimeTypes = {
    '.html': 'text/html',
    '.js': 'text/javascript',
    '.css': 'text/css',
    '.json': 'application/json',
    '.png': 'image/png',
    '.jpg': 'image/jpg',
    '.gif': 'image/gif',
    '.svg': 'image/svg+xml',
    '.wav': 'audio/wav',
    '.mp4': 'video/mp4',
    '.woff': 'application/font-woff',
    '.ttf': 'application/font-ttf',
    '.eot': 'application/vnd.ms-fontobject',
    '.otf': 'application/font-otf',
    '.wasm': 'application/wasm',
  };

  const contentType = mimeTypes[extname] || 'application/octet-stream';

  fs.readFile(filePath, (error, content) => {
    if (error) {
      if (error.code === 'ENOENT') {
        res.writeHead(404, { 'Content-Type': 'text/html' });
        res.end('<h1>404 Not Found</h1>', 'utf-8');
      } else {
        res.writeHead(500);
        res.end(`Server Error: ${error.code}`, 'utf-8');
      }
    } else {
      res.writeHead(200, { 'Content-Type': contentType });
      res.end(content, 'utf-8');
    }
  });
});

server.on('request', (req, _res) => {
  console.log(`📡 ${new Date().toISOString()} - ${req.method} ${req.url}`);
});

server.on('error', error => {
  console.error('❌ Server error:', error);
});

server.listen(PORT, () => {
  console.log(`🌤️ Poland Weather Data Lake running at:`);
  console.log(`   Local:   http://localhost:${PORT}`);
  console.log(`   Network: http://127.0.0.1:${PORT}`);
  console.log('');
  console.log('⚡ Features available:');
  console.log('   • Real-time weather data from Open-Meteo API');
  console.log('   • 16 major Polish cities');
  console.log('   • Current, hourly, and daily forecasts');
  console.log('   • Data pipeline status monitoring');
  console.log('');
  console.log(
    '🔧 Debug mode enabled - check browser console for detailed logs'
  );
  console.log('Press Ctrl+C to stop the server');
});
