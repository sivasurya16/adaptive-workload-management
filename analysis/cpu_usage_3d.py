import sympy as sp
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib import cm


def compute_rho(lambda_i, N, m, mu_i):
    return lambda_i / (N * m * mu_i)


def compute_pi_0(lambda_i, N, m, mu_i, K):
    rho_i = compute_rho(lambda_i, N, m, mu_i)
    res = 1

    if rho_i != 1:
        res += sum(((m*rho_i) ** k) / sp.factorial(k) for k in range(1, m))
        res += ((1 - (rho_i**(K-m+1)))*pow(m*rho_i, m)) / \
            (sp.factorial(m)*(1-rho_i))

    else:
        res += sum((m**k)/sp.factorial(k) for k in range(1, m))
        res += (m**m) * (K-m+1)/sp.factorial(m)

    return 1/res


def compute_pi_n(lambda_i, N, m, mu_i, K, n):
    pi_0 = compute_pi_0(lambda_i, N, m, mu_i, K)
    rho_i = compute_rho(lambda_i, N, m, mu_i)

    if n < m:
        res = (m*rho_i) ** n / sp.factorial(n)
    else:
        res = (rho_i**n) * (m**m) / sp.factorial(m)

    return res*pi_0


def compute_lambda_dash(lambda_i, N, m, mu_i, K):
    return lambda_i * (1 - compute_pi_n(lambda_i, N, m, mu_i, K, K))/N


def compute_cpu_usage(lambda_i, N, m, mu_i, K):
    u = sum(j*compute_pi_n(lambda_i, N, m, mu_i, K, j) for j in range(0, m))
    u += sum(m*compute_pi_n(lambda_i, N, m, mu_i, K, j)
             for j in range(m+1, K+1))

    u /= m
    return u


def compute_rejection_probablity(lambda_i, N, m, mu_i, K):
    return compute_pi_n(lambda_i, N, m, mu_i, K, K)


# Parameters
K = 100  # Queue capacity
mu_i = 90  # Service rate

# Ranges for the variables
lambda_values = np.linspace(1, 2000, 50)  # Adjusted range for lambda
m_value = np.linspace(1, 40, 10)  # Adjusted range for VMs

# Create the grid
X, Y = np.meshgrid(lambda_values, m_value)
print(X.shape, Y.shape)

# Calculate CPU usage for each combination
Z = np.zeros_like(X)
for i in range(X.shape[0]):
    for j in range(Y.shape[1]):
        lambda_i = int(X[i, j])
        m = int(Y[i, j])
        cpu_usage = (compute_cpu_usage(lambda_i, 1, m, mu_i, K) * 100)
        Z[i, j] = cpu_usage


# Create the 3D plot
fig = plt.figure(figsize=(10, 8))
ax = fig.add_subplot(111, projection='3d')

# Use the 'jet' color map and increase resolution
surf = ax.plot_surface(X, Y, Z, cmap='jet', rstride=1,
                       cstride=1, edgecolor='none')

# Set labels and title
ax.set_xlabel('Tasks/s')
ax.set_ylabel('Number of VMs')
ax.set_zlabel('CPU usage (%)')
ax.set_title('CPU Usage vs. Number of VMs and Tasks/s')

# Adjust view angle to match the first image
ax.view_init(elev=10, azim=-110)

# Add color bar
fig.colorbar(surf, shrink=0.5, aspect=5)

plt.show()

