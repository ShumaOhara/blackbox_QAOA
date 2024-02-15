import json
import os
from scipy.optimize import minimize
from qiskit import QuantumCircuit, Aer
from qiskit.circuit import Parameter
import time
import math


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

# TTSを得る
def time_to_solution(tau, feasible_rate, target_probability):
    if feasible_rate == 1:
        time = tau
    else:
        time = tau * math.ceil(math.log(1-target_probability)/math.log(1-feasible_rate))
    return time

# 問題の目的関数を定義する
def blackbox_obj(solution, columns, Gce):
    solution_array = list(map(int, solution))

    obj = 0
    
    # 目的関数の計算
    for i in range(len(Gce)):
        note = 0
        for j in range(len(Gce[0])):
            note += (Gce[i][j] * solution_array[j])
            obj += ((note-1)**2)
    return obj

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
    # 量子ビットはXeの部分に落とし込む
    nqubits = len(Gce[0])
    n_layers = len(theta)//2
    beta = theta[:n_layers]
    gamma = theta[n_layers:]
    
    qc = QuantumCircuit(nqubits)
    qc.h(range(nqubits))

    # |γ, β>のところ
    for layer_index in range(n_layers):
        for pair in list(columns):
            qc.rzz(gamma[layer_index], pair[0], pair[1])
        for qubit in range(nqubits):
            qc.rx(2 * beta[layer_index], qubit)
        
    qc.measure_all()
    return qc

# 期待値を得る(shots=512なので512回ずつ実行する(?))
def get_expectation(columns, Gce, shots=512):
    backend = Aer.get_backend('qasm_simulator')
    backend.shots = shots
    
    # 回路を実行する
    def execute_circ(theta):
        qc = create_qaoa_circ(columns, Gce, theta)
        counts = backend.run(qc).result().get_counts()
        return compute_expectation(counts, columns, Gce)
    
    return execute_circ

# JSONファイルをインポートして、columnをつくる(columnsは使わない)
columns, Gce = ImportImputJSON('ChengRW100')
column = []
# columnはGceの横に見た際のどこに1があるかを示すタプル
for i, row in enumerate(Gce):
    indices = [idx for idx, val in enumerate(row) if val == 1]
    if len(indices) == 2:
        column.append((indices[0], indices[1]))

# 前までのコードで期待値を得るものをexpectationに格納しておく
expectation = get_expectation(column, Gce)
# [2, 2]はγ、βの初期値
res = minimize(expectation, [2.0, 2.0], method='COBYLA')


# ここからは作った量子回路で0を得るまでの時間

