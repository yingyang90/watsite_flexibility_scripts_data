#!/usr/bin/python
import os, sys, getopt, math
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt

###################################################################################################

FILENAME = "HydrationSites.pdb"
OUTPUT = "thermo_prop_15A_full.png"

fst_file = "by35A/WATsite_OUT/" + FILENAME
snd_file = "by15A/WATsite_OUT/" + FILENAME
distance_cutoff = 1.0

# read first file 
fst_list = []
f1 = open(fst_file, 'r')
for oneline in f1:
	if oneline.split()[0] == 'ATOM' and oneline.split()[3] == 'WAT':
		fst_list.append(oneline)
		#print oneline
num_fst = len(fst_list)

# read second file
snd_list = []
f2 = open(snd_file, 'r')
for oneline in f2:
	if oneline.split()[0] == 'ATOM' and oneline.split()[3] == 'WAT':
		#print oneline
		snd_list.append(oneline)
num_snd = len(snd_list)

# set up a 2D array
dis = np.zeros((num_fst, num_snd))

for i in range(num_fst):
	x1,y1,z1 = float(fst_list[i].split()[6]), float(fst_list[i].split()[7]),float(fst_list[i].split()[8])
	for j in range(num_snd):
		x2,y2,z2 = float(snd_list[j].split()[6]), float(snd_list[j].split()[7]),float(snd_list[j].split()[8])
		dis[i][j] = ( (x1-x2)**2 + (y1-y2)**2 + (z1-z2)**2 ) ** 0.5

num = min(num_fst, num_snd)
print "Number of pairs: %d\n" % num
num_all = (num_fst+num_snd)/2

pairs = []
distance = []
#		occ_1 = []
#		occ_2 = []
while num > 0:
	x = np.where( dis == np.nanmin(dis) ) 
	# eg: (array([15]), array([17])) fst number is the row, snd number is the column of the value
	print x
	ind_fst = x[0][0]
	ind_snd = x[1][0]
	num = num - 1
	#print num 

	if dis[ind_fst][ind_snd] <=  distance_cutoff:
#				print dis[ind_fst][ind_snd]
		pairs.append(ind_fst)
		pairs.append(ind_snd)
#				occ_1.append(ind_fst)
#				occ_2.append(ind_snd)
		distance.append(dis[ind_fst][ind_snd])
	dis[ind_fst, 0:num_snd] = np.nan
	dis[0:num_fst,ind_snd] = np.nan
	print "pair: fst_%d snd_%d     dis: %f" % (ind_fst+1, ind_snd+1, dis[ind_fst][ind_snd])


num_pair = len(distance)
percent = float(num_pair) / float(num_all)
print "percentage=%f\n\n"%percent


#####################
# put data into array
#####################
G1_array = []	
G2_array = []
for i in range(len(distance)):
	G1_array.append( float( fst_list[ pairs[2*i] ].split()[10] ) )
	G2_array.append( float( snd_list[ pairs[2*i + 1] ].split()[10] ) )
S1_array = []
S2_array = []
for i in range(len(distance)):
	S1_array.append( float( fst_list[ pairs[2*i] ].split()[9] ) )
	S2_array.append( float( snd_list[ pairs[2*i + 1] ].split()[9] ) )
H1_array = []
H2_array = []
for i in range(len(distance)):
	H1_value = float( fst_list[ pairs[2*i] ].split()[10] ) - float( fst_list[ pairs[2*i] ].split()[9] )
	H2_value = float( snd_list[ pairs[2*i + 1] ].split()[10] ) - float( snd_list[ pairs[2*i + 1] ].split()[9] )
	H1_array.append( H1_value )
	H2_array.append( H2_value )

print G1_array
print G2_array

print S1_array
print S2_array

print H1_array
print H2_array

############
# free energy
############d

fig = plt.figure(figsize=(33,6))
cm = plt.cm.get_cmap('RdYlBu')
ax1 = fig.add_subplot(131)
ax1.set_xlim([min(G2_array)-1,max(G2_array)+1])
ax1.set_ylim([min(G2_array)-1,max(G2_array)+1])
ax1.grid(True)
figureName = "$\Delta$G (kcal/mol)\n"
ax1.set_title(figureName, fontsize=20)
sys1 = ax1.scatter(G1_array, G2_array, c=distance, vmin=0, vmax=1, s=80, cmap=cm, marker='o', label="")

# regression through y=x
Gx = G1_array
Gy = G2_array
Gybar = sum(Gy) / len(Gy)

fitG = [1, 0]
fitG_fn = np.poly1d(fitG)
fit1 = ax1.plot(Gx, fitG_fn(Gx), '--k')

SSres = 0
SStot = 0
for i in range( len(Gx) ):
	print "Gx=%f" %Gx[i]
	print "Gy=%f" %Gy[i]
	print "fitG_fn(Gx[i]) = %f" %fitG_fn(Gx[i])
	SSres = SSres + ( Gy[i] - fitG_fn(Gx[i]) )**2
	SStot = SStot + ( Gy[i] - Gybar)**2

print SSres
print SStot
r2 = 1 - float(SSres) / float(SStot) 
print "R2=%f\n" % r2
plt.text(2,2,'$R^2 = %s$' % (str(r2)[:4]),fontsize=14)
ax1.set_ylabel('\nEnergies from 20 A truncated simulation',fontsize=20)

############
# entropy
############

ax2 = fig.add_subplot(133)
ax2.set_xlim([min(S2_array)-1,max(S2_array)+1])
ax2.set_ylim([min(S2_array)-1,max(S2_array)+1])
ax2.grid(True)
figureName = "-T$\Delta$S (kcal/mol)\n"
ax2.set_title(figureName, fontsize=20)
sys1 = ax2.scatter(S1_array, S2_array, c=distance, vmin=0, vmax=1, s=80, cmap=cm, marker='o', label="")

# regression through y=x
Sx = S1_array
Sy = S2_array
Sybar = sum(Sy) / len(Sy)

fitS = [1, 0]
fitS_fn = np.poly1d(fitS)
fit1 = ax2.plot(Sx, fitS_fn(Sx), '--k')

SSres = 0
SStot = 0
for i in range( len(Sx) ):
	SSres = SSres + ( Sy[i] - fitS_fn(Sx[i]) )**2
	SStot = SStot + ( Sy[i] - Sybar)**2
r2 = 1 - float(SSres) / float(SStot) 
print "R2=%f\n" % r2
plt.text(3,2,'$R^2 = %s$' % (str(r2)[:4]),fontsize=14)


cbar = plt.colorbar(sys1, use_gridspec=True)
cbar.ax.set_ylabel('\n  Distance between\npaired hydration sites', rotation=90, fontsize=20)

############
# enthalpy
############

ax3 = fig.add_subplot(132)
ax3.set_xlim([min(H2_array)-1,max(H2_array)+1])
ax3.set_ylim([min(H2_array)-1,max(H2_array)+1])
ax3.grid(True)
figureName = "$\Delta$H (kcal/mol)\n"
ax3.set_title(figureName, fontsize=20)
sys1 = ax3.scatter(H1_array, H2_array, c=distance, vmin=0, vmax=1, s=80, cmap=cm, marker='o', label="")
ax3.set_xlabel("Energies from full protein simulation",fontsize=20)

# regression through y=x
Hx = H1_array
Hy = H2_array
Hybar = sum(Hy) / len(Hy)

fitH = [1, 0]
fitH_fn = np.poly1d(fitH)
fit1 = ax3.plot(Hx, fitH_fn(Hx), '--k')
SSres = 0
SStot = 0
for i in range( len(Hx) ):
	SSres = SSres + ( Hy[i] - fitH_fn(Hx[i]) )**2
	SStot = SStot + ( Hy[i] - Hybar)**2
r2 = 1 - float(SSres) / float(SStot) 
print "R2=%f\n" % r2
plt.text(0.5,0,'$R^2 = %s$' % (str(r2)[:4]),fontsize=14)

plt.savefig(OUTPUT)
plt.show()
