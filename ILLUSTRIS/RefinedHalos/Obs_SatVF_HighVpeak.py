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

# Gravitational constant
G = 6.67e-11 * (1.e-3)**2. * (2.e30)/(3.086e19) 

n_bins_def = 200
host_count_def = 50
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

# List of velocities
velocities = []

# Acquiring the subhalos
c.execute("SELECT Subhalos.SubhaloID, SubhaloPos.Y, SubhaloPos.Z, SubhaloVel.X, Subhalos.StellarMass FROM Subhalos INNER JOIN SubhaloPos ON SubhaloPos.SubhaloID = Subhalos.SubhaloID INNER JOIN SubhaloVel ON SubhaloVel.SubhaloID = Subhalos.SubhaloID WHERE Subhalos.SubhaloVmax > {Vp}".format(Vp = Vpeak))
Satellites = c.fetchall()

# Acquiring halos
c.execute("SELECT Groups.GroupID, GroupPos.X, GroupPos.Y, GroupPos.Z, Groups.StellarMass, Groups.Group_R_Crit200, GroupVel.X, Groups.Group_M_Crit200 FROM Groups INNER JOIN RefinedGroups ON RefinedGroups.GroupID = Groups.GroupID INNER JOIN GroupPos ON Groups.GroupID = GroupPos.GroupID INNER JOIN GroupVel ON Groups.GroupID = GroupVel.GroupID")
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
	GroupPosX = Halo[1]
	GroupPosY = Halo[2]
	GroupPosZ = Halo[3]
	GroupMass = Halo[4]
	GroupRvir = Halo[5]
	GroupVelX = Halo[6]
	GroupMvir = Halo[7]

	#for Sat in Satellites:
	for k in range(0,len(Satellites)):
		
		Sat = Satellites[k]
		SatID = Sat[0]
		SatPosY = Sat[1]
		SatPosZ = Sat[2]
		SatVelX = Sat[3]
		SatMass = Sat[4]

		Dist = (((SatPosY - GroupPosY)**2)+((SatPosZ - GroupPosZ)**2))**(0.5)
		Vvir = ((G * GroupMvir/GroupRvir)*(3e8/1e10))**(0.5)

		if (Dist < GroupRvir) and (SatMass < GroupMass) and (numpy.absolute(SatVelX - GroupVelX) < Vvir):
			velocities.append(SatVelX)	
print "\n"
# Create the plot
fig, ax = plt.subplots()
n, bins, patches = ax.hist(velocities, n_bins, normed = 1, histtype = 'stepfilled', stacked = True)
ax.set_xlabel('Vx (km/s) of satellites')
ax.set_ylabel('Probability')
plt.xlim([-200,200])
ax.set_title('Velocity function of observational satellites of refined halos\nSample size = {size}; bin size = {bin}; '.format(size = host_count, bin = n_bins)+"$\mu =$ {mean}; $\sigma =$ {std}".format(mean = '%.3f'% mean(velocities), std = '%.3f'% std(velocities)))
plt.grid(True)
fig.set_size_inches(10,10)	
plt.savefig("plots/Obs_SatVF_HighVpeak.png")
plt.close()
conn.commit()
conn.close()

