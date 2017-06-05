import sqlite3
import numpy

conn = sqlite3.connect('halos_and_subhalos.db')

c = conn.cursor()

# Newton's constant G in km^2 kpc/Msun*s^2 units
G = 6.67e-11 * (1.e-3)**2. * (2.e30)/(3.086e19) 

for i in range(1,4):
	c.execute("SELECT GroupPos.GroupID, GroupPos.X, GroupPos.Y, GroupPos.Z FROM GroupPos INNER JOIN Range{index} WHERE GroupPos.GroupID = Range{index}.GroupID".format(index = i))
	groups = c.fetchall()
	# groups[i][0] = group ID
	# groups[i][1] = group X
	# groups[i][2] = group Y
	# groups[i][3] = group Z
	for group in groups:
		c.execute("CREATE TABLE {groupid}_satellites(SubhaloID)".format(groupid = group[0]))
		c.execute("SELECT SubhaloPos.SubhaloID, SubhaloPos.X, SubhaloPos.Y, SubhaloPos.Z FROM SubhaloPos")
		subhalos = c.fetchall()
		c.execute("SELECT Group_R_Crit200 FROM Groups WHERE GroupID = ?",(group[0],))
		Rvir = c.fetchall()[0][0]
		for subhalo in subhalos:
			if ((group[2] - subhalo[2])**2 + (group[3] - subhalo[3])**2)**(0.5) < Rvir:
				c.execute("SELECT StellarMass FROM Subhalos WHERE SubhaloID = ?",(subhalo[0],))
				SatStellarMass = c.fetchall()[0][0]
				c.execute("SELECT StellarMass FROM Groups WHERE GroupID = ?", (group[0],))
				HostStellarMass = c.fetchall()[0][0]
				if SatStellarMass < HostStellarMass:
					c.execute("SELECT X FROM SubhaloPos WHERE SubhaloID = ?",(subhalo[0],))
					SatVelX = c.fetchall()[0][0]
					c.execute("SELECT X FROM GroupPos WHERE GroupID = ?", (group[0],))
					HostVelX = c.fetchall()[0][0]	
					c.execute("SELECT Group_M_Crit200, Group_R_Crit200gt FROM Groups WHERE GroupID = ?", (group[0],))
					GroupMvir = c.fetchall[0]
					GroupRvir = c.fetchall[0]
					if numpy.absolute(HostVelX - SatVelX) < 3*(G*GroupMvir/GroupRvir)**(0.5):
						c.execute("INSERT INTO {groupid}_satellites VALUES(?)".format(groupid = group[0]),(subhalo[0],))
						
						
			
	
