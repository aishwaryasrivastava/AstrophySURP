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

# 2D array of velocities of satellites for each range
velocities = []

n_bins_def = 200
host_count_def = 400
Vpeak = 12

# n_bins = 200 is a good choice
n_bins = raw_input("\nEnter no. of bins (Press Enter for default = {Def}): ".format(Def = n_bins_def))
if len(n_bins) == 0:
	n_bins = n_bins_def
else:
	n_bins = int(n_bins)

# Number of hosts (100 is a good choice)
host_count = raw_input("\nEnter set size (Press Enter for default = {Def}): ".format(Def = host_count_def))
if len(host_count) == 0:
	host_count = host_count_def
else:
	host_count = int(host_count)


# Acquiring halos
c.execute("SELECT Groups.GroupID, Groups.GroupNsubs, Groups.GroupFirstSub, GroupVel.X FROM (RefinedGroups INNER JOIN Groups ON RefinedGroups.GroupID = Groups.GroupID INNER JOIN GroupVel ON GroupVel.GroupID = Groups.GroupID)")
Halos = c.fetchall()

#Loading bar
barwidth = 50
fraction = host_count/(barwidth-1)
sys.stdout.write("Creating velocity function:\t[%s]"%(" "*barwidth))
sys.stdout.flush()
sys.stdout.write("\b"*(barwidth+1))

# Selecting random hosts
RandomHosts = []
for j in range(0,host_count):
	if j % fraction == 0:
		sys.stdout.write("#")
		sys.stdout.flush()
	
	ind = np.random.choice(len(Halos))
	while Halos[ind] in RandomHosts:
		ind = np.random.choice(len(Halos))
	Halo = Halos[ind]
	RandomHosts.append(Halos[ind])

	GroupID = Halo[0]
	GroupNSubs = Halo[1]
	GroupFirstSub = Halo[2]
	GroupVelX = Halo[3]
	Satellites = range(GroupFirstSub, GroupFirstSub+GroupNSubs)
	for SatID in Satellites:
		# Adding relative satellite velocity to the 2D array
		c.execute("SELECT SubhaloVel.X, Subhalos.StellarMass, Subhalos.SubhaloVmax FROM Subhalos INNER JOIN SubhaloVel ON Subhalos.SubhaloID = SubhaloVel.SubhaloID WHERE Subhalos.SubhaloID = ?",(SatID,))
		result = c.fetchall()		
		SatVelX = result[0][0]
		SatMass = result[0][1]
		SatVmax = result[0][2]
		# TO-DO: Add a mass cut for satellites
		if SatVmax > Vpeak:
			velocities.append(SatVelX - GroupVelX)

print "\n"
# Create the plot
fig, ax = plt.subplots()
n, bins, patches = ax.hist(velocities, n_bins, normed = 1, histtype = 'stepfilled', stacked = True)
ax.set_xlabel('Vx (km/s) of satellites')
ax.set_ylabel('Probability')
plt.ylim([0,0.12])
plt.xlim([-200,200])
ax.set_title('Velocity function of satellites of refined halos\nSample size = {size}; bin size = {bin}; '.format(size = host_count, bin = n_bins)+"$\mu =$ {mean}; $\sigma =$ {std}".format(mean = '%.3f'% mean(velocities), std = '%.3f'% std(velocities)))
plt.grid(True)
fig.set_size_inches(10,10)	
plt.savefig("SubFind_SatVF_HighVpeak.png")
plt.close()

# Close the connection
conn.commit()
conn.close()

