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

h = 0.704
# Returns the distance between P1 and P2 (in kpc)
def Distance_3D(P1, P2):
	x1 = P1[0]
	x2 = P2[0]
	y1 = P1[1]
	y2 = P2[1]
	z1 = P1[2]
	z2 = P2[2]
	return (((x1-x2)**2 + (y1-y2)**2 + (z1-z2)**2)**0.5)/h

# Connecting to the database
conn = sqlite3.connect('../ILLUSTRIS.db')
c = conn.cursor()

# List of distances between host and satellite
distances = []

n_bins_def = 500
host_count_def = 100

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
c.execute("SELECT Groups.GroupID, Groups.GroupNsubs, Groups.GroupFirstSub, GroupVel.X, GroupPos.X, GroupPos.Y, GroupPos.Z FROM (RefinedGroups INNER JOIN Groups ON RefinedGroups.GroupID = Groups.GroupID INNER JOIN GroupVel ON GroupVel.GroupID = Groups.GroupID INNER JOIN GroupPos ON GroupPos.GroupID = Groups.GroupID)")
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
	GroupPos = (Halo[4], Halo[5], Halo[6])
	Satellites = range(GroupFirstSub, GroupFirstSub+GroupNSubs)
	for SatID in Satellites:
		# Adding relative satellite velocity to the 2D array
		c.execute("SELECT SubhaloVel.X, Subhalos.StellarMass, SubhaloPos.X, SubhaloPos.Y, SubhaloPos.Z, Subhalos.SubhaloID FROM Subhalos INNER JOIN SubhaloVel ON Subhalos.SubhaloID = SubhaloVel.SubhaloID INNER JOIN SubhaloPos ON Subhalos.SubhaloID = SubhaloPos.SubhaloID WHERE Subhalos.SubhaloID = ?",(SatID,))
		result = c.fetchall()		
		SatVelX = result[0][0]
		SatPos = (result[0][2], result[0][3], result[0][4])
		SatID = result[0][5]
		# TO-DO: Add a mass cut for satellites
		Dist = Distance_3D(GroupPos, SatPos)
		if not Dist == 0:
			distances.append(Distance_3D(GroupPos, SatPos))

print "\n"
# Create the plot
fig, ax = plt.subplots()
n, bins, patches = ax.hist(distances, n_bins, normed = 1, histtype = 'stepfilled', stacked = True)
ax.set_xlabel('Distance (kpc)')
ax.set_ylabel('Probability')
ax.set_title('Separation between refined halos and their satellites\nSample size = {size}; bin size = {bin}; '.format(size = host_count, bin = n_bins)+"$\mu =$ {mean}; $\sigma =$ {std}".format(mean = '%.3f'% mean(distances), std = '%.3f'% std(distances)))
plt.grid(True)
fig.set_size_inches(10,10)	
plt.savefig("plots/SubFind_Separation.png")
plt.close()

# Close the connection
conn.commit()
conn.close()

