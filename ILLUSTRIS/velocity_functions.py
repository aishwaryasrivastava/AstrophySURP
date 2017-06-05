
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

n_bins = 20

for i in range(1,4):
	c.execute("SELECT Groups.GroupID, Groups.GroupNsubs, Groups.GroupFirstSub FROM Range{index} INNER JOIN Groups WHERE Range{index}.GroupID = Groups.GroupID".format(index = i))
	halos = c.fetchall()
	# halos[i][0] = i-th halo GroupID
	# halos[i][1] = i-th halo GroupNSubs
	# halos[i][2] = i-th halo GroupFirstSub

	# Finding random hosts
	random_hosts = []
	for j in range(0,2):
		ind = random.choice(len(halos))
		while halos[ind] in random_hosts:
			ind = random.choice(len(halos))
		random_hosts.append(halos[ind])

	satellite_velocities = []
	for host in random_hosts:
		satellites = range(host[2], host[2]+host[1])
		velocities = []
		# satellites = list of indices in the Subhalo table
		for satID in satellites:
			c.execute("SELECT X FROM SubhaloVel WHERE SubhaloID = ?",(satID,))
			VelX = c.fetchall()[0][0]
			velocities.append(VelX)
		satellite_velocities.append(velocities)
		
	# satellite_velocities is a list containing the satellite velocities of each host {[host1sat1velocity, host1sat2velocity...][host2sat1velocity, host2sat2velocity...]}

	fig, ax = plt.subplots()
	labels = []
	for j in range(0,2):
		labels.append("#{HostID}: $\mu =$ {mean}; $\sigma =$ {sigma}".format(HostID = random_hosts[j][0], mean = '%.3f'%mean(satellite_velocities[j]), sigma = '%.3f'%std(satellite_velocities[j])))
	
	n, bins, patches = ax.hist(satellite_velocities, n_bins, normed = 1, histtype = 'bar', label = labels)
	#y = mlab.normpdf(bins, mu, sigma)
	#ax.plot(bins, y, '--')
	ax.set_xlabel('Vx (km/s) of satellites')
	ax.set_ylabel('Probability')
	ax.legend(prop = {'size': 10})
	plt.grid(True)
	fig.set_size_inches(10,10)
	ax.set_title("Velocity function of hosts in range {index}".format(index = i))
	plt.savefig("Range{i1}/range{i2}_velocity_function.png".format(i1 = i, i2 = i))
	plt.close()
conn.commit()
conn.close()
		
		
	
