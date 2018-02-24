'''
Implement the independent set problem as an integer program formulation, then implement it as a linear program. 
Check how the solutions compare. 
'''

import networkx as nx
import pulp

karate = nx.read_gml('karate.gml')
power = nx.read_gml('power.gml')

# IP formulation
def independent_set_ip(graph):
    """Computes a maximum independent set of a graph using an integer program.
    
    Args:
      - graph (nx.Graph): an undirected graph
    
    Returns:
        (list[(int, int)]) The IP solution as a list of node-value pairs.
        
    """    
    # Initiate problem
    prob = pulp.LpProblem("Max Independent Set", pulp.LpMaximize)
    
    # Define variable
    nodes = graph.nodes()
    x = pulp.LpVariable.dicts("nodes", (i for i in nodes), lowBound = 0, upBound = 1, cat='Integer')
    
    # Define constraint
    for i,j in graph.edges_iter():
        prob += x[i] + x[j] <= 1
    
    # Define objective
    prob += pulp.lpSum(x)
        
    prob.solve()
    solution = pulp.value(sum(x))
    
    # Build (list[(int, int)])
    solution_set = []
    for var in x: 
        item = (int(var), int(x[var].value()))
        solution_set.append(item)
        
    return solution_set

def set_weight(solution):
    """Computes the total weight of the solution of an LP or IP for independent set.
    
    Args:
      - solution (list[int, float]): the LP or IP solution
    
    Returns:
      (float) Total weight of the solution
    
    """
    return sum(value for (node, value) in solution)


# Show results
karate_ind_set = independent_set_ip(karate)
print "Size of karate set = ", set_weight(karate_ind_set)
power_ind_set = independent_set_ip(power)
print "Size of power set = ", set_weight(power_ind_set)


# LP formulation
def independent_set_lp(graph):
    """Computes the solution to the linear programming relaxation for the
    maximum independent set problem.
    
    Args:
      - graph (nx.Graph): an undirected graph
    
    Returns:
        (list[(int, float)]) The LP solution as a list of node-value pairs.
        
    """    
    # Initiate problem
    prob = pulp.LpProblem("Max Independent Set", pulp.LpMaximize)
    
    # Define variable
    nodes = graph.nodes()
    x = pulp.LpVariable.dicts("nodes", (i for i in nodes), lowBound = 0, upBound = 1, cat='Continuous')
    
    # Define constraint
    for i,j in graph.edges_iter():
        prob += x[i] + x[j] <= 1
    
    # Define objective
    prob += pulp.lpSum(x)
        
    prob.solve()
    solution = pulp.value(sum(x))
    
    # Build (list[(int, float)])
    solution_set = []
    for var in x: 
        item = (int(var), x[var].value())
        solution_set.append(item)
        
    return solution_set

# Show results
karate_ind_set_relax = independent_set_lp(karate)
print "Value of karate set = ", set_weight(karate_ind_set_relax)
power_ind_set_relax = independent_set_lp(power)
print "Value of power set = ", set_weight(power_ind_set_relax)


def round_solution(solution, graph):
    """Finds the subgraph corresponding to the rounding of
    a solution to the independent set LP relaxation.
    
    Args:
      - solution (list[(int, float)]): LP solution
      - graph (nx.Graph): the original graph
      
    Returns:
        (nx.Graph) The subgraph corresponding to rounded solution
    
    """
    subgraph_nodes = []
    for n, val in solution:
        if val > 0.5:
            subgraph_nodes.append(n)
        else:
            continue
            
    return graph.subgraph(subgraph_nodes)


def solution_quality(rounded, optimal):
    """Computes the percent optimality of the rounded solution.
    
    Args:
      - rounded (nx.Graph): the graph obtained from rounded LP solution
      - optimal: size of maximum independent set
    
    """
    num_nodes = rounded.number_of_nodes() - rounded.number_of_edges()
    return float(num_nodes) / optimal


# Compare IP and LP results
karate_rounded = round_solution(karate_ind_set_relax, karate)
karate_quality = solution_quality(karate_rounded, set_weight(karate_ind_set))
print "Quality of karate rounded solution = {:.0f}%".format(karate_quality*100)

power_rounded = round_solution(power_ind_set_relax, power)
power_quality = solution_quality(power_rounded, set_weight(power_ind_set))
print "Quality of power rounded solution = {:.0f}%".format(power_quality*100)