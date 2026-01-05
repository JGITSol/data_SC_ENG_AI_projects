# Numerical Methods: A Beginner's Guide
## How Computers Solve Math (When Formulas Fail)

![Stack](https://img.shields.io/badge/Frontend-Streamlit-red?logo=streamlit)
![Stack](https://img.shields.io/badge/Core-Python_3.10-3776AB?logo=python)
![Stack](https://img.shields.io/badge/Math-NumPy_SciPy-013243?logo=numpy)

---

## **The Problem: The Thermostat & The Swimming Pool**

### **1. The Thermostat (Root Finding)**
Imagine you have a heater with a dial from 0 to 10. You want the room to be exactly **21°C**.
- You turn it to 5. Room is 18°C. (Too cold)
- You turn it to 8. Room is 25°C. (Too hot)
- You try 6.5... then 6.2...

You are manually doing **Root Finding**. You are trying to find the input $x$ (dial setting) where the output function $f(x)$ (temperature error) is zero.

### **2. The Swimming Pool (Integration)**
Imagine you need to buy a cover for a kidney-shaped swimming pool.
- You can't just do `Length × Width` because it's curvy.
- **Solution:** You cover the pool with small rectangular tiles. You count the tiles.
- The smaller the tiles, the more accurate your count.

This is **Numerical Integration**. You are slicing a complex curve into simple shapes to find the area.

---

## **The Solution: Algorithms**

This library implements the "Smart Guessing" and "Smart Slicing" algorithms used in engineering.

### **1. Newton-Raphson (The Smart Guesser)**
Instead of guessing randomly, this algorithm looks at the *slope* of the temperature change.
> *"If turning the knob by 1 degree raised the temp by 5 degrees, I should turn it down exactly 0.8 degrees."*
- **Pros:** Extremely fast (converges quadratically).
- **Cons:** Needs to know the slope (derivative).

### **2. Simpson's Rule (The Smart Slicer)**
Instead of using flat rectangles (Trapezoidal Rule), this algorithm uses **curved tops** (parabolas) to match the pool's edge.
- **Result:** You get a much more accurate area with fewer slices.

---

## **Features**

- **Root Finding**:
    - **Bisection**: Slow but guaranteed (The "Divide and Conquer" approach).
    - **Newton-Raphson**: Fast but risky (The "Tangent Line" approach).
- **Numerical Integration**:
    - **Trapezoidal**: Simple straight lines.
    - **Simpson's Rule**: Curved approximations.
- **Interactive UI**: A Streamlit dashboard to visualize how these algorithms converge step-by-step.

---

## **How to Use the Lab**

### **Step 1: Choose Your Problem**
- Select **Root Finding** to solve equations like $x^2 - 2 = 0$.
- Select **Integration** to find the area under curves like $\sin(x)$.

### **Step 2: Configure Parameters**
- **Tolerance:** How precise do you need to be? ($10^{-6}$ is standard).
- **Max Iterations:** When should the computer give up? (Prevents infinite loops).

### **Step 3: Visualize**
- Click **Run**.
- Watch the graph. See how the "Guess" (red dot) moves closer to the solution with every step.

---

## **Key Takeaways for Interviews**

| Concept | Explanation |
|---|---|
| **Convergence** | How fast an algorithm finds the answer. Newton's is "Quadratic" (doubles digits every step). |
| **Discretization** | Breaking a continuous problem (smooth curve) into chunks (steps/slices) a computer can handle. |
| **Truncation Error** | The error caused by using an approximation (like Simpson's rule) instead of the perfect math formula. |
| **Round-off Error** | The error caused by the computer having limited decimal places (floating point limits). |

---

## **Tech Stack**
- **Language**: Python 3.10+
- **Libraries**: NumPy, SciPy, Matplotlib
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
