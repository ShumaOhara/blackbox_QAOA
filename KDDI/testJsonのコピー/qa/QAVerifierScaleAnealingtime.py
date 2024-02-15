import json
import os
from pyqubo import Array, Constraint, Placeholder
import openjij as oj
import dimod
import time
import math
import numpy as np
import statistics as stats
import pandas as pd
import sys

from QAVerifierOneshot import ImportImputJSON, AnnealingInfo, ExecuteQA

def getArgments():
    if len(sys.argv) != 4:
        print('python -u "/Users/natsuki/Desktop/Serializable/testJson/qa/QAVerifierScaleAnealingtime.py" 10 301 10')
    else:
        args = []
        args.append(int(sys.argv[1]))
        args.append(int(sys.argv[2]))
        args.append(int(sys.argv[3]))
    return args

def ExportResult(Result, filename):
    df = pd.DataFrame.from_dict(Result)
    df = df.T
    path = f'output/{filename}.json'
    df.to_json(path)
    print(df)

def Main():
    filename = 'ChengRW200' #ここを変えればいい！
    edges, Group = ImportImputJSON(filename)

    parameters = AnnealingInfo(edges, Group)

    ranges = getArgments()

    Result = {}
    for annealing_time in range(ranges[0], ranges[1], ranges[2]):
        parameters.ChangeParameters(annealing_time = annealing_time)
        resultTable = ExecuteQA(edges, Group, parameters)
        Result[f'{annealing_time}'] = resultTable 
        print(annealing_time)

    ExportResult(Result, filename) #'test'部分を保存したい名前に変更．できれば自動化したいな

if __name__ == "__main__":
    Main()