#!/usr/bin/python
import os, sys, re, getopt
import numpy as np
from argparse import ArgumentParser
import matplotlib.pyplot as plt

parser = ArgumentParser(description='This will shift the geometry center of the system to the center of box.')
parser.add_argument('--omm', dest='ommHS', metavar='<waterindex.wtndx FILE>', help='Input waterindex.wtndx file to center the system to box center')
parser.add_argument('--gro', dest='groHS', metavar='<Enthalpy.txt FILE>', help='Input Enthalpy.txt file to center the system to box center')

opt = parser.parse_args()

if opt.ommHS:
    with open(opt.ommHS,"r") as Fi:
        line = Fi.readline()
        line = Fi.readline()
        line = Fi.readline()
        numWAT    = int( line.split()[0] )
        numHS     = int( line.split()[1] )
        numFrame  = int( line.split()[2] )

        info = np.zeros((numHS, numFrame))

        line = Fi.readline()
        while line and len( line.split() ) > 2:
            wat_num   = int( line.split()[1] )
            frame_num = int( line.split()[3] )
            for i in range(frame_num):
                line = Fi.readline()
                cluster = int( line.split()[0] )
                frame   = int( line.split()[1] )
                info[cluster][frame] = wat_num
            line = Fi.readline()
    print info
    egy = np.empty((numHS, numFrame))
    egy[:] = np.NAN

    for i in range(numFrame):
        with open("../waterEnergy/watEgy_%d" % (i+1), "r") as f:
            #print "watEgy_%d  "% (i+1)
            alllines = f.readlines()
        store = {}
        for k in range( 1, len(alllines) ):
            wat_num = int( alllines[k].split()[0] )
            wat_egy = 0-(float( alllines[k].split()[1]) * 2 + 21.15)
            store[wat_num] = wat_egy 

        for j in range(numHS):
            if info[j][i] in store:
                key = info[j][i]
                egy[j][i] = store[ key ]
                #print "frame(%d) -- wat_num(%d) -- egy(%f)" % (i+1, info[j][i], egy[j][i])
    print egy

elif opt.groHS:
    with open(opt.groHS, "r") as f:
        line = f.readline()
        numHS     = int( line.split()[1] )
        numFrame  = int( line.split()[2] )
        alllines = f.readlines()

    egy = np.empty((numHS, numFrame))
    egy[:] = np.NAN

    for i in range( 1, len(alllines) ):
        cluster = int( alllines[i].split()[0] )
        frame   = int( alllines[i].split()[1] )
        energy  = float( alllines[i].split()[2]*2)
        egy[cluster][frame] = energy
    print egy

print "Done reading water energies..."
os.mkdir("HS_enthalpy")
os.chdir("HS_enthalpy")
for i in range(numHS):
    y = np.zeros(numFrame)
    with open("HS_%d" % (i+1), "w") as f:
        for j in range(numFrame):
            if not np.isnan(egy[i][j]):
                f.write("%d \t %5.5f\n" % (j+1, egy[i][j] ) )

    x = np.arange(1, numFrame+1, 1)
    y = egy[i]
    ave = np.nanmean(y)
    std = np.nanstd(y)
    plt.scatter(x, y, s=5, c=x, marker='+')
    plt.xlabel('Frame')
    plt.ylabel('Enthalpy (kcal/mol)')
    plt.title('Enthalpy Distribution for HS_%d' % (i+1))
    plt.xlim(-25, 10500)
    plt.ylim(-12,14)
    plt.errorbar([10250],[ave],yerr=[std], fmt='o', capthick=2)
    #plt.show()
    plt.savefig("HS_%d.png" % (i+1))
    plt.clf()  # Clear the figure for the next loop
os.chdir("../")
