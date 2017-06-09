""" This program creates an SHM ratio relationship with stellar mass of the subhalos in the Illustrus-1 (Dark) Catalog """

import illustris_python as il
import matplotlib.pyplot as plt
import sys
import numpy as np

basePath = './Illustris-1/'
fields = ['SubhaloMass']
subhalos = il.groupcat.loadSubhalos(basePath, 135, fields = fields)
solar_mass = 1.989e30
mass_msun = (subhalos * 1.e10 / 0.704)	# Mh (Msun)
log_Mh = np.log(mass_msun)		# log(Mh)

SHMratio = []				# m/M (To be calculated using the relation)

N10 = 		0.0351+0.0058		# N10 + sigmaN10
gamma10 = 	0.608+0.059		# gamma10 + sigma(gamma10)
beta10 = 	1.376+0.153		# beta10 + sigma(beta10)
M10 = 		10**(11.590+0.236)	# 10^(M10 + sigmaM10) (Should it be 10^M10 + sigmaM10?) 

# Loading bar -- ignore!
toolbar_width = (len(mass_msun)/100000)+1
sys.stdout.write("Creating plot [%s]" % (" " * toolbar_width))
sys.stdout.flush()
sys.stdout.write("\b" * (toolbar_width+1)) 

# Calculating ratio
for j in range(0,len(mass_msun)):
	M = mass_msun[j]
	if j % 100000 == 0:
		sys.stdout.write("#")
		sys.stdout.flush()
	SHMratio.append(2*N10*(((M/M10)**(-beta10))+((M/M10)**gamma10))**(-1))


plt.title("Stellar mass to halo ratio in relationship with total stellar mass")
plt.plot(log_Mh, SHMratio, '.')
plt.xlabel('$log(M_h/M_\odot)$')
plt.ylabel('$m/M$')
#plt.show()
plt.savefig("SHMRatio.png")
print np.log(M10/solar_mass)
print "\nFigure saved!"
plt.clf()

sys.exit()




