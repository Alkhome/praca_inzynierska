import random

sample_list_min = []

for i in range(1000):
    sample_list_min.append(random.randrange(1000))
    print(sample_list_min)
    if len(sample_list_min) == 30:
        sample_list_min.sort(reverse=False) #bierze min -> max
        sample_list_min.sort(reverse=True)  #bierze max -> min
        sample_list_min = sample_list_min[5:10]


