from qiskit import QuantumCircuit, Aer, transpile, QuantumRegister, ClassicalRegister, assemble
from qiskit.circuit import ParameterVector
from qiskit.circuit.library.standard_gates import SXGate, HGate
from math import pi, cos, sin, acos
# import random
from scipy.optimize import minimize


angles = ParameterVector('0', 6)

address=QuantumRegister(2, name="a")
memory=QuantumRegister(4, name="m")
grid=QuantumRegister(4, name="g")
winner=QuantumRegister(1, name="w")
winner_output=ClassicalRegister(1)
grid_measure=ClassicalRegister(4)
qc=QuantumCircuit(address, memory, grid, winner, winner_output, grid_measure)

# X's turn

qc.ry(angles[0], address[1])
qc.cry(angles[1], address[1], address[0])
qc.x(address[1])
qc.cry(angles[2], address[1], address[0])


qc.ccx(address[0], address[1], memory[1])
qc.cx(memory[1], grid[1])
qc.x(address[0])
qc.ccx(address[0], address[1], memory[0])
qc.cx(memory[0], grid[0])
qc.x(address[1])
qc.ccx(address[0], address[1], memory[2])
qc.cx(memory[2], grid[2])
qc.x(address[0])
qc.ccx(address[0], address[1], memory[3])
qc.cx(memory[3], grid[3])

qc.reset(address)

# O's turn

ccsx = SXGate().control(2)

qc.cry(2*acos(0.667**0.5), memory[1], address[1])
qc.x(memory[1])
qc.cry(2*acos(0.333**0.5), memory[1], address[1])
qc.x(memory[1])

qc.append(ccsx, [memory[2], address[1], address[0]])
qc.append(ccsx, [memory[3], address[1], address[0]])
qc.cry(pi/2, address[1], address[0])
qc.append(ccsx, [memory[2], address[1], address[0]])
qc.append(ccsx.inverse(), [memory[3], address[1], address[0]])

qc.x(address[1])

qc.append(ccsx, [memory[0], address[1], address[0]])
qc.append(ccsx, [memory[1], address[1], address[0]])
qc.cry(pi/2, address[1], address[0])
qc.append(ccsx, [memory[0], address[1], address[0]])
qc.append(ccsx.inverse(), [memory[1], address[1], address[0]])


qc.ccx(address[0], address[1], memory[1])
qc.x(address[0])
qc.ccx(address[0], address[1], memory[0])
qc.x(address[1])
qc.ccx(address[0], address[1], memory[2])
qc.x(address[0])
qc.ccx(address[0], address[1], memory[3])


qc.reset(address)


# X's turn


qc.append(ccsx, [memory[0],memory[1],address[1]])
qc.append(ccsx, [memory[2],memory[3],address[1]])
qc.ry(angles[3], address[1])
qc.append(ccsx, [memory[0],memory[1],address[1]])
qc.append(ccsx.inverse(), [memory[2],memory[3],address[1]])

qc.append(ccsx, [memory[2], address[1], address[0]])
qc.append(ccsx, [memory[3], address[1], address[0]])
qc.cry(angles[4], address[1], address[0])
qc.append(ccsx, [memory[2], address[1], address[0]])
qc.append(ccsx.inverse(), [memory[3], address[1], address[0]])

qc.x(address[1])

qc.append(ccsx, [memory[0], address[1], address[0]])
qc.append(ccsx, [memory[1], address[1], address[0]])
qc.cry(angles[5], address[1], address[0])
qc.append(ccsx, [memory[0], address[1], address[0]])
qc.append(ccsx.inverse(), [memory[1], address[1], address[0]])


qc.ccx(address[0], address[1], grid[1])
qc.x(address[0])
qc.ccx(address[0], address[1], grid[0])
qc.x(address[1])
qc.ccx(address[0], address[1], grid[2])
qc.x(address[0])
qc.ccx(address[0], address[1], grid[3])

# Determine winner

qc.ccx(grid[0], grid[1], winner[0])
qc.ccx(grid[0], grid[3], winner[0])


qc.measure(winner[0], winner_output[0])
qc.measure(grid, grid_measure)


simulator = Aer.get_backend('qasm_simulator')
transpiled_qc = transpile(qc, simulator, optimization_level=3)


def X_opt(x_moves, qc):

    print(x_moves)

    b_qc=qc.bind_parameters({angles: list(x_moves)})
    result = simulator.run(b_qc).result()
    counts = result.get_counts(b_qc)
    xwins=0

    for m in counts.keys():
        xwins+=int(m[-1])*counts[m]

    # print(counts)
    print(xwins)

    return -xwins

fin_res = minimize(
X_opt,
x0=[7.8 for _ in range(6)],
args=(transpiled_qc,),
method='Powell',
bounds=[(2*pi,3*pi) for _ in range(6)],
options={'maxfev': 250}
)



# b_qc=transpiled_qc.bind_parameters({angles: [6.40756813, 7.16736623, 6.40916729, 6.3799214,  9.24836642, 7.16510583]})
b_qc=transpiled_qc.bind_parameters({angles: fin_res.x})
result = simulator.run(b_qc).result()
counts = result.get_counts(b_qc)

print(counts)

probabilities = {"center": cos(fin_res.x[0]/2)*cos(fin_res.x[2]/2), "middle right": cos(fin_res.x[0]/2)*sin(fin_res.x[2]/2), "bottom center": sin(fin_res.x[0]/2)*cos(fin_res.x[1]/2), "bottom right": sin(fin_res.x[0]/2)*sin(fin_res.x[1]/2)}
max_key = max(probabilities, key=probabilities.get)
print("Best move for X: ", max_key)
print("Expected outcome: ", (max(counts, key=counts.get))[::-1][2:])
