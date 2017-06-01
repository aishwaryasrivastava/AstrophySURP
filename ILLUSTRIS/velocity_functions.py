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

i = 2
c.execute("SELECT haloID FROM range{index}".format(index = i))
haloIDs = c.fetchall()
haloIDs_inrange = []
for haloID in haloIDs:
	haloIDs_inrange.append(str(haloID[0]))
random_hosts = []
for j in range(0,2):
	host = random.choice(haloIDs_inrange)
	while host in random_hosts:
		host = random.choice(haloIDs_inrange)
	random_hosts.append(host)
satellites = []
for hostID in random_hosts:
	c.execute("SELECT subhaloID FROM satellites WHERE haloID = '%s'"% hostID)
	subhaloIDs = c.fetchall()
	host_satellites =  []
	for ID in subhaloIDs:
		host_satellites.append(ID[0])
	# host_satellites now has the IDs for satellites of hostID
	sat_velocities = []
	for satelliteID in host_satellites:
		c.execute("SELECT SubhaloVel FROM subhalos WHERE subhaloID = '%s'" % hostID)
		vel = c.fetchall()
		sat_velocities.append(float(str(vel[0][0]).split()[0]))
	satellites.append(sat_velocities)

fig, ax = plt.subplots()
labels = []
for j in range(0,2):
	labels.append("#{HostID}: $\mu =$ {mean}; $\sigma =$ {sigma}".format(HostID = random_hosts[j], mean = '%.3f'%mean(satellites[j]), sigma = '%.3f'%std(satellites[j])))
	
n, bins, patches = ax.hist(satellites, n_bins, normed = 1, histtype = 'bar', label = labels)
y = mlab.normpdf(bins, mu, sigma)
ax.plot(bins, y, '--')
ax.set_xlabel('Vx (km/s) of satellites')
ax.set_ylabel('Probability')
ax.legend(prop = {'size': 10})
plt.grid(True)
fig.set_size_inches(10,10)
ax.set_title("Velocity function of hosts in range {index}".format(index = i))
plt.savefig("Range{i1}/range{i2}_velocity_function.png".format(i1 = i, i2 = i))
plt.close()

		
		
	
