import re, os, sys
from argparse import ArgumentParser

OUT = "crystal_water.pdb"

parser = ArgumentParser()
group = parser.add_argument_group('Input/Output file options')
group.add_argument('-g', '--dx', dest='gf', help='DX file')
group.add_argument('-c', dest='cw', help='')
opt = parser.parse_args()

if opt.gf:
	filename_gf = opt.gf

if opt.cw:
	filename_cw = opt.cw

f = open(filename_gf, "r")
line=f.readline().split()
gsize=[int(line[-3]),int(line[-2]),int(line[-1])]

#read the origin of the system
line=f.readline().split()
origin=[float(line[-3]),float(line[-2]),float(line[-1])]

#read grid spacing
line=f.readline().split()
deltax=[float(line[-3]),float(line[-2]),float(line[-1])]
line=f.readline().split()
deltay=[float(line[-3]),float(line[-2]),float(line[-1])]
line=f.readline().split()
deltaz=[float(line[-3]),float(line[-2]),float(line[-1])]

constraints = [] # X min, Y min, Z min, X max, Y max, Z max

constraints.extend(origin)
constraints.append(origin[0]+(deltax[0]*gsize[0]))
constraints.append(origin[1]+(deltay[1]*gsize[1]))
constraints.append(origin[2]+(deltaz[2]*gsize[2]))

f.close()

f = open(filename_cw, "r")
f_out = open(OUT, "w")

for line in f:
	if line.split()[0] == "ATOM" or line.split()[0] == "HETATM":
		x,y,z = float(line.split()[6]), float(line.split()[7]), float(line.split()[8])
		if constraints[0] <= x and x <= constraints[3]:
			if constraints[1] <= y and y <= constraints[4]:
				if constraints[2] <= z and z <= constraints[5]:
					f_out.write(line)

f.close()
f_out.close()