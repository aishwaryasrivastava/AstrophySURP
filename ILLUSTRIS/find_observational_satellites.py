import sqlite3
import numpy
import sys

conn = sqlite3.connect('halos_and_subhalos.db')

c = conn.cursor()

# Newton's constant G in km^2 kpc/Msun*s^2 units
G = 6.67e-11 * (1.e-3)**2. * (2.e30)/(3.086e19) 
cutoff = 1.e5
velocities_by_range = [[],[],[]]
labels = []
for i in range(1,4):
	little = []
	big = []
	c.execute("SELECT GroupPos.GroupID, GroupPos.X, GroupPos.Y, GroupPos.Z, Groups.StellarMass, Groups.Group_R_Crit200, GroupVel.X, Groups.Group_M_Crit200 FROM GroupPos INNER JOIN Range{index} INNER JOIN Groups INNER JOIN GroupVel WHERE GroupPos.GroupID = Range{index}.GroupID AND Groups.GroupID = GroupPos.GroupID AND GroupVel.GroupID = Groups.GroupID".format(index = i))
	groups = c.fetchall()
	"""
	fraction = 1000
	barwidth = (len(groups)/fraction)+1
	sys.stdout.write("Finding Range{index} satellites...[%s]".format(index = i)%(" " * barwidth))
	sys.stdout.flush()
	sys.stdout.write("\b" * (barwidth+1))
	"""
	for j in range(len(groups)):
		print j
		groupID   = groups[j][0]
		groupPosX = groups[j][1]	# ckpc/h
		groupPosY = groups[j][2] 
		groupPosZ = groups[j][3]
		groupMass = groups[j][4]	# 10^10 Msun/h
		groupRvir = groups[j][5]	# ckpc/h
		groupVelX = groups[j][6]	# km/s
		groupMvir = groups[j][7]	# 10^10 Msun/h
		"""
		if j % fraction == 0:
			sys.stdout.write("#") 
			sys.stdout.flush()
		"""
		Distance_Condition = "(SubhaloPos.Y - {Y})*(SubhaloPos.Y - {Y})+(SubhaloPos.Z - {Z})*(SubhaloPos.Z - {Z}) < {Rvir}*{Rvir}".format(Y = groupPosY, Z = groupPosZ, Rvir = groupRvir)

		Mass_Condition = "Subhalos.StellarMass < {GroupStellarMass}".format(GroupStellarMass = groupMass)

		Vvir = (G*groupMvir/groupRvir * 3e8/1e10)**(0.5)

		Velocity_Condition = "abs(SubhaloVel.X - {X}) < {limit}".format(X = groupVelX, limit = Vvir)
		print "finding satellites"
		c.execute("SELECT SubhaloPos.SubhaloID, SubhaloVel.X, Subhalos.StellarMass FROM SubhaloPos INNER JOIN Subhalos INNER JOIN SubhaloVel WHERE Subhalos.SubhaloID = SubhaloPos.SubhaloID AND SubhaloVel.SubhaloID = Subhalos.SubhaloID AND ".format(ID = groupID) + Distance_Condition + " AND " + Mass_Condition + " AND " + Velocity_Condition)
		
		print "making plots"
		satellites = c.fetchall()
		for sat in satellites:
			print "reading satellites"
			SatID = sat[0]
			SatVelX = sat[1]
			SatStellarMass = sat[2]
			velocities_by_range[i-1].append(SatVelX)
			if SatStellarMass < cutoff:
				little.append(SatVelX)
			else:
				big.append(SatVelX)
	n_bins = 20
	n, bins, patches = ax.hist([little, big], n_bins, normed = 1, histtype = 'stepfilled', stacked = True, label = ["Mstar < {cutoffmass} Msun; $\mu =$ {littlemean}; $\sigma =$ {littlestd}".format(cutoffmass = '%.2e' % cutoff, littlemean = '%.3f'% mean(little), littlestd =  '%.3f'% std(little)), "Mstar > {cutoffmass} Msun; $\mu =$ {bigmean}; $\sigma =$ {bigstd}".format(cutoffmass = '%.2e' % cutoff, bigmean =  '%.3f'%mean(big), bigstd =  '%.3f'%std(big))])
	ax.set_xlabel('Vx (km/s) of satellites')
	ax.set_ylabel('Probability')
	ax.legend(prop = {'size': 10})
	ax.set_title("Range {index}: Comparison of velocity functions of satellites of new and little hosts (cutoff = {cutoffmass} Msun)".format(index = i, cutoffmass = '%.2e'%cutoff))
	plt.grid(True)
	fig.set_size_inches(10,10)		
	plt.savefig( "Range{index}/range{index}_velocity_function_cut_by_mass.png".format(index = i))
	plt.close()		

	labels.append("Range {index}: $\mu =$ {mean}; $\sigma =$ {std}".format(index = i, mean = '%.3f'% mean(velocities_by_range[i-1]), std = '%.3f'% std(velocities_by_range[i-1])))

n_bins = 20
fig, ax = plt.subplots()
n, bins, patches = ax.hist(velocities_by_range, n_bins, normed = 1, histtype = 'stepfilled', stacked = True, label = labels)
ax.set_xlabel('Vx (km/s) of satellites')
ax.set_ylabel('Probability')
plt.xlim([-200,200])
ax.legend(prop = {'size': 10})
ax.set_title('Velocity function of satellites in different stellar mass ranges')
plt.grid(True)
fig.set_size_inches(10,10)	
plt.savefig("Observational/satellite_velocity_function_by_range.png")
plt.close()
fig, ax = plt.subplots()
	

						
						
			
	
