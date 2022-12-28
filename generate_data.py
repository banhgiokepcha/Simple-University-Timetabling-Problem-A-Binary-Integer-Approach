from random import randint

f = open("data/test18.txt", "w")

num_courses = 50
num_classrooms = 5
num_teachers = 10
min_student = 20
max_student = 200
min_time = 2
max_time = 6

small_room_rate = 0.5

f.write("{} {}\n".format(num_courses, num_classrooms))
for i in range(num_courses):
    f.write("{} {} {}\n".format(randint(min_time, max_time), randint(1, num_teachers), randint(min_student, max_student)))

for i in range(num_classrooms):
    if i < num_classrooms * small_room_rate:
        f.write("60\n")
    else: 
        f.write("200\n")