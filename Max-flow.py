'''Movie distribution - max flow algorithm

Suppose a movie distributor would like to ship a copy of a film from CA to every other state. 
There are therefore 48 units to ship out of CA, and each other state receives 1 unit.
The dataset contiguous-usa.dat lists the adjacent states in the US. Each line lists two adjacent states; 
thus AK and HI are omitted, but DC is included in the data.'''


import networkx as nx
G = nx.Graph()

# reading in the graph of US states
usa = open('/Users/melindasong/Documents/@Columbia/Algorithms for Data Science/HW/contiguous-usa.dat.txt')
for line in usa:
    s1, s2 = line.strip().split()
    G.add_edge(s1, s2)

 # encode demands into graph G
for state in G.nodes():
	if state != 'CA':
		G.node[state]['demand'] = 1
G.node['CA']['demand'] = -48


'''
First assign a uniform capacity of 16 to each edge. 
Since CA has only three adjacent states, this is the smallest possible uniform capacity that allows one to ship all 48 units out of CA. 
As we have created an undirected graph, and flows have directions, we first convert the graph to a directed graph.
'''
G = nx.DiGraph(G)
uniform_capacity = 16
for (s1, s2) in G.edges():
    G.edge[s1][s2]['capacity'] = uniform_capacity


def flow_with_demands(graph):
    """Computes a flow with demands over the given graph.
    
    Args:
        graph: A directed graph with nodes annotated with 'demand' properties and edges annotated with 'capacity' 
            properties.
        
    Returns:
        A dict of dicts containing the flow on each edge. For instance, flow[s1][s2] should provide the flow along
        edge (s1, s2).
        
    Raises:
        NetworkXUnfeasible: An error is thrown if there is no flow satisfying the demands.
    """
    
    G.add_node('Source')
    G.add_node('Sink')
    
    # Add edges from states to super node and super sink. Calculate total demand and total supply. 
    demand_sum = 0
    supply_sum = 0
    for state in G.nodes():
        if state == 'Source' or state == 'Sink':
            continue
        elif G.node[state]['demand'] > 0:
            demand_sum += G.node[state]['demand']
            G.add_edge(state, 'Sink')
            G.edge[state]['Sink']['capacity'] = G.node[state]['demand']
        elif G.node[state]['demand'] < 0:
            supply_sum += G.node[state]['demand']
            G.add_edge('Source', state)
            G.edge['Source'][state]['capacity'] = abs(G.node[state]['demand'])
    
    # Raise error if total demand doesn't equal total supply
    if demand_sum + supply_sum != 0:
        raise nx.NetworkXUnfeasible("No flow satisfies the demands")

    # Compute max-flow    
    flow_value, flow_dict = nx.maximum_flow(G, 'Source', 'Sink')
    
    # Raise error if total flow doesn't satisfy total demand or total supply
    if flow_value != demand_sum:
        raise nx.NetworkXUnfeasible("No flow satisfies the demands")
        
    # Remove keys in flow_dict associated with super-source or super-sink
    del flow_dict['Source']
    del flow_dict['Sink']
    
    # Remove values in flow_dict associated with super-source or super-sink
    for key, value in flow_dict.items():
        if 'Sink' in value:
            del flow_dict[key]['Sink']
        elif 'Source' in value:
            del flow_dict[key]['Source']
    
    # Remove edges connected to super-source or super-sink in graph
    for state in G.nodes():
        if state == 'Source' or state == 'Sink':
            continue
        elif G.node[state]['demand'] > 0:
            G.remove_edge(state, 'Sink')
        elif G.node[state]['demand'] < 0:
            G.remove_edge('Source', state)

    # Remove super source and super sink in graph
    G.remove_node('Source')
    G.remove_node('Sink')
    
    return flow_dict



def divergence(flow):
    """Computes the total flow into each node according to the given flow dict.
    
    Args:
        flow: the flow dict recording flow between nodes.
        
    Returns:
        A dict of the net flow into each node.
    """
    net_flow = {}
    state_outflow = {}
    state_inflow = {}
    for state in flow:
        adj = flow.get(state)
        state_outflow[state] = sum(adj.itervalues())
        for key, value in adj.items():
            if key not in state_inflow:
                state_inflow[key] = value
            else:
                state_inflow[key] += value
    
    for key, value in state_inflow.items():
        net_flow[key] = value - state_outflow[key]
    
    return net_flow

