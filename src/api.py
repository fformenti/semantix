from flask import Flask
from flask.ext.restful import Api, Resource, reqparse, fields, marshal, abort
import pandas as pd
import itertools
import functools
import json
import sys

import g_func
import read_data_from_path

app = Flask(__name__)
api = Api(app)

# ===== INPUT DATA ============

edges = []

# If path is not provided it starts with a graph with no edges
if len(sys.argv) > 1:
    edges = read_data_from_path.read_data(path = sys.argv[1])


# ===== NODES =================

# Dictionary for parsing nodes fields
node_fields = {
    'node': fields.String,
    'centrality': fields.Float
}

# NodeList
# shows a list of all nodes, and lets you POST to add new nodes
class NodeListAPI(Resource):

    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('node', type=str, required=True,
                                   help='No node name provided',
                                   location='json')
        self.reqparse.add_argument('centrality', type=int, location='json')
        super(NodeListAPI, self).__init__()

    def abort_if_not_fully_connected(self,edge_distances):
        """
        Input: The distance for all pair of nodes
        Return: Abort if graphs is not fully connected
        """
        if not edge_distances.empty:
            if any(edge_distances.value.unique() == -1):
                abort(404, message= "The graphs is not Fully Connected")

    def get(self):
        """ shows a list of all nodes ranked by their centrality """
        # Tranforming edges from JSON to Dataframe
        json_str = json.dumps(edges)
        edges_df = pd.read_json(json_str)

        # Getting nodes from the graph's edges    
        nodes = g_func.get_nodes_from_edges(edges_df)

        # checking if it's not empty
        if nodes:
            # Calculating Edge distances
            edges_distance = pd.DataFrame(map(functools.partial(g_func.get_distance, edges_df), itertools.combinations(nodes, 2)))

            # Checking if graph is fully connected
            self.abort_if_not_fully_connected(edges_distance)

            # Calculating Nodes centrality
            nodes_centrality = g_func.get_centrality(edges_distance)
            nodes_centrality.sort(['centrality'], ascending= False, inplace= True)

            # Tranforming to JSON
            json_str = nodes_centrality.to_json(orient= 'records')
            nodes = json.loads(json_str)

        return {'nodes': [marshal(node, node_fields) for node in nodes]}

# ===== EDGES ===================

# Dictionary for parsing edges fields
edge_fields = {
    'edge_id': fields.Integer,
    'name': fields.List(fields.Integer)
}

class EdgeListAPI(Resource):

    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('name', type=list, action='store', required=True,
                                   help='No edge name provided',
                                   location='json')

        super(EdgeListAPI, self).__init__()

    def abort_if_already_exists(self, edge, edges):
        """
        Input: One edge and a list of all edges of the graph
        Return: Abort if if edge already exists
        """
        i_edge_set = set(edge['name'])
        all_edge_sets = map(lambda x: set(x['name']), edges)
        if i_edge_set in all_edge_sets:
            abort(404, message="Edge {} already exist".format(edge['name']))

    def get(self):
        """ shows a list of all edges """
        return {'edges': [marshal(edge, edge_fields) for edge in edges]}

    def post(self, eid= 1):
        """ lets you POST to add new edge"""
        args = self.reqparse.parse_args()
        if len(edges) > 0:
            eid = edges[-1]['edge_id'] + 1
        edge = {
            'edge_id': eid,
            'name': args['name']
        }
        self.abort_if_already_exists(edge, edges)
        edges.append(edge)
        return {'edge': marshal(edge, edge_fields)}, 201

##
## Actually setup the Api resource routing here
##
api.add_resource(NodeListAPI, '/nodes', endpoint='nodes')
api.add_resource(EdgeListAPI, '/edges', endpoint='edges')

if __name__ == '__main__':
    app.run(debug=True)


