import sympy as sp
import numpy as np
import matplotlib.pyplot as plt


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

# keep N as 1 as we care about only vms
N, m, K = 1, 15, 100

service_rate = (45, 90, 150)

lambda_values = np.linspace(0, 2*10**4, 50).astype(int)
rejection_probablity = [[], [], []]

# Calculate CPU usage for each lambda
for lambda_i in lambda_values:
    for i, mu_i in enumerate(service_rate):
        rejection = compute_rejection_probablity(lambda_i, N, m, mu_i, K)
        rejection_probablity[i].append(rejection)


# Plot the graph
plt.plot(lambda_values, rejection_probablity[0], label="Small")
plt.plot(lambda_values, rejection_probablity[1], label="Medium")
plt.plot(lambda_values, rejection_probablity[2], label="Large")
plt.xlabel("Arrival Rate (lambda)")
plt.ticklabel_format(style='sci', axis='x', scilimits=(0,0))
plt.ylabel("Rejection Probablity")
plt.title("Rejection Probablity vs Arrival Rate (lambda)")
plt.grid(True)
plt.legend()
plt.show()
