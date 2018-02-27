#!/usr/bin/python
from __future__ import division, print_function

import os, sys, math
from argparse import ArgumentParser

import parmed as pmd
from parmed import unit as u
import numpy as np

import simtk.openmm as mm
import simtk.openmm.app as app
from simtk.openmm.app.internal.unitcell import computeLengthsAndAngles
from collections import defaultdict, OrderedDict
import itertools

from re import sub
import copy

def EnergyDecomposition(Sim, verbose=False):
    # Before using EnergyDecomposition, make sure each Force is set to a different group.
    EnergyTerms = OrderedDict()
    Potential = Sim.context.getState(getEnergy=True).getPotentialEnergy() / u.kilojoules_per_mole
    Kinetic = Sim.context.getState(getEnergy=True).getKineticEnergy() / u.kilojoules_per_mole
    for i in range(Sim.system.getNumForces()):
        EnergyTerms[Sim.system.getForce(i).__class__.__name__] = Sim.context.getState(getEnergy=True,groups=2**i).getPotentialEnergy() / u.kilojoules_per_mole
    EnergyTerms['Potential'] = Potential
    EnergyTerms['Kinetic'] = Kinetic
    EnergyTerms['Total'] = Potential+Kinetic
    return EnergyTerms

def printcool_dictionary(Dict,title="General options",bold=False,color=2,keywidth=25,topwidth=50):
    if Dict == None: return
    bar = printcool(title,bold=bold,color=color,minwidth=topwidth)
    def magic_string(str):
        return eval("\'%%-%is\' %% '%s'" % (keywidth,str.replace("'","\\'").replace('"','\\"')))
    if isinstance(Dict, OrderedDict):
        print('\n'.join(["%s %s " % (magic_string(str(key)),str(Dict[key])) for key in Dict if Dict[key] != None]) )
    else:
        print('\n'.join(["%s %s " % (magic_string(str(key)),str(Dict[key])) for key in sorted([i for i in Dict]) if Dict[key] != None]) )
    print(bar)

def printcool(text,sym="#",bold=False,color=2,ansi=None,bottom='-',minwidth=50):
    def newlen(l):
        return len(sub("\x1b\[[0-9;]*m","",line))
    text = text.split('\n')
    width = max(minwidth,max([newlen(line) for line in text]))
    bar = ''.join([sym for i in range(width + 8)])
    print('\n'+bar)
    for line in text:
        padleft = ' ' * int((width - newlen(line)) / 2)
        padright = ' '* int(width - newlen(line) - len(padleft))
        if ansi != None:
            ansi = str(ansi)
            print("%s| \x1b[%sm%s" % (sym, ansi, padleft),line,"%s\x1b[0m |%s" % (padright, sym))
        elif color != None:
            print("%s| \x1b[%s9%im%s" % (sym, bold and "1;" or "", color, padleft),line,"%s\x1b[0m |%s" % (padright, sym) )
        else:
            warn_press_key("Inappropriate use of printcool")
    print(bar)
    return sub(sym,bottom,bar)

parser = ArgumentParser()
group = parser.add_argument_group('Input/Output file options')
group.add_argument('-p', '--pdb', dest='pdb', metavar='<PDB FILE>', help='PDB file with target system')
group.add_argument('-f', '--forcefield', dest='ff', metavar='<ForceField FILE>', nargs='+', default=['amoeba2013'], help='''Target force field to use. Should be one of the XML force field files bundled with OpenMM. Default is %(default)s''')
group.add_argument('-i', '--inpcrd', dest='crd', metavar='<CRD FILE>', help='Amber inpcrd file with target system \x1b[1;91m(Required)\x1b[0m')
group.add_argument('-t', '--topology', dest='top', metavar='<TOP FILE>', help='Amber prmtop file with target system \x1b[1;91m(Required)\x1b[0m')
group.add_argument('-s', '--system-xml', dest='system', metavar='FILE', default='system.xml', help='''Name of the \x1b[1;91moutput\x1b[0m OpenMM System XML file that will be written by this script. Default is %(default)s''')
group.add_argument('--cuda', dest='cuda', default='0', metavar='INT', help='''Index of CUDA device: 0, 1, 2...''')

group = parser.add_argument_group('Positional Restraint / Repulsion for Probe Options')
group.add_argument('--reference', dest='reference', metavar='PDB FILE', help='restraint reference PDB structure (default None)', default=None)
group.add_argument('--restrain-mask', dest='restraints', metavar='MASK', help='restraint mask (default None)', default=None)
group.add_argument('-k','--restrain-k', dest='force_constant', type=float, metavar='FLOAT', help='''Force constant for cartesian constraints. Default 10 kcal/mol/A^2''', default=10)
group.add_argument('--dummy-mask', dest='dummy_mask', metavar='<txt FILE>', help='File contains masks to define dummy atoms', default=None)
group.add_argument('--ep-mask',dest='ep_mask', metavar='<txt FILE>', help='File contains the masks to define extra particles. eg., for halogen Br, Cl, I')

group = parser.add_argument_group('Potential energy function parameters')
group.add_argument('-l', '--longrange', dest='longrange', default='PME', choices=['Ewald', 'PME','NoCutoff'], help='''Method to treat long range electrostatic interactions''')
group.add_argument('-c', '--cutoff', metavar='FLOAT', default=10, type=float,help='''Cutoff in Angstroms to use for nonbondedinteractions. Default is \x1b[1;91m%(default)s Angstroms\x1b[0m (tailored toward AMOEBA simulations). Where vdW and electrostatic cutoffs can differ (only AMOEBA), this is *only* the electrostatic cutoff. -v/--vdw-cutoff for the van der Waals cutoff option.''', dest='cut')
group.add_argument('-e', '--ewaldTolerance', metavar='FLOAT', default=5e-4, dest='ewaldTolerance',help='''The error tolerance to use if nonbondedMethod is Ewald or PME. Default is \x1b[1;91m%(default)g\x1b[0m.''', type=float)

group = parser.add_argument_group('Amoeba Force Field Additional Input')
group.add_argument('-v', '--vdw-cutoff', metavar='FLOAT', type=float, help='''Cutoff in Angstroms to use for van derWaals interactions. This is only applicable to AMOEBA forcefields and will be ignored otherwise. Default is \x1b[1;91m%(default)s Angstroms\x1b[0m''', dest='vdwcut')
group.add_argument('--epsilon', metavar='FLOAT', dest='eps',help='''Convergence criteria for mutually induced polarizabledipoles in the AMOEBA force field. Default is \x1b[1;91m%(default)g\x1b[0m.This option is ignored for fixed-charge FFs''', type=float)

group = parser.add_argument_group('Integration-related options')
group.add_argument('--shake', dest='shake', action='store_true', default=False, help='''Constrain bonds containing hydrogen (using SETTLE on waters). Default is NOT to apply SHAKE''')

opt = parser.parse_args()

##########################################################
if opt.longrange == 'PME':
    longrange_method = app.PME
elif opt.longrange == 'Ewald':
    longrange_method = app.Ewald
elif opt.longrange == 'NoCutoff':
    longrange_method = app.NoCutoff

if opt.shake:
    print('Constraining bonds with hydrogens')
    constraints = app.HBonds
else:
    print('No constraints applied')
    constraints = None
amoeba = False

if opt.crd and opt.top:
    # Parse the amber files
    print('Parsing the Amber files [%s] [%s]...' % (opt.crd, opt.top) )
    prmtop = app.AmberPrmtopFile(opt.top)
    inpcrd = app.AmberInpcrdFile(opt.crd)

    print('Creating the System...')
    system = prmtop.createSystem(nonbondedMethod=longrange_method, nonbondedCutoff=opt.cut*u.angstroms, 
                                rigidWater=opt.shake, constraints=constraints, ewaldErrorTolerance=opt.ewaldTolerance)
    pos = inpcrd.positions
    top = prmtop.topology
    parm = pmd.amber.AmberParm(opt.top, opt.crd) 
    useAmberFile = True

elif opt.pdb and opt.ff:
    print('Parsing the PDB file [%s]...' % opt.pdb)
    #pdb = pmd.load_file(opt.pdb)
    pdb = app.PDBFile(opt.pdb, extraParticleIdentifier='EP')

    ff = opt.ff[0][:-4] if opt.ff[0].endswith('.xml') else opt.ff[0]
    print('Loading the force field [%s.xml]...' % ff)
    if ff.find("amoeba")> -1:
        amoeba = True
        ff = app.ForceField(ff + '.xml')
    else:
        ffwat = opt.ff[1][:-4] if opt.ff[1].endswith('.xml') else opt.ff[1]
        ff = app.ForceField(ff + '.xml', ffwat + '.xml')

    print('Creating the System...')
    if opt.eps: # use polarization method mutual
        system = ff.createSystem(pdb.topology, nonbondedMethod=longrange_method, nonbondedCutoff=opt.cut*u.angstroms, 
                 rigidWater=opt.shake, constraints=constraints, ewaldErrorTolerance=opt.ewaldTolerance, 
                 polarization='mutual', mutualInducedTargetEpsilon=opt.eps )
    else:
        system = ff.createSystem(pdb.topology, nonbondedMethod=longrange_method, nonbondedCutoff=opt.cut*u.angstroms,
                 rigidWater=opt.shake, constraints=constraints, ewaldErrorTolerance=opt.ewaldTolerance, 
                 polarization='extrapolated')
    pos = pdb.positions
    top = pdb.topology
    parm = pmd.load_file(opt.pdb)
    useAmberFile = False

# Now scan through our forces and change the cutoff for the van der Waals force
# to 9 angstroms, and change our dipole convergence to 1e-6
if amoeba and opt.vdwcut:
    for force in system.getForces():
        if isinstance(force, mm.AmoebaVdwForce):
            print('Adjusting the vdW cutoff to %g Angstroms...' % opt.vdwcut)
            force.setCutoff(opt.vdwcut*u.angstroms)

########################################################################
# This will be serialized in system.xml

# add Left-side Flat Bottom CustomNonbondedForce for Protein-Ligand Restraint            
const = 2.5 * u.kilocalories_per_mole/u.angstroms**2  # Need to test K and min_distance
const = const.value_in_unit_system(u.md_unit_system)
max_dis = 2.0 * u.angstroms
max_dis = max_dis.value_in_unit_system(u.md_unit_system)

flat_bottom_force = mm.CustomNonbondedForce('step(r-r0) * k * (r-r0)^2')
flat_bottom_force.addGlobalParameter('k', const)
flat_bottom_force.addGlobalParameter('r0', max_dis)

flat_bottom_force.setNonbondedMethod(2) # { NoCutoff = 0, CutoffNonPeriodic = 1, CutoffPeriodic = 2 }

for i in range(system.getNumParticles()):
    flat_bottom_force.addParticle()

ZN_index = list( pmd.amber.AmberMask(parm, '@ZN').Selected() )
print(ZN_index)

atom_index = list( pmd.amber.AmberMask(parm, ':142,146,166,318@NE2,OE2,O14').Selected() )
print(atom_index)

flat_bottom_force.addInteractionGroup(ZN_index, atom_index)
system.addForce(flat_bottom_force)


nfrc = system.getNumForces()
for i in range(nfrc):
    system.getForce(i).setForceGroup(i)
    print('Force # %i -- %s' % (i, system.getForce(i).__class__.__name__) )

# Now we are done creating our system. Let's serialize it by writing an XML file
print('Serializing the System...')
with open(opt.system, 'w') as f:
    f.write(mm.XmlSerializer.serialize(system))

########################################################################
# Add cartesian restraints if desired
if opt.restraints:
    print('Adding restraints (k=%s kcal/mol/A^2) from %s' % (opt.force_constant, opt.restraints))
    sel = pmd.amber.AmberMask(parm, opt.restraints).Selection()
    const = opt.force_constant * u.kilocalories_per_mole/u.angstroms**2
    const = const.value_in_unit_system(u.md_unit_system)
    force = mm.CustomExternalForce('k*periodicdistance(x, y, z, x0, y0, z0)^2')
    force.addGlobalParameter('k', const)
    force.addPerParticleParameter('x0')
    force.addPerParticleParameter('y0')
    force.addPerParticleParameter('z0')
    for i, atom_crd in enumerate(parm.positions):
        if sel[i]:
            force.addParticle(i, atom_crd.value_in_unit(u.nanometers))
    system.addForce(force)


########################################################################
# setting the platform 
platform = mm.Platform_getPlatformByName("CUDA")
platformProperties = {}
platformProperties['CudaPrecision'] = 'single'
platformProperties['CudaDeviceIndex'] = opt.cuda

# create the simulation 
print('Creating the Simulation...')
sim = app.Simulation(top, system, mm.VerletIntegrator(0.001), platform, platformProperties)

########################################################################
# Start the minimization
print('Energy minimization ...')
sim.context.setPositions(pos)
sim.context.applyConstraints(1e-5)

e=sim.context.getState(getEnergy=True).getPotentialEnergy()
print(' Initial energy = %10.4f kcal/mol' % e.value_in_unit(u.kilocalories_per_mole))
eda = EnergyDecomposition(sim)
eda_kcal = OrderedDict([(i, "%10.4f" % (j/4.184)) for i, j in eda.items()])
printcool_dictionary(eda_kcal, title="Energy Decomposition (kcal/mol)")

sim.minimizeEnergy()
e=sim.context.getState(getEnergy=True).getPotentialEnergy()
print('   Final energy = %10.4f kcal/mol' % e.value_in_unit(u.kilocalories_per_mole))
eda = EnergyDecomposition(sim)
eda_kcal = OrderedDict([(i, "%10.4f" % (j/4.184)) for i, j in eda.items()])
printcool_dictionary(eda_kcal, title="Energy Decomposition (kcal/mol)")

########################################################################
# Save the final coordinates into pdb, and write restart file in XML format

# Now write a serialized state that has coordinates
print('Finished. Writing serialized XML restart file...')
final_state = sim.context.getState(getPositions=True, getVelocities=True, getForces=True, enforcePeriodicBox=system.usesPeriodicBoundaryConditions(), getEnergy=True)
positions = final_state.getPositions()
pbc_box = final_state.getPeriodicBoxVectors()
a, b, c, alpha, beta, gamma = computeLengthsAndAngles(pbc_box)
RAD_TO_DEG = 180/math.pi

outpdb = 'sys_min.pdb'
outxml = 'sys_min.xml'

with open(outxml, 'w') as f:
    f.write( mm.XmlSerializer.serialize(final_state) )

app.PDBFile.writeModel(top, positions, open(outpdb, 'w'))
Fo = open(outpdb, 'a')
Fo.write("CRYST1%9.3f%9.3f%9.3f%7.2f%7.2f%7.2f P 1           1 \n" % (a*10, b*10, c*10, alpha*RAD_TO_DEG, beta*RAD_TO_DEG, gamma*RAD_TO_DEG) )
Fo.write("END\n\n")

# Finish progress report
print('Done.')

