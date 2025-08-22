import numpy as np
import matplotlib.pyplot as plt

t = np.arange(0.0, 2.0, 0.01)
t2 = t**2
t3 = t**3
t4 = t**4

fig, axs = plt.subplots(2, 2, figsize=(10, 8))
x = np.arange(len(t))
axs[0, 0].scatter(x, t, color='red', marker='o')
axs[0,1].scatter(x, t2, color='blue', marker='s')
axs[1, 0].scatter(x, t3, color='green', marker='^')
axs[1, 1].scatter(x, t4, color='red', linestyle='--')
plt.suptitle("examSubplots.png")
plt.show()
plt.savefig("examSubplots.png")