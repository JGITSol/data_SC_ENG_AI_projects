"""Tests for Pendulum class"""
import pytest
import numpy as np
from src.pendulum import Pendulum


def test_initialization():
    """Test default initialization"""
    p = Pendulum()
    assert p.length == 1.0
    assert p.mass == 1.0
    assert p.angle == 0.2
    assert p.angular_velocity == 0.0


def test_angular_acceleration_gravity():
    """Test acceleration due to gravity only"""
    # Pendulum at 90 degrees (pi/2)
    # Torque = -mgL sin(theta)
    # I = mL^2
    # alpha = Torque/I = -g/L sin(theta)
    p = Pendulum(length=2.0, angle=np.pi/2, gravity=10.0)
    
    expected = -(10.0 / 2.0) * 1.0  # -5.0
    assert pytest.approx(p.angular_acceleration()) == expected


def test_angular_acceleration_damping():
    """Test acceleration with damping"""
    # Vertical position (no gravity torque) but moving
    p = Pendulum(angle=0.0, angular_velocity=2.0, damping=0.5)
    
    # alpha = -damping * omega
    expected = -0.5 * 2.0
    assert pytest.approx(p.angular_acceleration()) == expected


def test_energy_conservation_static():
    """Test energy calculation for static pendulum"""
    p = Pendulum(length=1.0, mass=2.0, angle=np.pi/2, angular_velocity=0.0)
    
    # KE should be 0
    assert p.kinetic_energy() == 0.0
    
    # PE = mgh = mgL(1 - cos(90)) = mgL
    expected_pe = 2.0 * 9.81 * 1.0
    assert pytest.approx(p.potential_energy()) == expected_pe
    assert pytest.approx(p.total_energy()) == expected_pe


def test_energy_conservation_moving():
    """Test energy calculation for moving pendulum at bottom"""
    p = Pendulum(length=1.0, mass=2.0, angle=0.0, angular_velocity=3.0)
    
    # PE should be 0 (at bottom)
    assert p.potential_energy() == 0.0
    
    # KE = 0.5 * I * w^2 = 0.5 * (mL^2) * w^2
    expected_ke = 0.5 * (2.0 * 1.0**2) * 3.0**2
    assert pytest.approx(p.kinetic_energy()) == expected_ke


def test_period_small_angle():
    """Test small angle period calculation"""
    p = Pendulum(length=1.0, gravity=9.81)
    expected = 2 * np.pi * np.sqrt(1.0 / 9.81)
    assert pytest.approx(p.period_small_angle()) == expected
