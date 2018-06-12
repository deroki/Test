from tinydb import TinyDB, Query

db = TinyDB("db.json")
db.insert({'site' : 'thissite',
           'ip' : '1.1.1.1'})

