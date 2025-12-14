"""Numerical integration methods"""
from typing import Callable
import numpy as np


def trapezoidal_rule(
    f: Callable[[float], float],
    a: float,
    b: float,
    n: int = 100
) -> float:
    """
    Integrate using trapezoidal rule
    
    Args:
        f: Function to integrate
        a: Lower limit
        b: Upper limit
        n: Number of intervals
        
    Returns:
        Approximate integral
    """
    x = np.linspace(a, b, n + 1)
    y = np.array([f(xi) for xi in x])
    h = (b - a) / n
    
    return h * (0.5 * y[0] + np.sum(y[1:-1]) + 0.5 * y[-1])


def simpsons_rule(
    f: Callable[[float], float],
    a: float,
    b: float,
    n: int = 100
) -> float:
    """
    Integrate using Simpson's 1/3 rule
    
    Args:
        f: Function to integrate
        a: Lower limit
        b: Upper limit
        n: Number of intervals (must be even)
        
    Returns:
        Approximate integral
    """
    if n % 2 != 0:
        n += 1  # Make even
    
    x = np.linspace(a, b, n + 1)
    y = np.array([f(xi) for xi in x])
    h = (b - a) / n
    
    # Simpson's: (h/3)[y0 + 4(y1+y3+...) + 2(y2+y4+...) + yn]
    even_sum = np.sum(y[2:-1:2])  # y2, y4, ...
    odd_sum = np.sum(y[1:-1:2])   # y1, y3, ...
    
    return (h / 3) * (y[0] + 4 * odd_sum + 2 * even_sum + y[-1])


def simpsons_3_8_rule(
    f: Callable[[float], float],
    a: float,
    b: float,
    n: int = 99
) -> float:
    """
    Integrate using Simpson's 3/8 rule
    
    Args:
        f: Function to integrate
        a: Lower limit
        b: Upper limit
        n: Number of intervals (must be divisible by 3)
        
    Returns:
        Approximate integral
    """
    if n % 3 != 0:
        n = ((n // 3) + 1) * 3
    
    x = np.linspace(a, b, n + 1)
    y = np.array([f(xi) for xi in x])
    h = (b - a) / n
    
    # 3/8 rule: (3h/8)[y0 + 3(y1+y2+y4+y5+...) + 2(y3+y6+...) + yn]
    indices_3 = np.arange(3, n, 3)
    indices_not_3 = np.array([i for i in range(1, n) if i % 3 != 0])
    
    sum_3 = np.sum(y[indices_3])
    sum_not_3 = np.sum(y[indices_not_3])
    
    return (3 * h / 8) * (y[0] + 3 * sum_not_3 + 2 * sum_3 + y[-1])


def romberg_integration(
    f: Callable[[float], float],
    a: float,
    b: float,
    max_steps: int = 10,
    tol: float = 1e-8
) -> float:
    """
    Integrate using Romberg integration (Richardson extrapolation)
    
    Args:
        f: Function to integrate
        a: Lower limit
        b: Upper limit
        max_steps: Maximum refinement steps
        tol: Tolerance
        
    Returns:
        Approximate integral
    """
    R = np.zeros((max_steps, max_steps))
    
    # R[0,0] is trapezoidal with n=1
    h = b - a
    R[0, 0] = 0.5 * h * (f(a) + f(b))
    
    for i in range(1, max_steps):
        # Trapezoidal with 2^i intervals
        h /= 2
        n = 2**i
        
        # Add intermediate points
        sum_new = sum(f(a + (2*k - 1) * h) for k in range(1, n//2 + 1))
        R[i, 0] = 0.5 * R[i-1, 0] + h * sum_new
        
        # Richardson extrapolation
        for j in range(1, i + 1):
            R[i, j] = R[i, j-1] + (R[i, j-1] - R[i-1, j-1]) / (4**j - 1)
        
        # Check convergence
        if i > 0 and abs(R[i, i] - R[i-1, i-1]) < tol:
            return R[i, i]
    
    return R[max_steps-1, max_steps-1]


def monte_carlo_integration(
    f: Callable[[float], float],
    a: float,
    b: float,
    n_samples: int = 10000
) -> float:
    """
    Integrate using Monte Carlo method
    
    Args:
        f: Function to integrate
        a: Lower limit
        b: Upper limit
        n_samples: Number of random samples
        
    Returns:
        Approximate integral
    """
    x = np.random.uniform(a, b, n_samples)
    y = np.array([f(xi) for xi in x])
    
    return (b - a) * np.mean(y)
