# -----------------------------------IMPORTS--------------------------------------
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

# -----------------------------------CLASS DEFINITIONS --------------------------------------

# A class for 3D values such as position and velocity
class ThreeDVector(object):
	def __init__(self, X, Y, Z):
		self.X = X
		self.Y = Y
		self.Z = Z
# A class for galaxies!
class Galaxy(object):
	def __init__ (self, halo, dataValues):
		self.ID = int(dataValues[0])
		self.Position = ThreeDVector(dataValues[1], dataValues[2], dataValues[3])
		self.Velocity = ThreeDVector(dataValues[4], dataValues[5], dataValues[6])
		self.Vmax = dataValues[7]
		self.Vpeak = dataValues[8]		
		self.Mvir = dataValues[9]
		self.Mpeak = dataValues[10]
		self.Rvir = dataValues[11]
		self.Rmax = dataValues[12]
		self.apeak = dataValues[13]
		self.Mstar_pref = dataValues[14]
		self.Mstar_B2013 = dataValues[15]
		self.npart = int(dataValues[16])
		self.PID = int(dataValues[17])
		self.UpID = int(dataValues[18])
		self.AssignedSatellites = []
		self.ObservedSatellites = []
		self.Halo = halo

# And a class for halos!
class Halo(object):
	def __init__(self, name):
		self.name = name
		self.Galaxies = []
		halo_info = read_catalog(name)
		for galaxy_info in halo_info:
			galaxy = Galaxy(self, galaxy_info)
			self.Galaxies.append(galaxy)
	def count():
		return len(self.Galaxies)

#----------------------------CONSTANTS-------------------------------------------------------

#For the first pass, I am only looking at the isolated halos.  There's no reason we can't do the same kind of analysis for the other data sets.
singleList = ['iBurr', 'iCharybdis', 'iCher', 'iDouglas', 'iHall', 'iHamilton', 'iHera', 'iKauket', 'iLincoln', 'iLouise', 'iOates', 'iOrion', 'iRemus', 'iRomulus', 'iRoy', 'iScylla', 'iSerana', 'iSiegfried', 'iSonny', 'iTaurus', 'iThelma', 'iVenus', 'iZeus'] 
pairedList = ['Kauket&Kek','Lincoln&Douglas','Romulus&Remus', 'Siegfried&Roy', 'Taurus&Orion','Thelma&Louise','Venus&Serana','Zeus&Hera']
#Sets the range of stellar mass to use, to identify host galaxies.  In this case, we are looking at 10^7 solar masses in stars to 3 x 10^7 solar masses.  These should really be input variables, or be used as variables once the code below is turned into a function.  But for now, I just define them here.  I am using the default relation between stellar and halo mass (Column 15, which is labeled 14 below because python uses zero offset arrays)

mstarmin_values = [1.e7, 1.e8, 1.e9]
mstarmax_values = [3.e7, 3.e8, 3.e9]


# Gravitational constant in km^2 kpc Msun^-1 s^-2
G = 4.301e-6 

NO_OF_RESAMPLES = 1000

SINGLE_OBS = 0
SINGLE_SF = 1
PAIRED_OBS = 2
PAIRED_SF = 3

# Creating the error bar. Should have 4 points, one for each range
def plot(X, Y, Xerr, Yerr, title, xlabel, ylabel, filename, labels, colors):
	import matplotlib.pyplot as plt
	plt.figure()

	# For each measure
	for i in range(4):
		plt.errorbar(X, [Y[0][i], Y[1][i], Y[2][i]], color = colors[i], label = labels[i], xerr = Xerr, yerr = [Yerr[0][i], Yerr[1][i], Yerr[2][i]])
		# TO-DO: Annotation?
	plt.xlabel(xlabel, fontsize = 18)
	plt.ylabel(ylabel, fontsize = 18)
	plt.legend(prop = {'size':10}, loc = 0)
	plt.title(title, fontsize = 24)
	#plt.savefig(filename)
	plt.show()
	plt.close()

#-------------------------------------DISTANCE B/W GALAXIES----------------------------------
""" Returns the 2D distance (in Kpc) between two galaxies """
def distance_2D(galaxy1, galaxy2):
	return 1000*math.sqrt(math.pow(galaxy1.Position.Y-galaxy2.Position.Y, 2)+math.pow(galaxy1.Position.Z-galaxy2.Position.Z, 2))

# -----------------------------------READ_CATALOG--------------------------------------
""" Reads a redshift catalog and returns a list of values for each galaxy """
def read_catalog(name):
	lines = []
	# Try opening the file
	try:
		catalog = open("ELVIS_Halo_Catalogs/"+name+".txt", "r")
		# Try reading a line
		try:
			lines = catalog.readlines()
		except Exception:
			print "Error reading file!"
		catalog.close()
	except Exception:
		print "Error opening file!"
		

	# Getting rid of the first three lines (comments)
	for i in range(3):
		lines.pop(0)
	# At this point, the list "dataList" consists of only numeric strings
	# {halo} is simply a list of data values for each galaxy
	halo = []
	for line in lines:
		galaxy_info = line.split()
		i = 0
		for i in range(len(galaxy_info)):	
			galaxy_info[i] = float(galaxy_info[i])
		halo.append(galaxy_info)
	return halo
# -----------------------------------CREATE HALOS--------------------------------------
""" This method creates a list of halos, each halo containing a list of galaxies that belong to it """
def create_halos(name_list):
	halos = []
	for name in name_list:
		halo = Halo(name)
		halos.append(halo)
	return halos



# -----------------------------------FINDING GALAXIES IN RANGE--------------------------------------
""" This method searches all the single galaxies and returns the the ones with mstar < {mstarmax} and mstar > {mstarmin} as a list """
def find_hosts_in_range(halos, rangeno):
	galaxies_in_range = []
	for halo in halos:
		for galaxy in halo.Galaxies:
			if (galaxy.PID == -1):
				if galaxy.Mstar_pref > mstarmin_values[rangeno-1] and galaxy.Mstar_pref < mstarmax_values[rangeno-1]:
					galaxies_in_range.append(galaxy)
	return galaxies_in_range

# -----------------------------------FIND SATELLITES--------------------------------------
""" Finds the satellites of the galaxies in {galaxies_in_range} inserts them to their satellite field """
def find_assigned_satellites(galaxies_in_range):

	for host in galaxies_in_range:
		for satellite in host.Halo.Galaxies:
			if satellite.PID == host.ID or satellite.UpID == host.ID:
				host.AssignedSatellites.append(satellite)

def find_observed_satellites(galaxies_in_range):
	for host in galaxies_in_range:
		for satellite in host.Halo.Galaxies:
			if distance_2D(host, satellite) < host.Rvir:
				if satellite.Mstar_pref < host.Mstar_pref:
					Vvir = ((G * host.Mvir)/(host.Rvir))**(0.5)
					if numpy.absolute(host.Velocity.X - satellite.Velocity.X) < 3*Vvir:
						host.ObservedSatellites.append(satellite)

# -----------------------------------SATELLITE VELOCITY--------------------------------------
def relvelx(galaxies_in_range, option):
	velocities = []
	for host in galaxies_in_range:
		if option == "o":
			for satellite in host.ObservedSatellites:
				velocities.append(satellite.Velocity.X - host.Velocity.X)
		elif option == "s":
			for satellite in host.AssignedSatellites:
				velocities.append(satellite.Velocity.X - host.Velocity.X)
	return velocities

# Finding the uncertainty in a list of std. deviations {Sigmas}
def Uncertainty(Sigmas):
	Uncertainty = 0
	BestEstimate = np.mean(Sigmas)
	for Sigma in Sigmas:
		Uncertainty += (Sigma - BestEstimate)**2
	return (Uncertainty/NO_OF_RESAMPLES)**0.5
#-------------------------------------MAIN----------------------------------------------------------

SingleHalos = create_halos(singleList)
PairedHalos = create_halos(pairedList)

Uncertainties = [[0,0,0,0],[0,0,0,0],[0,0,0,0]]
SigmaMeans = [[0,0,0,0],[0,0,0,0],[0,0,0,0]]

AvgStellarMass = []
AvgVmax = []


# Sigmas[i][j] = a 1000 std. deviations of range i satellites in measure j
Sigmas = [[[],[],[],[]],[[],[],[],[]],[[],[],[],[]]]

for i in range(1,4):

	
	SingleHosts = find_hosts_in_range(SingleHalos, i)
	PairedHosts = find_hosts_in_range(PairedHalos, i)

	AvgStellarMass.append(np.mean([host.Mstar_pref for host in SingleHosts+PairedHosts]))
	AvgVmax.append(np.mean([host.Vmax for host in SingleHosts+PairedHosts]))

	find_assigned_satellites(SingleHosts)
	find_observed_satellites(SingleHosts)

	find_assigned_satellites(PairedHosts)
	find_observed_satellites(PairedHosts)

	# Take a sample of 1000 hosts
	indices = np.random.random_integers(0, len(SingleHosts)-1, size = 1000)
	SingleHosts = [SingleHosts[k] for k in indices]
	
	# Take a sample of 1000 hosts
	indices = np.random.random_integers(0, len(PairedHosts)-1, size = 1000)
	PairedHosts = [PairedHosts[k] for k in indices]

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

		# Resample
		indices = np.random.random_integers(0, len(SingleHosts)-1, size = 1000)
		SampleSingleHosts = [SingleHosts[k] for k in indices]

		indices = np.random.random_integers(0, len(PairedHosts)-1, size = 1000)
		SamplePairedHosts = [PairedHosts[k] for k in indices]

		# Get the delta Vx of assigned and observed satellites
		# TO-DO: Add a constraint on the halo mass?
		SingleRelVelObs = relvelx(SampleSingleHosts, "o")
		PairedRelVelObs = relvelx(SamplePairedHosts, "o")

		SingleRelVelSF = relvelx(SampleSingleHosts, "s")
		PairedRelVelSF = relvelx(SamplePairedHosts, "s")

		# Calculate the Sigma (non clipped)
		Sigmas[i-1][SINGLE_OBS].append(np.std(SingleRelVelObs))
		Sigmas[i-1][PAIRED_OBS].append(np.std(PairedRelVelObs))
		Sigmas[i-1][SINGLE_SF].append(np.std(SingleRelVelSF))
		Sigmas[i-1][PAIRED_SF].append(np.std(PairedRelVelSF))

	for j in range(4):

		# Finding the uncertainties of the sigmas
		Uncertainties[i-1][j] = Uncertainty(Sigmas[i-1][j])

		# Finding the means of the Sigmas
		SigmaMeans[i-1][j] = np.mean(Sigmas[i-1][j])

for i in range(3):
	print "\nRANGE {ind}".format(ind = i+1)
	for j in range(4):
		print "Uncertainty: " + `Uncertainties[i][j]` + " Sigma: " + `SigmaMeans[i][j]`

	Labels = ['Single halos with observed satellites', 'Single halos with assigned satellites', 'Paired halos with observed satellites', 'Paired halos with assigned satellites']
	Colors = ['red', 'green', 'blue', 'black']

plot(X = AvgVmax, Y = SigmaMeans, Xerr = 0, Yerr = Uncertainties, title = "$\Delta v_x$ distribution as a function of average $V_{max}$", xlabel = "Average Vmax of satellites (km/s)", ylabel = "$\sigma_{\Delta{v_x, best}}$ (km/s)", filename = "Uncertainty_Vmax.png", labels = Labels, colors = Colors )

plot(X = AvgStellarMass, Y = SigmaMeans, Xerr = 0, Yerr = Uncertainties, title = "$\Delta v_x$ distribution as a function of average stellar mass for different stellar mass ranges", xlabel = "Average stellar mass of satellites ($M_\odot$)", ylabel = "$\sigma_{\Delta{v_x, best}}$ (km/s)", filename = "Uncertainty_Mass.png", labels = Labels, colors = Colors)

