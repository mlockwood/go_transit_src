import numpy as np
import math

N = 1000
a = np.random.rand(N) * 10
mean = np.mean(a)
stdev = np.std(a)
print(mean, stdev)
b = np.random.rand(N) * 15
mean_b = np.mean(b)
print(mean_b)

math.ceil(math.log(mean_b - mean + math.exp(1)) * (mean_b - mean)/stdev)
