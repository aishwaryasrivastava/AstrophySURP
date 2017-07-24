import sqlite3

conn = sqlite3.connect('ILLUSTRIS.db')
c = conn.cursor()

conn1 = sqlite3.connect('RANGE1.db')
c1 = conn1.cursor()

conn2 = sqlite3.connect("RANGE2.db")
c2 = conn2.cursor()

conn3 = sqlite3.connect("RANGE3.db")
c3 = conn3.cursor()

c_arr = [c1, c2, c3]

for i in range(1,4):
	c.execute("CREATE TABLE Range{Index}ObsRelVel (SubhaloID int, RelVelX float, StellarMass float, Vmax float, GroupID int, SubhaloMass float)".format(Index = i))
	c_arr[i-1].execute("Select * from Range{Index}ObsRelVel2".format(Index =i))
	g = c_arr[i-1].fetchall()
	for value in g:
		c.execute("insert into Range{Index}ObsRelVel values (?, ?, ?, ?, ?, ?)".format(Index = i), value)

conn.commit()
conn1.commit()
conn2.commit()
conn3.commit()

conn.close()
conn1.close()
conn2.close()
conn3.close()
