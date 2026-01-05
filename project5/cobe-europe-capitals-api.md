# Cobe Globe API Documentation: Europe Capitals Visualization

Complete guide for rendering an interactive, zoomable Europe globe with capital city markers using Cobe.js. Cobe is a lightweight (5KB gzipped), WebGL-powered globe library that uses Canvas 2D for rendering.

---

## Table of Contents

1. [Overview](#overview)
2. [Installation & Setup](#installation--setup)
3. [Core API Reference](#core-api-reference)
4. [Configuration Parameters](#configuration-parameters)
5. [Markers System](#markers-system)
6. [Europe Zoom Implementation](#europe-zoom-implementation)
7. [Rendering Loop & Animation](#rendering-loop--animation)
8. [Labels & Text Overlays](#labels--text-overlays)
9. [Interactive Controls](#interactive-controls)
10. [Performance Optimization](#performance-optimization)
11. [Complete Example](#complete-example)

---

## Overview

### What is Cobe?

Cobe is a lightweight, high-performance 3D globe renderer optimized for:
- **Minimal footprint**: ~5KB gzipped
- **WebGL rendering**: Hardware-accelerated 3D graphics
- **Canvas-based map dots**: Customizable population density visualization
- **Marker system**: Built-in support for location pins
- **Animation-friendly**: Designed for smooth rotations and pans

### Use Case: European Capitals

This documentation covers rendering multiple European capital cities as markers on a globe, with:
- Auto-zoomed view of Europe
- Interactive marker placement
- Capital name labels with hover effects
- Smooth camera animation from world view to Europe view

---

## Installation & Setup

### NPM/Package Manager

```bash
npm install cobe
# or
yarn add cobe
# or
pnpm add cobe
```

### CDN (Browser Direct)

```html
<script src="https://cdn.jsdelivr.net/npm/cobe@1.0.0/dist/cobe.umd.js"></script>
```

### Basic HTML Structure

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Cobe - European Capitals</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            background: #0f0f0f;
            color: #fff;
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
        }

        #canvas {
            display: block;
            width: 100%;
            height: 100vh;
        }

        #info {
            position: absolute;
            top: 20px;
            left: 20px;
            background: rgba(0, 0, 0, 0.7);
            padding: 20px;
            border-radius: 8px;
            max-width: 300px;
        }

        #info h2 {
            margin-bottom: 10px;
            font-size: 18px;
        }

        #info p {
            font-size: 14px;
            line-height: 1.6;
            color: #ccc;
        }

        .controls {
            position: absolute;
            bottom: 30px;
            left: 50%;
            transform: translateX(-50%);
            display: flex;
            gap: 10px;
            background: rgba(0, 0, 0, 0.8);
            padding: 15px;
            border-radius: 8px;
        }

        button {
            padding: 8px 16px;
            background: #2196F3;
            color: white;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-size: 14px;
            transition: background 0.3s ease;
        }

        button:hover {
            background: #1976D2;
        }

        button:active {
            background: #1565C0;
        }

        .marker-label {
            position: absolute;
            font-size: 12px;
            font-weight: 500;
            background: rgba(0, 0, 0, 0.8);
            padding: 4px 8px;
            border-radius: 4px;
            pointer-events: none;
            white-space: nowrap;
            transform: translate(-50%, -100%);
            opacity: 0;
            transition: opacity 0.2s ease;
        }

        .marker-label.visible {
            opacity: 1;
        }
    </style>
</head>
<body>
    <div id="info">
        <h2>European Capitals</h2>
        <p>Hover over markers to see capital names. Use mouse to drag and rotate.</p>
    </div>

    <div id="canvas-container" style="position: relative; width: 100%; height: 100vh;">
        <canvas id="canvas"></canvas>
        <div id="labels-container" style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; pointer-events: none;"></div>
    </div>

    <div class="controls">
        <button onclick="resetView()">Reset View</button>
        <button onclick="zoomToEurope()">Focus Europe</button>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/cobe@1.0.0/dist/cobe.umd.js"></script>
    <script src="globe.js"></script>
</body>
</html>
```

---

## Core API Reference

### Cobe Constructor

```javascript
const globe = cobe.default({
    canvas: HTMLCanvasElement,
    onRender: (state) => void
});
```

### Configuration Object Structure

```typescript
interface CobeConfig {
    // Canvas element reference
    canvas: HTMLCanvasElement;

    // Rendering callback (called every frame)
    onRender: (state: RenderState) => void;

    // Canvas resolution multiplier for high-DPI displays
    devicePixelRatio?: number;
    
    // Camera rotation angles (spherical coordinates)
    phi?: number;      // Azimuth: 0 to 2π
    theta?: number;    // Polar: -π to π
    
    // Visual appearance
    dark?: number;     // Dark mode intensity (0-1)
    diffuse?: number;  // Diffuse lighting intensity (0-1)
    
    // Map rendering settings
    mapSamples?: number;      // Number of population density dots (0-100000)
    mapBrightness?: number;   // Brightness of map dots (0-1+)
    mapBaseBrightness?: number; // Brightness of non-mapped areas (0-1+)
    
    // Colors (RGB format: 0-1 range)
    baseColor?: [r: number, g: number, b: number];
    markerColor?: [r: number, g: number, b: number];
    glowColor?: [r: number, g: number, b: number];
    
    // Scale and position
    scale?: number;            // Globe size multiplier (0.5-3+)
    offset?: [x: number, y: number]; // Canvas offset in pixels
    
    // Marker definitions
    markers?: Marker[];        // Array of marker objects
    
    // Texture opacity
    opacity?: number;          // Texture transparency (0-1)
}

interface RenderState {
    phi: number;       // Current azimuth angle
    theta: number;     // Current polar angle
    width: number;     // Canvas width
    height: number;    // Canvas height
}

interface Marker {
    location: [lat: number, lon: number]; // [latitude, longitude]
    size?: number;     // Marker size multiplier (default: 1.0)
}
```

---

## Configuration Parameters

### Understanding Camera Angles

**Phi (φ) - Azimuth (Horizontal Rotation)**
- Range: `0` to `2π` (0° to 360°)
- `0`: Prime Meridian facing right
- `π/2`: Europe visible
- `π`: Prime Meridian facing left (Americas)
- `3π/2`: Asia-Pacific visible

**Theta (θ) - Polar (Vertical Rotation)**
- Range: `-π` to `π` (-180° to 180°)
- `0`: Equator view
- `π/2`: North Pole
- `-π/2`: South Pole

### European View Coordinates

```javascript
// World view (default)
const worldView = {
    phi: 0,
    theta: 0.5
};

// Europe-focused view
const europeView = {
    phi: Math.PI / 2,    // 90° rotation to show Europe
    theta: Math.PI / 4   // 45° tilt
};

// Europe rotated for optimal viewing
const europtimalView = {
    phi: Math.PI / 2.2,  // Slightly adjusted
    theta: 0.4           // Shallower angle
};
```

### Color Format Explanation

Colors in Cobe use **normalized RGB** (0.0 to 1.0 per channel):

```javascript
// Red: [1, 0, 0]
const red = [1, 0, 0];

// Green: [0, 1, 0]
const green = [0, 1, 0];

// Blue: [0, 0, 1]
const blue = [0, 0, 1];

// White: [1, 1, 1]
const white = [1, 1, 1];

// Black: [0, 0, 0]
const black = [0, 0, 0];

// Custom: Teal
const teal = [0.2, 0.8, 0.9];

// Helper function to convert
function hexToRgb(hex) {
    const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
    if (!result) return [0, 0, 0];
    return [
        parseInt(result[1], 16) / 255,
        parseInt(result[2], 16) / 255,
        parseInt(result[3], 16) / 255
    ];
}

// Usage: hexToRgb("#1E90FF") → [0.12, 0.565, 1]
```

---

## Markers System

### Marker Object Structure

```javascript
const marker = {
    // Required: Location in [latitude, longitude] format
    location: [51.5074, -0.1278],  // London
    
    // Optional: Size multiplier (default 1.0)
    // Useful for emphasizing certain capitals
    size: 1.2,
    
    // Optional: Custom metadata (not used by Cobe, for your app)
    name: "London",
    country: "United Kingdom"
};
```

### Coordinate System

- **Latitude**: -90 (South Pole) to +90 (North Pole)
- **Longitude**: -180 (West) to +180 (East)

### European Capitals Marker Dataset

```javascript
const europeanCapitals = [
    { location: [48.8566, 2.3522], name: "Paris", country: "France" },
    { location: [52.5200, 13.4050], name: "Berlin", country: "Germany" },
    { location: [48.2082, 16.3738], name: "Vienna", country: "Austria" },
    { location: [47.4979, 19.0402], name: "Budapest", country: "Hungary" },
    { location: [50.0755, 14.4378], name: "Prague", country: "Czech Republic" },
    { location: [52.2297, 21.0122], name: "Warsaw", country: "Poland" },
    { location: [54.6872, 25.2797], name: "Vilnius", country: "Lithuania" },
    { location: [59.3293, 18.0686], name: "Stockholm", country: "Sweden" },
    { location: [60.1699, 24.9384], name: "Helsinki", country: "Finland" },
    { location: [55.7558, 37.6173], name: "Moscow", country: "Russia" },
    { location: [59.9139, 10.7522], name: "Oslo", country: "Norway" },
    { location: [51.2194, 6.7760], name: "Düsseldorf", country: "Germany (Düsseldorf)" }, // Alt. capital
    { location: [41.3851, 2.1734], name: "Barcelona", country: "Spain (Barcelona)" },
    { location: [41.9028, 12.4964], name: "Rome", country: "Italy" },
    { location: [40.4168, -3.7038], name: "Madrid", country: "Spain" },
    { location: [38.7223, -9.1393], name: "Lisbon", country: "Portugal" },
    { location: [39.4699, -0.3763], name: "Valencia", country: "Spain (Valencia)" },
    { location: [43.3528, -8.3826], name: "Santiago", country: "Spain (Santiago de Compostela)" },
    { location: [50.8503, 4.3517], name: "Brussels", country: "Belgium" },
    { location: [52.0705, 4.3007], name: "The Hague", country: "Netherlands" },
    { location: [46.9479, 7.4474], name: "Bern", country: "Switzerland" },
    { location: [45.4642, 9.1900], name: "Milan", country: "Italy (Milan)" },
    { location: [43.2965, 5.3698], name: "Marseille", country: "France (Marseille)" },
    { location: [43.7384, 7.4246], name: "Nice", country: "France (Nice)" },
    { location: [46.2041, 6.1431], name: "Geneva", country: "Switzerland (Geneva)" },
    { location: [45.5017, -73.5673], name: "Quebec", country: "Canada" }, // Out of scope - example removal
];

// Filter to actual European capitals only
const majorEuropeanCapitals = [
    { location: [48.8566, 2.3522], name: "Paris", country: "France" },
    { location: [52.5200, 13.4050], name: "Berlin", country: "Germany" },
    { location: [48.2082, 16.3738], name: "Vienna", country: "Austria" },
    { location: [47.4979, 19.0402], name: "Budapest", country: "Hungary" },
    { location: [50.0755, 14.4378], name: "Prague", country: "Czech Republic" },
    { location: [52.2297, 21.0122], name: "Warsaw", country: "Poland" },
    { location: [54.6872, 25.2797], name: "Vilnius", country: "Lithuania" },
    { location: [59.3293, 18.0686], name: "Stockholm", country: "Sweden" },
    { location: [60.1699, 24.9384], name: "Helsinki", country: "Finland" },
    { location: [55.7558, 37.6173], name: "Moscow", country: "Russia" },
    { location: [59.9139, 10.7522], name: "Oslo", country: "Norway" },
    { location: [50.8503, 4.3517], name: "Brussels", country: "Belgium" },
    { location: [52.0705, 4.3007], name: "Amsterdam", country: "Netherlands" },
    { location: [46.9479, 7.4474], name: "Bern", country: "Switzerland" },
    { location: [41.9028, 12.4964], name: "Rome", country: "Italy" },
    { location: [40.4168, -3.7038], name: "Madrid", country: "Spain" },
    { location: [38.7223, -9.1393], name: "Lisbon", country: "Portugal" },
    { location: [50.8503, 4.3517], name: "Brussels", country: "Belgium" },
];
```

---

## Europe Zoom Implementation

### Smooth Camera Animation

```javascript
// Animate camera from world view to Europe view
function animateCameraToEurope(globe, duration = 2000) {
    const startTime = Date.now();
    
    // Start position (world view)
    const startPhi = 0;
    const startTheta = 0.5;
    
    // End position (Europe optimal view)
    const endPhi = Math.PI / 2.2;
    const endTheta = 0.4;
    
    const animationFrame = () => {
        const elapsed = Date.now() - startTime;
        const progress = Math.min(elapsed / duration, 1);
        
        // Easing function: ease-out-cubic
        const easeProgress = 1 - Math.pow(1 - progress, 3);
        
        // Interpolate angles
        globe.phi = startPhi + (endPhi - startPhi) * easeProgress;
        globe.theta = startTheta + (endTheta - startTheta) * easeProgress;
        
        if (progress < 1) {
            requestAnimationFrame(animationFrame);
        }
    };
    
    animationFrame();
}

// Alternative: Using cubic Bezier easing
function easeOutQuad(t) {
    return 1 - (1 - t) * (1 - t);
}

function animateCameraSmooth(globe, targetPhi, targetTheta, duration = 1500) {
    const startTime = Date.now();
    const startPhi = globe.phi;
    const startTheta = globe.theta;
    
    const animate = () => {
        const now = Date.now();
        const elapsed = now - startTime;
        const progress = Math.min(elapsed / duration, 1);
        const ease = easeOutQuad(progress);
        
        globe.phi = startPhi + (targetPhi - startPhi) * ease;
        globe.theta = startTheta + (targetTheta - startTheta) * ease;
        
        if (progress < 1) {
            requestAnimationFrame(animate);
        }
    };
    
    animate();
}
```

### Viewport Constraints

To prevent users from rotating away from Europe:

```javascript
function constrainViewToEurope(phi, theta) {
    // Europe is roughly between phi: π/2.5 to π/1.8
    const minPhi = Math.PI / 2.5;
    const maxPhi = Math.PI / 1.8;
    
    // Latitude constraints: Europe is between ~35°N to ~70°N
    const minTheta = 0.2;  // ~35°
    const maxTheta = 1.2;  // ~70°
    
    return {
        phi: Math.max(minPhi, Math.min(maxPhi, phi)),
        theta: Math.max(minTheta, Math.min(maxTheta, theta))
    };
}
```

---

## Rendering Loop & Animation

### Basic Rendering Loop

```javascript
let globeInstance = null;

function initGlobe() {
    const canvas = document.getElementById('canvas');
    
    globeInstance = cobe.default({
        canvas: canvas,
        
        // Rendering callback - called every frame
        onRender: (state) => {
            // state contains: { phi, theta, width, height }
            // This is where you update labels, check interactions, etc.
        },
        
        // Initial camera position
        phi: 0,
        theta: 0.5,
        
        // Visual settings
        dark: 0.6,           // 60% dark mode
        diffuse: 1.0,        // Full diffuse lighting
        scale: 1.1,          // Slightly enlarged
        
        // Map quality
        mapSamples: 15000,   // Population density dots
        mapBrightness: 0.6,  // Moderate brightness
        mapBaseBrightness: 0.1,
        
        // Colors
        baseColor: [0.06, 0.06, 0.12],    // Deep blue-black
        markerColor: [0.2, 0.8, 0.9],     // Cyan
        glowColor: [0.2, 0.6, 1.0],       // Blue glow
        
        // Markers
        markers: majorEuropeanCapitals,
        
        // Device pixel ratio for high-DPI screens
        devicePixelRatio: window.devicePixelRatio
    });
}

// Auto-rotate globe
let autoRotate = true;
let rotationSpeed = 0.0003;

function updateGlobeRotation(state) {
    if (autoRotate && globeInstance) {
        globeInstance.phi += rotationSpeed;
        if (globeInstance.phi > Math.PI * 2) {
            globeInstance.phi -= Math.PI * 2;
        }
    }
}
```

### Animation State Management

```javascript
// Track animation state
const animationState = {
    isAnimating: false,
    currentView: 'world', // 'world' or 'europe'
    isDragging: false,
    lastX: 0,
    lastY: 0
};

// Mouse drag interaction
canvas.addEventListener('mousedown', (e) => {
    animationState.isDragging = true;
    animationState.lastX = e.clientX;
    animationState.lastY = e.clientY;
    autoRotate = false; // Stop auto-rotation when user drags
});

canvas.addEventListener('mousemove', (e) => {
    if (!animationState.isDragging || !globeInstance) return;
    
    const deltaX = (e.clientX - animationState.lastX) * 0.005;
    const deltaY = (e.clientY - animationState.lastY) * 0.005;
    
    globeInstance.phi -= deltaX;
    globeInstance.theta -= deltaY;
    
    // Apply constraints if zoomed to Europe
    if (animationState.currentView === 'europe') {
        const constrained = constrainViewToEurope(globeInstance.phi, globeInstance.theta);
        globeInstance.phi = constrained.phi;
        globeInstance.theta = constrained.theta;
    }
    
    animationState.lastX = e.clientX;
    animationState.lastY = e.clientY;
});

canvas.addEventListener('mouseup', () => {
    animationState.isDragging = false;
    autoRotate = true;
});
```

---

## Labels & Text Overlays

### Label Rendering System

**Note**: Cobe doesn't natively render text labels. You must project 3D coordinates to 2D canvas coordinates and render labels separately.

```javascript
// Helper function to project 3D globe coordinates to 2D canvas
function projectLocationToCanvas(lat, lon, canvasWidth, canvasHeight, phi, theta) {
    // Convert to radians
    const latRad = (lat * Math.PI) / 180;
    const lonRad = (lon * Math.PI) / 180;
    
    // 3D sphere coordinates
    const x3d = Math.cos(latRad) * Math.cos(lonRad);
    const y3d = Math.sin(latRad);
    const z3d = Math.cos(latRad) * Math.sin(lonRad);
    
    // Apply rotation (phi and theta)
    // Rotation matrix for spherical coordinates
    const cosPhi = Math.cos(phi);
    const sinPhi = Math.sin(phi);
    const cosTheta = Math.cos(theta);
    const sinTheta = Math.sin(theta);
    
    // Rotate around Y-axis (phi)
    let rotX = x3d * cosPhi + z3d * sinPhi;
    let rotZ = -x3d * sinPhi + z3d * cosPhi;
    let rotY = y3d;
    
    // Rotate around X-axis (theta)
    const finalX = rotX;
    const finalY = rotY * cosTheta - rotZ * sinTheta;
    const finalZ = rotY * sinTheta + rotZ * cosTheta;
    
    // Skip if point is behind camera
    if (finalZ < 0) return null;
    
    // Perspective projection
    const scale = 1.0 / (finalZ + 2);
    const screenX = (canvasWidth / 2) + (finalX * scale * canvasWidth * 0.4);
    const screenY = (canvasHeight / 2) - (finalY * scale * canvasHeight * 0.4);
    
    return { x: screenX, y: screenY, depth: finalZ };
}

// Render labels with Canvas 2D API
function renderLabels(canvas, state, markers) {
    const ctx = canvas.getContext('2d');
    
    // Clear previous labels
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    
    // Sort markers by depth for correct z-ordering
    const projectedMarkers = markers
        .map(marker => ({
            ...marker,
            projected: projectLocationToCanvas(
                marker.location[0],
                marker.location[1],
                canvas.width,
                canvas.height,
                state.phi,
                state.theta
            )
        }))
        .filter(m => m.projected !== null)
        .sort((a, b) => a.projected.depth - b.projected.depth);
    
    // Draw labels
    ctx.font = '12px system-ui, -apple-system, sans-serif';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'bottom';
    
    projectedMarkers.forEach(marker => {
        const { x, y } = marker.projected;
        
        // Label background
        ctx.fillStyle = 'rgba(0, 0, 0, 0.7)';
        ctx.fillRect(x - 50, y - 20, 100, 18);
        
        // Label text
        ctx.fillStyle = '#fff';
        ctx.fillText(marker.name, x, y - 4);
        
        // Marker dot
        ctx.fillStyle = '#4caf50';
        ctx.beginPath();
        ctx.arc(x, y, 3, 0, Math.PI * 2);
        ctx.fill();
    });
}
```

### Label DOM Overlay System (Alternative)

```javascript
// Using HTML DOM for labels (better for interactive tooltips)
const labelsContainer = document.getElementById('labels-container');

function updateLabelPositions(state, markers) {
    const canvas = document.getElementById('canvas');
    
    markers.forEach(marker => {
        const projected = projectLocationToCanvas(
            marker.location[0],
            marker.location[1],
            canvas.width,
            canvas.height,
            state.phi,
            state.theta
        );
        
        if (projected === null) {
            // Hide label if behind globe
            const label = document.getElementById(`label-${marker.name}`);
            if (label) label.classList.remove('visible');
            return;
        }
        
        // Get or create label element
        let label = document.getElementById(`label-${marker.name}`);
        if (!label) {
            label = document.createElement('div');
            label.id = `label-${marker.name}`;
            label.className = 'marker-label';
            label.innerHTML = `<strong>${marker.name}</strong><br><small>${marker.country}</small>`;
            labelsContainer.appendChild(label);
        }
        
        // Position label
        label.style.left = `${projected.x}px`;
        label.style.top = `${projected.y}px`;
        label.classList.add('visible');
    });
}

// Call in the onRender callback
function updateLabelsOnRender(state) {
    updateLabelPositions(state, majorEuropeanCapitals);
}
```

### Interactive Tooltips

```javascript
// Track hovered marker
let hoveredMarker = null;

canvas.addEventListener('mousemove', (e) => {
    const rect = canvas.getBoundingClientRect();
    const mouseX = e.clientX - rect.left;
    const mouseY = e.clientY - rect.top;
    
    // Check if mouse is near any marker
    hoveredMarker = null;
    
    majorEuropeanCapitals.forEach(marker => {
        const projected = projectLocationToCanvas(
            marker.location[0],
            marker.location[1],
            canvas.width,
            canvas.height,
            globeInstance.phi,
            globeInstance.theta
        );
        
        if (projected === null) return;
        
        // Distance from mouse to marker
        const dist = Math.hypot(
            mouseX - projected.x,
            mouseY - projected.y
        );
        
        // Hover radius: 20 pixels
        if (dist < 20) {
            hoveredMarker = marker;
            canvas.style.cursor = 'pointer';
        }
    });
    
    if (hoveredMarker === null) {
        canvas.style.cursor = 'grab';
    }
});

// Show tooltip for hovered marker
canvas.addEventListener('click', () => {
    if (hoveredMarker) {
        console.log(`Clicked: ${hoveredMarker.name}`);
        // Handle click - e.g., show details panel
    }
});
```

---

## Interactive Controls

### Programmatic Camera Control

```javascript
// Reset to world view
function resetView() {
    animationState.isAnimating = true;
    animationState.currentView = 'world';
    
    animateCameraSmooth(globeInstance, 0, 0.5, 1500);
    
    setTimeout(() => {
        animationState.isAnimating = false;
        autoRotate = true;
    }, 1500);
}

// Focus on Europe
function zoomToEurope() {
    animationState.isAnimating = true;
    animationState.currentView = 'europe';
    autoRotate = false;
    
    const targetPhi = Math.PI / 2.2;
    const targetTheta = 0.4;
    
    animateCameraSmooth(globeInstance, targetPhi, targetTheta, 1500);
    
    setTimeout(() => {
        animationState.isAnimating = false;
    }, 1500);
}

// Fly to specific capital
function flyToCapital(capitalName) {
    const capital = majorEuropeanCapitals.find(c => c.name === capitalName);
    if (!capital) return;
    
    // Calculate phi and theta to point at capital
    const lat = capital.location[0];
    const lon = capital.location[1];
    
    // Approximate phi and theta for viewing location
    let phi = (lon * Math.PI) / 180;
    let theta = (Math.PI / 2) - (lat * Math.PI) / 180;
    
    animationState.isAnimating = true;
    autoRotate = false;
    
    animateCameraSmooth(globeInstance, phi, theta, 2000);
    
    setTimeout(() => {
        animationState.isAnimating = false;
    }, 2000);
}
```

### Control Panel

```javascript
// Add keyboard shortcuts
document.addEventListener('keydown', (e) => {
    if (animationState.isAnimating) return;
    
    switch (e.key) {
        case 'r':
            resetView();
            break;
        case 'e':
            zoomToEurope();
            break;
        case ' ':
            autoRotate = !autoRotate;
            break;
        case 'ArrowUp':
            globeInstance.theta -= 0.1;
            break;
        case 'ArrowDown':
            globeInstance.theta += 0.1;
            break;
        case 'ArrowLeft':
            globeInstance.phi -= 0.1;
            break;
        case 'ArrowRight':
            globeInstance.phi += 0.1;
            break;
    }
});
```

---

## Performance Optimization

### Recommended Settings for Europe View

```javascript
const cobeConfig = {
    // Reduce map samples for better performance
    mapSamples: 8000,       // vs 15000 for world view
    
    // Slightly reduced brightness
    mapBrightness: 0.5,
    mapBaseBrightness: 0.05,
    
    // Lower diffuse for less computation
    diffuse: 0.8,
    
    // Appropriate scale for viewport
    scale: 1.2,
    
    // Use device pixel ratio for clarity
    devicePixelRatio: Math.min(window.devicePixelRatio, 2)
};
```

### Canvas Resizing

```javascript
function handleCanvasResize() {
    const canvas = document.getElementById('canvas');
    const container = canvas.parentElement;
    
    canvas.width = container.clientWidth;
    canvas.height = container.clientHeight;
    
    // Notify Cobe of size change
    if (globeInstance) {
        globeInstance.resize();
    }
}

window.addEventListener('resize', handleCanvasResize);
```

### Label Rendering Optimization

```javascript
// Only update labels every other frame if performance is an issue
let frameCount = 0;
const labelUpdateFrequency = 2; // Update every 2 frames

function onRender(state) {
    frameCount++;
    
    if (frameCount % labelUpdateFrequency === 0) {
        updateLabelPositions(state, majorEuropeanCapitals);
    }
    
    updateGlobeRotation(state);
}
```

---

## Complete Example

### Full Working Implementation

```javascript
// globe.js - Complete implementation

// ====== Configuration ======
const EUROPEAN_CAPITALS = [
    { location: [48.8566, 2.3522], name: "Paris", country: "France" },
    { location: [52.5200, 13.4050], name: "Berlin", country: "Germany" },
    { location: [48.2082, 16.3738], name: "Vienna", country: "Austria" },
    { location: [47.4979, 19.0402], name: "Budapest", country: "Hungary" },
    { location: [50.0755, 14.4378], name: "Prague", country: "Czech Republic" },
    { location: [52.2297, 21.0122], name: "Warsaw", country: "Poland" },
    { location: [54.6872, 25.2797], name: "Vilnius", country: "Lithuania" },
    { location: [59.3293, 18.0686], name: "Stockholm", country: "Sweden" },
    { location: [60.1699, 24.9384], name: "Helsinki", country: "Finland" },
    { location: [55.7558, 37.6173], name: "Moscow", country: "Russia" },
    { location: [59.9139, 10.7522], name: "Oslo", country: "Norway" },
    { location: [50.8503, 4.3517], name: "Brussels", country: "Belgium" },
    { location: [52.0705, 4.3007], name: "Amsterdam", country: "Netherlands" },
    { location: [46.9479, 7.4474], name: "Bern", country: "Switzerland" },
    { location: [41.9028, 12.4964], name: "Rome", country: "Italy" },
    { location: [40.4168, -3.7038], name: "Madrid", country: "Spain" },
    { location: [38.7223, -9.1393], name: "Lisbon", country: "Portugal" },
];

const GLOBE_CONFIG = {
    dark: 0.6,
    diffuse: 1.0,
    scale: 1.1,
    mapSamples: 15000,
    mapBrightness: 0.6,
    mapBaseBrightness: 0.1,
    baseColor: [0.06, 0.06, 0.12],
    markerColor: [0.2, 0.8, 0.9],
    glowColor: [0.2, 0.6, 1.0],
};

// ====== State ======
let globeInstance = null;
const animationState = {
    isAnimating: false,
    currentView: 'world',
    isDragging: false,
    lastX: 0,
    lastY: 0
};

let autoRotate = true;
let rotationSpeed = 0.0003;
let hoveredMarker = null;

// ====== Initialization ======
function initGlobe() {
    const canvas = document.getElementById('canvas');
    
    globeInstance = cobe.default({
        canvas: canvas,
        onRender: onRender,
        phi: 0,
        theta: 0.5,
        ...GLOBE_CONFIG,
        markers: EUROPEAN_CAPITALS,
        devicePixelRatio: window.devicePixelRatio
    });
    
    setupEventListeners();
    handleCanvasResize();
    window.addEventListener('resize', handleCanvasResize);
}

function setupEventListeners() {
    const canvas = document.getElementById('canvas');
    
    canvas.addEventListener('mousedown', onMouseDown);
    canvas.addEventListener('mousemove', onMouseMove);
    canvas.addEventListener('mouseup', onMouseUp);
    canvas.addEventListener('mouseleave', onMouseLeave);
    canvas.addEventListener('click', onClick);
}

// ====== Mouse Events ======
function onMouseDown(e) {
    animationState.isDragging = true;
    animationState.lastX = e.clientX;
    animationState.lastY = e.clientY;
    autoRotate = false;
}

function onMouseMove(e) {
    const canvas = document.getElementById('canvas');
    const rect = canvas.getBoundingClientRect();
    const mouseX = e.clientX - rect.left;
    const mouseY = e.clientY - rect.top;
    
    // Check hover
    hoveredMarker = null;
    EUROPEAN_CAPITALS.forEach(marker => {
        const projected = projectLocationToCanvas(
            marker.location[0],
            marker.location[1],
            canvas.width,
            canvas.height,
            globeInstance.phi,
            globeInstance.theta
        );
        
        if (projected && Math.hypot(mouseX - projected.x, mouseY - projected.y) < 20) {
            hoveredMarker = marker;
        }
    });
    
    canvas.style.cursor = hoveredMarker ? 'pointer' : 'grab';
    
    // Handle drag
    if (!animationState.isDragging || !globeInstance) return;
    
    const deltaX = (e.clientX - animationState.lastX) * 0.005;
    const deltaY = (e.clientY - animationState.lastY) * 0.005;
    
    globeInstance.phi -= deltaX;
    globeInstance.theta -= deltaY;
    
    if (animationState.currentView === 'europe') {
        const constrained = constrainViewToEurope(globeInstance.phi, globeInstance.theta);
        globeInstance.phi = constrained.phi;
        globeInstance.theta = constrained.theta;
    }
    
    animationState.lastX = e.clientX;
    animationState.lastY = e.clientY;
}

function onMouseUp() {
    animationState.isDragging = false;
    autoRotate = true;
}

function onMouseLeave() {
    animationState.isDragging = false;
    canvas.style.cursor = 'default';
}

function onClick() {
    if (hoveredMarker) {
        console.log(`Clicked: ${hoveredMarker.name}, ${hoveredMarker.country}`);
    }
}

// ====== Rendering ======
function onRender(state) {
    if (autoRotate && !animationState.isDragging) {
        globeInstance.phi += rotationSpeed;
        if (globeInstance.phi > Math.PI * 2) {
            globeInstance.phi -= Math.PI * 2;
        }
    }
    
    updateLabelPositions(state);
}

// ====== Projection ======
function projectLocationToCanvas(lat, lon, canvasWidth, canvasHeight, phi, theta) {
    const latRad = (lat * Math.PI) / 180;
    const lonRad = (lon * Math.PI) / 180;
    
    const x3d = Math.cos(latRad) * Math.cos(lonRad);
    const y3d = Math.sin(latRad);
    const z3d = Math.cos(latRad) * Math.sin(lonRad);
    
    const cosPhi = Math.cos(phi);
    const sinPhi = Math.sin(phi);
    const cosTheta = Math.cos(theta);
    const sinTheta = Math.sin(theta);
    
    let rotX = x3d * cosPhi + z3d * sinPhi;
    let rotZ = -x3d * sinPhi + z3d * cosPhi;
    let rotY = y3d;
    
    const finalX = rotX;
    const finalY = rotY * cosTheta - rotZ * sinTheta;
    const finalZ = rotY * sinTheta + rotZ * cosTheta;
    
    if (finalZ < 0) return null;
    
    const scale = 1.0 / (finalZ + 2);
    const screenX = (canvasWidth / 2) + (finalX * scale * canvasWidth * 0.4);
    const screenY = (canvasHeight / 2) - (finalY * scale * canvasHeight * 0.4);
    
    return { x: screenX, y: screenY, depth: finalZ };
}

// ====== Labels ======
function updateLabelPositions(state) {
    const canvas = document.getElementById('canvas');
    const labelsContainer = document.getElementById('labels-container');
    
    EUROPEAN_CAPITALS.forEach(marker => {
        const projected = projectLocationToCanvas(
            marker.location[0],
            marker.location[1],
            canvas.width,
            canvas.height,
            state.phi,
            state.theta
        );
        
        let label = document.getElementById(`label-${marker.name}`);
        
        if (projected === null) {
            if (label) label.classList.remove('visible');
            return;
        }
        
        if (!label) {
            label = document.createElement('div');
            label.id = `label-${marker.name}`;
            label.className = 'marker-label';
            label.innerHTML = `<strong>${marker.name}</strong><br><small>${marker.country}</small>`;
            labelsContainer.appendChild(label);
        }
        
        label.style.left = `${projected.x}px`;
        label.style.top = `${projected.y}px`;
        label.classList.add('visible');
    });
}

// ====== Camera Animation ======
function animateCameraSmooth(targetPhi, targetTheta, duration = 1500) {
    const startTime = Date.now();
    const startPhi = globeInstance.phi;
    const startTheta = globeInstance.theta;
    
    const animate = () => {
        const elapsed = Date.now() - startTime;
        const progress = Math.min(elapsed / duration, 1);
        const ease = 1 - Math.pow(1 - progress, 3);
        
        globeInstance.phi = startPhi + (targetPhi - startPhi) * ease;
        globeInstance.theta = startTheta + (targetTheta - startTheta) * ease;
        
        if (progress < 1) {
            requestAnimationFrame(animate);
        }
    };
    
    animate();
}

function constrainViewToEurope(phi, theta) {
    const minPhi = Math.PI / 2.5;
    const maxPhi = Math.PI / 1.8;
    const minTheta = 0.2;
    const maxTheta = 1.2;
    
    return {
        phi: Math.max(minPhi, Math.min(maxPhi, phi)),
        theta: Math.max(minTheta, Math.min(maxTheta, theta))
    };
}

// ====== Controls ======
function resetView() {
    animationState.isAnimating = true;
    animationState.currentView = 'world';
    animateCameraSmooth(0, 0.5, 1500);
    
    setTimeout(() => {
        animationState.isAnimating = false;
        autoRotate = true;
    }, 1500);
}

function zoomToEurope() {
    animationState.isAnimating = true;
    animationState.currentView = 'europe';
    autoRotate = false;
    
    animateCameraSmooth(Math.PI / 2.2, 0.4, 1500);
    
    setTimeout(() => {
        animationState.isAnimating = false;
    }, 1500);
}

function handleCanvasResize() {
    const canvas = document.getElementById('canvas');
    const container = canvas.parentElement;
    
    canvas.width = container.clientWidth;
    canvas.height = container.clientHeight;
}

// ====== Startup ======
document.addEventListener('DOMContentLoaded', initGlobe);
```

---

## API Summary Table

| Property | Type | Range | Default | Description |
|----------|------|-------|---------|-------------|
| `canvas` | HTMLElement | — | Required | Canvas element reference |
| `onRender` | Function | — | Required | Render callback (state) |
| `phi` | Number | 0–2π | 0 | Azimuth angle (horizontal rotation) |
| `theta` | Number | -π–π | 0 | Polar angle (vertical rotation) |
| `dark` | Number | 0–1 | 0.5 | Dark mode intensity |
| `diffuse` | Number | 0–1+ | 1 | Diffuse lighting strength |
| `mapSamples` | Number | 0–100000 | 10000 | Population density dots |
| `mapBrightness` | Number | 0–1+ | 0.6 | Map dot brightness |
| `mapBaseBrightness` | Number | 0–1+ | 0.1 | Non-mapped area brightness |
| `baseColor` | [r,g,b] | 0–1 | [0.06, 0.06, 0.12] | Globe base color |
| `markerColor` | [r,g,b] | 0–1 | [1, 1, 1] | Marker color |
| `glowColor` | [r,g,b] | 0–1 | [1, 1, 1] | Glow color |
| `scale` | Number | 0.1–5 | 1 | Globe size multiplier |
| `offset` | [x,y] | Pixels | [0, 0] | Canvas offset |
| `markers` | Array | — | [] | Marker objects array |
| `opacity` | Number | 0–1 | 1 | Texture opacity |
| `devicePixelRatio` | Number | 1–2 | 1 | DPI multiplier |

---

## Best Practices

1. **Always constrain camera** when focusing on a region to prevent disorientation
2. **Use easing functions** for smooth animations (ease-out-cubic, ease-out-quad)
3. **Project coordinates in render loop** to keep labels in sync with camera
4. **Batch label updates** to avoid excessive DOM manipulation
5. **Handle window resize** to maintain canvas aspect ratio
6. **Reduce map samples** for mobile devices (<8000)
7. **Disable auto-rotation** when user is interacting
8. **Test label visibility** before rendering (check if location is behind globe)

---

## References

- **Cobe Library**: https://cobe.vercel.app
- **WebGL Concepts**: https://developer.mozilla.org/en-US/docs/Web/API/WebGL_API
- **Canvas 2D API**: https://developer.mozilla.org/en-US/docs/Web/API/Canvas_API
- **Spherical Coordinates**: https://en.wikipedia.org/wiki/Spherical_coordinate_system
