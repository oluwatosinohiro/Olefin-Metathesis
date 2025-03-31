from ase import Atoms, Atom
from ase.calculators.vasp import Vasp
from ase.neb import NEB
from ase.io import write, read
from ase.visualize import view
import os
###############################################################################
# This function will shift the coordinates of your initial and final structures.
# This function can be used to fix the issue when your reactants are devided
# by the periodic boundary conditions.
###############################################################################
def adjust_positions(atoms, x_offset, y_offset):
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
###############################################################################
###############################################################################

initial = read("../../1_WO2/CONTCAR")  # Reads in your initial
slab = read("CONTCAR_1e") 
center = initial.get_center_of_mass()

# x_shift = 0 
# y_shift = 0
# initial = adjust_positions(initial, x_shift, y_shift)  # Shifts the coordiantes
# final = adjust_positions(final, x_shift, y_shift)


adjust = initial.positions[202] - slab.positions[213]

for atom in slab:
	atom.position += adjust
view(slab)
 
write("CONTCAR_1e_mod", slab, format="vasp")

