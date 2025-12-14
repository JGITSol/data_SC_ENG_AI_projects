"""Tests for pendulum simulator"""
import pytest
import numpy as np
from src.pendulum import Pendulum
from src.simulator import rk4_step, run_simulation


def test_rk4_step_updates_state():
    """Test that RK4 step updates pendulum state"""
    p = Pendulum(angle=0.5, angular_velocity=0.0)
    initial_angle = p.angle
    
    rk4_step(p, dt=0.1)
    
    # Angle should decrease (swinging down)
    assert p.angle < initial_angle
    # Velocity should become negative
    assert p.angular_velocity < 0


def test_simulation_runs():
    """Test full simulation execution"""
    p = Pendulum()
    duration = 1.0
    dt = 0.1
    
    results = run_simulation(p, duration, dt)
    
    expected_steps = int(duration / dt)
    assert len(results['time']) == expected_steps
    assert len(results['angle']) == expected_steps
    assert len(results['total_energy']) == expected_steps


def test_energy_conservation():
    """Test energy conservation in simulation (no damping)"""
    p = Pendulum(damping=0.0)
    results = run_simulation(p, duration=2.0, dt=0.01)
    
    energies = results['total_energy']
    initial_energy = energies[0]
    final_energy = energies[-1]
    
    # Energy should be conserved within numerical error
    # RK4 is very accurate, so error should be small
    assert pytest.approx(final_energy, rel=1e-4) == initial_energy


def test_damping_energy_loss():
    """Test that damping reduces total energy"""
    p = Pendulum(damping=0.5)
    results = run_simulation(p, duration=5.0, dt=0.01)
    
    energies = results['total_energy']
    assert energies[-1] < energies[0]
