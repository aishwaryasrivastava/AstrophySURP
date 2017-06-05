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

velocities = [[],[],[]]
labels = []
n_bins = 20

for i in range(1,4):
	print "range " + `i`
	c.execute("SELECT Groups.GroupID, Groups.GroupNsubs, Groups.GroupFirstSub FROM Range{index} INNER JOIN Groups WHERE Range{index}.GroupID = Groups.GroupID".format(index = i))
	Halos = c.fetchall()
	print "fetching halos"

	fraction = 1000
	barwidth = (len(Halos)/fraction)+1
	sys.stdout.write("Fetching halos...[%s]"%(" " * barwidth))
	sys.stdout.flush()
	sys.stdout.write("\b" * (barwidth+1))

	for j in range(len(Halos)):
		if j%fraction==0:
			sys.stdout.write("#")
			sys.stdout.flush()
		Halo = Halos[j]
		Satellites = range(Halo[2], Halo[1]+Halo[2])
		c.execute("SELECT X FROM GroupVel WHERE GroupID = ?", (Halo[0],))
		HostVelX = c.fetchall()[0][0]
		for SatID in Satellites:
			c.execute("SELECT X FROM SubhaloVel WHERE SubhaloID = ?", (SatID,))
			SatVelX = c.fetchall()[0][0]
			velocities[i-1].append(SatVelX-HostVelX)
	labels.append("Range {index}: $\mu =$ {mean}; $\sigma =$ {std}".format(index = i, mean = '%.3f'% mean(velocities[i-1]), std = '%.3f'% std(velocities[i-1])))
fig, ax = plt.subplots()
n, bins, patches = ax.hist(velocities, n_bins, normed = 1, histtype = 'stepfilled', stacked = True, label = labels)
ax.set_xlabel('Vx (km/s) of satellites')
ax.set_ylabel('Probability')
plt.xlim([-200,200])
ax.legend(prop = {'size': 10})
ax.set_title('Velocity function of satellites in different stellar mass ranges')
plt.grid(True)
fig.set_size_inches(10,10)	
plt.savefig("satellite_velocity_function_by_range.png")
plt.close()

