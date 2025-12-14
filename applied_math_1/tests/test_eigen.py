"""Tests for eigenvalue algorithms"""
import pytest
import numpy as np
from src.eigen import power_method, qr_algorithm


def test_power_method():
    """Test Power Method for dominant eigenvalue"""
    # Matrix with eigenvalues 3 and 1
    A = np.array([[2, 1], [1, 2]], dtype=float)
    
    eigenval, eigenvec = power_method(A)
    
    # Dominant eigenvalue should be 3
    assert pytest.approx(abs(eigenval), 0.1) == 3.0
    
    # Check eigenvector property: Av = lambda*v
    # Note: Power method convergence depends on the ratio of eigenvalues
    # For eigenvalues 3 and 1, ratio is 1/3, so convergence should be good
    # But we'll use a slightly looser tolerance for robustness
    assert np.allclose(np.dot(A, eigenvec), eigenval * eigenvec, atol=1e-4)


def test_qr_algorithm():
    """Test QR Algorithm for all eigenvalues"""
    # Symmetric matrix with eigenvalues 3 and 1
    A = np.array([[2, 1], [1, 2]], dtype=float)
    
    eigenvals = qr_algorithm(A)
    
    # Sort for comparison
    eigenvals = np.sort(eigenvals)
    expected = np.array([1.0, 3.0])
    
    assert np.allclose(eigenvals, expected, atol=1e-5)
