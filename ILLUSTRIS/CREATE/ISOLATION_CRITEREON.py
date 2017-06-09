import sqlite3
import sys

# Connect to database
cursor = sqlite3.connect('../ILLUSTRIS.db').cursor()

# Constants
c = 3e8
h = 0.704
r = 300*h/c

# Returns True/False whether {Host} is the biggest in {r} kpc radius in the refined list of halos 
def isBiggest(Host):
	HostID = Host[0]
	HostX = Host[1]
	HostY = Host[2]
	HostZ = Host[3]
	HostMass = Host[4]

	# Find neighbors within {r} kpc radius that are bigger than {Host}
	cursor.execute("SELECT COUNT(RefinedHalos.GroupID) FROM GroupPos INNER JOIN RefinedHalos ON GroupPos.GroupID = RefinedHalos.GroupID INNER JOIN Groups ON Groups.GroupID = RefinedHalos.GroupID WHERE (GroupPos.X - {x})*(GroupPos.X - {x})+(GroupPos.Y - {y})*(GroupPos.Y - {y})+(GroupPos.Z - {z})*(GroupPos.Z - {z}) < {radius_sqr} AND Groups.StellarMass >= {HostStellarMass}".format(x = HostX, y = HostY, z = HostZ, radius_sqr = r**2, HostStellarMass = HostMass))
	count = cursor.fetchall()[0][0]
	
	# If no such neighbors exist (count == 0), then {Host} is biggest in the radius, returns True; False otherwise
	return (count == 0)
	

cursor.execute('SELECT Groups.GroupID, GroupPos.X, GroupPos.Y, GroupPos.Z, Groups.StellarMass FROM Groups INNER JOIN GroupPos ON Groups.GroupID = GroupPos.GroupID')
Groups = cursor.fetchall()
cursor.execute('CREATE TABLE RefinedHalos (GroupID)')

barwidth = 50
fraction = len(Groups)/barwidth
sys.stdout.write("Refining halos:\t[%s]"%(" " * barwidth))
sys.stdout.flush()
sys.stdout.write("\b" * (barwidth+1))
# Add a loading bar
for i in range(len(Groups)):
	if i % fraction == 0:
		sys.stdout.write("#")
		sys.stdout.flush()
	if isBiggest(Groups[i]):
		cursor.execute('INSERT INTO RefinedHalos VALUES (?)',(Groups[i][0],))

	

