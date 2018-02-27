#!/usr/bin/python
import os, sys, getopt, math
import itertools
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
from scipy import stats

###################################################################################################
def main(argv):

    distance_cutoff = 1.5
    bin = 0.1

    crystal_water = "WATout_c0/HydrationSites.pdb"
    hs_list = [100,100,500,1000]

    pair_list = []
    dist_list = []
    for one_hs in hs_list:
        predict_hs = "c0_" + str(one_hs) + "/HydrationSites.pdb"

        percent, distance = read_data(predict_hs, crystal_water, bin, distance_cutoff )
        pair_list.append(percent)
        dist_list.append(distance)
    plot_hist(hs_list, pair_list, dist_list, bin)

def read_data(fst_file, snd_file, bin, distance_cutoff):
    # read first file 
    fst_list = []
    f1 = open(fst_file, 'r')
    for oneline in f1:
        if oneline.find('ATOM') > -1 or oneline.find('HETATM') > -1:
            fst_list.append(oneline)
            #print oneline
    num_fst = len(fst_list)

    # read second file
    snd_list = []
    f2 = open(snd_file, 'r')
    for oneline in f2:
        if oneline.find('ATOM') > -1 or oneline.find('HETATM') > -1:
            #print oneline
            snd_list.append(oneline)
    num_snd = len(snd_list)
    num_crystal = num_snd


    # set up a 2D array
    dis = np.zeros((num_fst, num_snd))
    for i in range(num_fst):
        x1,y1,z1 = float(fst_list[i].split()[6]), float(fst_list[i].split()[7]),float(fst_list[i].split()[8])
        for j in range(num_snd):
            x2,y2,z2 = float(snd_list[j].split()[6]), float(snd_list[j].split()[7]),float(snd_list[j].split()[8])
            #print "1: ", x1, y1, z1, "  2:", x2, y2, z2
            dis[i][j] = ( (x1-x2)**2 + (y1-y2)**2 + (z1-z2)**2 ) ** 0.5
    num = min(num_fst, num_snd)
    print "Most number of pairs: %d\n" % num
    total_num = min(num_fst, num_snd)
    num_of_pair = 0
    pairs = []
    distance = []
    while num > 0:
        x = np.where( dis == np.nanmin(dis) ) 
        # eg: (array([15]), array([17])) fst number is the row, snd number is the column of the value
        #print x
        ind_fst = x[0][0]
        ind_snd = x[1][0]
        num = num - 1
        #print num 

        if dis[ind_fst][ind_snd] <=  distance_cutoff:
            pairs.append(ind_fst)
            pairs.append(ind_snd)
            distance.append(dis[ind_fst][ind_snd])
        print "pair-%d: fst_%d snd_%d     dis: %f" % ( (total_num - num), ind_fst+1, ind_snd+1, dis[ind_fst][ind_snd])
        if dis[ind_fst][ind_snd] <= 1:
            num_of_pair = total_num - num

        dis[ind_fst, 0:num_snd] = np.nan
        dis[0:num_fst,ind_snd] = np.nan
    return "%d/%d" % (num_of_pair, num_crystal), distance

def plot_hist(hs_list, pair_list, dist_list, bin):       #Print 4 graphs together
    bin_list = []
    y = 0 # minimum of bin
    while y < 1.5:
       bin_list.append(y)
       y += bin

    # row and column sharing
    fig, ((ax1), (ax2), (ax3), (ax4)) = plt.subplots(4, 1, sharex='col', sharey='col')
    ax1.hist(dist_list[0], bins = bin_list, range=[0,1], facecolor='magenta')
    ax1.set_title('%s: %s' % (hs_list[0], pair_list[0]))# ,fontsize=45)
    ax2.hist(dist_list[1], bins = bin_list, range=[0,1], facecolor='blue')
    ax2.set_title('%s: %s' % (hs_list[1], pair_list[1]))# ,fontsize=45)
    ax3.hist(dist_list[2], bins = bin_list, range=[0,1], facecolor='yellow')
    ax3.set_title('%s: %s' % (hs_list[2], pair_list[2]))# ,fontsize=45)
    ax4.hist(dist_list[3], bins = bin_list, range=[0,1], facecolor='green')
    ax4.set_title('%s: %s' % (hs_list[3], pair_list[3]))# ,fontsize=45)
    ax1.axvline(1, color='k', linestyle='--')
    ax2.axvline(1, color='k', linestyle='--')
    ax3.axvline(1, color='k', linestyle='--')
    ax4.axvline(1, color='k', linestyle='--')
    fig_name =  "hist.png"
#   plt.savefig(fig_name)

    plt.show()

###################################################################################################
if __name__ == "__main__":
    main(sys.argv[1:])
