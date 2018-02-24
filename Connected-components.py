'''
Using the NetworkX package to construct and manipulate graph based on the a data set that contains
interactions between characters in Homer's Iliad.

Format of data file:
After some comment lines (beginning with *), the file lists a codename for each character (i.e., node of the graph),
followed by a description. The file then lists the groups of characters that interact in each chapter, which form the edges.

For instance, the first line has the form:
1:CH,AG,ME,GS;AP,CH;HE,AC;AC,AG,CA;HE,AT;AT,AC;AT,OG;NE,AG,AC;CS,OD
This means that CH,AG,ME,GS interacted, so there are edges for all pairs of these nodes. Groups of characters that interacted are separated by semicolons. The lines start with chapter information of the form 1: or &:, which can be ignored for this problem.
'''


import urllib2

homer = urllib2.urlopen('http://people.sc.fsu.edu/~jburkardt/datasets/sgb/homer.dat')


def read_nodes(gfile):
    """Reads in the nodes of the graph from the input file.

    Args:
        gfile: A handle for the file containing the graph data, starting at the top.

    Returns:
        A generator of the nodes in the graph, yielding a list of the form:
            ['CH', 'AG, 'ME', ...]
    """
    nodes = []
    for n in gfile:
        node = n[:2]  # create node based on character code
        if node != '* ':  # create nodes from 'AZ' to '9Z'
            if node != '\n':
                nodes.append(node)
            else:
                return nodes


def read_edges(gfile):
    """Reads in the edges of the graph from the input file.

    Args:
        gfile: A handle for the file containing the graph data, starting at the top
            of the edges section.

    Returns:
        A generator of the edges in the graph, yielding a list of pairs of the form:
            [('CH', 'AG'), ('AG', 'ME'), ...]
    """

    def clean_edges(gfile):
        lines = []
        for n in gfile:
            line = n[2:]  # remove number and colons in beginning of lines
            line = line.replace('\n', '').replace(':', '')  # remove '\n' and ':'; create new line to separate interactions
            if line != 'End of file "homer.dat"':  # end the edges section before last line
                lines.append(line)
            else:
                return lines

    def get_pairs(gfile):
        for line in gfile:
            group = line.split(';')  # split separate interactions by ';'
            for pairs in group:
                nodes = pairs.split(',')  # split interactions by nodes
                for n in range(len(nodes)):
                    if n < len(nodes) - 1:
                        node = nodes[n]
                        next_node = nodes[n + 1]
                        yield node, next_node

    edge_pairs = list(get_pairs(clean_edges(gfile)))
    return edge_pairs

# Create graph
import networkx as nx
G = nx.Graph()
G.add_nodes_from(read_nodes(homer))
G.add_edges_from(read_edges(homer))


def Search(graph, root):
    """Runs depth-first search through a graph, starting at a given root. Neighboring
    nodes are processed in alphabetical order.

    Args:
        graph: the given graph, with nodes encoded as strings.
        root: the node from which to start the search.

    Returns:
        A list of nodes in the order in which they were first visited.
    """

    def subSearch(graph, root):
        adj = graph.neighbors(root)
        adj.sort()
        for node in adj:
            if node not in visited:
                visited.append(node)
                subSearch(graph, node)

    visited = []
    subSearch(graph, root)
    return visited


def connected_components(graph):
    """Computes the connected components of the given graph.

    Args:
        graph: the given graph, with nodes encoded as strings.

    Returns:
        The connected components of the graph. Components are listed in
        alphabetical order of their root nodes.
    """
    all_nodes = graph.nodes()
    all_nodes.sort()

    seen = []
    flattened = []
    for root in all_nodes:
        if root not in flattened:
            visited_nodes = Search(graph, root)
            if len(visited_nodes) != 0:
                seen.append(visited_nodes)
                flattened = [item for sublist in seen for item in sublist]
            else:
                seen.append([root])
                flattened = [item for sublist in seen for item in sublist]
    return seen




