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
basePath = './Illustris-1-Full/'
snapNum = 135

print "Reading catalog..."

CATALOG 	= il.groupcat.load(basePath, snapNum)
HALOS		= CATALOG['halos']
#------------------------------CREATING HALOS----------------------------#


c.execute("CREATE TABLE Groups (GroupID int PRIMARY KEY, Group_M_Crit200 float, Group_R_Mean200 float, GroupMass float, Group_M_Mean200 float, GroupStarMetallicity float, GroupBHMass float, Group_R_Crit200 float, GroupFirstSub int, GroupSFR float, Group_M_TopHat200 float, Group_M_Crit500 float, Group_R_Crit500, GroupNsubs int, Group_R_TopHat200 float, GroupGasMetallicity float, GroupBHMdot float, GroupWindMass float, GroupLen int)")

c.execute("CREATE TABLE GroupLenType(GroupID int PRIMARY KEY, Type1 float, Type2 float, Type3 float, Type4 float, Type5 float, Type6 float, FOREIGN KEY(GroupID) REFERENCES Groups(GroupID))")

c.execute("CREATE TABLE GroupMassType(GroupID int PRIMARY KEY, Type1 float, Type2 float, Type3 float, Type4 float, Type5 float, Type6 float, FOREIGN KEY(GroupID) REFERENCES Groups(GroupID))")

c.execute("CREATE TABLE GroupPos(GroupID int PRIMARY KEY, X float, Y float, Z float, FOREIGN KEY(GroupID) REFERENCES Groups(GroupID))")

c.execute("CREATE TABLE GroupVel(GroupID int PRIMARY KEY, X float, Y float, Z float, FOREIGN KEY(GroupID) REFERENCES Groups(GroupID))")

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
	GroupParams = (GroupID, float(HALOS['Group_M_Crit200'][i])*mass_constant, float(HALOS['Group_R_Mean200'][i]), float(HALOS['GroupMass'][i])*mass_constant, float(HALOS['Group_M_Mean200'][i])*mass_constant, float(HALOS['GroupStarMetallicity'][i]), float(HALOS['GroupBHMass'][i]), float(HALOS['Group_R_Crit200'][i]), int(HALOS['GroupFirstSub'][i]), float(HALOS['GroupSFR'][i]), float(HALOS['Group_M_TopHat200'][i])*mass_constant, float(HALOS['Group_M_Crit500'][i])*mass_constant, float(HALOS['Group_R_Crit500'][i]), int(HALOS['GroupNsubs'][i]), float(HALOS['Group_R_TopHat200'][i]), float(HALOS['GroupGasMetallicity'][i]), float(HALOS['GroupBHMdot'][i]), float(HALOS['GroupWindMass'][i]), int(HALOS['GroupLen'][i]))


	
	c.execute("INSERT INTO Groups VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", GroupParams)

	GroupLenParams = (GroupID, int(HALOS['GroupLenType'][i][0]), int(HALOS['GroupLenType'][i][1]), int(HALOS['GroupLenType'][i][2]), int(HALOS['GroupLenType'][i][3]), int(HALOS['GroupLenType'][i][4]), int(HALOS['GroupLenType'][i][5]))
	c.execute("INSERT INTO GroupLenType VALUES(?, ?, ?, ?, ?, ?, ?)", GroupLenParams)

	GroupMassParams = (GroupID, float(HALOS['GroupMassType'][i][0]*mass_constant), float(HALOS['GroupMassType'][i][1]*mass_constant), float(HALOS['GroupMassType'][i][2]*mass_constant), float(HALOS['GroupMassType'][i][3]*mass_constant), float(HALOS['GroupMassType'][i][4]*mass_constant), float(HALOS['GroupMassType'][i][5]*mass_constant))
	c.execute("INSERT INTO GroupMassType VALUES(?, ?, ?, ?, ?, ?, ?)", GroupMassParams)

	GroupPosParams = (GroupID, float(HALOS['GroupPos'][i][0]), float(HALOS['GroupPos'][i][1]), float(HALOS['GroupPos'][i][2]))
	c.execute("INSERT INTO GroupPos VALUES (?, ?, ?, ?)", GroupPosParams)

	GroupVelParams = (GroupID, float(HALOS['GroupVel'][i][0]), float(HALOS['GroupVel'][i][1]), float(HALOS['GroupVel'][i][2]))
	c.execute("INSERT INTO GroupVel VALUES (?, ?, ?, ?)", GroupVelParams)
print("\n")
conn.commit()
conn.close()