import numpy as np
import sys

k = int(sys.argv[1])
n = int(sys.argv[2])
L_disk = float(sys.argv[3])
L_machine = float(sys.argv[4])
MTTR_diskData_h = float(sys.argv[5])
MTTR_machineData_h = float(sys.argv[6])

MTTR_diskData = MTTR_diskData_h / 24 /365
MTTR_machineData = MTTR_machineData_h / 24 /365

L = L_disk + L_machine
U = (L_disk + L_machine) / (MTTR_diskData * L_disk + MTTR_machineData * L_machine)
L_S = (np.math.factorial(n) * np.power(L, n-k+1)) / (np.math.factorial(n-k) * np.math.factorial(k-1) * np.power(U, n-k))

print L_S

# python CalcReliability.py 9 18 0.02 0.01 24 72 -> 2.2298e-31
# python CalcReliability.py 1 4 0.02 0.01 16 48 -> 9.1398e-14
