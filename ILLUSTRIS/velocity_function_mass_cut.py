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

conn = sqlite3.connect('halos_and_subhalos.db')
c = conn.cursor()
# TO-DO Add check for arguments
cutoff = 1.e5

for i in range(1,4):
	little = []
	big = []
	c.execute("SELECT Groups.GroupID, Groups.GroupNsubs, Groups.GroupFirstSub FROM Groups INNER JOIN Range{index} WHERE Range{index}.GroupID = Groups.GroupID".format(index = i))
	Halos = c.fetchall()
	RandomHosts = []
	for j in range(0,2):
		ind = (random.choice(len(Halos)))
		while Halos[ind] in RandomHosts:
			ind = random.choice(len(Halos))
		RandomHosts.append(Halos[ind])
	for Halo in RandomHosts:
		Satellites = range(Halo[2], Halo[2]+Halo[1])
		for SatID in Satellites:

			c.execute("SELECT X FROM SubhaloVel WHERE SubhaloID = ?", (SatID,))
			VelX = c.fetchall()[0][0]
			c.execute("SELECT StellarMass FROM Subhalos WHERE SubhaloID = ?", (SatID,))
			Mass = c.fetchall()[0][0]

			if Mass < cutoff:
				little.append(VelX)
			else:
				big.append(VelX)
	fig, ax = plt.subplots()
	n_bins = 20
	n, bins, patches = ax.hist([little, big], n_bins, normed = 1, histtype = 'stepfilled', stacked = True, label = ["Mstar < {cutoffmass} Msun; $\mu =$ {littlemean}; $\sigma =$ {littlestd}".format(cutoffmass = '%.2e' % cutoff, littlemean = '%.3f'% mean(little), littlestd =  '%.3f'% std(little)), "Mstar > {cutoffmass} Msun; $\mu =$ {bigmean}; $\sigma =$ {bigstd}".format(cutoffmass = '%.2e' % cutoff, bigmean =  '%.3f'%mean(big), bigstd =  '%.3f'%std(big))])
	ax.set_xlabel('Vx (km/s) of satellites')
	ax.set_ylabel('Probability')
	ax.legend(prop = {'size': 10})
	ax.set_title("Range {index}: Comparison of velocity functions of satellites of new and little hosts (cutoff = {cutoffmass} Msun)".format(index = i, cutoffmass = '%.2e'%cutoff))
	plt.grid(True)
	fig.set_size_inches(10,10)		
	plt.savefig( "Range{index}/range{index}_velocity_function_cut_by_mass.png".format(index = i))
	plt.close()

conn.commit()
conn.close()
			
