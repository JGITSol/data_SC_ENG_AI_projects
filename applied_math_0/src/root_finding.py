"""Root finding algorithms"""
from typing import Callable, Tuple
import numpy as np


def bisection(
    f: Callable[[float], float],
    a: float,
    b: float,
    tol: float = 1e-6,
    max_iter: int = 100
) -> Tuple[float, int]:
    """
    Find root using bisection method
    
    Args:
        f: Function to find root of
        a: Left bracket
        b: Right bracket
        tol: Tolerance
        max_iter: Maximum iterations
        
    Returns:
        (root, iterations)
    """
    if f(a) * f(b) > 0:
        raise ValueError("Function must have opposite signs at a and b")
    
    for i in range(max_iter):
        c = (a + b) / 2
        fc = f(c)
        
        if abs(fc) < tol or abs(b - a) / 2 < tol:
            return c, i + 1
        
        if f(a) * fc < 0:
            b = c
        else:
            a = c
    
    raise RuntimeError(f"Did not converge in {max_iter} iterations")


def newton_raphson(
    f: Callable[[float], float],
    df: Callable[[float], float] = None,
    x0: float = 1.0,
    tol: float = 1e-6,
    max_iter: int = 100
) -> Tuple[float, int]:
    """
    Find root using Newton-Raphson method
    
    Args:
        f: Function to find root of
        df: Derivative of f (if None, uses finite difference)
        x0: Initial guess
        tol: Tolerance
        max_iter: Maximum iterations
        
    Returns:
        (root, iterations)
    """
    x = x0
    
    for i in range(max_iter):
        fx = f(x)
        
        if abs(fx) < tol:
            return x, i + 1
        
        # Calculate derivative
        if df is None:
            h = 1e-8
            dfx = (f(x + h) - fx) / h
        else:
            dfx = df(x)
        
        if abs(dfx) < 1e-14:
            raise RuntimeError("Derivative too small")
        
        x = x - fx / dfx
    
    raise RuntimeError(f"Did not converge in {max_iter} iterations")


def secant(
    f: Callable[[float], float],
    x0: float,
    x1: float,
    tol: float = 1e-6,
    max_iter: int = 100
) -> Tuple[float, int]:
    """
    Find root using secant method
    
    Args:
        f: Function to find root of
        x0: First initial guess
        x1: Second initial guess
        tol: Tolerance
        max_iter: Maximum iterations
        
    Returns:
        (root, iterations)
    """
    for i in range(max_iter):
        fx0 = f(x0)
        fx1 = f(x1)
        
        if abs(fx1) < tol:
            return x1, i + 1
        
        if abs(fx1 - fx0) < 1e-14:
            raise RuntimeError("Denominator too small")
        
        # Secant step
        x_new = x1 - fx1 * (x1 - x0) / (fx1 - fx0)
        x0, x1 = x1, x_new
    
    raise RuntimeError(f"Did not converge in {max_iter} iterations")


def fixed_point(
    g: Callable[[float], float],
    x0: float,
    tol: float = 1e-6,
    max_iter: int = 100
) -> Tuple[float, int]:
    """
    Find fixed point using fixed-point iteration: x = g(x)
    
    Args:
        g: Function where fixed point x* satisfies x* = g(x*)
        x0: Initial guess
        tol: Tolerance
        max_iter: Maximum iterations
        
    Returns:
        (fixed_point, iterations)
    """
    x = x0
    
    for i in range(max_iter):
        x_new = g(x)
        
        if abs(x_new - x) < tol:
            return x_new, i + 1
        
        x = x_new
    
    raise RuntimeError(f"Did not converge in {max_iter} iterations")
