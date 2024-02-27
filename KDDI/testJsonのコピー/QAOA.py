import json
import os
import scipy.optimize
from qiskit import QuantumCircuit, Aer
from qiskit.circuit import Parameter
from scipy.optimize import minimize
import time
import math
import numpy as np

def ImportImputJSON(fileName):
    columns_path = os.path.join('json', fileName, 'columns.json')
    table_path = os.path.join('json', fileName, 'Table.json')

    if not os.path.exists(columns_path) or not os.path.exists(table_path):
        print("Error: Files not found.")
        return None, None
    
    with open(columns_path) as f:
        columns = json.load(f)

    with open(table_path) as f:
        Table = json.load(f)

    return columns, Table

def blackbox_obj(solution, columns, Gce):
    solution_array = list(map(int, solution))
    obj = 0

    for i in range(len(Gce)):
        note = 0
        for j in range(len(columns)*2):
            note += (Gce[i][j] * solution_array[j])
        obj += ((note-1)**2)
    
    return obj

def time_to_solution(tau, feasibleRate, targetProbability):
    if feasibleRate == 1:
        time = tau
    else:
        time = tau * math.ceil(math.log(1-targetProbability)/math.log(1-feasibleRate))
    return time

def compute_expectation(counts, columns, Gce):
    avg = 0
    sum_count = 0
    for bit_string, count in counts.items():
        obj = blackbox_obj(bit_string, columns, Gce)
        avg += obj * count
        sum_count += count
    return avg/sum_count

def create_qaoa_circ(columns, Gce, theta):
    nqubits = len(Gce[0])
    n_layers = len(theta)//2
    beta = theta[:n_layers]
    gamma = theta[n_layers:]
    
    qc = QuantumCircuit(nqubits)

    qc.h(range(nqubits))

    for layer_index in range(n_layers):
        for pair in list(columns):
            qc.rzz(gamma[layer_index], pair[0], pair[1])
        for qubit in range(nqubits):
            qc.rx(2 * beta[layer_index], qubit)
        
    qc.measure_all()
    return qc

def get_expectation(columns, Gce, shots):
    backend = Aer.get_backend('qasm_simulator')
    backend.shots = shots
    
    def execute_circ(theta):
        qc = create_qaoa_circ(columns, Gce, theta)
        counts = backend.run(qc, seed_simulator=10, nshots=512).result().get_counts()
        return compute_expectation(counts, columns, Gce)
    
    return execute_circ

def get_violation_count(counts, columns, Gce):
    violation_count = 0
    for items, values in counts.items():
        obj = blackbox_obj(items, columns, Gce)
        if obj > 0:
            violation_count += values
    return violation_count

columns, Gce = ImportImputJSON('ChengRW100')
column = []
for i, row in enumerate(Gce):
    indices = [idx for idx, val in enumerate(row) if val == 1]
    if len(indices) == 2:
        column.append((indices[0], indices[1]))

backend = Aer.get_backend('aer_simulator')
backend.shots = 1024

feasibleRate1 = 0
feasibleRate5 = 0
feasibleRate10 = 0
feasibleRate15 = 0
feasibleRate20 = 0

tau1 = 0
tau5 = 0
tau10 = 0
tau15 = 0
tau20 = 0

opt_time1 = 0
opt_time5 = 0
opt_time10 = 0
opt_time15 = 0
opt_time20 = 0

for i in range(1000):
    maximum_iteration = 1
    op_opt_time = time.time()
    expectation = get_expectation(column, Gce, 1024)
    res1 = scipy.optimize.minimize(expectation,
                [1.0, 1.0],
                method='COBYLA',
                options={'maxiter':maximum_iteration})
    ed_opt_time = time.time()
    opt_time1 += ed_opt_time - op_opt_time

    op_time = time.time()
    qc_res1 = create_qaoa_circ(column, Gce, res1.x)
    counts = backend.run(qc_res1, seed_simulator=10, shots=1024).result().get_counts()
    ed_time = time.time()
    tau1 += (ed_time-op_time)/backend.shots

    feasibleRate1 += 1-get_violation_count(counts, column, Gce)/backend.shots

    maximum_iteration = 5
    op_opt_time = time.time()
    expectation = get_expectation(column, Gce, 1024)
    res5 = scipy.optimize.minimize(expectation,
                [1.0, 1.0],
                method='COBYLA',
                options={'maxiter':maximum_iteration})
    ed_opt_time = time.time()
    opt_time5 += ed_opt_time - op_opt_time

    op_time = time.time()
    qc_res5 = create_qaoa_circ(column, Gce, res5.x)
    counts = backend.run(qc_res5, seed_simulator=10, shots=1024).result().get_counts()
    ed_time = time.time()
    tau5 += (ed_time-op_time)/backend.shots

    feasibleRate5 += 1-get_violation_count(counts, column, Gce)/backend.shots

    maximum_iteration = 15
    op_opt_time = time.time()
    expectation = get_expectation(column, Gce, 1024)
    res15 = scipy.optimize.minimize(expectation,
                [1.0, 1.0],
                method='COBYLA',
                options={'maxiter':maximum_iteration})
    ed_opt_time = time.time()
    opt_time15 += ed_opt_time - op_opt_time

    op_time = time.time()
    qc_res15 = create_qaoa_circ(column, Gce, res15.x)
    counts = backend.run(qc_res15, seed_simulator=10, shots=1024).result().get_counts()
    ed_time = time.time()
    tau15 += (ed_time-op_time)/backend.shots

    feasibleRate15 += 1-get_violation_count(counts, column, Gce)/backend.shots

    maximum_iteration = 10
    op_opt_time = time.time()
    expectation = get_expectation(column, Gce, 1024)
    res10 = scipy.optimize.minimize(expectation,
                [1.0, 1.0],
                method='COBYLA',
                options={'maxiter':maximum_iteration})
    ed_opt_time = time.time()
    opt_time10 += ed_opt_time - op_opt_time

    op_time = time.time()
    qc_res10 = create_qaoa_circ(column, Gce, res10.x)
    counts = backend.run(qc_res10, seed_simulator=10, shots=1024).result().get_counts()
    ed_time = time.time()
    tau10 += (ed_time-op_time)/backend.shots

    feasibleRate10 += 1-get_violation_count(counts, column, Gce)/backend.shots


    # アングルを決めるまで20回の場合(＝制限ない場合)
    maximum_iteration = 20
    op_opt_time = time.time()
    expectation = get_expectation(column, Gce, 1024)
    res20 = scipy.optimize.minimize(expectation,
                [1.0, 1.0],
                method='COBYLA',
                options={'maxiter':maximum_iteration})
    ed_opt_time = time.time()
    opt_time20 += ed_opt_time - op_opt_time

    op_time = time.time()
    qc_res20 = create_qaoa_circ(column, Gce, res20.x)
    counts = backend.run(qc_res20, seed_simulator=10, shots=1024).result().get_counts()
    ed_time = time.time()
    tau20 += (ed_time-op_time)/backend.shots

    feasibleRate20 += 1-get_violation_count(counts, column, Gce)/backend.shots


feasibleRate1 = feasibleRate1/1000
feasibleRate15 = feasibleRate15/1000
feasibleRate5 = feasibleRate5/1000
feasibleRate10 = feasibleRate10/1000
feasibleRate20 = feasibleRate20/1000

tau1 = tau1/1000
tau15 = tau15/1000
tau5 = tau5/1000
tau10 = tau10/1000
tau20 = tau20/1000

opt_time1 = opt_time1/1000
opt_time15 = opt_time15/1000
opt_time5 = opt_time5/1000
opt_time10 = opt_time10/1000
opt_time20 = opt_time20/1000

tts1 = time_to_solution(tau1, feasibleRate1, 0.99)
tts15 = time_to_solution(tau15, feasibleRate15, 0.99)
tts5 = time_to_solution(tau5, feasibleRate5, 0.99)
tts10 = time_to_solution(tau10, feasibleRate10, 0.99)
tts20 = time_to_solution(tau20, feasibleRate20, 0.99)
tts20_999 = time_to_solution(tau20, feasibleRate20, 0.999)
tts20_9999 = time_to_solution(tau20, feasibleRate20, 0.9999)

# 以下、測定結果# 出力結果を保存するためのテキスト
output_text = f"""
Optimize Time(1):  {opt_time1}
Optimize Time(15):  {opt_time15}
Optimize Time(5):  {opt_time5}
Optimize Time(10): {opt_time10}
Optimize Time(20): {opt_time20}

Time to Solution(1):  {tts1}
Time to Solution(15):  {tts15}
Time to Solution(5):  {tts5}
Time to Solution(10): {tts10}
Time to Solution(20): {tts20}
Time to Solution(20.9): {tts20_999}
Time to Solution(20.99): {tts20_9999}

Feasible Solution Rate(1):  {feasibleRate1}
Feasible Solution Rate(15):  {feasibleRate15}
Feasible Solution Rate(5):  {feasibleRate5}
Feasible Solution Rate(10): {feasibleRate10}
Feasible Solution Rate(20): {feasibleRate20}

Optimized Parameters(1):  {res1.x}
Optimized Parameters(15):  {res15.x}
Optimized Parameters(5):  {res5.x}
Optimized Parameters(10): {res10.x}
Optimized Parameters(20): {res20.x}

Average Objective Function(1):  {res1.fun}
Average Objective Function(15):  {res15.fun}
Average Objective Function(5):  {res5.fun}
Average Objective Function(10): {res10.fun}
Average Objective Function(20): {res20.fun}
"""

# ファイルに書き込む
with open('output_results.txt', 'w') as file:
    file.write(output_text)
