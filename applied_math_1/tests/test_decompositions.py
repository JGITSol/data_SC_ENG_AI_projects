"""Tests for matrix decompositions"""
import pytest
import numpy as np
from src.decompositions import lu_decomposition, qr_gram_schmidt, cholesky_decomposition


def test_lu_decomposition():
    """Test LU decomposition A = LU"""
    A = np.array([[4, 3], [6, 3]], dtype=float)
    L, U = lu_decomposition(A)
    
    # Check L is lower triangular with 1s on diagonal
    assert np.allclose(np.tril(L), L)
    assert np.allclose(np.diag(L), np.ones(2))
    
    # Check U is upper triangular
    assert np.allclose(np.triu(U), U)
    
    # Check reconstruction
    assert np.allclose(np.dot(L, U), A)


def test_qr_gram_schmidt():
    """Test QR decomposition A = QR"""
    A = np.array([[1, 1, 0], [1, 0, 1], [0, 1, 1]], dtype=float)
    Q, R = qr_gram_schmidt(A)
    
    # Check Q is orthogonal: Q.T @ Q = I
    assert np.allclose(np.dot(Q.T, Q), np.eye(3))
    
    # Check R is upper triangular
    assert np.allclose(np.triu(R), R)
    
    # Check reconstruction
    assert np.allclose(np.dot(Q, R), A)


def test_cholesky_decomposition():
    """Test Cholesky decomposition A = LL^T"""
    # Symmetric positive definite matrix
    A = np.array([[4, 12, -16], [12, 37, -43], [-16, -43, 98]], dtype=float)
    L = cholesky_decomposition(A)
    
    # Check L is lower triangular
    assert np.allclose(np.tril(L), L)
    
    # Check reconstruction
    assert np.allclose(np.dot(L, L.T), A)


def test_cholesky_non_positive_definite():
    """Test Cholesky raises error for non-positive definite matrix"""
    A = np.array([[1, 2], [2, 1]], dtype=float)  # Indefinite
    with pytest.raises(ValueError):
        cholesky_decomposition(A)
