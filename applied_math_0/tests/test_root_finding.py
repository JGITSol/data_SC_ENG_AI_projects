"""Tests for root finding algorithms"""
import pytest
import numpy as np
from src.root_finding import bisection, newton_raphson, secant, fixed_point


def test_bisection():
    """Test bisection method"""
    # Root of x^2 - 4 = 0 is 2
    f = lambda x: x**2 - 4
    root, iters = bisection(f, 0, 3)
    assert pytest.approx(root, abs=1e-5) == 2.0
    assert iters > 0


def test_newton_raphson():
    """Test Newton-Raphson method"""
    # Root of x^2 - 4 = 0 is 2
    f = lambda x: x**2 - 4
    df = lambda x: 2*x
    root, iters = newton_raphson(f, df, x0=3.0)
    assert pytest.approx(root, abs=1e-5) == 2.0
    assert iters > 0


def test_secant():
    """Test secant method"""
    # Root of x^2 - 4 = 0 is 2
    f = lambda x: x**2 - 4
    root, iters = secant(f, x0=0, x1=3)
    assert pytest.approx(root, abs=1e-5) == 2.0
    assert iters > 0


def test_fixed_point():
    """Test fixed point iteration"""
    # x = cos(x)
    g = lambda x: np.cos(x)
    root, iters = fixed_point(g, x0=0.5)
    # Check if root satisfies x = cos(x)
    assert pytest.approx(root, abs=1e-5) == np.cos(root)
    assert iters > 0
