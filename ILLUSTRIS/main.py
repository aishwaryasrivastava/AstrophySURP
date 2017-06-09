import sys
import os

#---------------------------------FUNCTIONS-----------------------------------
""" Creates a directory titled {directory} with directories for Range 1-3 in it """
def change_dir(directory):
	if not os.path.exists(directory):
		os.makedirs(directory)
	os.chdir(directory)
	for i in range(1,4):
		rangedir = "Range{index}".format(index = i)
		if not os.path.exists(rangedir):
			os.makedirs(rangedir)
#--------------------------------CREATE DATABASE------------------------------
choice = raw_input('Create database? (Y/N): ')
while choice not in ['Y', 'y', 'N', 'n']:
	choice = raw_input('Invalid option! Try again: ')
if choice == 'Y' or choice == 'y':
	os.chdir('CREATE')
	import CREATE_HALOS
	import CREATE_SUBHALOS
	import FIND_RANGES
	os.chdir('..')

print "Database saved as ILLUSTRIS.db in the root folder."

#-------------------------CHOOSE SATELLITE FINDING METHOD------------------------

choice = raw_input("Press A/a to use satellites through FoF\nPress B/b to use satellites through FoF with Vmax > 12 km/s\nPress C/c to use closest subhalos\nPress D/d to use closest subhalos with Vmax > 12 km/s\n")
while choice not in ['A', 'a', 'B', 'b', 'C', 'c', 'D', 'd']:
	choice = raw_input('Invalid option! Try again: ')
directory = ''
if choice == 'a' or choice == 'A':
	print "Using satellites through FoF"
	change_dir('FoF')
elif choice == 'b' or choice == 'B':
	print "Using satellites through FoF with Vmax > 12"
	change_dir('FoF_Vmax')
elif choice == 'c' or choice == 'C':
	print "Using closest satellites"
	change_dir('Observational')
elif choice == 'd' or choice == 'D':
	print "Using closest satellites with Vmax > 12"
	 change_dir('Observational_Vmax')

print "Creating velocity function...."
import velocity_functions

print "Creating comparison of velocities by range..."
import velocity_functions_by_range

print "Creating mass cut in velocity functions..."
import MassCutVF

print "Done!"


