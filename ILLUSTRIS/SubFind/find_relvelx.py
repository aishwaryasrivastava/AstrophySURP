import sqlite3 
import sys

conn = sqlite3.connect('../ILLUSTRIS.db')
cursor = conn.cursor()

# Fields
ID = 0
STELLARMASS = 1
VELX = 2
VMAX = 3
FIRSTSUB = 3
NSUBS = 4

# Fetch subhalos
print "Fetching subhalos..."
cursor.execute("SELECT Subhalos.SubhaloID, Subhalos.StellarMass, SubhaloVel.X, Subhalos.SubhaloVmax FROM Subhalos INNER JOIN SubhaloVel ON Subhalos.SubhaloID = SubhaloVel.SubhaloID")
Subhalos = cursor.fetchall()

# Fetch groups
print "Fetching groups..."
for i in range(1,5):
	
	cursor.execute("CREATE TABLE Range{Index}RelVel (SubhaloID int, RelVelX float, StellarMass float, Vmax float)".format(Index = i))
	cursor.execute("SELECT Groups.GroupID, Groups.StellarMass, GroupVel.X, Groups.GroupFirstSub, Groups.GroupNsubs FROM Groups INNER JOIN GroupVel ON Groups.GroupID = GroupVel.GroupID INNER JOIN Range{Index} ON Groups.GroupID = Range{Index}.GroupID".format(Index = i))
	Groups = cursor.fetchall()

	barwidth = 50
	fraction = len(Groups)/(barwidth-1)
	sys.stdout.write("\nFinding deltavx for Range{Index}:\t[%s]".format(Index = i)%(" "*barwidth))
	sys.stdout.flush()
	sys.stdout.write("\b"*(barwidth+1))

	for j in range(len(Groups)):	
	
		if fraction > 0 and j % fraction  == 0:
			sys.stdout.write("#")
			sys.stdout.flush()
		Group = Groups[j]
		SatIDs = range(Group[FIRSTSUB], Group[FIRSTSUB] + Group[NSUBS])
		for ID in SatIDs:
			cursor.execute("INSERT INTO Range{Index}RelVel VALUES (?, ?, ?, ?)".format(Index = i), (ID, Subhalos[ID][VELX] - Group[VELX], Subhalos[ID][STELLARMASS], Subhalos[ID][VMAX]))
			



conn.commit()
conn.close()


