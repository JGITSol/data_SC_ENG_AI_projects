"""Pendulum class for angular motion simulation"""
import numpy as np


class Pendulum:
    """Simple pendulum with angular dynamics"""
    
    def __init__(
        self,
        length: float = 1.0,
        mass: float = 1.0,
        angle: float = 0.2,
        angular_velocity: float = 0.0,
        damping: float = 0.0,
        gravity: float = 9.81
    ):
        """
        Initialize pendulum
        
        Args:
            length: Length of pendulum (m)
            mass: Mass of bob (kg)
            angle: Initial angle from vertical (radians)
            angular_velocity: Initial angular velocity (rad/s)
            damping: Damping coefficient
            gravity: Gravitational acceleration (m/s^2)
        """
        self.length = length
        self.mass = mass
        self.angle = angle
        self.angular_velocity = angular_velocity
        self.damping = damping
        self.g = gravity
        
    def angular_acceleration(self) -> float:
        """Calculate angular acceleration using θ'' = -(g/L)sin(θ) - γω"""
        gravity_term = -(self.g / self.length) * np.sin(self.angle)
        damping_term = -self.damping * self.angular_velocity
        return gravity_term + damping_term
    
    def potential_energy(self) -> float:
        """PE = mgh = mgL(1 - cos(θ))"""
        height = self.length * (1 - np.cos(self.angle))
        return self.mass * self.g * height
    
    def kinetic_energy(self) -> float:
        """KE = 0.5 * I * ω^2, where I = mL^2 for point mass"""
        moment_of_inertia = self.mass * self.length**2
        return 0.5 * moment_of_inertia * self.angular_velocity**2
    
    def total_energy(self) -> float:
        """Total mechanical energy"""
        return self.kinetic_energy() + self.potential_energy()
    
    def period_small_angle(self) -> float:
        """Period using small-angle approximation: T = 2π√(L/g)"""
        return 2 * np.pi * np.sqrt(self.length / self.g)
