from ortools.sat.python import cp_model
from ortools.linear_solver import pywraplp
import numpy as np

print(cp_model.OPTIMAL) #4
print(cp_model.FEASIBLE) #2
print(cp_model.INFEASIBLE) #3
print(cp_model.MODEL_INVALID) #1
print(cp_model.UNKNOWN) #0

print()
print(pywraplp.Solver.OPTIMAL) #0
print(pywraplp.Solver.FEASIBLE) #1
print(pywraplp.Solver.INFEASIBLE) #2

print(cp_model.infinity())
