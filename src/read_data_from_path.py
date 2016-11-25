import pandas as pd
import json
from flask.ext.restful import abort

def read_data_pd(path):
	try:
		edges_df = pd.read_table(path, sep= ' ', header= None, names= ['v1','v2'])
		edges_df['name'] = map(lambda x,y: [x,y], edges_df['v1'], edges_df['v2'])
		edges_df['edge_id'] = edges_df.index
		edges_df.drop(['v1','v2'], axis=1, inplace=True)
		json_str = edges_df.to_json(orient= 'records')
		edges = json.loads(json_str)
	except Exception as e:
		print e
		edges = []
	return edges

def read_data(path):
	try:
		f_list = open(path).read().splitlines() # List of file lines as string
		edges = [{'edge_id': i, 'name':(int(x[0]), int(x[1]))} for i, x in enumerate((line.split(' ') for line in f_list),1)]
	except Exception as e:
		print e
		edges = []
	return edges


if __name__ == '__main__':
	graph_path = '../data/edges.dat'
	edges = read_data(graph_path)
	print edges
