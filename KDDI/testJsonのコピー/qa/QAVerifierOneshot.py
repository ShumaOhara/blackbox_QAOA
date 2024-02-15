import json
from pyqubo import Array, Constraint, Placeholder
import dimod
import time
import math
import numpy as np
import statistics as stats
from dwave.system.samplers import DWaveSampler
from dwave.system.composites import EmbeddingComposite

def ImportImputJSON(fileName):
    print('json/' + fileName + '/columns.json')
    with open('json/' + fileName + '/columns.json') as f:
        columns = json.load(f)

    with open('json/' + fileName + '/Table.json') as f:
        Table = json.load(f)
    
    print("edges")
    print(columns)
    print()

    print("Group")
    print(Table)
    print()

    return columns, Table

#各種アニーリングパラメータを設定するクラス
class AnnealingInfo:

    #コンストラクタ 全ての必要なパラメータ値を入手する
    def __init__(self, edges, Group):
        self.num_reads = 1000
        self.annealing_time = 20

        self.num_const = len(Group)
        self.num_edges = len(edges)

        self.feed_dict = {"w_selectEdge" : 1}
        self.printDetails = False

        print("success for build constractor")

    def Print(self):
        print()
        print(f"#constraints = {self.num_const}, #edges = {self.num_edges}")
        print()

        print(f"annealing_time : {self.annealing_time}")
        print(f"num_reads : {self.num_reads}")
        print()

        print(f"w_selectEdge = {self.feed_dict['w_selectEdge']}")
        print()
    
    #アニーリングのパラメータを変更したい時の関数
    def ChangeParameters(self, num_reads=1000, annealing_time=20, w_selectEdge=1, printDetails=False):
        self.num_reads = num_reads
        self.feed_dict['w_selectEdge'] = w_selectEdge
        self.annealing_time = annealing_time
        self.printDetails = printDetails

def TimeToSolution(tau, feasibleRate, targetProbability):
    if feasibleRate==1:
        time = tau
    else:
        time = tau * math.ceil(math.log(1-targetProbability)/math.log(1-feasibleRate))
    return time

def ExecuteQA(edges, Group, parameters):
    #QUBO式を作っていく
    x = Array.create('x', shape=(parameters.num_edges), vartype='BINARY')

    #目的関数、制約関数の設定
    def buildQuboConstraint(x):
        H = Constraint(
                sum((sum(Group[c][e] * x[e] for e in range(parameters.num_edges)) - 1)**2 
                    for c in range(parameters.num_const)),
                    'w_selectEdge')
        return H

    
    #ここから時間計測開始
    anneal_start = time.time()
    prepare_start = time.time()

    #関数をQUBOに引き出す
    H_constraint = Placeholder('w_selectEdge') * buildQuboConstraint(x)
    Q = H_constraint

    #モデルにコンパイルする
    model = Q.compile()
    qubo, offset = model.to_qubo(feed_dict=parameters.feed_dict)

    prepare_end = time.time()
    prepare_time = prepare_end - prepare_start

    # 接続情報をオプションとして渡す場合は以下のようにします。
    endpoint = 'https://cloud.dwavesys.com/sapi'
    token = 'rCeY-676158a994ab2c64eaee29749e95d4c998bfdc20'
    solver = 'Advantage_system4.1'

    #QAにかける
    # DWaveSamplerを用います。
    dw = DWaveSampler(endpoint=endpoint, token=token, solver=solver)
    # キメラグラフに埋め込みを行います。
    sampler = EmbeddingComposite(dw)
    response = sampler.sample_qubo(Q=qubo, annealing_time = parameters.annealing_time, num_reads = parameters.num_reads)

    


    violation = {'w_selectEdge':0}

    violation_count = 0
    sol_violation_count = 0

    #実行結果を得る
    solution_energies = []
    for record in response.record:
        sol, energy, num_occ = record[0], record[1], record[2]
        decoded_solution = model.decode_sample(dict(zip(response.variables,sol)), vartype='BINARY', feed_dict=parameters.feed_dict)
        solution_energy = model.energy(dict(zip(response.variables,sol)), vartype='BINARY', feed_dict=parameters.feed_dict)
        x_solution = {}
        for e in range(parameters.num_edges):
            x_solution[e] = decoded_solution.array('x', (e))
        for penalty in decoded_solution.constraints(only_broken=True).keys():
            violation[penalty] += int(decoded_solution.constraints(only_broken=True)[penalty][1])
        solution_energies.append(solution_energy)
        if len(decoded_solution.constraints(only_broken=True)) > 0:
            sol_violation_count += 1
    for (id, value) in violation.items():
        if id != 0:
            violation_count += value

    minimum_cost = response.first[1]
    count = response.first[2]
    feasibleSolutionRate = 1-sol_violation_count/parameters.num_reads
    oneExecTime = response.info['timing']['qpu_sampling_time'] / parameters.num_reads /1000

    resultTable = {}
    resultTable['min'] = min(solution_energies)
    resultTable['mean'] = stats.mean(solution_energies)
    resultTable['max'] = max(solution_energies)
    resultTable['feasibleRate'] = feasibleSolutionRate
    resultTable['time'] = oneExecTime
    resultTable['TTS'] = TimeToSolution(oneExecTime, feasibleSolutionRate, 0.99)


    if parameters.printDetails==True:
        print()
        print('[Execution Result]')
        print('Feasible Solution Rate:',1-sol_violation_count/parameters.num_reads)
        print('Each Violation Count:', violation)
        print('Minimum Cost:', minimum_cost)
        print('Minimum Cost Result Count:', count)
        print()
        print('[Execution Time (ms)]')
        print('prepare_time: ', prepare_time * 1000)
        print('sampling_time: ', response.info['timing']['qpu_sampling_time'] / 1000)
        print('execution_time/a execution: ', response.info['timing']['qpu_sampling_time'] / parameters.num_reads /1000)
        print('Time to Solution (TTS): ', TimeToSolution(oneExecTime, feasibleSolutionRate, 0.99))
        #print('total_time: ', prepare_time * 1000+response.info['sampling_time'] / 1000+response.info['execution_time'] / 1000)
        #print('annealing_time: ',anneal_time * 1000)
        print()
        print('[Energy statistics]')
        print('最小値:', min(solution_energies))
        print('最大値:', max(solution_energies))
        """
        print('平均値:', stats.mean(solution_energies))
        print('中央値:', stats.median(solution_energies))
        print('分散:', stats.variance(solution_energies))
        print('標準偏差:', stats.stdev(solution_energies))
        print('25%tile:', np.percentile(np.array(solution_energies), 25))
        print('75%tile:', np.percentile(np.array(solution_energies), 75))
        """
    
    return resultTable
    
def Main(fileName):
    edges, Group = ImportImputJSON(fileName)

    #AnnealingInfoのインスタンス作成
    parameters = AnnealingInfo(edges, Group)
    parameters.ChangeParameters(printDetails=True)
    parameters.Print()

    resultTable = ExecuteQA(edges, Group, parameters)


if __name__ == "__main__":
    Main('twitter10000')