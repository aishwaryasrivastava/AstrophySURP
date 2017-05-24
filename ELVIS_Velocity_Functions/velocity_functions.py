""" Doing a couple of tests with the isolated halos in ELVIS
 "" Identifying interesting velocity functions.
 ''
 "" From Shea's documentation:
 "" 1: ID of halo
 "" 2-4: XYZ in Mpc
 "" 5-7:VxVyVz in km/s
 "" 8: Vmax at z=0 in km/s
 "" 9: Vpeak
 "" 10: Virial/bound mass at z=0 in Msun
 "" 11: Mpeak
 "" 12: Rvir in kpc
 "" 13: Rmax in kpc
 "" 14: apeak
 "" 15: Mstar for G-K abundance matching, Msun
 "" 16: Mstar for Behroozi abundance matching, Msun
 "" 17: number of particles in the halo
 "" 18: parent ID (-1 for centrals)
 "" 19: ID of topmost halo in hierarchy for non-centrals
 ""
""  Annika Peter, 4/20/17
"""

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
		self.Satellites = []
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


# -----------------------------------CONSTANTS--------------------------------------

# Sets a threshold for vpeak.  The catalog is mostly complete above this value.
vpeak = 12. 

# Newton's constant G in km^2 kpc/Msun*s^2 units
G = 6.67e-11 * (1.e-3)**2. * (2.e30)/(3.086e19) 

#For the first pass, I am only looking at the isolated halos.  There's no reason we can't do the same kind of analysis for the other data sets.
singleList = ['iBurr', 'iCharybdis', 'iCher', 'iDouglas', 'iHall', 'iHamilton', 'iHera', 'iKauket', 'iLincoln', 'iLouise', 'iOates', 'iOrion', 'iRemus', 'iRomulus', 'iRoy', 'iScylla', 'iSerana', 'iSiegfried', 'iSonny', 'iTaurus', 'iThelma', 'iVenus', 'iZeus'] 
pairedList = ['Kauket&Kek','Lincoln&Douglas','Romulus&Remus', 'Siegfried&Roy', 'Taurus&Orion','Thelma&Louise','Venus&Serana','Zeus&Hera']
#Sets the range of stellar mass to use, to identify host galaxies.  In this case, we are looking at 10^7 solar masses in stars to 3 x 10^7 solar masses.  These should really be input variables, or be used as variables once the code below is turned into a function.  But for now, I just define them here.  I am using the default relation between stellar and halo mass (Column 15, which is labeled 14 below because python uses zero offset arrays)

mstarmin_values = [1.e7, 1.e8, 1.e9]
mstarmax_values = [3.e7, 3.e8, 3.e9]



# -----------------------------------READ_CATALOG--------------------------------------
""" Reads a redshift catalog and returns a list of values for each galaxy """
def read_catalog(name):
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

# -----------------------------------VELOCITY FUNCTION--------------------------------------
""" This function creates the velocity function of 2 hosts belonging to {galaxies_in_range} belonging to range {rangeindex} """
def velocity_function(galaxies_in_range, rangeindex, stacked):
	filename = ""
	title = ""
	random_hosts = []
	velocities = []
	i = 0
	# Finding two random, distinct hosts in {galaxies_in_range}
	for i in range(2):
		host = random.choice(galaxies_in_range)
		# If already picked this host, then pick another
		while host in random_hosts:
			host = random.choice(galaxies_in_range)
		random_hosts.append(host)
		velocities.append(satellite_velocities(host))
	n_bins = 20
	mu = mean(velocities[0]+velocities[1])
	sigma = std(velocities[0]+velocities[1])
	fig, ax = plt.subplots()
	labels = []
	for i in range(0,2):
		labels.append("{HaloName} (#{HostID}): $\mu =$ {mean}; $\sigma =$ {sigma}".format(HaloName = random_hosts[i].Halo.name, HostID = random_hosts[i].ID, mean = '%.3f'%mean(velocities[i]), sigma = '%.3f'%std(velocities[i])))
		
	n, bins, patches = ax.hist(velocities, n_bins, normed = 1, histtype = 'bar', label = labels)
	y = mlab.normpdf(bins, mu, sigma)
	ax.plot(bins, y, '--')
	ax.set_xlabel('Vx (km/s) of satellites')
	ax.set_ylabel('Probability')
	ax.legend(prop = {'size': 10})
	plt.grid(True)
	fig.set_size_inches(10,10)

	if not stacked:
		filename = "Range{i1}/range{i2}_velocity_function.png".format(i1 = rangeindex, i2 = rangeindex)
		title = "Velocity function of hosts in range {index} ({mstarminvalue} Msun to {mstarmaxvalue} Msun)".format(index = "1, 2, and 3", mstarminvalue = mstarmin_values[rangeindex-1], mstarmaxvalue = mstarmax_values[rangeindex-1])
	else:
		filename = "stacked_velocity_function.png"
		title = "Velocity function of hosts in ranges 1, 2 and 3"

	ax.set_title(title)
	plt.savefig(filename)
	plt.close()

# -----------------------------------VELOCITY FUNCTION BY RANGE-----------------------------
""" This function creates a comparison of the satellite velocities of the three different ranges """
def velocity_function_by_range(galaxies):
	# {velocities} is a list (size 3), each element is a list of satellite velocities of the respective range 
	velocities = []
	i = 0
	for i in range(3):
		velocities.append([])
		for host in galaxies[i]:
			velocities[i]+=(satellite_velocities(host))
	filename = "satellite_velocity_function_by_range.png"

	fig, ax = plt.subplots()
	n_bins = 20
	labels = []
	for i in range(0,3):
		labels.append("Range {index}: $\mu =$ {mean}; $\sigma =$ {std}".format(index = i+1, mean = '%.3f'% mean(velocities[i]), std = '%.3f'% std(velocities[i])))

	n, bins, patches = ax.hist(velocities, n_bins, normed = 1, histtype = 'stepfilled', stacked = True, label = labels)
	ax.set_xlabel('Vx (km/s) of satellites')
	ax.set_ylabel('Probability')
	ax.legend(prop = {'size': 10})
	ax.set_title('Velocity function of satellites in different stellar mass ranges')
	plt.grid(True)
	fig.set_size_inches(10,10)	
	plt.savefig(filename)
	plt.close()

# -----------------------------------SATELLITE VELOCITY--------------------------------------
def satellite_velocities(host):
	velocities = []
	for satellite in host.Satellites:
		velocities.append(satellite.Velocity.X - host.Velocity.X)
	return velocities
#-----------------------------------CREATE DIRECTORY----------------------------------------
def create_directory(dirname):
	if not os.path.exists(dirname):
    		os.makedirs(dirname)
	os.chdir(dirname)
	for i in range(1,4):
		if not os.path.exists("Range"+`i`):
			os.makedirs("Range"+`i`)

#-------------------------------------DISTANCE B/W GALAXIES----------------------------------
""" Returns the 2D distance (in Kpc) between two galaxies """
def distance_2D(galaxy1, galaxy2):
	return 1000*math.sqrt(math.pow(galaxy1.Position.Y-galaxy2.Position.Y, 2)+math.pow(galaxy1.Position.Z-galaxy2.Position.Z, 2))

#-------------------------------------DISTANCE B/W GALAXIES----------------------------------
""" Returns the 3D distance (in Kpc) between two galaxies """
def distance_3D(galaxy1, galaxy2):
	return 1000*math.sqrt(math.pow(galaxy1.Position.Y-galaxy2.Position.Y, 2)+math.pow(galaxy1.Position.Z-galaxy2.Position.Z, 2)+math.pow(galaxy1.Position.X-galaxy2.Position.X, 2))

# -----------------------------------FIND SATELLITES--------------------------------------
""" Finds the satellites of the galaxies in {galaxies_in_range} inserts them to their satellite field """
def find_satellites(galaxies_in_range, choice):
	if choice == 'A' or choice == 'a':
		for host in galaxies_in_range:
			for satellite in host.Halo.Galaxies:
				if satellite.PID == host.ID or satellite.UpID == host.ID:
					host.Satellites.append(satellite)

	elif choice == 'B' or choice == 'b':
		for host in galaxies_in_range:
			for satellite in host.Halo.Galaxies:
				if distance_2D(host, satellite) < host.Rvir:
					if satellite.Mstar_pref < host.Mstar_pref:
						if numpy.absolute(host.Velocity.X - satellite.Velocity.X) < 3*host.Vmax:
							host.Satellites.append(satellite)
	elif choice == 'C' or choice == 'c':
		for host in galaxies_in_range:
			for satellite in host.Halo.Galaxies:
				if (satellite.PID == host.ID or satellite.UpID == host.ID) and satellite.Vpeak > vpeak:
					host.Satellites.append(satellite)

	elif choice == 'D' or choice == 'd':
		for host in galaxies_in_range:
			for satellite in host.Halo.Galaxies:
				if distance_2D(host, satellite) < host.Rvir:
					if satellite.Mstar_pref < host.Mstar_pref:
						if numpy.absolute(host.Velocity.X - satellite.Velocity.X) < 3*host.Vmax:
							if satellite.Vpeak > vpeak:							
								host.Satellites.append(satellite)
				
 

# -----------------------------------WRITE SATELLITE DATA--------------------------------------
""" Creates a text file and writes satellite data for {galaxies_in_range} to it """
def get_satellite_data(galaxies_in_range, rangeindex):
	filename = "Range{i1}/range{i2}_satellite_info.txt".format(i1 = rangeindex, i2 = rangeindex)
	try:
		outputfile = open(filename, "w+")
		try:
			outputfile.write("#\n{:<10}\t{:<10}\t{:<10}\t{:<10}\t{:<10}\n#".format("# Halo", "Host ID", "#Satellites", "Mean Vx (km/s)", "Std. Deviation of Vx (km/s)"))
			for host in galaxies_in_range:
				mu = 0.0
				sigma = 0.0
				velocities = satellite_velocities(host)
				if len(velocities)>0:
					mu = mean(velocities)
					sigma = std(velocities)
					#todo - mean of sat velocities
				outputfile.write("\n{:<10}\t{:<10}\t{:<10}\t{:<10}\t{:<10}".format(host.Halo.name, host.ID, len(host.Satellites), mu, sigma))
					
		except Exception:
			print('Error writing to ' + filename)
	except Exception:
		print('Error opening/creating ' + filename)

# -----------------------------------CUT VELOCITY FUNCTION BY MASS--------------------------------------
""" Creates a velocity function of {galaxies} cut by mass (mstar > cutoffmass and mass < cutoffmass) """
def velocity_function_mstar_cut(galaxies, cutoffmass, rangeindex):
	filename = "Range{i1}/range{i2}_velocity_function_cut_by_mass.png".format(i1 = rangeindex, i2 = rangeindex)
	little = []
	big = []
	for host in galaxies:
		for satellite in host.Satellites:
			velocity = satellite.Velocity.X - host.Velocity.X
			if satellite.Mstar_pref < cutoffmass:
				little.append(velocity)
			else:
				big.append(velocity)
	
	fig, ax = plt.subplots()
	n_bins = 20
	n, bins, patches = ax.hist([little, big], n_bins, normed = 1, histtype = 'stepfilled', stacked = True, label = ["Mstar < {cutoff} Msun; $\mu =$ {littlemean}; $\sigma =$ {littlestd}".format(cutoff = '%.2e' % cutoffmass, littlemean = '%.3f'% mean(little), littlestd =  '%.3f'% std(little)), "Mstar > {cutoff} Msun; $\mu =$ {bigmean}; $\sigma =$ {bigstd}".format(cutoff = '%.2e' % cutoffmass, bigmean =  '%.3f'%mean(big), bigstd =  '%.3f'%std(big))])
	ax.set_xlabel('Vx (km/s) of satellites')
	ax.set_ylabel('Probability')
	ax.legend(prop = {'size': 10})
	ax.set_title("Range {galaxy_range}: Comparison of velocity functions of satellites of new and little hosts (cutoff = {cutoff} Msun)".format(galaxy_range = rangeindex, cutoff = '%.2e'%cutoffmass))
	plt.grid(True)
	fig.set_size_inches(10,10)		
	plt.savefig(filename)
	plt.close()



# -----------------------------------CUT VELOCITY FUNCTION BY PEAK SCALE FACTOR--------------------------------------
def velocity_function_apeak_cut(galaxies, cutoffapeak, rangeindex):
	filename = "Range{i1}/range{i2}_satellites_apeak_{cutoff}_cut.png".format(i1 = rangeindex, i2 = rangeindex, cutoff = cutoffapeak)
	old = []	
	new = []
	for host in galaxies:
		for sat in host.Satellites:
			velocity = sat.Velocity.X - host.Velocity.X
			if sat.apeak < cutoffapeak:
				old.append(velocity)
			else:
				new.append(velocity)

	fig, ax = plt.subplots()
	n_bins = 20

	n, bins, patches = ax.hist([new, old], n_bins, normed = 1, histtype = 'stepfilled', stacked = True, label = ["apeak < {cutoff}; $\mu =$ {newmean}; $\sigma =$ = {newstd}".format(cutoff = cutoffapeak, newmean = '%.3f'%mean(new), newstd = '%.3f'%std(new)), "apeak > {cutoff}; $\mu =$ = {oldmean}; $\sigma =$  {oldstd}".format(cutoff = cutoffapeak, oldmean = '%.3f'%mean(old), oldstd = '%.3f'%std(old))])

	ax.set_xlabel('Vx (km/s) of satellites')
	ax.set_ylabel('Probability')
	ax.legend(prop = {'size': 10})
	ax.set_title("Range {galaxy_range}: Comparison of velocity functions of satellites of new and old hosts (cutoff = {cutoff})".format(galaxy_range = rangeindex, cutoff = cutoffapeak))
	plt.grid(True)
	fig.set_size_inches(10,10)		
	plt.savefig(filename)
	plt.close()
# -----------------------------------DISTANCE PLOT OF SATELLITES --------------------------------------
def satellite_distance_plot(ranges):
	filename = "satellite_distance_plot.png"
	distances = [[],[],[]]
	for i in range(0,3):
			for host in ranges[i]:
				for sat in host.Satellites:
					if numpy.absolute(sat.Velocity.X - host.Velocity.X) > 100:
						distances[i].append(distance_3D(host, sat))
	fig, ax = plt.subplots()
	n_bins = 20
	labels = []
	for i in range(0,3):
		labels.append("Range {index}: $\mu =$ {mean}; $\sigma =$ {std}".format(index = i+1, mean = '%.3f'% mean(distances[i]), std = '%.3f'% std(distances[i])))	

	n, bins, patches = ax.hist(distances, n_bins, stacked = True, normed = 1, histtype = 'stepfilled', label = labels)
	ax.set_xlabel('3D distance from host')
	ax.set_ylabel('Probability')
	ax.legend(prop = {'size': 10})
	plt.grid(True)
	fig.set_size_inches(10,10)
	ax.set_title("Distance of satellites (Vx > 100 km/s) from their hosts")
	plt.savefig(filename)
	plt.close()
# -----------------------------------ASSIGNED Vs. NEAREST SATELLITES --------------------------------------
def compare_assigned_and_nearest(galaxies_in_range, rangeindex):
	filename = "Range{i1}/range{i2}_stray_satellites.txt".format(i1 = rangeindex, i2 = rangeindex)
	

	try:
		outputfile = open(filename, "w+")
		try:
			outputfile.write("#\n{:<10}\t{:<10}\t{:<10}\t{:<10}\n#".format("# Sat ID", "Host ID", "Sat PID", "Sat UpID"))
			for host in galaxies_in_range:
				for sat in host.Satellites:
					if not (sat.PID == host.ID) and not (sat.UpID == host.ID):
						outputfile.write("\n{:<10}\t{:<10}\t{:<10}\t{:<10}".format(sat.ID, host.ID, sat.PID, sat.UpID))
					
		except Exception:
			print('Error writing to ' + filename)
	except Exception:
		print('Error opening/creating ' + filename)
			
# -----------------------------------GENERATE DATA --------------------------------------
def generate_data(halos, satMethod):
	ranges = []
	for i in range(1,4):

		mstarmin = mstarmin_values[i-1]
		mstarmax = mstarmax_values[i-1]

		galaxies_in_range = find_hosts_in_range(halos, i)

		find_satellites(galaxies_in_range, satMethod)
		
		get_satellite_data(galaxies_in_range, i)

		velocity_function(galaxies_in_range, i, stacked = False)

		velocity_function_mstar_cut(galaxies_in_range, 1.e5, i)

		velocity_function_apeak_cut(galaxies_in_range, 0.5, i)
	
		ranges.append(galaxies_in_range)

		if satMethod == 'B' or satMethod == 'b' or satMethod == 'D' or satMethod == 'd':
			compare_assigned_and_nearest(galaxies_in_range,i)
	
	satellite_distance_plot(ranges)

	velocity_function(ranges[0]+ranges[1]+ranges[2], 0, stacked = True)

	velocity_function_by_range(ranges)
	
# -----------------------------------MAIN --------------------------------------
List = singleList+pairedList


continue_input = 'y'
while continue_input != 'n' and continue_input != 'N':
	if continue_input == 'Y' or continue_input == 'y':
		print "Creating halos..."
		halos = create_halos(List)
		print "How should I find the satellites?"
		# We can add more options as we continue!
		print "A/a: Through PID/UpID"
		print "B/b: Through distance"
		print "C/c: Through PID/UpID with Vpeak > 12 km/s"
		print "D/d: Through distance with Vpeak > 12 km/s"
		options = ['A','a','B','b','C','c','D','d']
		choice = raw_input("Enter a choice: ")
		while choice not in options:
			choice = raw_input("Invalid input! Try again: ")
		if choice == 'A' or choice == 'a':
			create_directory("AssignedSatellites")
			print "Generating data using assigned satellites..."
			generate_data(halos, choice)
		elif choice == 'B' or choice == 'b':
			create_directory("ClosestSatellites")
			print "Generating data using closest satellites..."
			generate_data(halos, choice)
		elif choice == 'C' or choice == 'c':
			create_directory("AssignedSatellites_HighVpeak")
			print "Generating data using assigned satellites with Vpeak > 12 km/s..."
			generate_data(halos, choice)
		elif choice == 'D' or choice == 'd':
			create_directory("ClosestSatellites_HighVpeak")
			print "Generating data using closest satellites with Vpeak > 12 km/s..."
			generate_data(halos, choice)

		os.chdir("..")
		print "\nDone! Saved all files."
		continue_input = raw_input("Run program again? (Y/N): ")
	else:
		continue_input = raw_input("Invalid input! Try again: ")

sys.exit()


