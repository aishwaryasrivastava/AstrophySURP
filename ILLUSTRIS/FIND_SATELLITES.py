import numpy as np
import illustris_python as il
np.seterr(divide = 'ignore', invalid = 'ignore')
import sqlite3
import sys

conn = sqlite3.connect('halos_and_subhalos.db')
c = conn.cursor()

print "Finding satellites..."
c.execute("CREATE TABLE Satellites(GroupID int, SubhaloID, FOREIGN KEY(GroupID) REFERENCES Groups(GroupID), FOREIGN KEY(SubhaloID) REFERENCES Subhalos(SubhaloID))")
c.execute("INSERT INTO Satellites SELECT Groups.GroupID, Subhalos.SubhaloID FROM Groups INNER JOIN Subhalos ON Groups.GroupID = Subhalos.SubhaloGrNr")

conn.commit()
conn.close()
