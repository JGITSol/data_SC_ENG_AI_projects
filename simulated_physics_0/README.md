# Physics Simulator

## Overview
A deterministic physics engine simulating rigid body dynamics using Verlet integration. Designed for educational simulations of particle systems, orbital mechanics, and collisions.

## Features
- **Integration**: Verlet and Euler solvers for stable trajectory simulation.
- **Forces**: Gravity, Drag, Spring, and custom force fields.
- **Collision**: Basic ground collision and restitution.
- **Interactive UI**: Streamlit dashboard for real-time parameter tuning.

## Tech Stack
- **Language**: Python 3.10+
- **Libraries**: NumPy, Matplotlib
- **UI**: Streamlit
- **Testing**: Pytest

## Getting Started

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run Interactive Lab**
   ```bash
   streamlit run streamlit_app.py
   ```

3. **Run Tests**
   ```bash
   pytest
   ```

## License
MIT
