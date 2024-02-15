import json
import os
import scipy.optimize
from qiskit import QuantumCircuit, Aer
from qiskit.circuit import Parameter
from qiskit.visualization import plot_histogram
from scipy.optimize import minimize
import time
import math
import numpy as np
import matplotlib.pyplot as plt

# JSONファイルをインプットする
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

# 目的関数を得る
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

# あるビット列bit_stringの目的関数の値を入手し、shot分まわすことで期待値を求める
def compute_expectation(counts, columns, Gce):
    avg = 0
    sum_count = 0
    for bit_string, count in counts.items():
        obj = blackbox_obj(bit_string, columns, Gce)
        avg += obj * count
        sum_count += count
    return avg/sum_count

# 量子回路の作成
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

# 期待値を得る(shotsの回数のデフォルトは1024回)
def get_expectation(columns, Gce, shots):
    backend = Aer.get_backend('qasm_simulator')
    backend.shots = shots
    
    def execute_circ(theta):
        qc = create_qaoa_circ(columns, Gce, theta)
        counts = backend.run(qc, seed_simulator=10, nshots=1024).result().get_counts()
        return compute_expectation(counts, columns, Gce)
    
    return execute_circ

# 目的関数が0になった回数を調べることによってFeasibleSolutionRateを求める
def get_violation_count(counts, columns, Gce):
    sum_count = 0
    for bit_string, count in counts.items():
        obj = blackbox_obj(bit_string, columns, Gce)
        if obj == 0:
            sum_count += count
    return sum_count

# JSONファイルをインポートして、columnをつくる(columnsは使わない)
columns, Gce = ImportImputJSON('ChengRW100')
column = []
for i, row in enumerate(Gce):
    indices = [idx for idx, val in enumerate(row) if val == 1]
    if len(indices) == 2:
        column.append((indices[0], indices[1]))

backend = Aer.get_backend('aer_simulator')
backend.shots = 1024

# アングルを決めるまで1回のみの場合
maximum_iteration = 1
op_opt_time = time.time()
expectation = get_expectation(column, Gce, 1024)
res1 = scipy.optimize.minimize(expectation,
               [1.0, 1.0],
               method='COBYLA',
               options={'maxiter':maximum_iteration})
ed_opt_time = time.time()
opt_time1 = ed_opt_time - op_opt_time

op_time = time.time()
qc_res = create_qaoa_circ(column, Gce, res1.x)
counts = backend.run(qc_res, seed_simulator=10, shots=1024).result().get_counts()
ed_time = time.time()
tau = (ed_time-op_time)/backend.shots

feasibleRate1 = 1-get_violation_count(counts, column, Gce)/backend.shots

tts1 = time_to_solution(tau, feasibleRate1, 0.99)

# アングルを決めるまで3回の場合
maximum_iteration = 3
op_opt_time = time.time()
expectation = get_expectation(column, Gce, 1024)
res3 = scipy.optimize.minimize(expectation,
               [1.0, 1.0],
               method='COBYLA',
               options={'maxiter':maximum_iteration})
ed_opt_time = time.time()
opt_time3 = ed_opt_time - op_opt_time

op_time = time.time()
qc_res = create_qaoa_circ(column, Gce, res3.x)
counts = backend.run(qc_res, seed_simulator=10, shots=1024).result().get_counts()
ed_time = time.time()
tau = (ed_time-op_time)/backend.shots

feasibleRate3 = 1-get_violation_count(counts, column, Gce)/backend.shots

tts3 = time_to_solution(tau, feasibleRate3, 0.99)

# アングルを決めるまで5回の場合
maximum_iteration = 5
op_opt_time = time.time()
expectation = get_expectation(column, Gce, 1024)
res5 = scipy.optimize.minimize(expectation,
               [1.0, 1.0],
               method='COBYLA',
               options={'maxiter':maximum_iteration})
ed_opt_time = time.time()
opt_time5 = ed_opt_time - op_opt_time

op_time = time.time()
qc_res = create_qaoa_circ(column, Gce, res5.x)
counts = backend.run(qc_res, seed_simulator=10, shots=1024).result().get_counts()
ed_time = time.time()
tau = (ed_time-op_time)/backend.shots

feasibleRate5 = 1-get_violation_count(counts, column, Gce)/backend.shots

tts5 = time_to_solution(tau, feasibleRate5, 0.99)

# アングルを決めるまで10回の場合
maximum_iteration = 10
op_opt_time = time.time()
expectation = get_expectation(column, Gce, 1024)
res10 = scipy.optimize.minimize(expectation,
               [1.0, 1.0],
               method='COBYLA',
               options={'maxiter':maximum_iteration})
ed_opt_time = time.time()
opt_time10 = ed_opt_time - op_opt_time

op_time = time.time()
qc_res = create_qaoa_circ(column, Gce, res10.x)
counts = backend.run(qc_res, seed_simulator=10, shots=1024).result().get_counts()
ed_time = time.time()
tau = (ed_time-op_time)/backend.shots

feasibleRate10 = 1-get_violation_count(counts, column, Gce)/backend.shots

tts10 = time_to_solution(tau, feasibleRate10, 0.99)

# アングルを決めるまで20回の場合(＝制限ない場合)
maximum_iteration = 20
op_opt_time = time.time()
expectation = get_expectation(column, Gce, 1024)
res20 = scipy.optimize.minimize(expectation,
               [1.0, 1.0],
               method='COBYLA',
               options={'maxiter':maximum_iteration})
ed_opt_time = time.time()
opt_time20 = ed_opt_time - op_opt_time

op_time = time.time()
qc_res = create_qaoa_circ(column, Gce, res20.x)
counts = backend.run(qc_res, seed_simulator=10, shots=1024).result().get_counts()
ed_time = time.time()
tau = (ed_time-op_time)/backend.shots

feasibleRate20 = 1-get_violation_count(counts, column, Gce)/backend.shots


tts20 = time_to_solution(tau, feasibleRate20, 0.99)

# 以下、測定結果
print('Optimize Time(1):  ', opt_time1)
print('Optimize Time(3):  ', opt_time3)
print('Optimize Time(5):  ', opt_time5)
print('Optimize Time(10): ', opt_time10)
print('Optimize Time(20): ', opt_time20)
print()
print('Time to Solution(1):  ', tts1)
print('Time to Solution(3):  ', tts3)
print('Time to Solution(5):  ', tts5)
print('Time to Solution(10): ', tts10)
print('Time to Solution(20): ', tts20)
print()
print('Fesible Solution Rate(1):  ', feasibleRate1)
print('Fesible Solution Rate(3):  ', feasibleRate3)
print('Fesible Solution Rate(5):  ', feasibleRate5)
print('Fesible Solution Rate(10): ', feasibleRate10)
print('Fesible Solution Rate(20): ', feasibleRate20)
print()
print('Optimized Parameters(1):  ', res1.x)
print('Optimized Parameters(3):  ', res3.x)
print('Optimized Parameters(5):  ', res5.x)
print('Optimized Parameters(10): ', res10.x)
print('Optimized Parameters(20): ', res20.x)
print()
print('Average Objective Function(1):  ', res1.fun)
print('Average Objective Function(3):  ', res3.fun)
print('Average Objective Function(5):  ', res5.fun)
print('Average Objective Function(10): ', res10.fun)
print('Average Objective Function(20): ', res20.fun)
