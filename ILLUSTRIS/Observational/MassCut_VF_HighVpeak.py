import sqlite3
import os
import sys
import random
import matplotlib.pyplot as plt
import numpy as np
np.seterr(divide = 'ignore', invalid = 'ignore')

# Connecting to the database
conn = sqlite3.connect('../ILLUSTRIS.db')
c = conn.cursor()

# TO-DO: make this a parameter while running the script
cutoff = float(sys.argv[1])
n_bins = int(sys.argv[2])	# n_bins = 50 is a good choice
Vpeak = 12

# Creating plot for ranges 1-3
for i in range(1,4):
	# List of velocities for satellites with mass < cutoff (little) and > cutoff (big)
	little = []	
	big = []	
	
	# Acquiring halos in range i
	c.execute("SELECT Groups.GroupID, Groups.GroupNsubs, Groups.GroupFirstSub FROM Groups INNER JOIN Range{index} WHERE Range{index}.GroupID = Groups.GroupID".format(index = i))
	Halos = c.fetchall()

	# Selecting random hosts
	RandomHosts = []
	for j in range(0,100):
		ind = np.random.choice(len(Halos))
		while Halos[ind] in RandomHosts:
			ind = np.random.choice(len(Halos))
		RandomHosts.append(Halos[ind])

	# Acquiring satellites of these random hosts
	for Halo in RandomHosts:
		Satellites = range(Halo[2], Halo[2]+Halo[1])

		# For each satellite, check mass and add to corresponding list
		for SatID in Satellites:
			c.execute("SELECT SubhaloVel.X, Subhalos.StellarMass, Subhalos.SubhaloVmax FROM (Subhalos INNER JOIN SubhaloVel ON Subhalos.SubhaloID = SubhaloVel.SubhaloID) WHERE Subhalos.SubhaloID = ?", (SatID,))
			Result = c.fetchall()

			VelX = Result[0][0]
			Mass = Result[0][1]
			Vmax = Result[0][2]

			if Vmax > Vpeak:
				if Mass < cutoff:
					little.append(VelX)
				else:
					big.append(VelX)

	# Plot the velocities
	fig, ax = plt.subplots()
	n, bins, patches = ax.hist([little, big], n_bins, normed = 1, histtype = 'stepfilled', stacked = True, label = ["Mstar < {cutoffmass} Msun; $\mu =$ {littlemean}; $\sigma =$ {littlestd}".format(cutoffmass = '%.2e' % cutoff, littlemean = '%.3f'% np.mean(little), littlestd =  '%.3f'% np.std(little)), "Mstar > {cutoffmass} Msun; $\mu =$ {bigmean}; $\sigma =$ {bigstd}".format(cutoffmass = '%.2e' % cutoff, bigmean =  '%.3f'%np.mean(big), bigstd =  '%.3f'%np.std(big))])
	ax.set_xlabel('Vx (km/s) of satellites')
	ax.set_ylabel('Probability')
	ax.legend(prop = {'size': 10})
	ax.set_title("Range {index}: Comparison of velocity functions of satellites of new and little hosts\n(cutoff = {cutoffmass} Msun, Vpeak > {Vp} km/s)".format(index = i, cutoffmass = '%.2e'%cutoff, Vp = Vpeak))
	plt.grid(True)
	fig.set_size_inches(10,10)		
	plt.savefig( "Range{index}/Range{index}_Mass_cut_VF_HighVpeak".format(index = i))
	plt.close()

# Save and close the connection
conn.commit()
conn.close()
			
