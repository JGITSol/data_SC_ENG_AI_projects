"""Linear system solvers"""
import numpy as np
from typing import Tuple, Optional


def gaussian_elimination(A: np.ndarray, b: np.ndarray) -> np.ndarray:
    """
    Solve Ax = b using Gaussian elimination
    
    Args:
        A: Coefficient matrix
        b: Constant vector
        
    Returns:
        Solution vector x
    """
    n = A.shape[0]
    if A.shape[1] != n:
        raise ValueError("Matrix A must be square")
    
    # Augmented matrix
    Ab = np.hstack([A, b.reshape(-1, 1)]).astype(float)
    
    # Forward elimination
    for i in range(n):
        # Pivot
        pivot_idx = i + np.argmax(np.abs(Ab[i:, i]))
        if abs(Ab[pivot_idx, i]) < 1e-10:
            raise ValueError("Singular matrix")
            
        # Swap rows
        if pivot_idx != i:
            Ab[[i, pivot_idx]] = Ab[[pivot_idx, i]]
            
        # Eliminate
        for j in range(i + 1, n):
            factor = Ab[j, i] / Ab[i, i]
            Ab[j, i:] -= factor * Ab[i, i:]
            
    # Back substitution
    x = np.zeros(n)
    for i in range(n - 1, -1, -1):
        sum_ax = sum(Ab[i, j] * x[j] for j in range(i + 1, n))
        x[i] = (Ab[i, n] - sum_ax) / Ab[i, i]
        
    return x


def jacobi_method(
    A: np.ndarray, 
    b: np.ndarray, 
    x0: Optional[np.ndarray] = None,
    tol: float = 1e-6,
    max_iter: int = 100
) -> Tuple[np.ndarray, int]:
    """
    Solve Ax = b using Jacobi iterative method
    
    Args:
        A: Coefficient matrix
        b: Constant vector
        x0: Initial guess
        tol: Convergence tolerance
        max_iter: Maximum iterations
        
    Returns:
        (x, iterations)
    """
    n = A.shape[0]
    if x0 is None:
        x0 = np.zeros(n)
        
    x = x0.copy()
    x_new = np.zeros_like(x)
    
    for k in range(max_iter):
        for i in range(n):
            s = sum(A[i, j] * x[j] for j in range(n) if j != i)
            x_new[i] = (b[i] - s) / A[i, i]
            
        if np.linalg.norm(x_new - x) < tol:
            return x_new, k + 1
            
        x[:] = x_new[:]
        
    raise RuntimeError(f"Did not converge in {max_iter} iterations")


def gauss_seidel(
    A: np.ndarray, 
    b: np.ndarray, 
    x0: Optional[np.ndarray] = None,
    tol: float = 1e-6,
    max_iter: int = 100
) -> Tuple[np.ndarray, int]:
    """
    Solve Ax = b using Gauss-Seidel iterative method
    
    Args:
        A: Coefficient matrix
        b: Constant vector
        x0: Initial guess
        tol: Convergence tolerance
        max_iter: Maximum iterations
        
    Returns:
        (x, iterations)
    """
    n = A.shape[0]
    if x0 is None:
        x0 = np.zeros(n)
        
    x = x0.copy()
    
    for k in range(max_iter):
        x_old = x.copy()
        
        for i in range(n):
            s1 = sum(A[i, j] * x[j] for j in range(i))
            s2 = sum(A[i, j] * x_old[j] for j in range(i + 1, n))
            x[i] = (b[i] - s1 - s2) / A[i, i]
            
        if np.linalg.norm(x - x_old) < tol:
            return x, k + 1
            
    raise RuntimeError(f"Did not converge in {max_iter} iterations")
