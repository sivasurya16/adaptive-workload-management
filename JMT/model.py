import pyJMT as jmt
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


def create_model(name, mu, arrival_rate=20, N=10, m=15, K=100):
    model = jmt.Network("M/M/c/K Task Classification System")

    # Define system components
    source = jmt.Source(model, "From Task Classifier")
    queue = jmt.Router(model, name + "_Queue")
    sink = jmt.Sink(model, "Task Completed")

    PMS = [jmt.Queue(model, f"{name}_PM_{i}",
                     jmt.SchedStrategy.FCFS, dropRule=jmt.DropStrategy.DROP) for i in range(N)]

    tasks = jmt.OpenClass(model, "Tasks")
    source.setArrival(tasks, jmt.Exp(arrival_rate))
    source.setRouting(tasks, jmt.RoutingStrategy.PROB)
    source.setProbRouting(tasks, queue, 1)
    # queue.setService(tasks, jmt.Exp(25000))
    queue.setRouting(tasks, jmt.RoutingStrategy.RROBIN)

    for pm in PMS:
        pm.setService(tasks, jmt.Exp(mu*m))
        pm.setNumberOfServers(m)
        pm.setCapacity(K)

        model.addLinks([
            (queue, pm),
            (pm, sink)
        ])
        model.addMetric(tasks, pm, jmt.Metrics.UTILIZATION)

    model.addMetric(tasks, model, jmt.Metrics.RESPONSE_TIME)
    model.addMetric(tasks, model, jmt.Metrics.THROUGHPUT)

    model.addLink(source, queue)
    model.defaultMetrics = False
    model.saveNamedJsimg(name)

    print(f"Created model {name}")
    return model


def get_avg_cpu_metrics(result):
    df = pd.DataFrame([
        {
            "node": node,
            "meanValue": float(data["meanValue"]),
            "measureType": data["measureType"],

        }
        for node, datas in result.items()
        for data in datas["Tasks"]
    ])

    utilization = df[df['measureType'] == "Utilization"]

    avg_util = utilization["meanValue"].sum()/len(utilization)
    print(len(utilization))

    return min(avg_util*15*100, 100)


create_model("Small", 45, 20)
create_model("Medium", 90, 20)
create_model("Large", 150, 20)


# model = create_model("Small", 45, 20000,1)
# model.jsimgOpen()
# model.saveNamedJsimg("Small")
# model.saveResultsFileNamed("Small")
# result = model.getResults()
# print(result)
# print(get_avg_cpu_metrics(result))


# service_rate = (45, 90, 150)

# lambda_values = np.linspace(20, 2*10**4, 10).astype(int)
# cpu_usage_values = [[], [], []]

# # Calculate CPU usage for each lambda
# for lambda_i in lambda_values:
#     for i, mu_i in enumerate(service_rate):
#         model = create_model("Small", mu_i, lambda_i)
#         result = model.getResults()
#         cpu_usage_values[i].append(get_avg_cpu_metrics(result))

# plt.scatter(lambda_values, cpu_usage_values[0], label="Small",
#             marker='o', edgecolors='black', facecolors='none')
# plt.scatter(lambda_values, cpu_usage_values[1], label="Medium",
#             marker='o', edgecolors='black', facecolors='none')
# plt.scatter(lambda_values, cpu_usage_values[2], label="Large",
#             marker='o', edgecolors='black', facecolors='none')
# plt.xlabel("Arrival Rate (lambda)")
# plt.ylabel("CPU Usage")
# plt.title("CPU Usage vs Arrival Rate (lambda)")
# plt.grid(True)
# plt.legend()
# plt.show()

# cpu = []
# for lambda_i in lambda_values:
#     # for i, mu_i in enumerate(service_rate):
#     #     res = compute_average_response_time(lambda_i, N, m, mu_i, K)
#     #     response_time[i].append(res)
#     model = create_model("Small", 45, lambda_i)
#     result = model.getResults()
#     cpu.append(get_avg_metrics(result)[0])
#     print(cpu[-1])

# plt.scatter(lambda_values, cpu, label="Small")
# plt.xlabel("CPU Utilization (lambda)")
# plt.ylabel("Response Time")
# plt.title("Response Time vs CPU Utilization (lambda)")
# plt.grid(True)
# plt.legend()
# plt.show()

# create_model("Medium", 90)
# create_model("Large", 150)
