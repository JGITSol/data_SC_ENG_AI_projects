# Cost Living Chart (Data Science)

## Overview
An interactive data visualization dashboard comparing living costs and quality of life metrics across Polish cities. Built with Vue.js and Chart.js, it consumes data from the Data Engineering pipeline.

## Features
- **Interactive Charts**: Dynamic bar and radar charts using Chart.js.
- **Real-time Data**: Fetches latest metrics from the Cloudflare Workers API.
- **Comparative Analysis**: Side-by-side city comparison tools.
- **Responsive UI**: Mobile-friendly dashboard layout.

## Tech Stack
- **Frontend**: Vue.js 3 (Composition API)
- **Visualization**: Chart.js
- **Hosting**: Cloudflare Pages
- **API Integration**: Fetch API

## Getting Started

1. **Install Dependencies**
   ```bash
   npm install
   ```

2. **Local Development**
   ```bash
   npx wrangler pages dev .
   ```

3. **Deploy**
   ```bash
   npx wrangler pages deploy .
   ```

## License
MIT
