import numpy as np
from ortools.sat.python import cp_model
import time


"""
    THE CP MODEL TO SOLVE THE UNIVERSITY TIMETABLING PROBLEM:

created by: Nguyen Duc Quyen 
student id: 20183617
date: Thursday, December 16th, 2021
"""

# Read data 
f = open("data/test18.txt", "r")

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

num_teachers = np.amax(teacher)

teacher_lst = []
for i in range(num_teachers+1):
    teacher_lst.append([])

for n in range(num_courses):
    teacher_lst[teacher[n]].append(n)

classroom_lst = []
for i in range(num_courses):
    classroom_lst.append([])

for n in range(num_courses):
    for m in range(num_classrooms):
        if(student[n] <= capacity[m]):
            classroom_lst[n].append(m)

print("Number of courses: ", num_courses)
print("Credit:", credit)
print("Teacher:", teacher)
print("Student:", student)
print("Number of classrooms: ", num_classrooms)
print("Capacity:", capacity)
print("Conflicts: \n", teacher_lst)
print("Rooms: \n", classroom_lst)


# Create the model 
model = cp_model.CpModel()



# Add variables
day = {}
slot = {}
room = {}
for n in range(num_courses):
    day[n] = model.NewIntVar(0, 4, 'day[{}]'.format(n))

for n in range(num_courses):
    slot[n] = model.NewIntVar(0, int(12 - credit[n]), 'slot[{}]'.format(n))

for n in range(num_courses):
    room[n] = model.NewIntVarFromDomain(cp_model.Domain.FromValues(classroom_lst[n]), 'room[{}]'.format(n))

# Boolean variables
same_day = {}
for i in range(num_courses):
    for j in range(num_courses):
        if i!= j:
            same_day[i,j] = model.NewBoolVar('same_day[{},{}]'.format(i,j))

are_intertwined = {}
for i in range(num_courses ):
    for j in range(num_courses):
        if i!= j:
            are_intertwined[i,j] = model.NewBoolVar('are_intertwined[{},{}]'.format(i,j))

# Add constraints

# if the courses took_place in the same day, the boolean variables must be equal to 1
for i in range(num_courses):
    for j in range(num_courses):
        if i!= j:
            model.Add(day[i] == day[j]).OnlyEnforceIf(same_day[i,j])
            model.Add(day[i] != day[j]).OnlyEnforceIf(same_day[i,j].Not())

for i in range(num_courses):
    for j in range(num_courses):
        if i!= j:
            model.AddLinearExpressionInDomain(slot[j] - slot[i], cp_model.Domain(0, int(credit[i] - 1))).OnlyEnforceIf(are_intertwined[i,j])
            model.AddLinearExpressionInDomain(slot[j] - slot[i], cp_model.Domain.FromIntervals([[-11,-1],[int(credit[i]), 11]])).OnlyEnforceIf(are_intertwined[i,j].Not())

# conflict classes cannot be taught at a same periods if they take place in the same day
for lst in teacher_lst:
    if lst: #if lst is not empty
        for i in lst:
            for j in lst:
                if(i != j):
                    model.Add(are_intertwined[i,j] == 0).OnlyEnforceIf(same_day[i,j])

# if the courses' periods are intertwined, they must be taught in different room
for i in range(num_courses):
    for j in range(num_courses):
        if i!= j:
            tmp = []
            tmp.append(are_intertwined[i,j])
            tmp.append(same_day[i,j])
            model.Add(room[i] != room[j]).OnlyEnforceIf(tmp)

# Create the solver
solver = cp_model.CpSolver()
start = time.time()
status = solver.Solve(model)
end = time.time()
print("Constraint Programming model:")
print("Status: {}".format(status))
print("Time: {}".format(end - start))
if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
    """    
    for n in range(num_courses):
        print("Course {} starts on day {}, at slot {} in room {}".format(n, solver.Value(day[n]), solver.Value(slot[n]), solver.Value(room[n])))
    
    for i in range(num_courses):
        for j in range(num_courses):
            if i == j: print('0', end="")
            else: print(solver.Value(same_day[i,j]),end="")
        print()

    for i in range(num_courses):
        for j in range(num_courses):
            if i == j: print('0', end="")
            else: print(solver.Value(are_intertwined[i,j]),end="")
        print()
    """ 

    Solutions = []
    for i in range(5):
        temp = -np.ones((num_classrooms, 12))
        Solutions.append(temp)

    for c in range(num_courses):
        for t in range(credit[c]):
            Solutions[solver.Value(day[c])][solver.Value(room[c]), solver.Value(slot[c]) + t] = c

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

print(model.Validate())