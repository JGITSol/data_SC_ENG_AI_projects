"""Eigenvalue algorithms"""
import numpy as np
from typing import Tuple


def power_method(
    A: np.ndarray, 
    tol: float = 1e-6, 
    max_iter: int = 100
) -> Tuple[float, np.ndarray]:
    """
    Find dominant eigenvalue and eigenvector using Power Method
    
    Args:
        A: Square matrix
        tol: Tolerance
        max_iter: Maximum iterations
        
    Returns:
        (eigenvalue, eigenvector)
    """
    n = A.shape[0]
    # Random initial vector
    v = np.random.rand(n)
    v = v / np.linalg.norm(v)
    
    lambda_old = 0.0
    
    for _ in range(max_iter):
        # Av
        w = np.dot(A, v)
        
        # Rayleigh quotient approximation for eigenvalue
        lambda_new = np.dot(v, w)
        
        # Normalize
        v = w / np.linalg.norm(w)
        
        if abs(lambda_new - lambda_old) < tol:
            return lambda_new, v
            
        lambda_old = lambda_new
        
    raise RuntimeError("Power method did not converge")


def qr_algorithm(
    A: np.ndarray, 
    tol: float = 1e-6, 
    max_iter: int = 100
) -> np.ndarray:
    """
    Find all eigenvalues using QR Algorithm
    
    Args:
        A: Square matrix
        tol: Tolerance
        max_iter: Maximum iterations
        
    Returns:
        Array of eigenvalues
    """
    A_k = A.copy()
    n = A.shape[0]
    
    for _ in range(max_iter):
        # QR decomposition
        Q, R = np.linalg.qr(A_k)
        
        # Next iteration: A_{k+1} = R * Q
        A_new = np.dot(R, Q)
        
        # Check convergence (off-diagonal elements close to zero)
        off_diagonal = np.sum(np.abs(A_new - np.diag(np.diagonal(A_new))))
        if off_diagonal < tol:
            return np.diagonal(A_new)
            
        A_k = A_new
        
    # Return diagonal elements even if not fully converged
    return np.diagonal(A_k)
