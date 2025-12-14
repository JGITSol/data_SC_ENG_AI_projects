# Applied Mathematics 5: Stochastic Processes

## Overview
Advanced implementation of stochastic processes, Monte Carlo methods, and probabilistic models for simulating random phenomena.

## Features
- **Random Walk**: 1D and 2D simulations
- **Brownian Motion**: Standard and geometric Brownian motion
- **Markov Chains**: Discrete and continuous time
- **Monte Carlo Methods**: Integration, variance reduction
- **Stochastic Differential Equations (SDEs)**: Euler-Maruyama method
- **Queueing Theory**: M/M/1, M/M/c queues

## Mathematical Topics
- Probability theory
- Random processes
- Markov properties
- Ito calculus
- Stochastic integration
- Martingales

## Key Equations
- `dX_t = μdt + σdW_t` (Ito SDE)
- `P(X_{n+1}=j | X_n=i) = p_{ij}` (Markov chain)
- `E[X_T] = X_0e^{μT}` (Geometric Brownian motion)

## Applications
- Financial modeling (Black-Scholes)
- Risk analysis
- Queueing systems
- Physics simulations

## Installation
```bash
pip install -r requirements.txt
```

## License
MIT License
