import sqlite3
import sys
import random
import numpy as np
import os
np.seterr(divide = 'ignore', invalid = 'ignore')

# Connect to the database
cursor = sqlite3.connect('ILLUSTRIS.db').cursor()

# Fields
ID = 0
RELVELX = 1
STELLARMASS = 2
VMAX = 3
GID = 4
HALOMASS = 5

FIRSTSUB = 1
NSUBS = 2

NO_OF_RESAMPLES = 1000
NO_OF_PLOTS = 1

# Measures
OBS = 0
SUBFIND = 1
OBSCLIPPED = 2
SUBFINDCLIPPED = 3 

#-----------------------------------FUNCTIONS-------------------------------------

# Creating the error bar. Should have 4 points, one for each range
def plot(X, Y, Xerr, Yerr, title, xlabel, ylabel, filename, labels, colors):
	import matplotlib.pyplot as plt
	plt.figure()

	# For each measure
	for i in range(2):
		plt.errorbar(X, [Y[0][i], Y[1][i], Y[2][i]], color = colors[i], label = labels[i], xerr = Xerr, yerr = [Yerr[0][i], Yerr[1][i], Yerr[2][i]])
		# TO-DO: Annotation?
	plt.xlabel(xlabel)
	plt.ylabel(ylabel)
	plt.legend(prop = {'size':10})
	#plt.savefig(filename)
	plt.title(title)
	plt.show()
	plt.close()	

# Finding the Std. Deviation of a list if values {List}
def GetSigma(List):
	Mean = np.mean(List)
	Sigma = 0
	for i in List:
		Sigma += (i - Mean)**2
	return (Sigma/len(List))**0.5

# Finding the uncertainty in a list of std. deviations {Sigmas}
def Uncertainty(Sigmas):
	Uncertainty = 0
	BestEstimate = np.mean(Sigmas)
	for Sigma in Sigmas:
		Uncertainty += (Sigma - BestEstimate)**2
	return (Uncertainty/NO_OF_RESAMPLES)**0.5



#-------------------------------------------------MAIN--------------------------------------------------

for L in range(NO_OF_PLOTS):
	
	# Uncertainties[i][j] = Uncertainty in delta vx of measure j sats in range i 
	Uncertainties = [[0,0],[0,0],[0,0]]

	# Sigmas[i][j] = list of std. deviations of delta vx of measure j sats in range i
	Sigmas = [[[],[]],[[],[]],[[],[]]]

	# SigmaMeans[i][j] = mean of Sigmas[i][j]
	SigmaMeans = [[0,0],[0,0],[0,0]]

	# AvgVmax[i] = Avg Vmax of hosts in range i
	AvgVmax = []

	# AvgStellarMass[i] Avg StellarMass of sats in range i
	AvgStellarMass = []

	# TO-DO: For stellar mass ranges 1,2,3
	for i in range(1,4):

		# Fetch the raw sets
		cursor.execute("SELECT * FROM Range{Index}ObsRelVel".format(Index = i))
		RawSetObservational = cursor.fetchall()

		cursor.execute("SELECT * FROM Range{Index}SubFindRelVel".format(Index = i))
		RawSetSubFind = cursor.fetchall()

		# Fetch the groups
		cursor.execute("SELECT Groups.GroupID, Groups.GroupFirstSub, GroupNsubs FROM Groups INNER JOIN Range{Index} ON Groups.GroupID = Range{Index}.GroupID".format(Index = i))
		Groups = cursor.fetchall()

	
		# Take a sample of 1000 hosts
		indices = np.random.random_integers(0, len(Groups)-1, size = 1000)
		Groups = [Groups[k] for k in indices]
	

		# Loading bar setup -- not important
		barwidth = 50
		fraction = NO_OF_RESAMPLES/(barwidth-1)
		sys.stdout.write("\nRange {index}:\t[%s]".format(index = i)%(" "*barwidth))
		sys.stdout.flush()
		sys.stdout.write("\b"*(barwidth+1))

		# Perform resampling {NO_OF_RESAMPLES} number of times
		for j in range(NO_OF_RESAMPLES):
			
			if j%fraction == 0:
				sys.stdout.write("#")
				sys.stdout.flush()

			# Resample hosts
			indices = np.random.random_integers(0, len(Groups)-1, size = 1000)
			SampledGroups = [Groups[k][ID] for k in indices]

			# Get the delta Vx of assigned and observed satellites
			RelVelObs = [Sat[RELVELX] for Sat in RawSetObservational if Sat[GID] in SampledGroups and Sat[HALOMASS] > 10**9 ]
			RelVelSubFind = [Sat[RELVELX] for Sat in RawSetSubFind if Sat[GID] in SampledGroups and Sat[HALOMASS] > 10**9 ]

			# Calculate the Sigma (non clipped)
			Sigmas[i-1][OBS].append(np.std(RelVelObs))
			# Sigmas[i-1][SUBFIND].append(np.std(RelVelSubFind))
			
			# Sigma clip
			for k in range(3):
				# RelVelObs = [R for R in RelVelObs if not (R > 3*GetSigma(RelVelObs) or R < -3*GetSigma(RelVelObs))]
				RelVelSubFind = [R for R in RelVelSubFind if not (R > 3*GetSigma(RelVelSubFind) or R < -3*GetSigma(RelVelSubFind))]

			# Calculate the Sigma (clipped)
			# Sigmas[i-1][OBSCLIPPED].append(GetSigma(RelVelObs))
			Sigmas[i-1][SUBFIND].append(GetSigma(RelVelSubFind))
			

		# After this loop, Sigmas[i-1] is a 4x500 matrix, as we have 500 sigmas for each measure (obs, subfind, etc.)
		print "\n"

		for j in range(2):

			# Finding the uncertainties of the sigmas
			Uncertainties[i-1][j] = Uncertainty(Sigmas[i-1][j])

			# Finding the means of the Sigmas
			SigmaMeans[i-1][j] = np.mean(Sigmas[i-1][j])
	
		# Finding Vmax of the groups in this range
		GroupVmaxes = []

		# Loading bar setup -- not important
		barwidth = 50
		fraction = len(Groups)/(barwidth-1)
		sys.stdout.write("\nFinding biggest subhalo:\t[%s]".format(index = i)%(" "*barwidth))
		sys.stdout.flush()
		sys.stdout.write("\b"*(barwidth+1))

		# Finding AvgVmax and AveStellarMass
		for j in range(len(Groups)):
			if j%fraction == 0:
				sys.stdout.write("#")
				sys.stdout.flush()
			Group = Groups[j]
			Sats = [Subhalo for Subhalo in RawSetObservational+RawSetSubFind if Subhalo[GID] == Group[ID]]
			GroupVmaxes+=[Sat[VMAX] for Sat in Sats if Sat[STELLARMASS] == max([S[STELLARMASS] for S in Sats])]

		AvgVmax.append(np.mean(GroupVmaxes))
		AvgStellarMass.append(np.mean([Data[STELLARMASS] for Data in RawSetObservational+RawSetSubFind]))

	print "\n"

	Labels = ['Observational', 'SubFind']
	Colors = ['red', 'green']

	plot(X = AvgVmax, Y = SigmaMeans, Xerr = 0, Yerr = Uncertainties, title = "Uncertainty in $\Delta v_x$ as a function of average $V_{max}$ for different stellar mass ranges", xlabel = "Average Vmax of satellites (km/s)", ylabel = "$\sigma_{\Delta{v_x, best}}$ (km/s)", filename = "Uncertainty_Vmax.png", labels = Labels, colors = Colors )

	plot(X = AvgStellarMass, Y = SigmaMeans, Xerr = 0, Yerr = Uncertainties, title = "Uncertainty in $\Delta v_x$ as a function of average stellar mass for different stellar mass ranges", xlabel = "Average stellar mass of satellites ($M_\odot$)", ylabel = "$\sigma_{\Delta{v_x, best}}$ (km/s)", filename = "Uncertainty_Mass.png", labels = Labels, colors = Colors)

