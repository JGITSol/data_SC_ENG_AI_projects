"""Tests for force calculations"""
import pytest
import numpy as np
from src.particle import Particle
from src.forces import (
    gravity_force, friction_force, spring_force, net_force, G_EARTH
)


def test_gravity_force():
    """Test gravitational force calculation"""
    p = Particle(mass=10.0, position=[0, 0])
    force = gravity_force(p)
    
    # Force should be [0, -m*g]
    expected = np.array([0.0, -10.0 * G_EARTH])
    assert np.allclose(force, expected)


def test_gravity_force_custom_g():
    """Test gravity with custom acceleration"""
    p = Particle(mass=5.0)
    force = gravity_force(p, g=1.62)  # Moon gravity
    
    expected = np.array([0.0, -5.0 * 1.62])
    assert np.allclose(force, expected)


def test_friction_force_stationary():
    """Test friction is zero for stationary particle"""
    p = Particle(mass=1.0, velocity=[0.0, 0.0])
    force = friction_force(p)
    
    assert np.allclose(force, [0.0, 0.0])


def test_friction_force_moving():
    """Test friction opposes motion"""
    p = Particle(mass=2.0, velocity=[3.0, 0.0])
    force = friction_force(p, coefficient=0.1)
    
    # Friction should point opposite to velocity
    assert force[0] < 0  # Opposes positive x velocity
    assert pytest.approx(force[1]) == 0.0


def test_friction_magnitude():
    """Test friction force magnitude"""
    p = Particle(mass=2.0, velocity=[10.0, 0.0])
    coeff = 0.2
    force = friction_force(p, coefficient=coeff)
    
    expected_magnitude = coeff * p.mass * G_EARTH
    actual_magnitude = np.linalg.norm(force)
    assert pytest.approx(actual_magnitude) == expected_magnitude


def test_spring_force_at_rest():
    """Test spring force is zero at rest length"""
    p = Particle(position=[5.0, 0.0])
    anchor = np.array([0.0, 0.0])
    force = spring_force(p, anchor, k=10.0, rest_length=5.0)
    
    # At rest length, force should be zero
    assert np.allclose(force, [0.0, 0.0], atol=1e-6)


def test_spring_force_stretched():
    """Test spring force when stretched"""
    p = Particle(position=[10.0, 0.0])
    anchor = np.array([0.0, 0.0])
    k = 5.0
    rest_length = 5.0
    force = spring_force(p, anchor, k=k, rest_length=rest_length)
    
    # Spring stretched by 5.0m, force should pull back
    assert force[0] < 0  # Points toward anchor
    expected_magnitude = k * 5.0  # F = k * extension
    assert pytest.approx(np.linalg.norm(force)) == expected_magnitude


def test_spring_force_compressed():
    """Test spring force when compressed"""
    p = Particle(position=[2.0, 0.0])
    anchor = np.array([0.0, 0.0])
    k = 10.0
    rest_length = 5.0
    force = spring_force(p, anchor, k=k, rest_length=rest_length)
    
    # Spring compressed, force should push away
    assert force[0] > 0  # Points away from anchor


def test_net_force_single():
    """Test net force with single force"""
    f1 = np.array([1.0, 2.0])
    result = net_force(f1)
    assert np.allclose(result, f1)


def test_net_force_multiple():
    """Test net force with multiple forces"""
    f1 = np.array([1.0, 2.0])
    f2 = np.array([3.0, -1.0])
    f3 = np.array([-2.0, 4.0])
    
    result = net_force(f1, f2, f3)
    expected = np.array([2.0, 5.0])
    assert np.allclose(result, expected)


def test_combined_forces():
    """Test realistic combination of forces"""
    p = Particle(mass=1.0, position=[0, 10], velocity=[2.0, 0])
    
    # Apply gravity and friction
    fg = gravity_force(p)
    ff = friction_force(p, coefficient=0.05)
    total = net_force(fg, ff)
    
    # Should have downward gravity and backward friction
    assert total[1] < 0  # Gravity pulls down
    assert total[0] < 0  # Friction opposes forward velocity
