#------------------------------------------SETUP---------------------------------------------------
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

# Connecting to the database
conn = sqlite3.connect('../ILLUSTRIS.db')
c = conn.cursor()

#-----------------------------------------CONSTANTS AND DEFAULTS---------------------------------

n_bins = 200
host_count = 400

# Common fields:
ID = 0
STELLARMASS = 2
# Group fields:
MVIR = 1
FIRSTSUB = 3
NSUBS = 4
# Subhalo fields:
VMAX = 1
GRNR = 3

# Fetch subhalos
c.execute("SELECT SubhaloID, SubhaloVmax, StellarMass, SubhaloGrNr from Subhalos")
Subhalos = c.fetchall()

#-----------------------------------------INPUTS------------------------------------------------

# Number of bins
user_input = raw_input("\nEnter no. of bins (Press Enter for default = {Def}): ".format(Def = n_bins))
while len(user_input) > 0 and int(user_input) < 0:
	user_input = raw_input("\nNumber of bins cannot be negative! Try again: ")
if not len(user_input) == 0:
	n_bins = int(user_input)

# Sample size
user_input = raw_input("\nEnter set size (Press Enter for default = {Def}): ".format(Def = host_count))
while len(user_input) > 0 and int(user_input) < 0:
	user_input = raw_input("\nSet size cannot be negative! Try again: ")
if not len(user_input) == 0:
	host_count = int(user_input)

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

# Returns a list of Satellites belonging to {Group} using the SubFind Algorithm
def SatellitesOf(Group):
	IDs = range(Group[FIRSTSUB], Group[FIRSTSUB] + Group[NSUBS])
	return [Subhalo for Subhalo in Subhalos if Subhalo[ID] in IDs]

def plot(List, Title, Xlabel, Filename):
	import matplotlib.pyplot as plt
	fig, ax = plt.subplots()	
	n, bins, patches = ax.hist(List, n_bins, normed = 1, histtype = 'stepfilled', label = VmaxLabels)
	ax.legend(prop = {'size':10})
	ax.set_xlabel(Xlabel)
	ax.set_ylabel('Probability')
	plt.grid(True)
	fig.set_size_inches(10,10)
	ax.set_title(Title)
	plt.savefig(Filename)
	plt.close()

#-----------------------------------------MAIN------------------------------------------------

Vmaxes = []
VmaxLabels = []
Masses = []
MassLabels = []

for i in range(1,4):
	Vmax = []
	Mass = []
	
	# Fetch groups
	c.execute("SELECT Groups.GroupID, Groups.Group_M_Crit200, Groups.StellarMass, Groups.GroupFirstSub, Groups.GroupNsubs FROM Groups INNER JOIN RefinedGroups ON Groups.GroupID = RefinedGroups.GroupID INNER JOIN Range{Index} ON Range{Index}.GroupID = Groups.GroupID".format(Index = i))
	Groups = c.fetchall()

	# Get {host_count} random groups
	RandomHosts = RandomElements(Groups, host_count)

	barwidth = 50
	fraction = host_count/(barwidth-1)
	sys.stdout.write("Creating histograms for Range{Index}:\t[%s]".format(Index = i)%(" "*barwidth))
	sys.stdout.flush()
	sys.stdout.write("\b"*(barwidth+1))
	
	for j in range(host_count):
		host = RandomHosts[j]
		
		if j%fraction == 0:
			sys.stdout.write("#")
			sys.stdout.flush()
		
		Mass.append(host[MVIR])

		Satellites = SatellitesOf(host)

		# Find the biggest subhalo in the group
		BiggestSubhalo = Satellites[0]	
		for Subhalo in Satellites:
			if Subhalo[STELLARMASS] > BiggestSubhalo[STELLARMASS]:
				BiggestSubhalo = Subhalo
	
		# Make sure the Biggest subhalo is within 10% of the group's stellar mass
		if ((host[STELLARMASS] - BiggestSubhalo[STELLARMASS])/host[STELLARMASS])*100 < 10:
			Vmax.append(BiggestSubhalo[VMAX])
	
	Vmaxes.append(Vmax)
	VmaxLabels.append("Range {index}: Median = {med}".format(index = i, med = numpy.median(Vmax)))
	Masses.append(Mass)
	MassLabels.append("Range {index}: Median = {med}".format(index = i, med = numpy.median(Mass)))


print "\n"

plot(List = Vmaxes, Title = "Maximum velocity of {count} random dark matter groups".format(count = host_count), Xlabel = "Vmax of groups (km/s)", Filename = "VmaxHistogram.png")
plot(List = Masses, Title = "Virial halo mass of {count} random dark matter groups".format(count = host_count), Xlabel = "Virial mass of Groups (Msun)", Filename = "MassHistogram.png")





