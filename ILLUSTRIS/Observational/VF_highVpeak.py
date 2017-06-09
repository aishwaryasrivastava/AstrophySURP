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
G = 6.67e-11 * (1.e-3)**2. * (2.e30)/(3.086e19) 
Vpeak = 12

# Acquiring the subhalos
c.execute("SELECT Subhalos.SubhaloID, SubhaloPos.Y, SubhaloPos.Z, SubhaloVel.X, Subhalos.StellarMass FROM Subhalos INNER JOIN SubhaloPos ON SubhaloPos.SubhaloID = Subhalos.SubhaloID INNER JOIN SubhaloVel ON SubhaloVel.SubhaloID = Subhalos.SubhaloID WHERE Subhalos.SubhaloVmax > {Vp}".format(Vp = Vpeak))
Satellites = c.fetchall()

count = 0
barwidth = 50
fraction = 3*5*len(Satellites)/barwidth

sys.stdout.write("Creating velocity function:\t[%s]"%(" "*barwidth))
sys.stdout.flush()
sys.stdout.write("\b" *(barwidth+1))

for i in range(1,4):
	# Acquiring halos
	c.execute("SELECT Groups.GroupID, GroupPos.X, GroupPos.Y, GroupPos.Z, Groups.StellarMass, Groups.Group_R_Crit200, GroupVel.X, Groups.Group_M_Crit200 FROM Groups INNER JOIN Range{index} ON Groups.GroupID = Range{index}.GroupID INNER JOIN GroupVel ON Groups.GroupID = GroupVel.GroupID INNER JOIN GroupPos ON Groups.GroupID = GroupPos.GroupID".format(index = i))
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
		GroupPosX = Halo[1]
		GroupPosY = Halo[2]
		GroupPosZ = Halo[3]
		GroupMass = Halo[4]
		GroupRvir = Halo[5]
		GroupVelX = Halo[6]
		GroupMvir = Halo[7]
		
		# List of satellite velocities
		velocities.append([])
		#for Sat in Satellites:
		for k in range(0,len(Satellites)):
			count = count + 1
			
			if count % fraction == 0:
				sys.stdout.write("#")
				sys.stdout.flush()
			
			Sat = Satellites[k]
			SatID = Sat[0]
			SatPosY = Sat[1]
			SatPosZ = Sat[2]
			SatVelX = Sat[3]
			SatMass = Sat[4]

			Dist = (((SatPosY - GroupPosY)**2)+((SatPosZ - GroupPosZ)**2))**(0.5)
			Vvir = ((G * GroupMvir/GroupRvir)*(3e8/1e10))**(0.5)

			if (Dist < GroupRvir) and (SatMass < GroupMass) and (numpy.absolute(SatVelX - GroupVelX) < Vvir):
				velocities[j].append(SatVelX)	
		"""
		# Acquiring satellites
		Satellites = range(GroupFirstSub, GroupFirstSub+GroupNSubs)
		for SatID in Satellites:
			c.execute("SELECT X FROM SubhaloVel WHERE SubhaloID = ?",(SatID,))
			VelX = c.fetchall()[0][0]
			velocities[j].append(VelX)
		"""
		mu = 0
		sigma = 0
		if len(velocities[j]) > 0:
			mu = mean(velocities[j])
			sigma = std(velocities[j])
		
		labels.append("#{HostID}: $\mu =$ {mean_v}; $\sigma =$ {std_v}".format(HostID = GroupID, mean_v = '%.3f'%mu, std_v = '%.3f'%sigma))
		
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
print "\n"
conn.commit()
conn.close()
		
		
	
