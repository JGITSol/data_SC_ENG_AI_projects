import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from src.particle import Particle
from src.forces import Gravity, SpringForce, DragForce
from src.solver import VerletSolver

st.set_page_config(page_title="Physics Lab", page_icon="⚛️")

st.title("⚛️ Simulated Physics Laboratory")
st.markdown("""
Interactive simulation of particle dynamics using Newtonian mechanics.
Configure forces and initial conditions to observe trajectories.
""")

st.sidebar.header("Simulation Config")

# Initial Conditions
st.sidebar.subheader("Initial Conditions")
mass = st.sidebar.number_input("Mass (kg)", 1.0, 100.0, 1.0)
x0 = st.sidebar.number_input("X Position (m)", -10.0, 10.0, 0.0)
y0 = st.sidebar.number_input("Y Position (m)", 0.0, 20.0, 10.0)
vx0 = st.sidebar.number_input("X Velocity (m/s)", -20.0, 20.0, 5.0)
vy0 = st.sidebar.number_input("Y Velocity (m/s)", -20.0, 20.0, 0.0)

# Forces
st.sidebar.subheader("Forces")
use_gravity = st.sidebar.checkbox("Gravity", True)
use_drag = st.sidebar.checkbox("Air Resistance", False)
use_spring = st.sidebar.checkbox("Spring (to origin)", False)

forces = []
if use_gravity:
    g = st.sidebar.slider("Gravity (m/s²)", 0.0, 20.0, 9.81)
    forces.append(Gravity(g=g))

if use_drag:
    c = st.sidebar.slider("Drag Coefficient", 0.0, 1.0, 0.1)
    forces.append(DragForce(c=c))

if use_spring:
    k = st.sidebar.slider("Spring Constant (k)", 0.1, 10.0, 1.0)
    forces.append(SpringForce(k=k, anchor=(0,0)))

# Simulation Parameters
dt = 0.01
t_max = st.sidebar.slider("Simulation Time (s)", 1.0, 20.0, 5.0)
steps = int(t_max / dt)

if st.button("Run Simulation"):
    # Setup
    p = Particle(mass=mass, position=[x0, y0], velocity=[vx0, vy0])
    solver = VerletSolver(dt=dt)
    
    # Run
    trajectory_x = []
    trajectory_y = []
    times = []
    
    for i in range(steps):
        trajectory_x.append(p.position[0])
        trajectory_y.append(p.position[1])
        times.append(i * dt)
        
        # Calculate net force
        net_force = np.zeros(2)
        for f in forces:
            net_force += f.apply(p)
            
        solver.step(p, net_force)
        
        # Ground collision
        if p.position[1] < 0:
            p.position[1] = 0
            p.velocity[1] *= -0.8 # Bounce
            
    # Plot
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(8, 10))
    
    # Trajectory
    ax1.plot(trajectory_x, trajectory_y, 'b-', label='Path')
    ax1.plot(x0, y0, 'go', label='Start')
    ax1.plot(trajectory_x[-1], trajectory_y[-1], 'ro', label='End')
    ax1.axhline(0, color='k', linestyle='-', alpha=0.5)
    ax1.set_title("Particle Trajectory")
    ax1.set_xlabel("X (m)")
    ax1.set_ylabel("Y (m)")
    ax1.grid(True)
    ax1.legend()
    ax1.axis('equal')
    
    # Height vs Time
    ax2.plot(times, trajectory_y, 'r-')
    ax2.set_title("Height vs Time")
    ax2.set_xlabel("Time (s)")
    ax2.set_ylabel("Height (m)")
    ax2.grid(True)
    
    st.pyplot(fig)
