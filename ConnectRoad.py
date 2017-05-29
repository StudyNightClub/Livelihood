# Request
import requests

webRequest = requests.get('http://data.taipei/opendata/datalist/apiAccess?scope=resourceAquire&rid=201d8ae8-dffc-4d17-ae1f-e58d8a95b162')

if webRequest.status_code == 200:
	print('Web (ROAD) request is ok.')
else:
	print(webRequest.status_code)
	
roadJSON = webRequest.json()


# Connect database
import sqlite3
conn = sqlite3.connect('Livelihood.db')
		
# Insert date to table
roadEvents = []
for roadEvent in roadJSON['result']['results']:
	te = (roadEvent['AC_NO'], roadEvent['SNO'], 
			roadEvent['X'], roadEvent['Y'], 
			roadEvent['C_NAME'], roadEvent['ADDR'], 
			roadEvent['CB_DA'], roadEvent['CE_DA'], 
			roadEvent['CO_TI'], roadEvent['NPURP'])
	roadEvents.append(te)

conn.executemany('''INSERT INTO RoadEvent VALUES 
					(?,?,?,?,?,?,?,?,?,?)''', roadEvents)

conn.commit()
conn.close()
