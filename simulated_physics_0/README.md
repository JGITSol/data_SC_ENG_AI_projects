# Physics Engine: A Beginner's Guide
## How Video Games Simulate Reality

![Stack](https://img.shields.io/badge/Frontend-Streamlit-red?logo=streamlit)
![Stack](https://img.shields.io/badge/Core-Python_3.10-3776AB?logo=python)
![Stack](https://img.shields.io/badge/Math-NumPy-013243?logo=numpy)

---

## **The Problem: The GPS Prediction**

Imagine you are driving a car, and your GPS loses signal for 5 seconds. It needs to guess where you are.

### **1. The Simple Guess (Euler Method)**
The GPS says: *"You were driving North at 60mph. So in 5 seconds, you are exactly 0.08 miles North."*
- **The Flaw:** What if you turned the steering wheel? The GPS assumes you travel in a straight line forever.
- **In Physics:** This causes errors to pile up. In a game, objects would drift apart or gain infinite energy and explode.

### **2. The Momentum Guess (Verlet Integration)**
The GPS says: *"I saw where you were 1 second ago. I see where you are now. I'll assume you keep that momentum."*
- **The Benefit:** It remembers your "flow". It handles curves and orbits much better.
- **In Physics:** This is "Symplectic" – it conserves energy. Planets stay in orbit instead of spiraling into the sun.

---

## **The Solution: The Solver Loop**

A physics engine is just a loop that runs 60 times a second:
1.  **Forces**: Calculate gravity, wind, springs. ($F = ma$)
2.  **Integrate**: Update position based on velocity. ($x_{new} = x_{old} + v \cdot dt$)
3.  **Constraints**: "The ball cannot go through the floor." (Move it back up).

---

## **Features**

- **Solvers**:
    - **Euler**: Good for simple movement, bad for orbits.
    - **Verlet**: Excellent for particles, cloth, and molecular dynamics.
- **Systems**:
    - **Pendulum**: Simple harmonic motion.
    - **Double Pendulum**: Chaos theory in action.
    - **N-Body**: Gravity simulation (Solar System).
- **Interactive UI**: Change gravity, friction, and time step ($dt$) in real-time.

---

## **How to Use the Lab**

### **Step 1: Select a System**
- Choose **Simple Pendulum** to see basic oscillation.
- Choose **Double Pendulum** to see how tiny changes lead to wildly different outcomes (The Butterfly Effect).

### **Step 2: Tweak the Universe**
- **Gravity ($g$):** Turn it off to see things float. Increase it to simulate Jupiter.
- **Friction:** Add air resistance to stop the motion eventually.
- **Time Step ($dt$):** Make it smaller for better accuracy, or larger to see the simulation break (explode).

### **Step 3: Run Simulation**
- Watch the animation.
- Observe the **Energy Graph**. In a perfect world (Verlet), total energy (Kinetic + Potential) should stay flat. If it grows, your universe is broken!

---

## **Key Takeaways for Interviews**

| Concept | Explanation |
|---|---|
| **Time Step ($dt$)** | The slice of time the computer calculates. Smaller = More Accurate but Slower. |
| **Energy Conservation** | A good physics engine shouldn't create or destroy energy (unless you add friction). |
| **Stability** | Does the simulation explode over time? Implicit methods (Verlet) are more stable than Explicit (Euler). |
| **Chaos** | In a Double Pendulum, you cannot predict the future because tiny errors multiply exponentially. |

---

## **Tech Stack**
- **Language**: Python 3.10+
- **Libraries**: NumPy (Vector math), Matplotlib (Plotting)
- **UI**: Streamlit
- **Testing**: Pytest

## **Getting Started**

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run Interactive Lab**
   ```bash
   streamlit run streamlit_app.py
   ```

3. **Run Tests**
   ```bash
   pytest
   ```

## License
MIT
