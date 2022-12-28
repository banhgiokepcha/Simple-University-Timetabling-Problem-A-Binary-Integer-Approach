import numpy as np
from ortools.sat.python import cp_model
from ortools.linear_solver import pywraplp
import time

"""
    THE CP MODEL TO SOLVE THE UNIVERSITY TIMETABLING PROBLEM:

created by: Nguyen Duc Quyen 
student id: 20183617
date: Thursday, December 16th, 2021
"""

# Read data 
f = open("data/test15.txt", "r")

line = f.readline()
args = line.split(" ")
num_courses = int(args[0])
num_classrooms = int(args[1])

credit = np.zeros(num_courses, dtype= int)
teacher = np.zeros(num_courses, dtype= int)
student = np.zeros(num_courses, dtype= int)
for i in range(num_courses):
    line = f.readline()
    args = line.split(" ")
    credit[i] = int(args[0])
    teacher[i] = int(args[1])
    student[i] = int(args[2])

capacity = np.zeros(num_classrooms, dtype= int)
for i in range(num_classrooms):
    line = f.readline()
    args = line.split(" ")
    capacity[i] = int(args[0])
"""
# Create the matrix of conflicts
conflicts = np.zeros((num_courses, num_courses))
for i in range(num_courses):
    for j in range(i, num_courses):
        if i!= j and teacher[i] == teacher[j]: 
            conflicts[i, j] = 1
            conflicts[j, i] = 1
"""
num_teachers = np.amax(teacher)

teacher_lst = []
for i in range(num_teachers+1):
    teacher_lst.append([])

for n in range(num_courses):
    teacher_lst[teacher[n]].append(n)

print("Number of courses: ", num_courses)
print("Credit:", credit)
print("Teacher:", teacher)
print("Student:", student)
print("Number of classrooms: ", num_classrooms)
print("Capacity:", capacity)
print("Conflicts: \n", teacher_lst)
# Create the model 
model = cp_model.CpModel()

# Add variables
x = {}
for i in range(5):
    for j in range(12):
        for m in range(num_classrooms):
            for n in range(num_courses):
                x[i, j, m, n] = model.NewIntVar(0, 1, 'x[{},{},{},{}]'.format(i, j, m, n))

# Add constraints
#   At most 1 course can take place in 1 classroom in each time slot and vise versa
for i in range(5):
    for j in range(12):
        for m in range(num_classrooms):
            model.AddLinearConstraint(sum(x[i,j,m,n] for n in range(num_courses)), 0, 1)

for i in range(5):
    for j in range(12):
        for n in range(num_courses):
            model.AddLinearConstraint(sum(x[i,j,m,n] for m in range(num_classrooms)), 0, 1)

#   The number of student in each class must be smaller than the capacity of the classroom
for i in range(5):
    for j in range(12):
        for m in range(num_classrooms):
            model.Add(sum(x[i,j,m,n]*(capacity[m]-student[n]) for n in range(num_courses)) >= 0)

for n in range(num_courses):
    total_slot = []
    for i in range (5):
        for j in range (12):
            for m in range(num_classrooms):
                total_slot.append(x[i,j,m,n])
    model.AddLinearConstraint(sum(total_slot), int(credit[n]), int(credit[n]))

#   Courses that have conflicts with each other cannot be taught at the same timeslot
"""
for n1 in range(num_courses):
    for n2 in range(n1, num_courses):
        if n2 != n1 and conflicts[n1, n2] == 1:
            for i in range(5):
                for j in range(12):
                    for m in range(num_classrooms):
                        model.AddAllDifferent([x[i,j,m,n1], x[i,j,m,n2]])
"""

for lst in teacher_lst:
    if lst: # if the list is not empty, add the constraints
        for i in range(5):
            for j in range(12):
                model.AddLinearConstraint(sum(x[i,j,m,n]for m in range (num_classrooms) for n in lst), 0, 1)


# Consecutiveness of each course
#   If the course starts at the begining of the day 
for i in range(5):
    for m in range(num_classrooms):
        for n in range(num_courses):
            for t in range(1, credit[n]):
                model.Add(x[i,0,m,n] - x[i,t,m,n] <= 0)
#   If the course ends at the end of the day
for i in range(5):
    for m in range(num_classrooms):
        for n in range(num_courses):
            for t in range(1, credit[n]):
                model.Add(x[i,11,m,n] - x[i,11-t,m,n] <= 0)
#   If the course starts and ends during the day
for i in range(5):
    for m in range(num_classrooms):
        for n in range(num_courses):
            for p in range(0, 10):
                for t in range(1, credit[n]):
                    if(p + t + 1<= 11):
                        model.Add(-x[i,p,m,n] + x[i,p+1,m,n] - x[i,p+t+1,m,n] <= 0)

#   Consistency of classroom
#   A course must be taught in a specific room through out the week
for i in range(5):
    for j in range(12):
        for m in range(num_classrooms):
            for n in range(num_courses):
                model.Add(x[i,j,m,n]*credit[n] <= sum(x[a,b,m,n] for a in range(5) for b in range (12)))
# Create the solver
solver = cp_model.CpSolver()
start = time.time()
status = solver.Solve(model)
end = time.time()
print("Constraint Programming model:")
print("Status: {}".format(status))
print("Time: {}".format(end - start))

Solutions = []
for i in range(5):
    temp = -np.ones((num_classrooms, 12))
    Solutions.append(temp)
# Display the solution
if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
    for i in range(5):
        for j in range(12):
            for m in range(num_classrooms):
                for n in range(num_courses):
                    if solver.Value(x[i,j,m,n]) > 0:
                        Solutions[i][m,j] = n
                    
for i in range(5):
    if i == 0: day = "Monday"
    elif i == 1: day = "Tuesday"
    elif i == 2: day = "Wednesday"
    elif i == 3: day = "Thursday"
    else: day = "Friday"
    print(day)
    for m in range(num_classrooms):
        print("Classroom no.{:2d} :".format(m), end= "")
        for j in range(12):
            if Solutions[i][m,j] == -1:
                print(" - ", end="")
            else:
                print("{:^3d}".format(int(Solutions[i][m,j])), end= "")
        print()