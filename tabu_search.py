import numpy as np
from random import randint
import time



"""
    THE TABU SEARCH SOLUTION TO THE UNIVERSITY TIMETABLING PROBLEM:

created by: Nguyen Duc Quyen 
student id: 20183617
date: Wednesday, December 22th, 2021
"""


# Read data 
f = open("data/test16.txt", "r")

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

# Create the list of conflict courses
conflict_lst = []
for i in range(num_courses):
    conflict_lst.append([])

for i in range(num_courses):
    for j in range(num_courses):
        if i == j:
            continue
        if teacher[i] == teacher[j]:
            conflict_lst[i].append(j)

print(conflict_lst)


print("Number of courses: ", num_courses)
print("Credit:", credit)
print("Teacher:", teacher)
print("Student:", student)
print("Number of classrooms: ", num_classrooms)
print("Capacity:", capacity)
print("Conflicts: \n", conflict_lst)

"""
    Tabu design
        Solution: x(num_courses, 3)
        x[0]: The day the course takes place
        x[1]: The time slot the course begins
        x[2]: The room in which the course is taught

    A Solution is a neighbor of solution x if it has one and only one variable different from that of x

    Tabu length

    Tabu minimum and maximun length 
"""

# Solution
x = -np.ones((num_courses, 3))
objective = 0
num_conflicts = 0

# Last Improved Solution
last_improved_x = -np.ones((num_courses, 3))
last_improved_objective = 100000
last_improved_num_conf = 100000

# Best Solution so far
best_x = -np.ones((num_courses, 3))
best_objective = 100000
best_num_conf = 100000
# Weights
wo = 1000 # Over conflicts
wt = 1000 # Time conflicts
wr = 1000 # Room conflicts
wc = 1000 # Capacity conflicts

# Tabu design
tabu = [0]*num_courses
tabu_length = 3

tabu_length_min = 2
tabu_length_max = 4

# Variable that checks the efficientcy of the current search strategy
stable = 0
stable_limit = 30

# Restart frequency
restart_freq = 100

# Number of iterations
max_iter = 1000

"""
    Generate random solution
    Used at the begining of the search
"""
def gen_rand_solution():
    #Global variables
    global x
    for course in range(num_courses):
        rand_day = randint(0, 4)
        rand_slot = randint(0,11)
        rand_room = randint(0, num_classrooms-1)

        x[course][0] = rand_day 
        x[course][1] = rand_slot
        x[course][2] = rand_room

def calculate_conflicts():
    over_conflicts = 0
    time_conflicts = 0
    room_conflicts = 0
    capacity_conflicts = 0
    
    # Calculate capacity conflicts
    for i in range(num_courses):
        if(student[i] > capacity[int(x[i][2])]):
            capacity_conflicts += 1
        if(x[i][1] + credit[i] - 1 > 11):
            over_conflicts += 1

    # Calculate room and time conflicts
    for i in range(num_courses):
        for j in range(num_courses):
            # If the courses are the same -> pass
            if(i == j):
                continue

            # If the courses are taught on different days -> pass
            if(x[i][0] != x[j][0]):
                continue

            # If another course begins in the middle of this course -> add collide
            if(x[j][1] >= x[i][1] and x[j][1] <= x[i][1] + credit[i] - 1):
                if(j in conflict_lst[i]):
                    time_conflicts += 1
                if(x[i][2] == x[j][2]):
                    room_conflicts += 1
                continue

            # If another course ends in the middle of this course -> add collide
            if(x[j][1] + credit[j] - 1 >= x[i][1] and x[j][1] + credit[j] - 1 <= x[i][1] + credit[i] - 1):
                if(j in conflict_lst[i]):
                    time_conflicts += 1
                if(x[i][2] == x[j][2]):
                    room_conflicts += 1
    
    return over_conflicts, time_conflicts, room_conflicts, capacity_conflicts

# Calculate objective value
def calculate_objective():
    over_conf, time_conf, room_conf, cap_conf = calculate_conflicts()
    num_conflicts = over_conf + time_conf + room_conf + cap_conf
    objective_term = 0
    for c in range(num_courses):
        objective_term += x[c][1]
    return wo*over_conf + wt*time_conf + wr*room_conf + wc*cap_conf + objective_term, num_conflicts

# Search solution
def search_neighbors():
    selected_course = -1
    selected_day = -1
    selected_slot = -1
    selected_room = -1
    new_objective = 100000
    num_conflicts = 100000

    for c in range(num_courses):
        # If the course is in the tabu list
        if tabu[c] > 0:
            continue

        current_day = x[c][0]
        current_slot = x[c][1]
        current_room = x[c][2]

        for i in range(5):
            for j in range(12):
                for m in range(num_classrooms):
                    if(i == current_day and j == current_slot and m == current_room):
                        continue
                    
                    x[c][0] = i
                    x[c][1] = j
                    x[c][2] = m

                    obj_value, conflicts = calculate_objective()
                    if obj_value < new_objective:
                        new_objective = obj_value
                        selected_course = c
                        selected_day = i
                        selected_slot = j
                        selected_room = m
                        num_conflicts = conflicts
                    
                    # return the value
                    x[c][0] = current_day
                    x[c][1] = current_slot
                    x[c][2] = current_room

    return selected_course, selected_day, selected_slot, selected_room, new_objective, num_conflicts


iter = 1
max_iter = 100

start = time.time()
gen_rand_solution()
objective, num_conflicts = calculate_objective()

"""
    The main loop
"""
while(iter < max_iter):
    iter += 1

    # If a feasible schedule is found
    if best_num_conf == 0:
        print("A FEASIBLE SCHEDULE HAS BEEN FOUND AT ITERATION: {}!".format(iter))
        break

    # Update the best objective
    if objective < best_objective:
        best_objective = objective
        for c in range(num_courses):
            best_x[c][0] = x[c][0]
            best_x[c][1] = x[c][1]
            best_x[c][2] = x[c][2]
        best_num_conf = num_conflicts
        # Reset the stable counter
        stable = 0

    # Return to the last improved solution if the current search does not show any improvement
    elif stable == stable_limit:
        print("Returning to the last improved solution...")
        objective = last_improved_objective
        for c in range(num_courses):
            x[c][0] = last_improved_x[c][0]
            x[c][1] = last_improved_x[c][1]
            x[c][2] = last_improved_x[c][2]
        # Reset the stable counter
        stable = 0

    # Otherwise increase the stable counter
    else: 
        stable += 1

    old_objective = objective

    course, day, slot, room, new_objective, new_num_conf = search_neighbors()
    print("Course: {}, Day: {}, Slot: {}, Room: {}, Conflicts: {}".format(course, day, slot, room, new_num_conf))

    # Move towards the best neighbor
    x[course][0] = day
    x[course][1] = slot 
    x[course][2] = room
    objective = new_objective
    num_conflicts = new_num_conf
    # Update the tabu list
    for c in range(num_courses):
        if(tabu[c] > 0):
            tabu[c] -= 1 

        tabu[course] = tabu_length

    # If the search shows improvement, encourage it
    if new_objective < old_objective:
        if tabu_length > tabu_length_min:
            tabu_length = tabu_length_min

    if new_objective > old_objective:
        if tabu_length < tabu_length_max:
            tabu_length = tabu_length_max

    # Update last improved solution
    if new_objective < old_objective:
        print("The solution has been improved...")
        last_improved_objective = new_objective
        for c in range(num_courses):
            last_improved_x[c][0] = x[c][0]
            last_improved_x[c][1] = x[c][1]
            last_improved_x[c][2] = x[c][2]
        last_improved_num_conf = num_conflicts
    # Restart the algorithm after a couple of iterations
    if(iter % restart_freq == 0):
        print("Restarting...")
        gen_rand_solution()

        for c in range(num_courses):
            tabu[c] = 0

end = time.time()
"""
    Display the final solution
"""
print("BEST SOLUTION FOUND")
Solutions = []
for i in range(5):
    temp = -np.ones((num_classrooms, 12))
    Solutions.append(temp)

for c in range(num_courses):
    for t in range(credit[c]):
        if(int(best_x[c][1]) + t <= 11):
            Solutions[int(best_x[c][0])][int(best_x[c][2]), int(best_x[c][1]) + t] = c

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

for c in range(num_courses):
    x[c][0] = best_x[c][0]
    x[c][1] = best_x[c][1]
    x[c][2] = best_x[c][2]

over_conf, time_conf, room_conf, cap_conf = calculate_conflicts()
objective = calculate_objective()

print("Number of over time courses: ", over_conf)
print("Number of time conflicts: ", time_conf)
print("Number of classroom conflicts: ", room_conf)
print("Number of capacity conflicts: ", cap_conf)
print("Best objective value recorded: ", objective)
print("Time consumed: ", end-start)