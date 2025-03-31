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


initial = read("CONTCAR_8h_hr")
final = read("CONTCAR_1a")  # Reads in your initial and final geometrie
center = initial.get_center_of_mass()

x_shift = 0 
y_shift = 1
initial = adjust_positions(initial, x_shift, y_shift)  # Shifts the coordiantes
final = adjust_positions(final, x_shift, y_shift)


# initial.positions[[210, 209]] = initial.positions[[209, 210]]
# initial.positions[[0, 1]] = initial.positions[[1, 0]]
# initial.positions[[2, 3]] = initial.positions[[3, 2]]
# initial.positions[[49, 48]] = initial.positions[[48, 49]]
# initial.positions[[50, 51]] = initial.positions[[51, 50]]
# initial.positions[[52, 51]] = initial.positions[[51, 52]]
# initial.positions[[54, 53]] = initial.positions[[53, 54]]
# initial.positions[[55, 53]] = initial.positions[[53, 55]]

num_images = 8  # Number of images you want to use
images = [initial]
images += [initial.copy() for i in range(num_images)]
images += [final]
neb = NEB(images, climb=True)
neb.interpolate()
view(images)

calc = Vasp(
    algo="Fast",
    xc="PBE",
    gga="RP",
    ncore=4,
    encut=500,
    ediffg=-1.00e-01,
    isif=0,
    icharg=2,
    ismear=0,
    ivdw=11,
    lasph=True,
    ldipol=True,  # switches on corrections to the potential and forces in VASP. Can be applied for charged molecules and molecules and slabs with a net dipole moment.
    idipol=3,  # dipole corrections in the direction of the third lattice vector are enabled.
    dipol=center,  # specifies the center of the cell in direct lattice coordinates with respect to which the total dipole-moment in the cell is calculated.
    lreal="Auto",
    nsw=200,
    prec="Normal",
    
    gamma=True,
    # kpts=[3, 3, 1],
    lwave=False,
    lcharg=False,
    sigma=0.2,
    ibrion=3,
    potim=0,
    lclimb=False,
    ichain=0,
    images=num_images,
    spring=-5.0,
)

# Creates a directory for each image and writes the proper POSCAR.
neb.images[0].set_calculator(calc)
calc.initialize(neb.images[0])
calc.write_incar(neb.images[0])
calc.write_potcar()
calc.write_kpoints()
for i in range(len(images)):
    os.system("mkdir %02i" % i)
    write("%02i/POSCAR" % i, neb.images[i], format="vasp")