from ase.io import read, write
from ase.visualize import view
import os
import sys
from ase.calculators.vasp import Vasp
import pandas as pd
import matplotlib
from matplotlib import pyplot as plt
from matplotlib import animation as animation
import numpy as np

path = os.getcwd()

a = []
energy = []


def adjust_position(atoms, x_offset, y_offset):
    cons = atoms.constraints
    atoms.set_constraint()
    pos = atoms.get_positions()
    cell = atoms.get_cell()
    pos[:, 0] += x_offset
    pos[:, 1] += y_offset
    atoms.set_positions(pos)
    atoms.wrap()
    atoms.set_constraint(cons)
    return atoms


# x_offset = 0.1
# y_offset = 0.1
x_offset = 0
y_offset = 0

# Get the sorted list of directories in the path
directories = sorted([entry for entry in os.listdir(path) if os.path.isdir(os.path.join(path, entry))])


for dirs in directories:
    contcar_file_path = os.path.join(path, dirs, 'CONTCAR')
    poscar_file_path = os.path.join(path, dirs, 'POSCAR')

    if os.path.exists(contcar_file_path):
        print(contcar_file_path)
        a += [adjust_position(read(contcar_file_path), x_offset, y_offset)]
    elif os.path.exists(poscar_file_path):
        print(poscar_file_path)
        a += [adjust_position(read(poscar_file_path), x_offset, y_offset)]

view(a)

# Save the energies
for dirs in directories:
    outcar_file_path = os.path.join(path, dirs, 'OUTCAR')

    if os.path.exists(outcar_file_path):
        print(outcar_file_path)
        outcar = read(outcar_file_path)
        energy.append(outcar.get_calculator().get_potential_energy())

energy = pd.DataFrame(energy, index=list([np.arange(1, len(energy) + 1)]), columns=["Potential Energy"])

print(energy)
print("")

energy.to_excel("Energy.xlsx")

energy.plot(kind='line', title='Potential Energy Plot')

# Save the plot to a file
plt.savefig('saddle_point.png', format='png', dpi=300)

plt.show()

write("neb_animation.gif", a)