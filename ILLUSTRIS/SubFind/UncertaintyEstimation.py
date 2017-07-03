import sqlite3
import sys
import random
import numpy as np
np.seterr(divide = 'ignore', invalid = 'ignore')

# Connect to the database
cursor = sqlite3.connect('../ILLUSTRIS.db').cursor()

# Fields
ID = 0
RELVELX = 1
STELLARMASS = 2
VMAX = 3

Uncertainties = []
AvgVmax = []
AvgStellarMass = []

# Creating the error bar. Should have 4 points, one for each range
def plot(X, Y, Xerr, Yerr, title, xlabel, ylabel, filename):
	import matplotlib.pyplot as plt
	plt.figure()
	plt.errorbar(X, Y , xerr = Xerr , yerr = Yerr)
	for i in range(1,5):
		plt.annotate("Range {Index}".format(Index = i), xy = (X[i-1], Y[i-1]), xytext =(X[i-1], Y[i-1]))
	plt.title(title)
	plt.xlabel(xlabel)
	plt.ylabel(ylabel)
	#plt.savefig(filename)
	plt.show()
	plt.close()	

for i in range(1,5):
	cursor.execute("SELECT * FROM Range{Index}RelVel".format(Index = i))
	RawSet = cursor.fetchall()
	Sigmas = []
	
	# Loading bar setup -- not important
	barwidth = 50
	fraction = 1000/(barwidth-1)
	sys.stdout.write("\nRange {index}:\t[%s]".format(index = i)%(" "*barwidth))
	sys.stdout.flush()
	sys.stdout.write("\b"*(barwidth+1))

	for j in range(1000):
		if j%fraction == 0:
			sys.stdout.write("#")
			sys.stdout.flush()

		# Get random satellites
		indices = np.random.random_integers(0, len(RawSet)-1, size = len(RawSet))
		RelVel = [RawSet[k][RELVELX] for k in indices]

		# Find the mean of their relative velocities
		Mean = np.mean(RelVel)
	
		# Find sum(delta(Vx,i) - mean(delta(Vx)))^2
		Sigma = 0
		for vxi in RelVel:
			Sigma += (vxi - Mean)**2

		# Find sigma(delta vx)
		Sigma = Sigma/(len(RawSet)**2)

		# Add it to the list of sigmas
		Sigmas.append(Sigma)

	Uncertainty = 0
	
	# Find the best estimate
	BestEstimate = np.mean(Sigmas)

	# Find the uncertainty in the estimate
	for Sigma in Sigmas:
		Uncertainty += (Sigma - BestEstimate)**2
	Uncertainty = Uncertainty/1000

	# Create lists for plotting
	Uncertainties.append(Uncertainty)
	AvgVmax.append(np.mean([Data[VMAX] for Data in RawSet]))
	AvgStellarMass.append(np.mean([Data[STELLARMASS] for Data in RawSet]))

print "\n"

plot(X = AvgVmax, Y = Uncertainties, Xerr = 0.5, Yerr = 1.e-6, title = "Uncertainty in $\Delta v_x$ as a function of average $V_{max}$ for different stellar mass ranges", xlabel = "Average Vmax of satellites (km/s)", ylabel = "Uncertainty on $\sigma_{\Delta{v_x, best}}$ (km/s)", filename = "Uncertainty_Vmax.png")

plot(X = AvgStellarMass, Y = Uncertainties, Xerr = 10**5, Yerr = 1.e-6, title = "Uncertainty in $\Delta v_x$ as a function of average stellar mass for different stellar mass ranges", xlabel = "Average stellar mass of satellites ($M_\odot$)", ylabel = "Uncertainty on $\sigma_{\Delta{v_x, best}}$ (km/s)", filename = "Uncertainty_Mass.png")
