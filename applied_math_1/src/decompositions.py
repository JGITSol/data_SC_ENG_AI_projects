"""Matrix decomposition algorithms"""
import numpy as np
from typing import Tuple, Optional


def lu_decomposition(A: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    """
    Perform LU decomposition: A = LU
    
    Args:
        A: Square matrix
        
    Returns:
        (L, U) tuple where L is lower triangular and U is upper triangular
    """
    n = A.shape[0]
    if A.shape[1] != n:
        raise ValueError("Matrix must be square")
        
    L = np.eye(n)
    U = A.copy().astype(float)
    
    for k in range(n-1):
        for i in range(k+1, n):
            if abs(U[k, k]) < 1e-10:
                raise ValueError("Zero pivot encountered")
                
            factor = U[i, k] / U[k, k]
            L[i, k] = factor
            U[i, k:] -= factor * U[k, k:]
            
    return L, U


def qr_gram_schmidt(A: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    """
    Perform QR decomposition using Gram-Schmidt process: A = QR
    
    Args:
        A: Matrix (m x n)
        
    Returns:
        (Q, R) tuple where Q is orthogonal and R is upper triangular
    """
    m, n = A.shape
    Q = np.zeros((m, n))
    R = np.zeros((n, n))
    
    for j in range(n):
        v = A[:, j].astype(float)
        
        for i in range(j):
            R[i, j] = np.dot(Q[:, i], A[:, j])
            v = v - R[i, j] * Q[:, i]
            
        R[j, j] = np.linalg.norm(v)
        
        if R[j, j] < 1e-10:
            # Handle linear dependence
            Q[:, j] = np.zeros(m)
        else:
            Q[:, j] = v / R[j, j]
            
    return Q, R


def cholesky_decomposition(A: np.ndarray) -> np.ndarray:
    """
    Perform Cholesky decomposition: A = LL^T
    
    Args:
        A: Symmetric positive-definite matrix
        
    Returns:
        L: Lower triangular matrix
    """
    n = A.shape[0]
    if A.shape[1] != n:
        raise ValueError("Matrix must be square")
        
    L = np.zeros_like(A, dtype=float)
    
    for i in range(n):
        for j in range(i + 1):
            sum_val = sum(L[i, k] * L[j, k] for k in range(j))
            
            if i == j:
                val = A[i, i] - sum_val
                if val <= 0:
                    raise ValueError("Matrix is not positive definite")
                L[i, j] = np.sqrt(val)
            else:
                L[i, j] = (1.0 / L[j, j]) * (A[i, j] - sum_val)
                
    return L
