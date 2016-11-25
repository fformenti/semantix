import pandas as pd
import itertools
import functools
import json

def get_nodes_from_edges(edges_df):
	"""
	Input: The edges of a network as a dataframe
	Return: Set of all nodes from the graph
	"""
	if edges_df.empty:
		return []
	return set(edges_df['name'].map(lambda x: x[0])).union(set(edges_df['name'].map(lambda x: x[1])))

def calc_dist(edges_df,start,finish, dist= 0):
	"""
	Input: The edges of a network as a dataframe, a start node, a destination node, dand a counter
	Return: Distance between the tuple of nodes
	"""
	N = len(get_nodes_from_edges(edges_df))
	if dist > N:	
		return -1 # Unreachability Assigment (The nodes are not connected through any path)

	if finish in start:	# base case
		return dist
	else:
		start = set(edges_df[edges_df['v1'].isin(start)]['v2']).union(set(edges_df[edges_df['v2'].isin(start)]['v1']))
		return calc_dist(edges_df, start, finish, dist+1)

def get_distance(edges_df, edge_tuple):
	"""
	Input: The edges of a network as a dataframe, a tuple of nodes
	Return: Distance between the tuple of nodes as a dict
	"""
	start = set([edge_tuple[0]])
	finish = edge_tuple[1]

	edges_df['v1'] = edges_df['name'].map(lambda x: x[0])
	edges_df['v2'] = edges_df['name'].map(lambda x: x[1])
	dist = calc_dist(edges_df, start, finish, dist= 0)

	return {'name': edge_tuple, 'value': dist}

def get_centrality(distance):
	"""
	Input: A dataframe of distances between all possible pair of nodes
	Return: A dataframe with every node and it's non normalized Centrality
	"""

	nodes = pd.concat([distance['name'].map(lambda x: x[0]), distance['name'].map(lambda x: x[1])], ignore_index= True)
	
	distance = pd.concat([distance, distance], ignore_index= True)
	distance['node'] = nodes

	centrality = distance.groupby(['node'], as_index= False)['value'].sum()
	centrality['centrality'] = centrality['value'].map(lambda x: 1.0/x)
	centrality['node_id'] = centrality.index
	return centrality[['node_id','node','centrality']]


if __name__ == '__main__':
	import read_data_from_path

	# ===== INPUT DATA ============
	edges = []
	graph_path = '../data/edges_sample.dat'
	if graph_path:
		edges = read_data_from_path.read_data(path = graph_path)
	# =============================

	#print 'edges: ', edges

	# Tranforming edges from JSON to Dataframe
	json_str = json.dumps(edges)
	edges_df = pd.read_json(json_str)
	#print 'edges_df: ', edges_df

	# Extracting Nodes
	nodes = get_nodes_from_edges(edges_df)

	if nodes:
		# Calculating Edge distances
		edges_distance = pd.DataFrame(map(functools.partial(get_distance, edges_df), itertools.combinations(nodes, 2)))
		#print 'edges_distance: ', edges_distance

		# Checking if graph is fully connected
		abort_if_not_fully_connected(edges_distance)

		# Calculating Nodes centrality
		nodes_centrality = get_centrality(edges_distance)

		# Tranforming to JSON
		json_str = nodes_centrality.to_json(orient= 'records')
		nodes = json.loads(json_str)
	print 'nodes: ', nodes

	edge_test = {'name': ['f','a']}
	#print 'edges: ', edges
	abort_if_already_exists(edge_test, edges)














