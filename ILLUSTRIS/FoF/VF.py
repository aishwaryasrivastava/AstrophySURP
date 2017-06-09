import sqlite3
import os
import sys
import numpy
import random
from numpy import * 
from numpy import linalg
import scipy
from scipy.optimize import brentq
import pylab as pl
import matplotlib.pyplot as plt
import matplotlib.mlab as mlab
import numpy as np
np.seterr(divide = 'ignore', invalid = 'ignore')

# Connecting to the database
conn = sqlite3.connect('../ILLUSTRIS.db')
c = conn.cursor()

n_bins = int(sys.argv[1])

for i in range(1,4):
	# Acquiring halos
	c.execute("SELECT Groups.GroupID, Groups.GroupNsubs, Groups.GroupFirstSub FROM Range{index} INNER JOIN Groups ON Range{index}.GroupID = Groups.GroupID".format(index = i))
	Halos = c.fetchall()

	velocities = []
	labels = []

	RandomHosts = []
	for j in range(0,5):
		# Selecting random hosts
		ind = random.choice(len(Halos))

		while ind in RandomHosts:
			ind = random.choice(len(Halos))
		RandomHosts.append(ind)
		Halo = Halos[ind]
		GroupID = Halo[0]
		GroupNSubs = Halo[1]
		GroupFirstSub = Halo[2]
		
		# List of satellite velocities
		velocities.append([])
		# Acquiring satellites
		Satellites = range(GroupFirstSub, GroupFirstSub+GroupNSubs)
		for SatID in Satellites:
			c.execute("SELECT X FROM SubhaloVel WHERE SubhaloID = ?",(SatID,))
			VelX = c.fetchall()[0][0]
			velocities[j].append(VelX)
		labels.append("#{HostID}: $\mu =$ {mean}; $\sigma =$ {sigma}".format(HostID = GroupID, mean = '%.3f'%mean(velocities[j]), sigma = '%.3f'%std(velocities[j])))
		
	# Creating the plot
	fig, ax = plt.subplots()	
	n, bins, patches = ax.hist(velocities, n_bins, normed = 1, histtype = 'bar', label = labels)
	ax.set_xlabel('Vx (km/s) of satellites')
	ax.set_ylabel('Probability')
	ax.legend(prop = {'size': 10})
	plt.grid(True)
	fig.set_size_inches(10,10)
	ax.set_title("Velocity function of hosts in range {index}".format(index = i))
	plt.savefig("Range{index}/Range{index}_VF.png".format(index = i))
	plt.close()
conn.commit()
conn.close()
		
		
	
