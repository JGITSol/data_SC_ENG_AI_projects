"""Tests for numerical integration methods"""
import pytest
import numpy as np
from src.particle import Particle
from src.integrator import euler_step, verlet_step, rk4_step
from src.forces import gravity_force


def test_euler_step_updates_position():
    """Test Euler integration updates position"""
    p = Particle(position=[0, 10], velocity=[5, 0])
    force = np.array([0, -9.81])
    dt = 0.1
    
    initial_pos = p.position.copy()
    euler_step(p, force, dt)
    
    # Position should have changed
    assert not np.allclose(p.position, initial_pos)


def test_euler_step_updates_velocity():
    """Test Euler integration updates velocity"""
    p = Particle(position=[0, 10], velocity=[5, 0])
    force = np.array([0, -9.81])
    dt = 0.1
    
    initial_vel = p.velocity.copy()
    euler_step(p, force, dt)
    
    # Velocity should have changed due to force
    assert not np.allclose(p.velocity, initial_vel)


def test_euler_step_free_fall():
    """Test Euler integration for free fall"""
    p = Particle(mass=1.0, position=[0, 100], velocity=[0, 0])
    force = gravity_force(p)
    dt = 0.1
    
    euler_step(p, force, dt)
    
    # After one step, velocity should be negative (falling)
    assert p.velocity[1] < 0
    # Position should have decreased
    assert p.position[1] < 100


def test_euler_constant_velocity():
    """Test Euler with no force maintains constant velocity"""
    p = Particle(position=[0, 0], velocity=[10, 5])
    force = np.array([0, 0])
    dt = 0.1
    
    initial_velocity = p.velocity.copy()
    euler_step(p, force, dt)
    
    # Velocity should remain constant with no force
    assert np.allclose(p.velocity, initial_velocity)
    # Position should increase by v*dt
    expected_pos = np.array([0, 0]) + initial_velocity * dt
    assert np.allclose(p.position, expected_pos)


def test_verlet_first_step():
    """Test Verlet falls back to Euler on first step"""
    p = Particle(position=[0, 10], velocity=[5, 0])
    force = np.array([0, -9.81])
    dt = 0.1
    
    # First step with no previous position
    verlet_step(p, force, dt, previous_position=None)
    
    # Should update position
    assert p.position[0] > 0
    assert p.position[1] < 10


def test_verlet_with_previous():
    """Test Verlet integration with previous position"""
    p = Particle(position=[1.0, 9.5], velocity=[5, -0.5])
    force = np.array([0, -9.81])
    dt = 0.1
    prev_pos = np.array([0.5, 10.0])
    
    verlet_step(p, force, dt, previous_position=prev_pos)
    
    # Position should continue moving
    assert p.position[0] > 1.0


def test_rk4_step():
    """Test RK4 integration"""
    p = Particle(mass=1.0, position=[0, 10], velocity=[5, 0])
    
    def force_func(particle):
        return gravity_force(particle)
    
    dt = 0.1
    initial_pos = p.position.copy()
    
    rk4_step(p, force_func, dt)
    
    # Position should have changed
    assert not np.allclose(p.position, initial_pos)
    # Should be moving forward and falling
    assert p.position[0] > initial_pos[0]
    assert p.position[1] < initial_pos[1]


def test_integration_energy_conservation():
    """Test that total energy is approximately conserved"""
    p = Particle(mass=1.0, position=[0, 10], velocity=[0, 0])
    
    def force_func(particle):
        return gravity_force(particle)
    
    # Calculate initial total energy
    ke_initial = p.kinetic_energy()
    pe_initial = p.mass * 9.81 * p.position[1]
    total_initial = ke_initial + pe_initial
    
    # Run several steps
    dt = 0.01
    for _ in range(10):
        rk4_step(p, force_func, dt)
    
    # Calculate final total energy
    ke_final = p.kinetic_energy()
    pe_final = p.mass * 9.81 * p.position[1]
    total_final = ke_final + pe_final
    
    # Energy should be approximately conserved (within 1%)
    assert pytest.approx(total_final, rel=0.01) == total_initial


def test_different_timesteps():
    """Test that smaller timesteps give more accurate results"""
    # Run with large timestep
    p1 = Particle(mass=1.0, position=[0, 10], velocity=[0, 0])
    force = gravity_force(p1)
    for _ in range(10):
        euler_step(p1, force, dt=0.1)
    
    # Run with small timestep
    p2 = Particle(mass=1.0, position=[0, 10], velocity=[0, 0])
    for _ in range(100):
        force = gravity_force(p2)
        euler_step(p2, force, dt=0.01)
    
    # Both should be falling, but won't be exactly the same
    assert p1.position[1] < 10
    assert p2.position[1] < 10
    assert p1.velocity[1] < 0
    assert p2.velocity[1] < 0
