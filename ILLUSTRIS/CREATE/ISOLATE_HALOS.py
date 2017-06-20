from numpy import *
from numpy.linalg import norm
import glob
import sys
import h5py
import sqlite3

''' Short program to start sifting through hosts.  Most hosts are in file 0, so I concentrate on that.  Make cuts on halo mass instead of Mstar for now, just to play with the data.
'' A Peter 6/15/17
'''
# Connect to the database
conn = sqlite3.connect('../ILLUSTRIS.db')
cursor = conn.cursor()
cursor.execute("CREATE TABLE RefinedGroups (GroupID int PRIMARY KEY, FOREIGN KEY (GroupID) REFERENCES Groups (GroupID))")

G = 6.67e-11 #Newton's constant in SI units
h = 0.7 #Hubble constant
Msun = 2e30 #solar mass in kg
kpc = 3.086e19 #kpc in m
km = 1.e3 #km in m
rlim = 1e2 #limit, in kpc/, where the host has to be the biggest thing 
Deltavxmax = 300. #in km/s, the velocity range that we consider associated with the host.

files = glob.glob('Illustris-1/groups_135/groups_135*.hdf5')
filename = 'Illustris-1/groups_135/groups_135.0.hdf5'
fileobjs = {}
failedhost = []
ctr = 0

#Read in files
for fi in files:
    fileobjs[fi] = h5py.File(fi,'r')
    ctr = ctr + 1

#Find host candidates.  Note that I drastically reduced the mass range, for testing purposes, so that I could refine my filters.
hosts = where( (fileobjs[filename]['Group']['Group_M_TopHat200'][:] * 1e10/h > 1e10) & (fileobjs[filename]['Group']['Group_M_TopHat200'][:] * 1e10/h < 1.01e10))[0]

barwidth = 50
fraction = len(hosts)/(barwidth-1)
sys.stdout.write("Refining halos:\t[%s]"%(" "*barwidth))
sys.stdout.flush()
sys.stdout.write("\b"*(barwidth+1))

for i in range(0, len(hosts)):
    inx = hosts[i]
    if i % fraction == 0:
        sys.stdout.write("#")
	sys.stdout.flush()
    #Properties of the candidate host
    M = fileobjs[filename]['Group']['Group_M_TopHat200'][inx]
    y = fileobjs[filename]['Group']['GroupPos'][inx,1]
    z = fileobjs[filename]['Group']['GroupPos'][inx,2]
    vx = fileobjs[filename]['Group']['GroupVel'][inx,0]
    #Look at Delta vx's for all halos in the 0 file.  Really should scan at least file 1, possibly also file 2.
    Deltavx = fileobjs[filename]['Group']['GroupVel'][:,0] - vx
    #Look at projected separation
    projected = sqrt( (fileobjs[filename]['Group']['GroupPos'][:,1] - y)**2. + (fileobjs[filename]['Group']['GroupPos'][:,2] - z)**2.)

    #First cut: If anything more massive lies within rlim in projection from the candidate host and is in the right velocity range.  Note that the cut is on the central position.
    if len( fileobjs[filename]['Group']['Group_M_TopHat200'][(projected < rlim) & (fileobjs[filename]['Group']['Group_M_TopHat200'][:] > M) & ( Deltavx < Deltavxmax) & ( Deltavx > - Deltavxmax)]  ) > 0:
        failedhost.append(inx)
    else:
        #Second cut is to make sure that the candidate host is not a satellite of a bigger host.  I widened the criterion a bit, because of the "backsplash" halo phenomenon---a lot of halos right outside of a big host have been through the big host, and as such, have been pretty perturbed by it.  So it's best to avoid that area.  There's a more efficient way to do this cut---working on a giant interloper basis instead of a candidate host basis---but this is OK for testing purposes.
        if len(fileobjs[filename]['Group']['Group_M_TopHat200'][(fileobjs[filename]['Group']['Group_M_TopHat200'][:] > M) & ( projected < 1.5 * fileobjs[filename]['Group']['Group_R_TopHat200'][:] )  & ( Deltavx < Deltavxmax) & ( Deltavx > - Deltavxmax)]  ) > 0:
            failedhost.append(inx)

refined = 0
for inx in hosts:
	if inx not in failedhost:
		cursor.execute("INSERT INTO RefinedGroups VALUES (?)", (inx,))
		refined +=1

print "\nRefined halos: " + `refined`

conn.commit()
conn.close()
