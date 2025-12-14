"""Tests for integration methods"""
import pytest
import numpy as np
from src.integration import (
    trapezoidal_rule, simpsons_rule, simpsons_3_8_rule,
    romberg_integration, monte_carlo_integration
)


def test_trapezoidal_rule():
    """Test trapezoidal rule"""
    # Integral of x^2 from 0 to 1 is 1/3
    f = lambda x: x**2
    result = trapezoidal_rule(f, 0, 1, n=100)
    assert pytest.approx(result, abs=1e-4) == 1/3


def test_simpsons_rule():
    """Test Simpson's rule"""
    # Integral of x^2 from 0 to 1 is 1/3
    f = lambda x: x**2
    result = simpsons_rule(f, 0, 1, n=100)
    assert pytest.approx(result, abs=1e-6) == 1/3


def test_simpsons_3_8_rule():
    """Test Simpson's 3/8 rule"""
    # Integral of x^2 from 0 to 1 is 1/3
    f = lambda x: x**2
    result = simpsons_3_8_rule(f, 0, 1, n=99)
    assert pytest.approx(result, abs=1e-6) == 1/3


def test_romberg_integration():
    """Test Romberg integration"""
    # Integral of x^2 from 0 to 1 is 1/3
    f = lambda x: x**2
    result = romberg_integration(f, 0, 1)
    assert pytest.approx(result, abs=1e-8) == 1/3


def test_monte_carlo_integration():
    """Test Monte Carlo integration"""
    # Integral of x^2 from 0 to 1 is 1/3
    f = lambda x: x**2
    # Monte Carlo is stochastic, so use loose tolerance
    np.random.seed(42)
    result = monte_carlo_integration(f, 0, 1, n_samples=100000)
    assert pytest.approx(result, abs=1e-2) == 1/3
