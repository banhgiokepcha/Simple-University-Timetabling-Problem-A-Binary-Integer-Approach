import numpy as np
from ortools.linear_solver import pywraplp
import time

"""
    THE IP MODEL TO SOLVE THE UNIVERSITY TIMETABLING PROBLEM:

"""

# Read data 
f = open("Simple-University-Timetabling-Problem-main/data/test1.txt", "r") 


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

# create the list of the courses assigned to each teacher
for n in range(num_courses):
    teacher_lst[teacher[n]].append(n)

print("Number of courses: ", num_courses)
print("Credit:", credit)
print("Teacher:", teacher)
print("Student:", student)
print("Number of classrooms: ", num_classrooms)
print("Capacity:", capacity)
print("Conflicts: \n", teacher_lst)

# Create solver
solver = pywraplp.Solver.CreateSolver('SCIP')

# Add variables
x = {}
for i in range(5):
    for j in range(12):
        for m in range(num_classrooms):
            for n in range(num_courses):
                x[i, j, m, n] = solver.IntVar(0, 1, 'x[{},{},{},{}]'.format(i, j, m, n))

# Add constraints
#   At most 1 course can take place in 1 classroom in each time slot and vice versa
for i in range(5):
    for j in range(12):
        for m in range(num_classrooms):
            ct = solver.Constraint(0, 1)
            for n in range (num_courses):
                ct.SetCoefficient(x[i,j,m,n], 1)
            

for i in range(5):
    for j in range(12):
        for n in range(num_courses):
            ct = solver.Constraint(0, 1)
            for m in range(num_classrooms):
                ct.SetCoefficient(x[i,j,m,n], 1)

#   The number of student in each class must be smaller than the capacity of the classroom
for i in range(5):
    for j in range(12):
        for m in range(num_classrooms):
            solver.Add(sum(x[i,j,m,n]*(capacity[m]-student[n]) for n in range(num_courses)) >= 0)

#   The number of timeslots assigned for each course must be equal to the course's credit
for n in range(num_courses):
    ct = solver.Constraint(float(credit[n]), float(credit[n]))
    for i in range(5):
        for j in range(12):
            for m in range(num_classrooms):
                ct.SetCoefficient(x[i,j,m,n], 1)

#   A teacher can only attend at most 1 class at each time slot
for lst in teacher_lst:
    if lst: # if the list is not empty, add the constraints
        for i in range(5):
            for j in range(12):
                ct = solver.Constraint(0, 1)
                for m in range(num_classrooms):
                    for n in lst:
                        ct.SetCoefficient(x[i,j,m,n], 1)

#   Consecutiveness of each course
#       If the course starts at the begining of the day;
for i in range(5):
    for m in range(num_classrooms):
        for n in range(num_courses):
            for t in range(1, credit[n]):
                ct = solver.Constraint(-solver.infinity(), 0)
                ct.SetCoefficient(x[i,0,m,n], 1)
                ct.SetCoefficient(x[i,t,m,n], -1)
#       If the course ends at the end of the day 
for i in range(5):
    for m in range(num_classrooms):
        for n in range(num_courses):
            for t in range(1, credit[n]):
                ct = solver.Constraint(-solver.infinity(), 0)
                ct.SetCoefficient(x[i,11,m,n], 1)
                ct.SetCoefficient(x[i,11-t,m,n], -1)
#       If the course starts and ends during the day
for i in range(5):
    for m in range(num_classrooms):
        for n in range(num_courses):
            for p in range(0, 10):
                for t in range(1, credit[n]):
                    if(p + t + 1 <= 11):
                        ct = solver.Constraint(-solver.infinity(), 0)
                        ct.SetCoefficient(x[i,p,m,n], -1)
                        ct.SetCoefficient(x[i,p+1,m,n], 1)
                        ct.SetCoefficient(x[i,p+t+1,m,n], -1)


#   Consistency of classroom
#   A course must be taught in a specific room through out the week
for i in range(5):
    for j in range(12):
        for m in range(num_classrooms):
            for n in range(num_courses):
                solver.Add(x[i,j,m,n]*credit[n] <= sum(x[a,b,m,n] for a in range(5) for b in range (12)))

# Add the objective

# Solve the problem 
start = time.time()
status = solver.Solve()
end = time.time()
print("Integer Programming model:")
print("Status: {}".format(status))
print("Time: {}".format(end - start))


# Display the solution
Solutions = []
for i in range(5):
    temp = -np.ones((num_classrooms, 12))
    Solutions.append(temp)

if status == pywraplp.Solver.OPTIMAL or status == pywraplp.Solver.FEASIBLE:
    for i in range(5):
        for j in range(12):
            for m in range(num_classrooms):
                for n in range(num_courses):
                    if x[i,j,m,n].solution_value() > 0:
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