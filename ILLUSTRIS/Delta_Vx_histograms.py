import sqlite3
import sys
import numpy as np
cursor = sqlite3.connect('ILLUSTRIS.db').cursor()

# Enter the range index
RANGE = sys.argv[1]
cont = bool(int(sys.argv[2]))

ID = 0
RELVELX = 1
STELLARMASS = 2
VMAX = 3
GID = 4
HALOMASS = 5

def plot(Obs, SubFind, title):
	import matplotlib.pyplot as plt
	fig, ax = plt.subplots()
	n, bins, patches = ax.hist([Obs, SubFind], 500 , alpha = 0.7, normed = 1, histtype = 'stepfilled', label = ["Observational (mean: {m})".format(m = np.mean(Obs)), "SubFind (mean: {m})".format(m = np.mean(SubFind))])
	ax.legend(prop = {'size':10})
	ax.set_xlabel("Delta Vx (km/s)")
	ax.set_ylabel('Probability')
	plt.grid(True)
	fig.set_size_inches(10,10)
	ax.set_title(title + "\nObs: [{obsmin}, {obsmax}]; SubFind: [{SFmin}, {SFmax}]".format(obsmin = min(Obs), obsmax = max(Obs), SFmax = max(SubFind), SFmin = min(SubFind)))
	plt.show()
	plt.close()

# Sigma clip here
def SigmaClip(List):
	#print len(RelVel)
	# Find the mean of their relative velocities
	Mean = np.mean(List)

	# Find sum(delta(Vx,i) - mean(delta(Vx)))^2
	Sigma = 0
	for l in List:
		Sigma += (l - Mean)**2

	# Find sigma(delta vx)
	Sigma = (Sigma/len(List))**0.5
	return [R for R in List if (R < 3*Sigma and R > -3*Sigma)]

# Get the observed satellites
cursor.execute("SELECT * from Range{Index}ObsRelVel".format(Index = RANGE))
Sats = cursor.fetchall()


if cont:
	print "Removing contamination..."
	Obs = [Sat[RELVELX] for Sat in Sats if Sat[HALOMASS] < max([S[HALOMASS] for S in Sats if S[GID] == Sat[GID]])]
else:
	Obs = [Sat[RELVELX] for Sat in Sats]

# Get the subfind satellites
cursor.execute("SELECT * from Range{Index}SubFindRelVel".format(Index = RANGE))
Sats = cursor.fetchall()

if cont:
	SubFind = [Sat[RELVELX] for Sat in Sats if not Sat[RELVELX] == 0]
else:
	SubFind = [Sat[RELVELX] for Sat in Sats]


# Sigma clip 3 times
for i in range(4):
	plot(Obs, SubFind, "Range {index} delta vx distribution (sigma clipping {clip})".format(index = RANGE, clip = i))
	Obs = SigmaClip(Obs)
	SubFind = SigmaClip(SubFind)

	
	


