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


def compute_tasks_in_queue(lambda_i, N, m, mu_i):
    rho = compute_rho(lambda_i, N, m, mu_i)
    return rho**2 / (1 - rho)


def compute_mean_waiting_time(lambda_i, N, m, mu_i, mu):
    rho = compute_rho(lambda_i, N, m, mu_i)
    return rho / (mu*(1-rho))


def compute_mean_waiting_tasks(lambda_i, N, m, mu_i, K):
    res = sum((j - m)*compute_pi_n(lambda_i, N, m, mu_i, K, j)
              for j in range(m+1, K+1))

    return res


def compute_mean_waiting_tasks(lambda_i, N, m, mu_i, K):
    Q_dash = compute_mean_waiting_tasks(lambda_i, N, m, mu_i, K)
    lambda_dash = compute_lambda_dash(lambda_i, N, m, mu_i, K)
    return Q_dash/lambda_dash


def compute_average_number_of_tasks_per_queue(lambda_i, N, m, mu_i):
    rho = compute_rho(lambda_i, N, m, mu_i)
    return rho / (1-rho)


def compute_average_queue_response_time(lambda_i, N, m, mu_i, mu):
    rho = compute_rho(lambda_i, N, m, mu_i)
    return 1 / (mu*(1-rho))


def compute_average_number_of_tasks_per_pm(lambda_i, N, m, mu_i, K):
    return sum(j*compute_pi_n(lambda_i, N, m, mu_i, K, j) for j in range(0, K+1))


def compute_average_response_time(lambda_i, N, m, mu_i, K):
    N_dash = compute_average_number_of_tasks_per_pm(lambda_i, N, m, mu_i, K)
    lambda_dash = compute_lambda_dash(lambda_i, N, m, mu_i, K)
    return N_dash/lambda_dash


N, m, K = 10, 15, 100

service_rate = (45, 90, 150)

lambda_values = np.linspace(0, 2*10**4, 100)
response_time = [[], [], []]

# Calculate CPU usage for each lambda
for lambda_i in lambda_values:
    for i, mu_i in enumerate(service_rate):
        res = compute_average_response_time(lambda_i, N, m, mu_i, K)
        response_time[i].append(res)


# Plot the graph
plt.plot(lambda_values, response_time[0], label="Small")
plt.plot(lambda_values, response_time[1], label="Medium")
plt.plot(lambda_values, response_time[2], label="Large")
plt.xlabel("Arrival Rate (lambda)")
plt.ylabel("Response Time")
plt.title("Response Time vs Arrival Rate (lambda)")
plt.grid(True)
plt.legend()
plt.show()
