"""Visualization utilities for physics simulations"""
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from typing import List


def plot_trajectory(
    positions: List[np.ndarray],
    title: str = "Particle Trajectory",
    save_path: str = None
) -> None:
    """
    Plot particle trajectory
    
    Args:
        positions: List of position vectors
        title: Plot title
        save_path: Optional path to save figure
    """
    positions = np.array(positions)
    
    plt.figure(figsize=(10, 6))
    plt.plot(positions[:, 0], positions[:, 1], 'b-', alpha=0.6, label='Path')
    plt.scatter(positions[0, 0], positions[0, 1], c='green', s=100, 
                marker='o', label='Start', zorder=5)
    plt.scatter(positions[-1, 0], positions[-1, 1], c='red', s=100, 
                marker='s', label='End', zorder=5)
    
    plt.xlabel('X Position (m)')
    plt.ylabel('Y Position (m)')
    plt.title(title)
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.axis('equal')
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.show()


def plot_energy(
    times: List[float],
    kinetic: List[float],
    potential: List[float] = None,
    title: str = "Energy Over Time"
) -> None:
    """
    Plot energy conservation
    
    Args:
        times: Time points
        kinetic: Kinetic energy values
        potential: Optional potential energy values
        title: Plot title
    """
    plt.figure(figsize=(10, 6))
    
    plt.plot(times, kinetic, 'b-', label='Kinetic Energy')
    
    if potential is not None:
        plt.plot(times, potential, 'r-', label='Potential Energy')
        total = np.array(kinetic) + np.array(potential)
        plt.plot(times, total, 'g--', label='Total Energy', linewidth=2)
    
    plt.xlabel('Time (s)')
    plt.ylabel('Energy (J)')
    plt.title(title)
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.show()


def plot_phase_space(
    positions: List[float],
    velocities: List[float],
    title: str = "Phase Space Diagram"
) -> None:
    """
    Plot phase space (position vs velocity)
    
    Args:
        positions: Position values (1D)
        velocities: Velocity values (1D)
        title: Plot title
    """
    plt.figure(figsize=(8, 8))
    plt.plot(positions, velocities, 'b-', alpha=0.6)
    plt.scatter(positions[0], velocities[0], c='green', s=100, 
                marker='o', label='Start', zorder=5)
    plt.scatter(positions[-1], velocities[-1], c='red', s=100, 
                marker='s', label='End', zorder=5)
    
    plt.xlabel('Position (m)')
    plt.ylabel('Velocity (m/s)')
    plt.title(title)
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.show()


def animate_simulation(
    positions: List[np.ndarray],
    interval: int = 50,
    save_path: str = None
) -> FuncAnimation:
    """
    Create animation of particle motion
    
    Args:
        positions: List of position vectors
        interval: Milliseconds between frames
        save_path: Optional path to save animation
        
    Returns:
        Animation object
    """
    positions = np.array(positions)
    
    fig, ax = plt.subplots(figsize=(10, 8))
    
    # Set up plot limits
    x_min, x_max = positions[:, 0].min(), positions[:, 0].max()
    y_min, y_max = positions[:, 1].min(), positions[:, 1].max()
    margin = 0.1
    ax.set_xlim(x_min - margin, x_max + margin)
    ax.set_ylim(y_min - margin, y_max + margin)
    
    # Initialize plot elements
    trail, = ax.plot([], [], 'b-', alpha=0.4, linewidth=1)
    particle, = ax.plot([], [], 'ro', markersize=10)
    
    ax.set_xlabel('X Position (m)')
    ax.set_ylabel('Y Position (m)')
    ax.set_title('Particle Motion Animation')
    ax.grid(True, alpha=0.3)
    
    def init():
        trail.set_data([], [])
        particle.set_data([], [])
        return trail, particle
    
    def update(frame):
        trail.set_data(positions[:frame, 0], positions[:frame, 1])
        particle.set_data([positions[frame, 0]], [positions[frame, 1]])
        return trail, particle
    
    anim = FuncAnimation(
        fig, update, init_func=init,
        frames=len(positions), interval=interval,
        blit=True, repeat=True
    )
    
    if save_path:
        anim.save(save_path, writer='pillow', fps=20)
    
    return anim
