"""Visualization tools for pendulum simulation"""
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from typing import Dict, Optional


def plot_results(
    results: Dict[str, list],
    title: str = "Pendulum Simulation"
) -> None:
    """
    Plot simulation results (angle, velocity, energy)
    
    Args:
        results: Dictionary from run_simulation
        title: Plot title
    """
    times = results['time']
    
    fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(10, 12), sharex=True)
    
    # Angle
    ax1.plot(times, results['angle'], 'b-', label='Angle (rad)')
    ax1.set_ylabel('Angle (rad)')
    ax1.set_title(f'{title} - Motion')
    ax1.grid(True, alpha=0.3)
    ax1.legend()
    
    # Phase Space
    ax2.plot(results['angle'], results['angular_velocity'], 'g-')
    ax2.set_ylabel('Angular Velocity (rad/s)')
    ax2.set_xlabel('Angle (rad)')
    ax2.set_title('Phase Space')
    ax2.grid(True, alpha=0.3)
    
    # Energy
    ax3.plot(times, results['kinetic_energy'], 'r--', label='Kinetic')
    ax3.plot(times, results['potential_energy'], 'g--', label='Potential')
    ax3.plot(times, results['total_energy'], 'k-', label='Total')
    ax3.set_ylabel('Energy (J)')
    ax3.set_xlabel('Time (s)')
    ax3.set_title('Energy Conservation')
    ax3.grid(True, alpha=0.3)
    ax3.legend()
    
    plt.tight_layout()
    plt.show()


def animate_pendulum(
    results: Dict[str, list],
    length: float,
    interval: int = 20,
    save_path: Optional[str] = None
) -> FuncAnimation:
    """
    Create animation of pendulum motion
    
    Args:
        results: Simulation results
        length: Pendulum length
        interval: Frame interval in ms
        save_path: Optional path to save animation
    """
    angles = np.array(results['angle'])
    times = np.array(results['time'])
    
    # Convert polar to cartesian
    x = length * np.sin(angles)
    y = -length * np.cos(angles)
    
    fig, ax = plt.subplots(figsize=(8, 8))
    
    # Set limits
    limit = length * 1.2
    ax.set_xlim(-limit, limit)
    ax.set_ylim(-limit, limit)
    ax.set_aspect('equal')
    ax.grid(True, alpha=0.3)
    
    # Plot elements
    rod, = ax.plot([], [], 'k-', linewidth=2)
    bob, = ax.plot([], [], 'ro', markersize=15)
    time_text = ax.text(0.05, 0.95, '', transform=ax.transAxes)
    
    def init():
        rod.set_data([], [])
        bob.set_data([], [])
        time_text.set_text('')
        return rod, bob, time_text
    
    def update(frame):
        # Rod connects origin (0,0) to bob (x,y)
        rod.set_data([0, x[frame]], [0, y[frame]])
        bob.set_data([x[frame]], [y[frame]])
        time_text.set_text(f'Time: {times[frame]:.2f}s')
        return rod, bob, time_text
    
    # Downsample for smoother animation if needed
    step = max(1, len(times) // 500)  # Limit to ~500 frames
    frames = range(0, len(times), step)
    
    anim = FuncAnimation(
        fig, update, init_func=init,
        frames=frames, interval=interval,
        blit=True
    )
    
    if save_path:
        anim.save(save_path, writer='pillow', fps=30)
        
    plt.show()
    return anim
