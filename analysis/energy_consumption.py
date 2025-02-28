import numpy as np
import matplotlib.pyplot as plt
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


def compute_cpu_usage(lambda_i, N, m, mu_i, K):
    u = sum(j*compute_pi_n(lambda_i, N, m, mu_i, K, j) for j in range(0, m))
    u += sum(m*compute_pi_n(lambda_i, N, m, mu_i, K, j)
             for j in range(m+1, K+1))

    u /= m
    return u


# energy consumption per machine
E_base = 100
# energy consumption per vm
E_vm = [20, 35, 50]
N, m, K = 10, 15, 100

# energy consumption for m vm's
E_m_vm = [m*x for x in E_vm]

service_rate = (45, 90, 150)

lambda_values = np.linspace(0, 500, 11).astype(int)
enegry_consumption = [[], [], []]

# Calculate CPU usage for each lambda
for lambda_i in lambda_values:
    for i, mu_i in enumerate(service_rate):
        cpu_usage = compute_cpu_usage(lambda_i, N, m, mu_i, K)
        # for n phyical machine
        energy_usage = E_base*N + E_m_vm[i] * cpu_usage
        enegry_consumption[i].append(energy_usage)


plt.figure(figsize=(8, 6))
plt.plot(lambda_values, enegry_consumption[0],
         'g-s', label='Small VMs', linewidth=1)
plt.plot(lambda_values, enegry_consumption[1],
         'y-^', label='Medium VMs', linewidth=1)
plt.plot(lambda_values, enegry_consumption[2],
         'r-d', label='Large VMs', linewidth=1)

plt.xlabel('Tasks/s')
plt.ylabel('Energy consumption (watts)')
plt.yticks(np.arange(1000, 1026, 5))
plt.ylim(1000, 1025)
plt.legend()
plt.grid(True, linestyle=':')
plt.title('Comparison of energy consumption for different VM sizes')
plt.show()
