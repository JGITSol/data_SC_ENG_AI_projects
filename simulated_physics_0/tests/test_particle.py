"""Tests for Particle class"""
import pytest
import numpy as np
from src.particle import Particle


def test_particle_initialization():
    """Test particle initialization with default values"""
    p = Particle()
    assert p.mass == 1.0
    assert np.allclose(p.position, [0.0, 0.0])
    assert np.allclose(p.velocity, [0.0, 0.0])


def test_particle_custom_values():
    """Test particle initialization with custom values"""
    p = Particle(mass=2.5, position=[1.0, 2.0], velocity=[3.0, 4.0])
    assert p.mass == 2.5
    assert np.allclose(p.position, [1.0, 2.0])
    assert np.allclose(p.velocity, [3.0, 4.0])


def test_apply_force():
    """Test force application updates acceleration correctly"""
    p = Particle(mass=2.0)
    force = np.array([4.0, 6.0])
    p.apply_force(force)
    
    expected_acceleration = force / p.mass
    assert np.allclose(p.acceleration, expected_acceleration)


def test_kinetic_energy():
    """Test kinetic energy calculation"""
    p = Particle(mass=2.0, velocity=[3.0, 4.0])
    # KE = 0.5 * m * v^2 = 0.5 * 2.0 * (3^2 + 4^2) = 0.5 * 2.0 * 25 = 25.0
    assert pytest.approx(p.kinetic_energy()) == 25.0


def test_kinetic_energy_zero():
    """Test kinetic energy is zero for stationary particle"""
    p = Particle(mass=1.0, velocity=[0.0, 0.0])
    assert p.kinetic_energy() == 0.0


def test_momentum():
    """Test momentum calculation"""
    p = Particle(mass=2.0, velocity=[3.0, 4.0])
    expected_momentum = np.array([6.0, 8.0])
    assert np.allclose(p.momentum(), expected_momentum)


def test_momentum_conservation():
    """Test that momentum equals mass times velocity"""
    p = Particle(mass=5.0, velocity=[1.0, -2.0])
    assert np.allclose(p.momentum(), p.mass * p.velocity)
