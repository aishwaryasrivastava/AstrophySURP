import sqlite3
import sys

# Connect to database
cursor = sqlite3.connect('../ILLUSTRIS.db').cursor()

def neighbors(A, R):
	Neighbors = []
	Ay = A[4]
	Az = A[5]
	for B in Groups:
		By = B[4]
		Bz = B[5]
		if ((Ay-By)**2 + (Az-Bz)**2)**(0.5) < R:
			Neighbors.append(B)
	return Neighbors

def biggest(Groups):
	Biggest = Groups[0]
	for Group in Groups:
		if Group[6] > Biggest[6]:
			Biggest = Group
	return Biggest


# Groups!
cursor.execute("SELECT Groups.GroupID, Groups.Group_M_Crit200, Groups.Group_R_Crit200, GroupVel.X, GroupPos.Y, GroupPos.Z, Groups.StellarMass FROM Groups INNER JOIN GroupVel ON Groups.GroupID = GroupVel.GroupID INNER JOIN GroupPos ON Groups.GroupID = GroupPos.GroupID")
Groups = cursor.fetchall()
cursor.execute("CREATE TABLE RefinedGroups (GroupID int PRIMARY KEY, FOREIGN KEY (GroupID) REFERENCES Groups (GroupID))")

# Constants
h = 0.704
r = 300*h	# Radius in kpc/h
G = 6.67e-11 * (1.e-3)**2. * (2.e30)/(3.086e19)		# km^2 kpc/Msun*s^2
"""
barwidth = 50
fraction = len(Groups)/barwidth
sys.stdout.write("Refining groups...\t[%s]"%(" "*barwidth))
sys.stdout.flush()
sys.stdout.write("\b" * (barwidth+1))
"""
for Group in Groups:
	print `Group[0]` + ": " + `len(Groups)`
	GroupID = Group[0]
	GroupMvir = Group[1]
	GroupRvir = Group[2]
	GroupVelX = Group[3]
	GroupPosY = Group[4]
	GroupPosZ = Group[5]
	GroupMass = Group[6]
	if not GroupRvir == 0:
		Vvir = (G * GroupMvir / GroupRvir)**0.5
		# Velocity cut
		if GroupVelX < 3*Vvir and GroupVelX > -3*Vvir:
			N = neighbors(Group, r)
			if not Group[0] == biggest(N)[0]:
				Groups.remove(Group)
			else:
				Groups = [x for x in Groups if (x not in N)]
				Groups.append(Group)

print "Removed {count} contaminations!".format(count = refined_count)

for Group in Groups:
	cursor.execute("INSERT INTO RefinedGroups VALUES (?)", (Group[0],))

# Returns neighbors of {A} in radius {R} (not including {A})

		
	

		
	
		


	

