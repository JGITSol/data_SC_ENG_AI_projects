import http from 'http';
import fs from 'fs';
import path from 'path';

const PORT = 3002;

const server = http.createServer((req, res) => {
    // Industry-standard health endpoint
    if (req.url === '/health') {
        res.writeHead(200, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({ status: 'ok' }));
        return;
    }
    // Obsługa endpointu /api/poland-gdp
    if (req.url.startsWith('/api/poland-gdp')) {
        // Prosty cache w pamięci na 1h
        if (!global._gdpCache) global._gdpCache = { value: null, timestamp: 0 };
        const now = Date.now();
        if (global._gdpCache.value && now - global._gdpCache.timestamp < 3600 * 1000) {
            res.writeHead(200, { 'Content-Type': 'application/json' });
            res.end(global._gdpCache.value);
            return;
        }
        fetch('https://api.worldbank.org/v2/country/PL/indicator/NY.GDP.PCAP.CD?format=json&date=2022')
            .then(apiRes => apiRes.json())
            .then(data => {
                const value = data?.[1]?.[0]?.value;
                const year = data?.[1]?.[0]?.date;
                if (!value || !year) {
                    res.writeHead(500, { 'Content-Type': 'application/json' });
                    res.end(JSON.stringify({ error: 'No GDP data' }));
                    return;
                }
                const result = JSON.stringify({ country: 'Poland', year, gdp_per_capita_usd: value });
                global._gdpCache = { value: result, timestamp: now };
                res.writeHead(200, { 'Content-Type': 'application/json' });
                res.end(result);
            })
            .catch(() => {
                res.writeHead(500, { 'Content-Type': 'application/json' });
                res.end(JSON.stringify({ error: 'Failed to fetch GDP data' }));
            });
        return;
    }
    // Set CORS headers
    res.setHeader('Access-Control-Allow-Origin', '*');
    res.setHeader('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE');
    res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

    let filePath = '.' + req.url;
    if (filePath === './') {
        filePath = './index.html';
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
        '.wasm': 'application/wasm'
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

server.on('request', (req, res) => {
    console.log(`📡 ${new Date().toISOString()} - ${req.method} ${req.url}`);
});

server.on('error', (error) => {
    console.error('❌ Server error:', error);
});

server.listen(PORT, () => {
    console.log(`🚀 Poland Living Standards Dashboard running at:`);
    console.log(`   Local:   http://localhost:${PORT}`);
    console.log(`   Network: http://127.0.0.1:${PORT}`);
    console.log('');
    console.log('📊 Features available:');
    console.log('   • Interactive cost of living charts');
    console.log('   • Real-time data from multiple sources');
    console.log('   • EU comparison analysis');
    console.log('   • 16 major Polish cities');
    console.log('');
    console.log('🔧 Debug mode enabled - check browser console for detailed logs');
    console.log('Press Ctrl+C to stop the server');
});