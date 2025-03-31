from ase import Atoms, Atom
from ase.calculators.vasp import Vasp
from ase.constraints import FixAtoms
#from ase.build import surface, add_adsorbate, molecule
#from ase.lattice.spacegroup import crystal
#from ase.spacegroup import crystal
#from ase.optimize import QuasiNewton
from ase.io import write, read
from ase.visualize import view
from ase.build import bulk

#Read the relaxed contcar file of molecule
molecule = read('../CONTCAR')
center = molecule.get_center_of_mass()

adsorbate_indices = [0, 1, 2, 3, 48, 49, 50, 51, 52, 53, 54, 55, 209, 275]
c = FixAtoms(indices = [atom.index for atom in molecule if atom.index not in adsorbate_indices])

# c = FixAtoms(mask=[True for atom in molecule])
molecule.set_constraint(c)

#Place Phenol in a cell of vacuum
# atoms = molecule # Creates a benzene molecule using the ase.build.molecule function
#atoms.set_cell((10,10,10)) # Setting cell with vacuum
# atoms.center(vacuum =10) # Putting atom in center of cell. Sets the vacuum spacing for your atom.
view(molecule) # View your molecule

# Define your calculator settings. These are modified based on your needs.
# For details, see the VASP manual at https://www.vasp.at/wiki/index.php/The_VASP_Manual
#For thermochemistry calculation of molecules set ibrion=5, nsw=1, potim =0.015, nfree=2
calc = Vasp(
    algo="Fast",
    xc="PBE",
    gga="RP",
    # ncore=4,
    encut=500.0,
    ediffg=-5.00e-02,
    ibrion=5.0,
    isif=0,
    icharg=2,
    ismear=0.0,
    ivdw=11,
    lasph=True,
    lcharg=True,
    ldipol=True,  # switches on corrections to the potential and forces in VASP. Can be applied for charged molecules and molecules and slabs with a net dipole moment.
    idipol=3,  # dipole corrections in the direction of the third lattice vector are enabled.
    dipol=center,  # specifies the center of the cell in direct lattice coordinates with respect to which the total dipole-moment in the cell is calculated.
    lreal="Auto",
    lwave=True,
    nfree=2,
    nsw=1,
    prec="Normal",
    potim=0.015, 
    sigma=0.2,
    kpts=[3, 3, 1],
)

# Initializes the calculator for your atoms and writes the necessary VASP input files
calc.initialize(molecule)
calc.write_incar(molecule) # Writes INCAR
calc.write_potcar() # Writes POTCAR
calc.write_kpoints() # Writes KPOINTS
write('POSCAR', molecule, format='vasp') # Writes POSCAR
