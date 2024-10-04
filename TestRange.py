import random

from Range import Range

test_range = Range(60, 2)
print(test_range.capacity)
for i in range(40):
    test_range.add(random.randint(1000, 2000), random.randint(0, 1000))

print(test_range.max)
print(test_range.min)

print(test_range.highs)
print(test_range.lows)