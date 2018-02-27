#! /usr/bin/python

import re, os, sys
import os.path as path
import time
import fnmatch

import numpy as np
from argparse import ArgumentParser


parser = ArgumentParser()
group = parser.add_argument_group('Input/Output file options')
group.add_argument('-d', '--dx', dest='dx', nargs='+', metavar='<DX FILE>', help='DX file')
group.add_argument('-o', dest='output', help='Output Destination')
opt = parser.parse_args()

clusters = ['c0', 'c1', 'c7'] #Change to 0,1,7 for all clusters
out_mean  = "mean-density.dx"
out_sd = "standard-deviation.dx"
out_err = "max-error.dx"
CUTOFF = 0
SD_CUTOFF = 0.04
REPLACEMENT = 10

_dxtemplate="""object 1 class gridpositions counts %i %i %i
origin %.3f %.3f %.3f
delta %.5f   0   0
delta 0   %.5f   0
delta 0   0   %.5f
object 2 class gridconnections counts %i %i %i
object 3 class array type double rank 0 items %i data follows
"""

if opt.output:
    out_dx = opt.output



for cluster in clusters:
    print("Starting cluster %s" % (cluster))
    file_count = 0
    sum_grids = []
    for i in range(0,10):
        dxf = "cluster_%s/subcluster_c%d/WATsite_out/grid_occupancy.dx" % (cluster, i)
        f = open(dxf, 'r')
        print("Starting subcluster %d" % (i))

        #read the header
        #header = f.readline()

        #read the grid size
        r=re.compile('\w+')
        gsize=r.findall(f.readline())
        gsize=[int(gsize[-3]),int(gsize[-2]),int(gsize[-1])]

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

        #Check if occupancy lower than 0.045
        #If yes, set to ten and exclude from std and max error

        #pay attention here, this assumes always orthogonal normalized space, but normally it should be ok
        delta=[deltax[0],deltay[1],deltaz[2]]
        
        #read the number of data
        f.readline()
        r=re.compile('\d+')
        n_entries=int(r.findall(f.readline())[2])

        #check correpondence with expected data points
        if(n_entries!=gsize[0]*gsize[1]*gsize[2]) :
            sys.exit("Error reading the file. The number of expected data points \
            does not correspond to the number of labeled data points in the header.")

        #load data into numpy array
        #reshaping to fit grid format (it keeps Z fast, Y medium, X slow data organization)
        grid = np.fromstring(f.read(), sep=' ', dtype=float).reshape(gsize)

        if grid.size != n_entries:
            sys.exit("Error reading the file. The number of expected data points\
            does not correspond to the number of labeled data points in the header.")
        f.close()
        
        print gsize, origin, delta

        new_grid = np.copy(grid)

        si, sj, sk = grid.shape
        for i in range(si):
            for j in range(sj):
                for k in range(sk):
                    new_val = 0.0
                    grid_val = grid[i][j][k]
                    new_val = grid_val
                    new_grid[i][j][k] = new_val
        sum_grids.append(new_grid)

    """
    Writes data into a DX Formated File
    """
    out_meanf = open(cluster + '_' + out_mean,'w')
    out_sdf = open(cluster + '_' + out_sd,'w')
    out_errf = open(cluster + '_' + out_err,'w')
    out_meanf.write(_dxtemplate%( grid.shape[0],grid.shape[1],grid.shape[2],
                            origin[0],origin[1],origin[2],
                            delta[0],delta[1],delta[2],
                            grid.shape[0],grid.shape[1],grid.shape[2],
                            grid.size))
    out_sdf.write(_dxtemplate%( grid.shape[0],grid.shape[1],grid.shape[2],
                            origin[0],origin[1],origin[2],
                            delta[0],delta[1],delta[2],
                            grid.shape[0],grid.shape[1],grid.shape[2],
                            grid.size))
    out_errf.write(_dxtemplate%( grid.shape[0],grid.shape[1],grid.shape[2],
                            origin[0],origin[1],origin[2],
                            delta[0],delta[1],delta[2],
                            grid.shape[0],grid.shape[1],grid.shape[2],
                            grid.size))

    #Generate bool mask
    bool_mask = np.zeros(np.shape(sum_grids), dtype=bool)
    count_mask = np.zeros(np.shape(new_grid))
    for k in range(0,10):
        for x in range(np.shape(new_grid)[0]):
            for y in range(np.shape(new_grid)[1]):
                for z in range(np.shape(new_grid)[2]):
                    if sum_grids[k][x][y][z] < CUTOFF:
                        bool_mask[k][x][y][z] = False
                    else:
                        bool_mask[k][x][y][z] = True
                        count_mask[x][y][z] = count_mask[x][y][z] + 1

    nonzero_count_mask = np.zeros(np.shape(new_grid), dtype=bool)
    rr, qq, zz = np.nonzero(count_mask)
    nonzero_count_mask[rr,qq,zz] = True

    #Calculate mean density
    density_grid = np.zeros(np.shape(new_grid))
    for k in range(0,10): 
        np.add(density_grid, sum_grids[k], density_grid, where=bool_mask[k])
    np.divide(density_grid, count_mask, density_grid, where=nonzero_count_mask)

    count=0
    for data in density_grid.flat:
        if count==3: out_meanf.write('\n'); count=0
        out_meanf.write('%8.5f\t'%(float(data)))
        count+=1
    out_meanf.write('\n')
    out_meanf.close()
    print('Writing Mean Grid')

    count_mask[count_mask == 1] = 2

    #Calculate standard deviation
    std_dev_grid = np.zeros(np.shape(new_grid))
    intermediate_grid = np.copy(sum_grids)
    intermediate_grid.fill(0)
    for k in range(0,10):
        np.subtract(density_grid, sum_grids[k], intermediate_grid[k], where=bool_mask[k])
        np.multiply(intermediate_grid[k], intermediate_grid[k], intermediate_grid[k], where=bool_mask[k]) # Squares array
        np.add(std_dev_grid, intermediate_grid[k], std_dev_grid, where=bool_mask[k])
    np.divide(std_dev_grid, count_mask-1, std_dev_grid, where=nonzero_count_mask)

    count=0
    for c,data in enumerate(std_dev_grid.flat):
        if density_grid.flat[c] < SD_CUTOFF:
            data = 10
        '''if (data < 0.00001 and data > 0):
            data = 10'''
        if count==3: out_sdf.write('\n'); count=0
        out_sdf.write('%8.5f\t'%(float(data)))
        count+=1
    out_sdf.write('\n')
    out_sdf.close()
    print('Writing Standard Deviation Grid')
    
    #Calculate max error
    err_grid = np.zeros(np.shape(new_grid))
    np.sqrt(intermediate_grid, intermediate_grid)
    for k in range(0,10): 
        np.maximum(err_grid, intermediate_grid[k], err_grid, where=bool_mask[k])

    count=0
    for data in err_grid.flat:
        if count==3: out_errf.write('\n'); count=0
        out_errf.write('%8.5f\t'%(float(data)))
        count+=1
    out_errf.write('\n')
    out_errf.close()
    print('Writing Error Grid')