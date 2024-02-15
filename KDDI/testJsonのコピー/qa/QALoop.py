import json
from pyqubo import Array, Constraint, Placeholder
import dimod
import time
import math
import numpy as np
import statistics as stats
from dwave.system import LeapHybridSampler
from QAVerifierOneshot import ExecuteQA, ImportImputJSON, AnnealingInfo, TimeToSolution



def ExecuteQALoop(edges, Group, parameters, num_loop):
    for __ in range(num_loop):
        resultTable = ExecuteQA(edges, Group, parameters)
        print(f"#loop = {__}")
    
def Main(fileName):
    edges, Group = ImportImputJSON(fileName)

    #AnnealingInfoのインスタンス作成
    parameters = AnnealingInfo(edges, Group)
    parameters.ChangeParameters(printDetails=True)
    parameters.Print()

    num_loop = 300
    ExecuteQALoop(edges, Group, parameters, num_loop)



if __name__ == "__main__":
    Main('twitter10000')