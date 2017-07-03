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

import matplotlib.mlab as mlab
import numpy as np
np.seterr(divide = 'ignore', invalid = 'ignore')

# Connect to a databse
conn = sqlite3.connect('../ILLUSTRIS.db')
c = conn.cursor()

#-----------------------------------------CONSTANTS/DEFAULTS--------------------------------------
# Fields:
ID = 0
VELX = 3
# Group fields:
FIRSTSUB = 1
NSUBS = 2
# Subhalo fields:
VMAX = 1
STELLARMASS = 2
GRNR = 4

host_count = 400

#-----------------------------------------FUNCTIONS------------------------------------------------

# Returns a list of {Count} random elements from {List}
def RandomElements(List, Count):
	print "\nFinding random elements..."
	# List of chosen elements
	Chosen = []
	for i in range(Count):
		# Pick a random element from {List}
		i = random.choice(len(List))
		# If {i} is already chosen, pick another
		while i in Chosen:
			i = random.choice(len(List))
		# Once a unique element {i} is chosen, add it to the list		
		Chosen.append(List[i])
	return Chosen

#Iterative sigma-clipping of background noise
def clip(arr,nsig=3.):
    a = arr.flatten()
    a.sort()
   
    m,s,l = a.mean(),a.std(),a.size

    while 1:
        a = a[abs(a-m)<s*nsig]
        
        if a.size==l:
            
            return s
        
        m,s,l = a.mean(),a.std(),a.size

# Returns a list of Satellites belonging to {Group} using the SubFind Algorithm
def SatellitesOf(Group):
	IDs = range(Group[FIRSTSUB], Group[FIRSTSUB] + Group[NSUBS])
	return [Subhalo for Subhalo in Subhalos if Subhalo[ID] in IDs]

def plot(X, Y, Xlabel, Ylabel, Title, Filename, logscale = False):
	import matplotlib.pyplot as plt
	plt.plot(X, Y, 'ro')
	for i in range(1,5):
		plt.annotate("Range {Index}".format(Index = i), xy = (X[i-1], Y[i-1]), xytext =(X[i-1], Y[i-1]))
	plt.xlabel(Xlabel)
	plt.ylabel(Ylabel)
	if logscale:
		plt.xscale('log')
	plt.title(Title)
	plt.savefig(Filename)
	plt.close()
#-----------------------------------------MAIN------------------------------------------------
Sigma = []
AvgVmax = []
AvgStellarMass = []
Labels = []

# Fetch subhalos
c.execute("SELECT Subhalos.SubhaloID, Subhalos.SubhaloVmax, Subhalos.StellarMass, SubhaloVel.X, Subhalos.SubhaloGrNr FROM Subhalos INNER JOIN SubhaloVel ON Subhalos.SubhaloID = SubhaloVel.SubhaloID")
Subhalos = c.fetchall() 


for i in range(1,5):
	RelVelX = []
	StellarMass = []
	Vmax = []
	c.execute("SELECT Groups.GroupID, Groups.GroupFirstSub, Groups.GroupNsubs, GroupVel.X FROM Groups INNER JOIN RefinedGroups ON Groups.GroupID = RefinedGroups.GroupID INNER JOIN GroupVel ON Groups.GroupID = GroupVel.GroupID INNER JOIN Range{Index} ON Range{Index}.GroupID = Groups.GroupID".format(Index = i))
	Groups = RandomElements(c.fetchall(), host_count)
	
	barwidth = 50
	fraction = host_count/(barwidth-1)
	sys.stdout.write("Sigma clipping for Range{Index}:\t[%s]".format(Index = i)%(" "*barwidth))
	sys.stdout.flush()
	sys.stdout.write("\b"*(barwidth+1))

	for j in range(0,host_count):

		if j % fraction == 0:
			sys.stdout.write("#")
			sys.stdout.flush()

		Satellites = SatellitesOf(Groups[j])

		# Find the biggest subhalo in the group
		BiggestSubhalo = Satellites[0]
		for Sat in Satellites:
			
			if Sat[STELLARMASS] > BiggestSubhalo[STELLARMASS]:
				BiggestSubhalo = Sat
		StellarMass.append(BiggestSubhalo[STELLARMASS])
		for Sat in Satellites:
			if not Sat[ID] == BiggestSubhalo[ID]:
				RelVelX.append(Sat[VELX]-Groups[j][VELX])

		# Make sure the Biggest subhalo is within 10% of the group's stellar mass
		if ((Groups[j][STELLARMASS] - BiggestSubhalo[STELLARMASS])/Groups[j][STELLARMASS])*100 < 10:
			Vmax.append(BiggestSubhalo[VMAX])
	
	print "\n"

	Sigma.append(clip(np.asarray(RelVelX)))
	AvgVmax.append(np.mean(Vmax))
	AvgStellarMass.append(np.mean(StellarMass))
	Labels.append("Range {Index}".format(Index = i))

plot(X = AvgVmax, Y = Sigma, Xlabel = "Average Vmax of hosts (km/s)",Ylabel = "Standard deviation in relative velocity of satellites (km/s)", Title = "Sigma clipping results as a function of the average maximum velocity of hosts", Filename = "SigmaClip_Vmax.png")

plot(X = AvgStellarMass, Y = Sigma, Xlabel = "Average stellar mass of hosts (Msun)", Ylabel = "Standard deviation in relative velocity of satellites (km/s)", Title = "Sigma clipping results as a function of the average stellar mass of hosts", Filename = "SigmaClip_Mass.png", logscale = True)

	
	



	
