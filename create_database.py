#!/usr/bin/env python3
# coding=utf-8


import sqlite3


database_name = 'livelihood_v5.db'


# Create database
conn = sqlite3.connect(database_name)


# Create event table
conn.execute("""CREATE TABLE event(
    event_id TEXT NOT NULL PRIMARY KEY, 
    event_type TEXT NOT NULL, 
    gov_serial_number TEXT NOT NULL, 
    city TEXT, 
    district TEXT, 
    road_street_boulevard_section TEXT, 
    lane_alley_number TEXT , 
    start_date TEXT NOT NULL, 
    end_date TEXT NOT NULL, 
    start_time TEXT, 
    end_time TEXT, 
    description TEXT, 
    update_status TEXT NOT NULL, 
    update_time TEXT NOT NULL)""")

# Create group table
conn.execute("""CREATE TABLE event_coord_group(
    group_id TEXT NOT NULL PRIMARY KEY, 
    event_id TEXT NOT NULL, 
    
    FOREIGN KEY(event_id) 
        REFERENCES event(event_id))""")

# Create coordinate table
conn.execute("""CREATE TABLE event_coordinate(
    coordinate_id TEXT NOT NULL PRIMARY KEY, 
    latitude REAL NOT NULL, 
    longitude REAL NOT NULL, 
    group_id TEXT NOT NULL, 
    
    FOREIGN KEY(group_id) 
        REFERENCES event_coord_group(group_id))""")


# Save (commit) the changes and close the connection
conn.commit()
conn.close()
