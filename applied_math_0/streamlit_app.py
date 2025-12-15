import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from src.root_finding import newton_raphson, bisection
from src.integration import simpsons_rule, trapezoidal_rule

st.set_page_config(page_title="Applied Math Lab", page_icon="🧮")

st.title("🧮 Applied Mathematics Laboratory")
st.markdown("""
This interactive lab demonstrates core numerical methods implemented in Python.
Select a module from the sidebar to explore.
""")

module = st.sidebar.selectbox("Select Module", ["Root Finding", "Numerical Integration"])

if module == "Root Finding":
    st.header("Root Finding Algorithms")
    st.markdown("Find roots of non-linear equations $f(x) = 0$.")

    equation_str = st.text_input("Enter function f(x) (using numpy as np)", "x**2 - 2")
    method = st.selectbox("Method", ["Newton-Raphson", "Bisection"])
    
    col1, col2 = st.columns(2)
    with col1:
        a = st.number_input("Start/Lower Bound", value=0.0)
    with col2:
        b = st.number_input("End/Upper Bound", value=2.0)

    if st.button("Find Root"):
        try:
            f = lambda x: eval(equation_str)
            
            if method == "Newton-Raphson":
                # Simple numerical derivative for demo
                df = lambda x: (f(x + 1e-5) - f(x)) / 1e-5
                root = newton_raphson(f, df, x0=(a+b)/2)
            else:
                root = bisection(f, a, b)
                
            st.success(f"Root found at x = {root:.6f}")
            st.info(f"f({root:.6f}) = {f(root):.6e}")
            
            # Plot
            x = np.linspace(a - 1, b + 1, 100)
            y = f(x)
            fig, ax = plt.subplots()
            ax.plot(x, y, label='f(x)')
            ax.axhline(0, color='k', linestyle='--', alpha=0.5)
            ax.scatter([root], [f(root)], color='red', label='Root')
            ax.legend()
            st.pyplot(fig)
            
        except Exception as e:
            st.error(f"Error: {str(e)}")

elif module == "Numerical Integration":
    st.header("Numerical Integration")
    st.markdown("Calculate definite integral $\int_a^b f(x) dx$.")
    
    equation_str = st.text_input("Enter function f(x)", "np.sin(x)")
    method = st.selectbox("Method", ["Simpson's Rule", "Trapezoidal Rule"])
    
    col1, col2, col3 = st.columns(3)
    with col1:
        a = st.number_input("Lower Limit (a)", value=0.0)
    with col2:
        b = st.number_input("Upper Limit (b)", value=np.pi)
    with col3:
        n = st.number_input("Steps (n)", value=100, min_value=2, step=2)

    if st.button("Calculate Integral"):
        try:
            f = lambda x: eval(equation_str)
            
            if method == "Simpson's Rule":
                result = simpsons_rule(f, a, b, n)
            else:
                result = trapezoidal_rule(f, a, b, n)
                
            st.success(f"Integral Result: {result:.6f}")
            
            # Visualization
            x = np.linspace(a, b, 100)
            y = f(x)
            fig, ax = plt.subplots()
            ax.plot(x, y, 'b', label='f(x)')
            ax.fill_between(x, y, alpha=0.3)
            ax.set_title(f"Area under curve = {result:.4f}")
            st.pyplot(fig)
            
        except Exception as e:
            st.error(f"Error: {str(e)}")
