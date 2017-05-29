# Request
import requests

webRequest = requests.get('http://data.taipei/opendata/datalist/apiAccess?scope=resourceAquire&rid=a242ee9b-b954-4ae9-9827-2344c5dfeaea')

if webRequest.status_code == 200:
	print('Web (WATER) request is ok.')
else:
	print(webRequest.status_code)
	
waterOutageJSON = webRequest.json()


# Connect database
import sqlite3
conn = sqlite3.connect('Livelihood.db')
		
# Insert date to table
waterEvents = []
coordinates = []
for waterEvent in waterOutageJSON['result']['results']:
	te = (waterEvent['SW_No'], waterEvent['FS_Date'], 
			waterEvent['FC_Date'], waterEvent['SW_Area'], 
			waterEvent['Description'], waterEvent['PubDate'])
	waterEvents.append(te)
	
	for coordinate in waterEvent['StopWaterSection_wgs84']['coordinates']:
		for point in coordinate:
			tc = (waterEvent['SW_No'], point[0], point[1])
			coordinates.append(tc)

conn.executemany('INSERT INTO WaterEvent VALUES (?,?,?,?,?,?)', waterEvents)
conn.executemany('''INSERT INTO WaterEventCoordinate 
					(EventSerialNumber, PointX, PointY) VALUES 
					(?,?,?)''', coordinates)

conn.commit()
conn.close()
