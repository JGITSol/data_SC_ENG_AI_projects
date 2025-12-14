"""Tests for linear solvers"""
import pytest
import numpy as np
from src.solvers import gaussian_elimination, jacobi_method, gauss_seidel


def test_gaussian_elimination():
    """Test Gaussian elimination"""
    A = np.array([[3, 2, -4], [2, 3, 3], [5, -3, 1]], dtype=float)
    b = np.array([3, 15, 14], dtype=float)
    
    x = gaussian_elimination(A, b)
    
    # Check solution: Ax = b
    assert np.allclose(np.dot(A, x), b)


def test_jacobi_method():
    """Test Jacobi iterative method"""
    # Diagonally dominant matrix for convergence
    A = np.array([[10, -1, 2, 0],
                  [-1, 11, -1, 3],
                  [2, -1, 10, -1],
                  [0, 3, -1, 8]], dtype=float)
    b = np.array([6, 25, -11, 15], dtype=float)
    
    x, iters = jacobi_method(A, b)
    
    assert np.allclose(np.dot(A, x), b, atol=1e-5)
    assert iters > 0


def test_gauss_seidel():
    """Test Gauss-Seidel iterative method"""
    # Diagonally dominant matrix
    A = np.array([[10, -1, 2, 0],
                  [-1, 11, -1, 3],
                  [2, -1, 10, -1],
                  [0, 3, -1, 8]], dtype=float)
    b = np.array([6, 25, -11, 15], dtype=float)
    
    x, iters = gauss_seidel(A, b)
    
    assert np.allclose(np.dot(A, x), b, atol=1e-5)
    assert iters > 0


def test_singular_matrix():
    """Test Gaussian elimination with singular matrix"""
    A = np.array([[1, 1], [1, 1]], dtype=float)
    b = np.array([1, 1], dtype=float)
    
    with pytest.raises(ValueError):
        gaussian_elimination(A, b)
