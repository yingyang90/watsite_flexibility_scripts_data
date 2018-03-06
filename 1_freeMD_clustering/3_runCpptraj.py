#! /usr/bin/python
import sys, os, os.path
from argparse import ArgumentParser
from collections import defaultdict

parser = ArgumentParser()
group = parser.add_argument_group('Input/Output file options')
group.add_argument('-c', '--redoCluster', dest='cluster', action='store_true', default=False, help='redo clustering for current cluster')
group.add_argument('-r', '--rms2d',       dest='rms2d',   action='store_true', default=False, help='generate one 2d rmsd gnu file for all rep')
group.add_argument('-f', '--get-frame', dest='frame', nargs='+', help='get frame numbers from original traj')
opt = parser.parse_args()


if opt.cluster:
    for i in range(25):
        fo = open("test.in","w")
        fo.write("parm ../../prot_fixed.prmtop [sys]\n")
        fo.write("trajin cluster_hier.c%d netcdf parm [sys]\n" % i)
        fo.write("cluster C0 \\\n")
        fo.write("hieragglo epsilon 0.35 clusters 10 complete \\\n")
        fo.write("rms :111,112,113,114,116,130,133,139,142,143,146,157,166,188,189,202,203,231,318&!@H= nofit \\\n")
        fo.write("summary c%d_summary.txt out c%d_frame.txt \\\n" % (i,i))
        #fo.write("repout rep_c%d repfmt restart\n" % (i))
        fo.write("repout rep_c%d repfmt pdb\n" % i)
        fo.write("go\n")
        fo.write("quit\n")
        fo.close()
        os.system("cpptraj < test.in")
    os.system("rm test.in")

if opt.rms2d:
    fo = open("test.in","w")
    fo.write("parm ../../prot_fixed.prmtop [sys]\n")
    for i in range(25):
        for j in range(5):
            fo.write("trajin rep_c%d.c%d.pdb pdb parm [sys]\n" % (i,j))
    fo.write("rms2d nofit :111,112,113,114,116,130,133,139,142,143,146,157,166,188,189,202,203,231,318&!@H= rmsout rms2d_10cluster.gnu\n")
    fo.write("go\n")
    fo.write("quit\n")
    fo.write("\n")
    fo.close()
    os.system("cpptraj < test.in")
    os.system("rm test.in")

if opt.frame:
    file1 = opt.frame[0]
    file2 = opt.frame[1]
    cluster_num = file2.split("_")[0].split("c")[-1]

    cluster_info = defaultdict(list)
    f1 = open(file1, "r")
    for line in f1:
        if line[0] != "#":
            frame, cluster = line.split()[0], line.split()[1]
            cluster_info[cluster].append(frame)
    f1.close()
    print(cluster_info['%s' % cluster_num])

    frame_list = []
    f2 = open(file2, "r")
    for i in range(11):
        line = f2.readline()
        if line[0] != "#":
            frame_num = int(line.split()[5])
            print(cluster_info[cluster_num][frame_num-1])
            frame_list.append( cluster_info[cluster_num][frame_num-1] )
    f2.close()


    fo = open("cpptraj_frame.in", "w")
    fo.write("parm ../../prot_fixed.prmtop [sys]\n")
    for i in range(1,26):
        fo.write("trajin ../../sys_md_%d.nc netcdf parm [sys]\n" % i)
    fo.write("trajout c%s restart parm [sys] onlyframes " % cluster_num)
    #fo.write("trajout test4.pdb pdb parm [sys] onlyframes ")#" 11445,11446")
    for j in range(10):
        fo.write("%d," %( int(frame_list[j]) ) )
        #print(int(frame_list[j]))
    fo.write("\n")
    fo.write("go\n")
    fo.write("quit\n")
    fo.close()
    os.system("cpptraj < cpptraj_frame.in")

    os.mkdir("cluster_c%s" % cluster_num)
    os.chdir("cluster_c%s" % cluster_num)
    for i in range(10):
        os.mkdir("subcluster_c%d" % i)
        os.system("cp ../c%s.%d subcluster_c%d/prot_amber.inpcrd" % (cluster_num, int(frame_list[i]), i)  )
        os.system("cp ../../../prot_fixed.prmtop subcluster_c%d/prot_amber.prmtop" % (i) )

        os.chdir("subcluster_c%d" % i)
        os.system("ambpdb -p prot_amber.prmtop -c prot_amber.inpcrd > prot_amber.pdb")
        os.chdir("../")


