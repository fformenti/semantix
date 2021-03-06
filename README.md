# semantix

## How to run the application:
Open the terminal and navigate to the root of the repo

Run the code below to start with an empty graph

```
$ python src/api.py
```

Run the code below to start with a graph given by the provided path

```
$ python src/api.py 'data/edges.dat'
```

## How to make requests:

Open another terminal tab and run the following commands (this works regardless of which directory you're at)

To get the list of all edges 

```
$ curl http://localhost:5000/edges
```

To add a new edge to the graph. Where node1 and node 2 are integers. The order does not matter since it's an undirected graph.

```
$ curl http://localhost:5000/edges -X POST -H "Content-Type: application/json" -d '{"name": [node1, node2]}'
```


To get the the list of all nodes ranked by their Non Normalized closeness

```
$ curl http://localhost:5000/nodes
```



