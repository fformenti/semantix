import pandas as pd
import itertools
import functools
import json


def dist_rc(edges,start,finish, dist= 0):
	N = len(set(edges['v1']).union(set(edges['v2'])))
	if dist > N:	# Unreachability Assigment
		return -1

	if finish in start:	# base case
		return dist
	else:
		start = set(edges[edges['v1'].isin(start)]['v2']).union(set(edges[edges['v2'].isin(start)]['v1']))
		return dist_rc(edges, start, finish, dist+1)

def get_distance(edges, edge_tuple):
	"""
	Input: The edges of a network as a dataframe, a tuple of nodes
	Return: Distance between the tuple of nodes as a dict
	"""
	start = list(edge_tuple[0])
	finish = edge_tuple[1]
	dist = dist_rc(edges, start, finish, dist= 0)

	return {'name': (edge_tuple[0], edge_tuple[1]), 'value': dist}

def get_centrality(distance):
	"""
	Input: A dataframe of distances between all possible pair of nodes
	Return: Centrality of every node as a dataframe
	"""

	nodes = pd.concat([distance['name'].map(lambda x: x[0]), distance['name'].map(lambda x: x[1])], ignore_index= True)
	
	distance = pd.concat([distance, distance], ignore_index= True)
	distance['node'] = nodes

	centrality = distance.groupby(['node'], as_index= False)['value'].sum()
	centrality['centrality'] = centrality['value'].map(lambda x: 1.0 / ((len(centrality)-1) * x))
	centrality['node_id'] = centrality.index
	return centrality[['node_id','node','centrality']]

if __name__ == '__main__':

	# Reading
	graph_path = '../data/edges_sample.dat'
	edges = pd.read_table(graph_path, sep= ' ', header= None, names= ['v1','v2'])

	# Extracting Nodes
	nodes = set(edges['v1']).union(set(edges['v2']))

	# Calculating Edge distances
	edges_distance = pd.DataFrame(map(functools.partial(get_distance, edges), itertools.combinations(nodes, 2)))
	print edges_distance

	# Calculating Nodes centrality
	nodes_centrality = get_centrality(edges_distance)
	print nodes_centrality

	# Tranforming to JSON
	json_str = nodes_centrality.to_json(orient= 'records')
	nodes = json.loads(json_str)

	edges['name'] = map(lambda x,y: [x,y], edges['v1'], edges['v2'])
	edges['edge_id'] = edges.index
	json_str = edges.to_json(orient= 'records')
	edges = json.loads(json_str)

	json_str = json.dumps(edges)
	edges_df = pd.read_json(json_str)






