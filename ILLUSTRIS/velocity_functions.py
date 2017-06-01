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
	c.execute("SELECT GroupID FROM Range{index}".format(index = i))
	rows = c.fetchall()
	IDs = []
	for row in rows:
		IDs.append(row[0])

	# Finding random hosts
	random_hosts = []
	for j in range(0,2):
		host = random.choice(IDs)
		while host in random_hosts:
			host = random.choice(IDs)
		random_hosts.append(host)
	velocities = []
	for hostID in random_hosts:
		satellite_velocities = []
		satelliteIDs = []
		c.execute("SELECT SubhaloID from Satellites WHERE GroupID = ?", (hostID,))
		rows = c.fetchall()
		for row in rows:
			satelliteIDs.append(row[0])
		for satellite in satelliteIDs:
			c.execute("SELECT X FROM SubhaloVel WHERE SubhaloID = ?", (satellite,))
			Vx = c.fetchall()[0][0]
			satellite_velocities.append(Vx)
		velocities.append(satellite_velocities)
		print len(satellite_velocities)
		
	# velocities now is a list containing the satellite velocities of each host {[host1sat1velocity, host1sat2velocity...][host2sat1velocity, host2sat2velocity...]}

	fig, ax = plt.subplots()
	labels = []
	for j in range(0,2):
		labels.append("#{HostID}: $\mu =$ {mean}; $\sigma =$ {sigma}".format(HostID = random_hosts[j], mean = '%.3f'%mean(velocities[j]), sigma = '%.3f'%std(velocities[j])))
	
	n, bins, patches = ax.hist(velocities, n_bins, normed = 1, histtype = 'bar', label = labels)
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
		
		
	
