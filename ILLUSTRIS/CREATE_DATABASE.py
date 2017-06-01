#--------------------------------IMPORTS-------------------------------#
import numpy as np
import illustris_python as il
np.seterr(divide = 'ignore', invalid = 'ignore')
import sqlite3
import sys
#--------------------------CONSTANTS-----------------------------------#
# Multiply the mass in Illustris catalog with this to get mass in Msun
mass_constant = 0.704/1.e10

# Given halo mass in Msun, returns stellar mass in Msun
def StellarMass(M):
	N10 = 		0.0351+0.0058		# N10 + sigmaN10
	gamma10 = 	0.608+0.059		# gamma10 + sigma(gamma10)
	beta10 = 	1.376+0.153		# beta10 + sigma(beta10)
	M10 = 		10**(11.590+0.236)	# 10^(M10 + sigmaM10) 
	return (2*M*N10*(((M/M10)**(-beta10))+((M/M10)**gamma10))**(-1))

#------------------SETTING UP THE DATABASE CONNECTION------------------#

conn = sqlite3.connect('halos_and_subhalos.db')
c = conn.cursor()

#------------------------------READING THE CATALOG--------------------#

# Setup the HDF5 file
basePath = './Illustris-1/'
snapNum = 135

print "Reading catalog..."

CATALOG 	= il.groupcat.load(basePath, snapNum)
SUBHALOS 	= CATALOG['subhalos']
HALOS		= CATALOG['halos']
HEADER		= CATALOG['header']

#------------------------------HALOS------------------------------------#

c.execute("CREATE TABLE Groups (GroupId, GroupFirstSub, GroupLen, GroupMass, GroupNsubs, Group_M_Crit200, Group_M_Crit500, Group_M_Mean200, Group_M_TopHat200, Group_R_Crit200, Group_R_Crit500, Group_R_Mean200, Group_R_TopHat200, StellarMass)")
c.execute("CREATE TABLE GroupLenType(GroupID, Type1, Type2, Type3, Type4, Type5, Type6)")
c.execute("CREATE TABLE GroupMassType(GroupID, Type1, Type2, Type3, Type4, Type5, Type6)")
c.execute("CREATE TABLE GroupPos(GroupID, X, Y, Z)")
c.execute("CREATE TABLE GroupVel(GroupID, X, Y, Z)")

fraction = 100000
barwidth = (HALOS['count']/fraction)+1
sys.stdout.write("Creating halos...[%s]"%(" " * barwidth))
sys.stdout.flush()
sys.stdout.write("\b" * (barwidth+1))
for i in range(0, HALOS['count']):
	GroupID = i
	if i % fraction == 0:
		sys.stdout.write("#")
		sys.stdout.flush()

	GroupParams = (GroupID, HALOS['GroupFirstSub'][i], HALOS['GroupLen'][i], HALOS['GroupMass'][i]*mass_constant, HALOS['GroupNsubs'][i], HALOS['Group_M_Crit200'][i]*mass_constant, HALOS['Group_M_Crit500'][i]*mass_constant, HALOS['Group_M_Mean200'][i]*mass_constant, HALOS['Group_M_TopHat200'][i]*mass_constant, HALOS['Group_R_Crit200'][i], HALOS['Group_R_Crit500'][i], HALOS['Group_R_Mean200'][i], HALOS['Group_R_TopHat200'][i], StellarMass(HALOS['GroupMass'][i]*mass_constant))
	c.execute("INSERT INTO Halos VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", GroupParams)

	GroupLenParams = (GroupID, HALOS['GroupLenType'][i][0], HALOS['GroupLenType'][i][1], HALOS['GroupLenType'][i][2], HALOS['GroupLenType'][i][3], HALOS['GroupLenType'][i][4], HALOS['GroupLenType'][i][5])
	c.execute("INSERT INTO GroupLen VALUES(?, ?, ?, ?, ?, ?, ?)", GroupLenParams)

	GroupMassParams = (GroupID, HALOS['GroupMassType'][i][0]*mass_constant, HALOS['GroupMassType'][i][1]*mass_constant, HALOS['GroupMassType'][i][2]*mass_constant, HALOS['GroupMassType'][i][3]*mass_constant, HALOS['GroupMassType'][i][4]*mass_constant, HALOS['GroupMassType'][i][5]*mass_constant)
	c.execute("INSERT INTO GroupMassType VALUES(?, ?, ?, ?, ?, ?, ?)", GroupMassParams)

	GroupPosParams = (GroupID, HALOS['GroupPos'][i][0], HALOS['GroupPos'][i][1], HALOS['GroupPos'][i][2])
	c.execute("INSERT INTO GroupPos VALUES (?, ?, ?, ?)", GroupPosParams)

	GroupVelParams = (GroupID, HALOS['GroupVel'][i][0], HALOS['GroupVel'][i][1], HALOS['GroupVel'][i][2])
	c.execute("INSERT INTO GroupVel VALUES (?, ?, ?, ?)", GroupVelParams)
print("\n")

#------------------------------SUBHALOS-------------------------------#
c.execute("CREATE TABLE Subhalos (SubhaloID,SubhaloGrNr,SubhaloHalfmassRad,SubhaloIDMostbound,SubhaloLen,SubhaloMass, SubhaloMassInHalfRad,SubhaloMassInMaxRad,SubhaloMassInRad, SubhaloParent, SubhaloVelDisp, SubhaloVmax, SubhaloVmaxRad  )")
c.execute("CREATE TABLE SubhaloCM (SubhaloID, X, Y, Z)")
c.execute("CREATE TABLE SubhaloHalfmassRadType (SubhaloID, Type1, Type2, Type3, Type4, Type5, Type6)")
c.execute("CREATE TABLE SubhaloLenType (SubhaloID, Type1, Type2, Type3, Type4, Type5, Type6)")
c.execute("CREATE TABLE SubhaloMassInHalfRadType (SubhaloID, Type1, Type2, Type3, Type4, Type5, Type6)")
c.execute("CREATE TABLE SubhaloMassInMaxRadType (SubhaloID, Type1, Type2, Type3, Type4, Type5, Type6)")
c.execute("CREATE TABLE SubhaloMassInRadType (SubhaloID, Type1, Type2, Type3, Type4, Type5, Type6)")
c.execute("CREATE TABLE SubhaloMassType (SubhaloID, Type1, Type2, Type3, Type4, Type5, Type6)")
c.execute("CREATE TABLE SubhaloPos (SubhaloID, X, Y, Z)")
c.execute("CREATE TABLE SubhaloSpin (SubhaloID, X, Y, Z)")
c.execute("CREATE TABLE SubhaloVel (SubhaloID, X, Y, Z)")

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
	SubhaloParams = (SubhaloID, SUBHALOS['SubhaloGrNr'][i], SUBHALOS['SubhaloHalfmassRad'][i], SUBHALOS['SubhaloIDMostbound'][i], SUBHALOS['SubhaloLen'][i], SUBHALOS['SubhaloMass'][i]*mass_constant, SUBHALOS['SubhaloMassInHalfRad'][i]*mass_constant, SUBHALOS['SubhaloMassInMaxRad'][i]*mass_constant, SUBHALOS['SubhaloMassInRad'][i]*mass_constant, SUBHALOS['SubhaloParent'][i], SUBHALOS['SubhaloVelDisp'][i], SUBHALOS['SubhaloVmax'][i], SUBHALOS['SubhaloVmaxRad'][i])
	c.execute("INSERT INTO Subhalos VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", SubhaloParams)

	SubhaloCMParams = (SubhaloID, SUBHALOS['SubhaloCM'][i][0],SUBHALOS['SubhaloCM'][i][1],SUBHALOS['SubhaloCM'][i][2])
	c.execute("INSERT INTO Subhalos VALUES(?, ?, ?, ?)", SubhaloCMParams)
	
	SubhaloHalfMassRadTypeParams = (SubhaloID, SUBHALOS['SubhaloHalfMassRadType'][i][0], SUBHALOS['SubhaloHalfMassRadType'][i][1], SUBHALOS['SubhaloHalfMassRadType'][i][2], SUBHALOS['SubhaloHalfMassRadType'][i][3], SUBHALOS['SubhaloHalfMassRadType'][i][4], SUBHALOS['SubhaloHalfMassRadType'][i][5])
	c.execute("INSERT INTO SubhaloHalfMassRadType VALUES (?, ?, ?, ?, ?, ?, ?)", SubhaloHalfMassRadTypeParams)
	
	SubhaloLenTypeParams = (SubhaloID, SUBHALOS['SubhaloLenType'][i][0], SUBHALOS['SubhaloLenType'][i][1], SUBHALOS['SubhaloLenType'][i][2], SUBHALOS['SubhaloLenType'][i][3], SUBHALOS['SubhaloLenType'][i][4], SUBHALOS['SubhaloLenType'][i][5])
	c.execute("INSERT INTO SubhaloLenType VALUES (?, ?, ?, ?, ?, ?, ?)", SubhaloLenTypeParams)

	SubhaloMassInHalfRadTypeParams = (SubhaloID, SUBHALOS['SubhaloMassInHalfRadType'][i][0]*mass_constant, SUBHALOS['SubhaloMassInHalfRadType'][i][1]*mass_constant, SUBHALOS['SubhaloMassInHalfRadType'][i][2]*mass_constant, SUBHALOS['SubhaloMassInHalfRadType'][i][3]*mass_constant, SUBHALOS['SubhaloMassInHalfRadType'][i][4]*mass_constant, SUBHALOS['SubhaloMassInHalfRadType'][i][5]*mass_constant)
	c.execute("INSERT INTO SubhaloMassInHalfRadType VALUES (?, ?, ?, ?, ?, ?, ?)", SubhaloMassInHalfRadTypeParams)

	SubhaloMassInMaxRadTypeParams = (SubhaloID, SUBHALOS['SubhaloMassInMaxRadType'][i][0]*mass_constant, SUBHALOS['SubhaloMassInMaxRadType'][i][1]*mass_constant, SUBHALOS['SubhaloMassInMaxRadType'][i][2]*mass_constant, SUBHALOS['SubhaloMassInMaxRadType'][i][3]*mass_constant, SUBHALOS['SubhaloMassInMaxRadType'][i][4]*mass_constant, SUBHALOS['SubhaloMassInMaxRadType'][i][5]*mass_constant)
	c.execute("INSERT INTO SubhaloMassInMaxRadType VALUES (?, ?, ?, ?, ?, ?, ?)", SubhaloMassInMaxRadTypeParams)

	SubhaloMassInRadTypeParams = (SubhaloID, SUBHALOS['SubhaloMassInRadType'][i][0]*mass_constant, SUBHALOS['SubhaloMassInRadType'][i][1]*mass_constant, SUBHALOS['SubhaloMassInRadType'][i][2]*mass_constant, SUBHALOS['SubhaloMassInRadType'][i][3]*mass_constant, SUBHALOS['SubhaloMassInRadType'][i][4]*mass_constant, SUBHALOS['SubhaloMassInRadType'][i][5]*mass_constant)
	c.execute("INSERT INTO SubhaloMassInRadType VALUES (?, ?, ?, ?, ?, ?, ?)", SubhaloMassInRadTypeParams)

	SubhaloMassTypeParams = (SubhaloID, SUBHALOS['SubhaloMassType'][i][0]*mass_constant, SUBHALOS['SubhaloMassType'][i][1]*mass_constant, SUBHALOS['SubhaloMassType'][i][2]*mass_constant, SUBHALOS['SubhaloMassType'][i][3]*mass_constant, SUBHALOS['SubhaloMassType'][i][4]*mass_constant, SUBHALOS['SubhaloMassType'][i][5]*mass_constant)
	c.execute("INSERT INTO SubhaloMassType VALUES (?, ?, ?, ?, ?, ?, ?)", SubhaloMassTypeParams)

	SubhaloPosParams = (SubhaloID, SUBHALOS['SubhaloPos'][i][0], SUBHALOS['SubhaloPos'][i][1], SUBHALOS['SubhaloPos'][i][2])
	c.execute("INSERT INTO SubhaloPos VALUES (?, ?, ?, ?)", SubhaloPosParams)

	SubhaloSpinParams = (SubhaloID, SUBHALOS['SubhaloSpin'][i][0], SUBHALOS['SubhaloSpin'][i][1], SUBHALOS['SubhaloSpin'][i][2])
	c.execute("INSERT INTO SubhaloSpin VALUES (?, ?, ?, ?)", SubhaloSpinParams)

	SubhaloVelParams = (SubhaloID, SUBHALOS['SubhaloVel'][i][0], SUBHALOS['SubhaloVel'][i][1], SUBHALOS['SubhaloVel'][i][2])
	c.execute("INSERT INTO SubhaloVel VALUES (?, ?, ?, ?)", SubhaloVelParams)
print "\n"
#------------------------------RANGES----------------------------------#

mstarmin = [1.e7 , 1.e8 , 1.e9]
mstarmax = [3.e7, 3.e8, 3.e9 ]

for i in range(1,4):
	c.execute("CREATE TABLE Range{index} (GroupID)".format(index = i))
	print "Finding range {index} halos...".format(index = i)
	c.execute("INSERT INTO Range{index} SELECT GroupID FROM GROUPS WHERE StellarMass > {minmass} AND StellarMass < {maxmass}", index = i, minmass = mstarmin[i-1], maxmass = mstarmax[i-1])

#------------------------------SATELLITES----------------------------------#

print "Finding satellites..."
c.execute("CREATE TABLE Satellites(GroupID, SubhaloID")
c.execute("INSERT INTO Satellites SELECT Groups.GroupID, Subhalos.SubhaloID FROM Groups INNER JOIN Subhalos ON Groups.GroupID = Subhalos.SubhaloGrNr")

conn.commit()
conn.close()


		
