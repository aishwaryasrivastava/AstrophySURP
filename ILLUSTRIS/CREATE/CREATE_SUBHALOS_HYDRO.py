#--------------------------------IMPORTS-------------------------------#
import numpy as np
import illustris_python as il
np.seterr(divide = 'ignore', invalid = 'ignore')
import sqlite3
import sys
#--------------------------CONSTANTS-----------------------------------#
# Multiply the mass in Illustris catalog with this to get mass in Msun
mass_constant = 1.e10/0.704

# Given halo mass in Msun, returns stellar mass in Msun
def StellarMass(M):
	N10 = 		0.0351+0.0058		# N10 + sigmaN10
	gamma10 = 	0.608+0.059		# gamma10 + sigma(gamma10)
	beta10 = 	1.376+0.153		# beta10 + sigma(beta10)
	M10 = 		10**(11.590+0.236)	# 10^(M10 + sigmaM10) 
	return (2*M*N10*(((M/M10)**(-beta10))+((M/M10)**gamma10))**(-1))

#------------------SETTING UP THE DATABASE CONNECTION------------------#

conn = sqlite3.connect('../ILLUSTRIS-HYDRO.db')
c = conn.cursor()

#------------------------------READING THE CATALOG--------------------#

# Setup the HDF5 file
basePath = './Illustris-1/'
snapNum = 135

print "Reading catalog..."

CATALOG 	= il.groupcat.load(basePath, snapNum)
SUBHALOS 	= CATALOG['subhalos']
#------------------------------SUBHALOS-------------------------------#


c.execute("CREATE TABLE Subhalos (SubhaloID int PRIMARY KEY, SubhaloBHMdot float, SubhaloVmax float, SubhaloWindMass float, SubhaloGasMetallicityMaxRad float, SubhaloVelDisp float, SubhaloSFR float, SubhaloStarMetallicityMaxRad float, SubhaloLen, SubhaloSFRinHaldRad float, SubhaloGasMetallicity float, SubhaloBHMass float, SubhaloIDMostbound, SubhaloStellarPhotometricsMassInRad float, SubhaloHalfmassRad float, SubhaloParent int, SubhaloStarMetallicityHalfRad float, SubhaloGasMetallicitySfrWeighted float, SubhaloGasMetallicityHalfRad float, SubhaloMassInRad float, SubhaloGrNr int, SubhaloMassInHalfRad float, SubhaloSFRinRad float, SubhaloMassInMaxRad float, SubhaloStarMetallicity float)")

c.execute("CREATE TABLE SubhaloPos (SubhaloID int PRIMARY KEY, X float, Y float, Z float, FOREIGN KEY(SubhaloID) REFERENCES Subhalos(SubhaloID))")

c.execute("CREATE TABLE SubhaloStellarPhotometrics (SubhaloID int PRIMARY KEY, U float, B float, V float, K float, g float, r float, i float, z float, FOREIGN KEY(SubhaloID) REFERENCES Subhalos(SubhaloID))")

c.execute("CREATE TABLE SubhaloMassType (SubhaloID int PRIMARY KEY, Type1 float, Type2 float, Type3 float, Type4 float, Type5 float, Type6 float, FOREIGN KEY(SubhaloID) REFERENCES Subhalos(SubhaloID))")

c.execute("CREATE TABLE SubhaloSpin (SubhaloID int PRIMARY KEY, X float, Y float, Z float, FOREIGN KEY(SubhaloID) REFERENCES Subhalos(SubhaloID))")

c.execute("CREATE TABLE SubhaloVel (SubhaloID int PRIMARY KEY, X float, Y float, Z float, FOREIGN KEY(SubhaloID) REFERENCES Subhalos(SubhaloID))")

c.execute("CREATE TABLE SubhaloLenType (SubhaloID int PRIMARY KEY, Type1 int, Type2 int, Type3 int, Type4 int, Type5 int, Type6 int, FOREIGN KEY(SubhaloID) REFERENCES Subhalos(SubhaloID))")

c.execute("CREATE TABLE SubhaloHalfmassRadType (SubhaloID int PRIMARY KEY, Type1 float, Type2 float, Type3 float, Type4 float, Type5 float, Type6 float, FOREIGN KEY(SubhaloID) REFERENCES Subhalos(SubhaloID))")

c.execute("CREATE TABLE SubhaloMassInMaxRadType (SubhaloID int PRIMARY KEY, Type1 float, Type2 float, Type3 float, Type4 float, Type5 float, Type6 float, FOREIGN KEY(SubhaloID) REFERENCES Subhalos(SubhaloID))")

c.execute("CREATE TABLE SubhaloCM (SubhaloID int, X float, Y float, Z float, FOREIGN KEY(SubhaloID) REFERENCES Subhalos(SubhaloID))")

fraction = 100000
barwidth = (SUBHALOS['count']/fraction)+1
sys.stdout.write("Creating subhalos...[%s]"%(" " * barwidth))
sys.stdout.flush()
sys.stdout.write("\b" * (barwidth+1))
for i in range(0, SUBHALOS['count']):
	SubhaloID = i
	if i % fraction == 0:
		sys.stdout.write("#")
		sys.stdout.flush()

	SubhaloParams = (SubhaloID, float(SUBHALOS['SubhaloBHMdot'][i]), float(SUBHALOS['SubhaloVmax'][i]), float(SUBHALOS['SubhaloWindMass'][i]), float(SUBHALOS['SubhaloGasMetallicityMaxRad'][i]), float(SUBHALOS['SubhaloVelDisp'][i]), float(SUBHALOS['SubhaloSFR'][i]), float(SUBHALOS['SubhaloStarMetallicityMaxRad'][i]), str(SUBHALOS['SubhaloLen'][i]), float(SUBHALOS['SubhaloSFRinHalfRad'][i]), float(SUBHALOS['SubhaloGasMetallicity'][i]), float(SUBHALOS['SubhaloBHMass'][i]), str(SUBHALOS['SubhaloIDMostbound'][i]), float(SUBHALOS['SubhaloStellarPhotometricsMassInRad'][i]), float(SUBHALOS['SubhaloHalfmassRad'][i]), long(SUBHALOS['SubhaloParent'][i]), float(SUBHALOS['SubhaloStarMetallicityHalfRad'][i]), float(SUBHALOS['SubhaloGasMetallicitySfrWeighted'][i]), float(SUBHALOS['SubhaloGasMetallicityHalfRad'][i]), float(SUBHALOS['SubhaloMassInRad'][i]), long(SUBHALOS['SubhaloGrNr'][i]), float(SUBHALOS['SubhaloMassInHalfRad'][i]), float(SUBHALOS['SubhaloSFRinRad'][i]), float(SUBHALOS['SubhaloMassInMaxRad'][i]), float(SUBHALOS['SubhaloMassInMaxRad'][i])
)
	c.execute("INSERT INTO Subhalos VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", SubhaloParams)

	SubhaloPosParams = (SubhaloID, float(SUBHALOS['SubhaloPos'][i][0]), float(SUBHALOS['SubhaloPos'][i][1]), float(SUBHALOS['SubhaloPos'][i][2]))
	c.execute("INSERT INTO SubhaloPos VALUES (?, ?, ?, ?)", SubhaloPosParams)

	SubhaloStellarPhotometricsParams = (SubhaloID, float(SUBHALOS['SubhaloStellarPhotometrics'][i][0]), float(SUBHALOS['SubhaloStellarPhotometrics'][i][1]),float(SUBHALOS['SubhaloStellarPhotometrics'][i][2]),float(SUBHALOS['SubhaloStellarPhotometrics'][i][3]),float(SUBHALOS['SubhaloStellarPhotometrics'][i][4]),float(SUBHALOS['SubhaloStellarPhotometrics'][i][5]),float(SUBHALOS['SubhaloStellarPhotometrics'][i][6]),float(SUBHALOS['SubhaloStellarPhotometrics'][i][7]))
	c.execute("INSERT INTO SubhaloStellarPhotometrics VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", SubhaloStellarPhotometricsParams)

	SubhaloMassTypeParams = (SubhaloID, float(SUBHALOS['SubhaloMassType'][i][0]*mass_constant), float(SUBHALOS['SubhaloMassType'][i][1]*mass_constant), float(SUBHALOS['SubhaloMassType'][i][2]*mass_constant), float(SUBHALOS['SubhaloMassType'][i][3]*mass_constant), float(SUBHALOS['SubhaloMassType'][i][4]*mass_constant), float(SUBHALOS['SubhaloMassType'][i][5]*mass_constant))
	c.execute("INSERT INTO SubhaloMassType VALUES (?, ?, ?, ?, ?, ?, ?)", SubhaloMassTypeParams)

	SubhaloSpinParams = (SubhaloID, float(SUBHALOS['SubhaloSpin'][i][0]), float(SUBHALOS['SubhaloSpin'][i][1]), float(SUBHALOS['SubhaloSpin'][i][2]))
	c.execute("INSERT INTO SubhaloSpin VALUES (?, ?, ?, ?)", SubhaloSpinParams)

	SubhaloVelParams = (SubhaloID, float(SUBHALOS['SubhaloVel'][i][0]), float(SUBHALOS['SubhaloVel'][i][1]), float(SUBHALOS['SubhaloVel'][i][2]))
	c.execute("INSERT INTO SubhaloVel VALUES (?, ?, ?, ?)", SubhaloVelParams)

	SubhaloLenTypeParams = (SubhaloID, int(SUBHALOS['SubhaloLenType'][i][0]), int(SUBHALOS['SubhaloLenType'][i][1]), int(SUBHALOS['SubhaloLenType'][i][2]), int(SUBHALOS['SubhaloLenType'][i][3]), int(SUBHALOS['SubhaloLenType'][i][4]), int(SUBHALOS['SubhaloLenType'][i][5]))
	c.execute("INSERT INTO SubhaloLenType VALUES (?, ?, ?, ?, ?, ?, ?)", SubhaloLenTypeParams)
	SubhaloHalfmassRadTypeParams = (SubhaloID, float(SUBHALOS['SubhaloHalfmassRadType'][i][0]), float(SUBHALOS['SubhaloHalfmassRadType'][i][1]), float(SUBHALOS['SubhaloHalfmassRadType'][i][2]), float(SUBHALOS['SubhaloHalfmassRadType'][i][3]), float(SUBHALOS['SubhaloHalfmassRadType'][i][4]), float(SUBHALOS['SubhaloHalfmassRadType'][i][5]))
	c.execute("INSERT INTO SubhaloHalfmassRadType VALUES (?, ?, ?, ?, ?, ?, ?)", SubhaloHalfmassRadTypeParams)

	SubhaloMassInMaxRadTypeParams = (SubhaloID, float(SUBHALOS['SubhaloMassInMaxRadType'][i][0]*mass_constant), float(SUBHALOS['SubhaloMassInMaxRadType'][i][1]*mass_constant), float(SUBHALOS['SubhaloMassInMaxRadType'][i][2]*mass_constant), float(SUBHALOS['SubhaloMassInMaxRadType'][i][3]*mass_constant), float(SUBHALOS['SubhaloMassInMaxRadType'][i][4]*mass_constant), float(SUBHALOS['SubhaloMassInMaxRadType'][i][5]*mass_constant))
	c.execute("INSERT INTO SubhaloMassInMaxRadType VALUES (?, ?, ?, ?, ?, ?, ?)", SubhaloMassInMaxRadTypeParams)

	SubhaloCMParams = (SubhaloID, float(SUBHALOS['SubhaloCM'][i][0]),float(SUBHALOS['SubhaloCM'][i][1]),float(SUBHALOS['SubhaloCM'][i][2]))
	c.execute("INSERT INTO SubhaloCM VALUES(?, ?, ?, ?)", SubhaloCMParams)


	


	

	
print "\n"

conn.commit()
conn.close()
