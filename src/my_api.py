from flask import Flask
from flask.ext.restful import Api, Resource, reqparse, fields, marshal, abort #checar se abort tb esta incluso
import pandas as pd
import itertools
import functools
import json
import g_func

app = Flask(__name__)
api = Api(app)

# Reading
graph_path = '../data/edges_sample.dat'
edges = pd.read_table(graph_path, sep= ' ', header= None, names= ['v1','v2'])
edges['name'] = map(lambda x,y: [x,y], edges['v1'], edges['v2'])
edges['edge_id'] = edges.index
json_str = edges.to_json(orient= 'records')
edges = json.loads(json_str)

# checking if node exists
def abort_if_node_doesnt_exist(node_id):
    if node_id not in nodes:
        abort(404, message="Node {} doesn't exist".format(node_id))

# checking if edge exists
def abort_if_edge_doesnt_exist(edge_id):
    if edge_id not in edges:
        abort(404, message="Edge {} doesn't exist".format(edge_id))

#checking if edge already exists
def abort_if_already_exists(edge_list):
    pass

#checking if edge already exists
def abort_if_not_fully_connected(edge_distances):
    if -1 in edge_distances['value']:
        abort(404, message= "The graphs is not Fully Connected")


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

    def get(self):
        # Getting nodes from graph Edges
        json_str = json.dumps(edges)
        edges_df = pd.read_json(json_str)
        nodes = set(edges_df['v1']).union(set(edges_df['v2']))
        N = len(nodes)

        # Calculating Edge distances
        edges_distance = pd.DataFrame(map(functools.partial(g_func.get_distance, edges_df), itertools.combinations(nodes, 2)))

        # Checking if graph is fully connected
        abort_if_not_fully_connected(edges_distance)

        # Calculating Nodes centrality
        nodes_centrality = g_func.get_centrality(edges_distance)

        # Tranforming to JSON
        json_str = nodes_centrality.to_json(orient= 'records')
        nodes = json.loads(json_str)
        return {'nodes': [marshal(node, node_fields) for node in nodes]}

    def post(self):
        args = self.reqparse.parse_args()
        node = {
            'node_id': nodes[-1]['node_id'] + 1,
            'node': args['node'],
            'centrality': args['centrality']
        }
        nodes.append(node)
        return {'node': marshal(node, node_fields)}, 201

# --------- EDGES -----------------

edge_fields = {
    'name': fields.List(fields.String),
    'v1': fields.String,
    'v2': fields.String
}

# EdgeAPI
# shows a single edge with it's centrality value and lets you delete a edge
class EdgeAPI(Resource):
    def get(self, edge_id):
        abort_if_edge_doesnt_exist(edge_id)
        return edges[edge_id]

    def delete(self, edge_id):
        abort_if_edge_doesnt_exist(edge_id)
        del edges[edge_id]
        return '', 204

# EdgeList
# shows a list of all edges, and lets you POST to add new edge
class EdgeListAPI(Resource):

    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('name', type=list, action='store', required=True,
                                   help='No edge name provided',
                                   location='json')
        super(EdgeListAPI, self).__init__()

    def get(self):
        return {'edges': [marshal(edge, edge_fields) for edge in edges]}

    def post(self):
        args = self.reqparse.parse_args()
        edge = {
            'edge_id': edges[-1]['edge_id'] + 1,
            'name': args['name'],
            'v1': args['name'][0],
            'v2': args['name'][1]
        }
        edges.append(edge)
        return {'edge': marshal(edge, edge_fields)}, 201

##
## Actually setup the Api resource routing here
##
api.add_resource(NodeListAPI, '/nodes')
api.add_resource(EdgeListAPI, '/edges', endpoint='edges')


if __name__ == '__main__':
    app.run(debug=True)