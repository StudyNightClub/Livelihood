# Create database
import sqlite3
conn = sqlite3.connect('Livelihood.db')


# Create table
# Water outage
conn.execute('''CREATE TABLE WaterEvent(
			SerialNumber TEXT NOT NULL PRIMARY KEY, 
			StartDate TEXT NOT NULL, 
			EndDate TEXT NOT NULL, 
			Area TEXT NOT NULL, 
			Description TEXT, 
			PublishDate TEXT
		)''')

conn.execute('''CREATE TABLE WaterEventCoordinate(
			SerialId INTEGER PRIMARY KEY AUTOINCREMENT,
			EventSerialNumber TEXT NOT NULL,  
			PointX REAL NOT NULL, 
			PointY REAL NOT NULL,			
			FOREIGN KEY(EventSerialNumber) REFERENCES WaterEvent(SerialNumber)
		)''')

# Road
conn.execute('''CREATE TABLE RoadEvent(
			SerialNumber TEXT NOT NULL, 
			NumberId TEXT NOT NULL, 
			CoordinateX TEXT NOT NULL, 
			CoordinateY TEXT NOT NULL, 
			Area TEXT NOT NULL,
			Address TEXT NOT NULL, 			
			StartDate TEXT NOT NULL, 
			EndDate TEXT NOT NULL, 
			Time TEXT, 			
			Description TEXT
		)''')
		
# Power outage
conn.execute('''CREATE TABLE PowerEvent(
			SerialNumber TEXT NOT NULL, 
			Description TEXT NOT NULL, 
			FirstDateTime TEXT NOT NULL, 
			SecondDateTime TEXT, 
			Area TEXT NOT NULL
		)''')


# Save (commit) the changes and close the connection
conn.commit()
conn.close()
