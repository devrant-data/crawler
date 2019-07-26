import shelfdb

db = shelfdb.open('./data/db')
db.shelf('users')
db.shelf('countries')

x = db.shelf("countries").filter(lambda u: u)

for us in x:
    print(us)