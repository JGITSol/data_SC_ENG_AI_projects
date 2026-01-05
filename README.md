# The Data & Simulation Laboratory
## Where Math Meets Reality

![Status](https://img.shields.io/badge/Status-Active-success)
![Standard](https://img.shields.io/badge/Standard-Laboratory_Gold-gold)

---

## **Welcome to the Lab**

This repository houses the **Data Science**, **Applied Mathematics**, and **Physics Simulation** wings of the portfolio.
Unlike typical code repositories, this is a **Laboratory**. Every project here is designed to:
1.  **Teach**: Explain complex concepts using simple analogies.
2.  **Visualize**: Don't just calculate numbers; show them moving.
3.  **Trace**: Every result can be traced back to its mathematical origin.

---

## **The Wings**

### **1. Applied Mathematics Wing**
*The Engine Room of Science.*
- **[Numerical Methods (Math 0)](./applied_math_0/README.md)**:
    - **Analogy**: The Thermostat & The Swimming Pool.
    - **Focus**: Solving equations that have no formula (Root Finding) and measuring complex shapes (Integration).
    - **Tech**: Python, NumPy, Streamlit.

### **2. Simulated Physics Wing**
*The Virtual Universe.*
- **[Physics Engine (Physics 0)](./simulated_physics_0/README.md)**:
    - **Analogy**: The GPS Prediction.
    - **Focus**: Simulating gravity, collisions, and chaos (Double Pendulum) without blowing up the computer.
    - **Tech**: Python, Matplotlib, Verlet Integration.

### **3. Data Engineering Wing**
*The Plumbing of the Internet.*
- **[Serverless ETL (Data Eng 0)](./data_engineering_0/README.md)**:
    - **Analogy**: The Water Treatment Plant.
    - **Focus**: Moving and cleaning data at the "Edge" of the internet using Cloudflare Workers.
    - **Tech**: TypeScript, Cloudflare D1, Wrangler.

### **4. Data Science Wing**
*The Detective Agency.*
- **[Data Visualization (Data Sci 0)](./data_science_0/README.md)**:
    - **Analogy**: The Detective & The Jury.
    - **Focus**: Turning raw evidence (CSV files) into a compelling story (Interactive Dashboards).
    - **Tech**: Python, Pandas, Plotly.

---

## **The "Laboratory Gold Standard"**

All projects in this lab adhere to strict engineering standards:

1.  **Traceability**: We don't just return `42`. We return `CalculationResult(value=42, method="Newton-Raphson", steps=...)`.
2.  **Safety**: Simulations must detect "Explosions" (Instability) and warn the user.
3.  **Accessibility**: Every complex math concept is explained with a real-world analogy (e.g., "The Goldilocks Dilemma").

---

## **Getting Started**

Each project is self-contained. Navigate to the folder and follow the `README.md`.

```bash
# Example: Run the Physics Lab
cd simulated_physics_0
pip install -r requirements.txt
streamlit run streamlit_app.py
```

## License
MIT
