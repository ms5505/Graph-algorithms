
'''
Given a flow network with capacities and costs, find a feasible flow such that the flow satisfy edge capacity constraints and
node demands, while minimizing the total cost of the flow. 
'''

import networkx as nx

def create_graph(infile):
    # This code works for gte.bad_40. Key modifications are in second 'for' loop. 
    """Creates a directed graph as specified by the input file. Edges are annotated with 'capacity'
    and 'weight' attributes, and nodes are annotated with 'demand' attributes.
    
    Args:
        infile: the input file using the format to specify a min-cost flow problem.
        
    Returns:
        A directed graph (but not a multi-graph) with edges annotated with 'capacity' and 'weight' attributes
        and nodes annotated with 'demand' attributes.
    """
    flow_file = open(infile)
    
    # Build multi-digraph M from infile
    M = nx.MultiDiGraph()
    
    node_demands = {}
    for line in flow_file:
        if line[0] == 'c'or line[0] == 'p':
            continue
        elif line[0] == 'n':
            s1, s2, s3 = line.strip().split()
            node_demands[s2]=int(s3) 
        elif line[0] == 'a':
            s1, s2, s3, s4, s5, s6 = line.strip().split()
            M.add_edge(s3, s2, capacity=float(s5), weight=float(s6))
    
    # Build simple di-graph from M
    G = nx.DiGraph()
    
    # If an edge already exists in G, then add a new node for each subsequent edge in order to separate the edges. 
    # Capacity on the new edge will be the same as original. Each of the two segments of the new edge will have original cost divided by 2
    counter_n = 1 # Set counter for new nodes 
    for i,j,data in M.edges_iter(data=True):
        if G.has_edge(i,j):
            new_n = i+'_'+str(counter_n)
            G.add_edge(i, new_n, capacity = data['capacity'], weight = data['weight']/2)
            G.add_edge(new_n, j, capacity = data['capacity'], weight = data['weight']/2)
            counter_n += 1
        else:
            G.add_edge(i,j, capacity=data['capacity'], weight=data['weight'])

    # Create dict for node demands
    for i in G.nodes_iter():
        if i not in node_demands:
            G.node[i]['demand'] = 0
        else: 
            G.node[i]['demand'] = node_demands[i]

    return G




'''
Formulate the min-cost problem as a linear program and use general-purpose LP solvers from the Python PuLP package to find the solution. 
'''

import pulp
def lp_flow_value(G):
    """Computes the value of the minimum cost flow by formulating and solving
    the problem as an LP.
    
    Args:
        G: a directed graph with edges annotated with 'capacity' and 'weight'
            attrbutes, and nodes annotated with 'demand' attributes.
            
    Returns:
        The value of the minimum cost flow.
    """
    # Initialize
    prob = pulp.LpProblem("Min Cost Flow Problem", pulp.LpMinimize)
    node_flow = {}
    mincost_var = []

    # Create dict for node demand and flow into and out of nodes    
    for n,data in G.nodes_iter(data=True):
        node_flow[n] = {'demand':data['demand'], 'inflow':[], 'outflow':[]}
        
    # Create LP variables for each edge; upperbound edge flow by capacity
    for i,j,data in G.edges_iter(data=True):
        var = pulp.LpVariable((i,j), lowBound=0, upBound=data['capacity'], cat='Integer')
        cost = data['weight']
        mincost_var.append(cost*var)
    
        # Keep track of the flow in and out of nodes
        node_flow[i]['inflow'].append(var)
        node_flow[j]['outflow'].append(var)
    
    # Add objective function: minimize sum of total cost
    prob += sum(mincost_var)
    
    # Create constraint for each node, where sum(inflow) - sum(outflow) = node demand
    for v, data in node_flow.iteritems():
        prob += (sum(data['inflow'])-sum(data['outflow'])==data['demand'])
        
    status = prob.solve()
    #print pulp.LpStatus[status] 
    return pulp.value(sum(mincost_var))