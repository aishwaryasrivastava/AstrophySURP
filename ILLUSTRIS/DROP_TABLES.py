import sqlite3
conn = sqlite3.connect('halos_and_subhalos.db')
c = conn.cursor()

# DROP GROUP TABLES
c.execute("DROP TABLE Groups")
c.execute("DROP TABLE GroupLenType")
c.execute("DROP TABLE GroupMassType")
c.execute("DROP TABLE GroupPos")
c.execute("DROP TABLE GroupVel")

# DROP SUBHALO TABLES
c.execute("DROP TABLE Subhalos")
c.execute("DROP TABLE SubhaloCM")
c.execute("DROP TABLE SubhaloHalfmassRadType")
c.execute("DROP TABLE SubhaloLenType")
c.execute("DROP TABLE SubhaloMassInHalfRadType")
c.execute("DROP TABLE SubhaloMassInMaxRadType")
c.execute("DROP TABLE SubhaloMassInRadType")
c.execute("DROP TABLE SubhaloMassType")
c.execute("DROP TABLE SubhaloPos")
c.execute("DROP TABLE SubhaloSpin")
c.execute("DROP TABLE SubhaloVel")

# DROP RANGE TABLES
c.execute("DROP TABLE Range1")
c.execute("DROP TABLE Range2")
c.execute("DROP TABLE Range3")



