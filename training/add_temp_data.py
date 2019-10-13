"""
This script will upload the file generated by the "extract_data_merged.py" file into the database
"""

import csv
import json
import psycopg2
import ast

# Time series data storer
class TimeSeries:
	def __init__(self):
		
		self.code = str
		self.operator_id = int
		self.catalog_id = str
		self.element = dict
		self.param = dict
		self.period = dict
		self.timestep = dict
		self.val = list
		self.descript = str
		
	def as_query(self, table):
		sql = \
			f"INSERT INTO {table} " \
			f"(code, operator_id, catalog_id, element, param, period, timestep, val, descript) " \
			f"VALUES " \
			f"('{self.code}', {self.operator_id}, '{self.catalog_id}', '{json.dumps(self.element)}', " \
			f" '{json.dumps(self.param)}', '{json.dumps(self.period)}', '{json.dumps(self.timestep)}', " \
			f" ARRAY{self.val}, '{self.descript}')"
		
		return sql


# Connect to postgres
try:
	conn = psycopg2.connect(database='giswater3', user='postgres', password='postgres', host='localhost')
	
except:
	raise

cursor = conn.cursor()


stations = ['CL', 'WW', 'U4', 'WE', 'VU', 'CI', 'VP', 'V5', 'VV', 'V3', 'CG']
dates = [2007, 2008, 2009, 2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018]
modes = ['max', 'min']
data = {}

cursor.execute('DELETE FROM api_ws_sample.ext_timeseries')

# Get the fist (and only) row in the file
file = next(csv.DictReader(open(f'C:/Users/user/Desktop/Data/new/merged.csv'), delimiter=';'))

for station in stations:
	for mode in modes:
		
		# Id of the data
		key = station + mode
		
		# Transform string like array into a python array
		vals = ast.literal_eval(file[key])
		
		# Create the data
		data = TimeSeries()
		
		data.code = key 				# TODO
		data.operator_id = 0 			# TODO
		data.catalog_id = f't{mode}'
		data.element = {
			'type': 'exploitation',
			'id': None
		}
		data.param = {
			'isUnitary': False,
			'units': 'ºC',
			'epa': {					# TODO
				'projectType': 'WS',
				'class': 'patern',
				'id': None,
				'type': None,
				'dmaRtcParameters': {
					'dmaId': None,
					'periodId': None,
				}
			},
			'source': {
				'type': None,
				'id': None,
				'import': {
					'type': None,
					'id': None
				}
			}
		}
		data.period = {
			'type': 'yearly',
			'id': key,				# La data és la id?
			'start': '2007-01',
			'end': '2018-12'
		}
		data.timestep = {			# 12 valos de 1 valor cada un
			'units': 'month',
			'value': 1,
			'number': 12 * 12		# 12 months per year * 12 years of data
		}
		data.val = vals
		data.descript = 'No description'
		
		# Upload the data
		cursor.execute(data.as_query(table='api_ws_sample.ext_timeseries'))

conn.commit()

