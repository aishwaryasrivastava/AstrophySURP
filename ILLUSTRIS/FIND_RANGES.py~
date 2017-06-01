#--------------------------------IMPORTS-------------------------------#
import numpy as np
import illustris_python as il
np.seterr(divide = 'ignore', invalid = 'ignore')
import sqlite3
import sys
conn = sqlite3.connect('halos_and_subhalos.db')
c = conn.cursor()

#--------------------------------RANGES--------------------------------#
mstarmin = [1.e7, 1.e8, 1.e9]
mstarmax = [3.e7, 3.e8, 3.e9]
for i in range(1, 4):
	print "Finding range {index}...".format(index = i)
	c.execute("CREATE TABLE Range{index} (GroupID int)".format(index = i))
	c.execute("INSERT INTO Range{index} SELECT GroupID FROM Groups WHERE StellarMass > {minmass} AND StellarMass < {maxmass}".format(index = i, minmass = mstarmin[i-1], maxmass = mstarmax[i-1]))
