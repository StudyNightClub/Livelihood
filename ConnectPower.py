# Download file #
import urllib.request
import urllib.parse

fileName = '台灣電力公司_計畫性工作停電資料.zip'

fileURL = 'http://data.taipower.com.tw/opendata/apply/file/d077004/' + urllib.parse.quote(fileName)

urllib.request.urlretrieve(fileURL, fileName)
print('Download (POWER) file is ok.')



# Unzip downloaded file #
import zipfile

myzip = zipfile.ZipFile(fileName)
myfile = myzip.extract('wkotgnews/102.txt')
print('Unzip (POWER) file is ok.')
myzip.close()



# Read the content of txt file #
file = open('wkotgnews/102.txt', 'r')

powerOutageTaipei = file.readlines()

powerOutageLine = []
powerOutageContent = []		# ['營業區處', '請求號數', '工作概述', '第一次停電時間', '第二次停電時間', '停電範圍', '查詢電話(1911)', '']
for Lines in powerOutageTaipei[1:]:
	LinesAdapted = Lines.strip()
	powerOutageLine = LinesAdapted.split('#')
	powerOutageContent.append(powerOutageLine)

print('Read (POWER) file is ok.')
file.close()



# Connect database #
import sqlite3
conn = sqlite3.connect('Livelihood.db')
		
# Insert date to table #
powerEvents = []
for powerEvent in powerOutageContent:
	te = (powerEvent[1], powerEvent[2], 
			powerEvent[3], powerEvent[4], 
			powerEvent[5])
	powerEvents.append(te)

conn.executemany('''INSERT INTO PowerEvent VALUES 
					(?,?,?,?,?)''', powerEvents)

conn.commit()
conn.close()
