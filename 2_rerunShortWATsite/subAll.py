#! /usr/bin/python
import sys, os, os.path, subprocess
import multiprocessing as mp

def main():

    clusters = [0, 1, 4]
    pool=mp.Pool(processes=4) 

    cwd = os.getcwd()
    for i in clusters:
        dir_cluster = "cluster_c%d" % i
        for j in range(10):
            dir_rep = "subcluster_c%d" % j
            gotoDir = cwd+"/"+dir_cluster+"/"+dir_rep
            pool.apply_async(runOMM, args=(gotoDir, j,))
    
    pool.close()
    pool.join()

def runOMM(gotoDir, num):

    if num % 2 == 0:
        subprocess.call("cd %s && /opt/data/klebe_mcpb/tln8_5nsWATsite/runMD4clusters_cuda0.sh" % gotoDir, shell=True)
    else:
        subprocess.call("cd %s && /opt/data/klebe_mcpb/tln8_5nsWATsite/runMD4clusters_cuda1.sh" % gotoDir, shell=True)
    cwd = os.getcwd()
    print cwd


main()
