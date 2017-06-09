import sqlite3
conn = sqlite3.connect('halos_and_subhalos.db')
c = conn.cursor()

# DROP GROUP TABLES
c.execute("DROP TABLE IF EXISTS  Groups")
c.execute("DROP TABLE IF EXISTS  GroupLenType")
c.execute("DROP TABLE IF EXISTS  GroupMassType")
c.execute("DROP TABLE IF EXISTS  GroupPos")
c.execute("DROP TABLE IF EXISTS  GroupVel")

# DROP SUBHALO TABLES
c.execute("DROP TABLE IF EXISTS  Subhalos")
c.execute("DROP TABLE IF EXISTS  SubhaloCM")
c.execute("DROP TABLE IF EXISTS  SubhaloHalfmassRadType")
c.execute("DROP TABLE IF EXISTS  IF EXISTS  SubhaloLenType")
c.execute("DROP TABLE IF EXISTS  SubhaloMassInHalfRadType")
c.execute("DROP TABLE IF EXISTS  SubhaloMassInMaxRadType")
c.execute("DROP TABLE IF EXISTS  SubhaloMassInRadType")
c.execute("DROP TABLE IF EXISTS  SubhaloMassType")
c.execute("DROP TABLE IF EXISTS  SubhaloPos")
c.execute("DROP TABLE IF EXISTS  SubhaloSpin")
c.execute("DROP TABLE IF EXISTS  SubhaloVel")

# DROP RANGE TABLES
c.execute("DROP TABLE IF EXISTS  Range1")
c.execute("DROP TABLE IF EXISTS  Range2")
c.execute("DROP TABLE IF EXISTS  Range3")

# DROP SATELLITE_TABLES
for i in range(1,4):
	c.execute("SELECT GroupID FROM Range{index}".format(index = i))
	groups = c.fetchall()
	for group in groups:
		c.execute("DROP TABLE IF EXISTS  Satellites_{groupid}".format(groupid = group[0]))



