import numpy as np
import matplotlib.pyplot as plt

results_folder = "/scratch2/yang570/runWATsite4clusters/all_HS/"
output_file = "c0_RMSE.png"
graphs = ["G", "H", "S"]
distance_cutoff = 1
all_subclusters = []
output = []
output_G = []
output_H = []
output_S = []
output_SC = []

for s in range(0,10):
	print "#" * 50
	print s

	md = results_folder + "c0_s%d_HS.pdb" % (s)
	md_lines = []
	fi = open(md, 'r')
	for oneline in fi:
		if oneline.split()[0] == 'ATOM' and oneline.split()[3] == 'WAT':
			md_lines.append(oneline)
	fi.close()
	all_subclusters.append(md_lines)



numHS1 = len(all_subclusters[0])
numHS2 = len(all_subclusters[1])
dis2D = np.zeros((numHS1, numHS2))

for i in range(numHS1):
	hs = all_subclusters[0][i]
	x1,y1,z1 = float(hs[31:38]), float(hs[39:46]), float(hs[47:54])
	for j in range(numHS2):
		hs2 = all_subclusters[1][j]
		x2,y2,z2 = float(hs2[31:38]), float(hs2[39:46]), float(hs2[47:54])
		dis2D[i][j] = ( (x1-x2)**2 + (y1-y2)**2 + (z1-z2)**2 ) ** 0.5

# find the paired hydration sites
left_md1 = range(numHS1)
left_md2 = range(numHS2)

dis_min = np.nanmin(dis2D)
while dis_min <= distance_cutoff:
	x = np.where( dis2D == np.nanmin(dis2D) )
	# eg: (array([15]), array([17])) fst number is the row, snd number is the column of the value
	ind_md1 = x[0][0]
	ind_md2 = x[1][0]

	dis2D[ind_md1, 0:numHS2] = np.nan
	dis2D[0:numHS1,ind_md2] = np.nan

	dis_min = np.nanmin(dis2D)
	
	x1,y1,z1 = float(all_subclusters[0][ind_md1].split()[6]), float(all_subclusters[0][ind_md1].split()[7]),float(all_subclusters[0][ind_md1].split()[8])
	x2,y2,z2 = float(all_subclusters[1][ind_md2].split()[6]), float(all_subclusters[1][ind_md2].split()[7]),float(all_subclusters[1][ind_md2].split()[8])
	matched = False
	avg_x = np.nanmean(np.array([x1,x2]))
	avg_y = np.nanmean(np.array([y1,y2]))
	avg_z = np.nanmean(np.array([z1,z2]))
	G1 = float(all_subclusters[0][ind_md1].split()[10])
	H1 = float(all_subclusters[0][ind_md1].split()[10]) - float(all_subclusters[1][ind_md2].split()[9])
	S1 = float(all_subclusters[0][ind_md1].split()[9])
	G2 = float(all_subclusters[1][ind_md2].split()[10])
	H2 = float(all_subclusters[1][ind_md2].split()[10]) - float(all_subclusters[1][ind_md2].split()[9])
	S2 = float(all_subclusters[1][ind_md2].split()[9])
	output_hs = [avg_x, avg_y, avg_z, x1, y1, z1, x2, y2, z2]
	output.append(output_hs)
	output_G.append([G1, G2])
	output_H.append([H1, H2])
	output_S.append([S1, S2])
	output_SC.append([0, 1])


for s in range(2,10):
	print("Starting subcluster %d" % (s))
	numHS1 = len(all_subclusters[s])
	numHS2 = len(output)
	dis2D = np.zeros((numHS1, numHS2))
	for i in range(numHS1):
		hs = all_subclusters[s][i]
		x1,y1,z1 = float(hs[31:38]), float(hs[39:46]), float(hs[47:54])
		for j in range(numHS2):
			hs2 = output[j]
			x2,y2,z2 = hs2[0],hs2[1],hs2[2]
			dis2D[i][j] = ( (x1-x2)**2 + (y1-y2)**2 + (z1-z2)**2 ) ** 0.5

	# find the paired hydration sites
	left_md1 = range(numHS1)
	print(left_md1)

	dis_min = np.nanmin(dis2D)
	while dis_min <= distance_cutoff:
		x = np.where( dis2D == np.nanmin(dis2D) )
		# eg: (array([15]), array([17])) fst number is the row, snd number is the column of the value
		ind_md1 = x[0][0]
		ind_md2 = x[1][0]

		dis2D[ind_md1, 0:numHS2] = np.nan
		dis2D[0:numHS1,ind_md2] = np.nan

		dis_min = np.nanmin(dis2D)
		x1,y1,z1 = float(all_subclusters[s][ind_md1].split()[6]), float(all_subclusters[s][ind_md1].split()[7]),float(all_subclusters[s][ind_md1].split()[8])

		matched = False
		G1 = float(all_subclusters[s][ind_md1].split()[10])
		H1 = float(all_subclusters[s][ind_md1].split()[10]) - float(all_subclusters[s][ind_md1].split()[9])
		S1 = float(all_subclusters[s][ind_md1].split()[9])
		for i, hs in enumerate(output):
			x2,y2,z2 = hs[0],hs[1],hs[2]
			dis = ( (x1-x2)**2 + (y1-y2)**2 + (z1-z2)**2 ) ** 0.5
			if dis < distance_cutoff:
				avg_x = np.nanmean(np.array([x1,x2]))
				avg_y = np.nanmean(np.array([y1,y2]))
				avg_z = np.nanmean(np.array([z1,z2]))
				output[i].extend([x2, y2, z2])
				output[i][0] = avg_x
				output[i][1] = avg_y
				output[i][2] = avg_z
				output_G[i].extend([G1])
				output_H[i].extend([H1])
				output_S[i].extend([S1])
				output_SC[i].extend([s])
				left_md1.pop(left_md1.index(ind_md1))
				matched = True
				break

	for i in left_md1:
		x,y,z = float(all_subclusters[s][i].split()[6]), float(all_subclusters[s][i].split()[7]),float(all_subclusters[s][i].split()[8])
		G1 = float(all_subclusters[s][i].split()[10])
		H1 = float(all_subclusters[s][i].split()[10]) - float(all_subclusters[s][i].split()[9])
		S1 = float(all_subclusters[s][i].split()[9])
		output_hs = [x, y, z, x, y, z]
		output.append(output_hs)
		output_G.append([G1])
		output_H.append([H1])
		output_S.append([S1])
		output_SC.append([s])

count = []
for k,hs in enumerate(output):
	hs_count = (len(hs)-3)/3
	count.append(hs_count)

# Write by HS to pdb
for by in np.unique(count):
	filename = "test_by%d.pdb" % (by)

	HS = []

	for k,hs in enumerate(output):
		hs_count = (len(hs)-3)/3
		if hs_count == by:
			HS.append(k)



	fw = open(filename, 'w')
	for k, hs in enumerate(HS):
		x = output[hs][0]
		y = output[hs][1]
		z = output[hs][2]
		line = ("ATOM    {:3d}  O   WAT A {:3d}    {:8.3f}{:8.3f}{:8.3f}  0.00   0.00           O\n").format(k,k,x,y,z)
		fw.write(line)
	fw.close()

ax_x = []
for bins in range(0,len(count)):
	for i in range(count[bins]):
		ax_x.append(bins)

for i,graph in enumerate(graphs):
	ax_y = []
	plot = 311+i
	if graph == "G":
		data = output_G
		label = "$\Delta$G"
	elif graph == "H":
		data = output_H
		label = "$\Delta$H"
	elif graph == "S":
		data = output_S
		label = "-T$\Delta$S"
	for by in np.unique(count):
		for k,hs in enumerate(data):
			hs_count = len(hs)
			#print(hs_count)
			if hs_count == by:
				for each_hs in range(hs_count):
					#ind = (each_hs*3)+3
					x = hs[each_hs]
					ax_y.append(x)

	ax_y.reverse()

	subclusters_x = [[],[],[],[],[],[],[],[],[],[]]
	subclusters_y = [[],[],[],[],[],[],[],[],[],[]]
	a = 0
	for hs in output_SC:
		for each_sc in hs:
			subclusters_y[each_sc].append(ax_y[a])
			subclusters_x[each_sc].append(ax_x[a])
			a += 1
		
	plt.subplot(plot)
	for y, sub_x in enumerate(subclusters_x):
		plt.scatter(sub_x, subclusters_y[y], label=y)
	plt.ylabel(label, rotation=0, fontsize=12)
	plt.ylim(min(ax_y)-2,max(ax_y)+2)

plt.subplot(311)
for i in range(0,len(count)):
	plt.text(i-0.5, 10, count[i], color='black', weight='roman', size='small')
plt.subplot(313)
plt.legend(loc='lower center', ncol=10, bbox_to_anchor=(0.5,-0.3))
plt.show()
plt.save('10HS_distribution.png')
