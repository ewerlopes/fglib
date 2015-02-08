"""Module for factor graphs.

This module contains the base class for factor graphs
with additional functions to convert arbitrary graphs to factor graphs.

Classes:
    FactorGraph: Class for factor graphs.

Functions:
    convert_to_fg: Convert to factor graph function.

"""

import networkx as nx

from . import nodes, edges


class FactorGraph(nx.Graph):

    """Class for factor graphs.

    A factor graphs represents the factorization of a function of several
    variables. Assume, for example, that some function f(x1, x2, x3, x4) can
    be factored as

        f(x1, x2, x3, x4) = fa(x1, x2) fb(x2, x3) fc(x2, x4).

    The factor graph representing the factorization is given as

      /--\      +----+      /--\      +----+      /--\
     | x1 |-----| fa |-----| x2 |-----| fb |-----| x3 |
      \--/      +----+      \--/      +----+      \--/
                             |
                           +----+
                           | fc |
                           +----+
                             |
                            /--\
                           | x4 |
                            \--/.

    The class for factor graphs is inherited from the base class
    for undirected graphs of the NetworkX library.

    """

    def __init__(self):
        """Initialize a factor graph."""
        super().__init__(self, name="Factor Graph")

    def set_node(self, node, **attr):
        """Add a single node to the factor graph.

        A single node is added to the factor graph.
        Optional attributes can be added to the single node by using keyword
        arguments.

        Args:
            node: A single node
            **attr: Optional attributes

        """
        node.graph = self
        FactorGraph.add_node(self, node,
                             attr,
                             type=node.type)

    def set_nodes(self, nodes):
        """Add multiple nodes to the factor graph.

        Multiple nodes are added to the factor graph.

        Args:
            nodes: A list of multiple nodes

        """
        for n in nodes:
            self.set_node(n)

    def set_edge(self, snode, tnode, init=None):
        """Add a single edge to the factor graph.

        A single edge is added to the factor graph.
        It can be initialized with a given random variable.

        Args:
            snode: Source node for edge
            tnode: Target node for edge
            init: Initial message for edge

        """
        self.add_edge(snode, tnode,
                      object=edges.Edge(snode, tnode, init))

    def set_edges(self, edges):
        """Add multiple edges to the factor graph.

        Multiple edges are added to the factor graph.

        Args:
            edges: A list of multiple edges

        """
        for (snode, tnode) in edges:
            self.set_edge(snode, tnode)

    def get_vnodes(self):
        """Return variable nodes of the factor graph.

        Returns:
            A list of all variable nodes.

        """
        return [n for (n, d) in self.nodes(data=True)
                if d['type'] == nodes.NodeType.variable_node]

    def get_fnodes(self):
        """Return factor nodes of the factor graph.

        Returns:
            A list of all factor nodes.

        """
        return [n for (n, d) in self.nodes(data=True)
                if d['type'] == nodes.NodeType.factor_node]


def convert_to_fg(graph, vnode, fnode, bipartite=False):
    """Convert to factor graph function.

    Convert NetworkX graph to a factor graph.
    If origin graph is not bipartite, all nodes are replaced by instances
    of the given variable node class.
    If origin graph is bipartite, all nodes with label 'bipartite' == 0 are
    replaced by instances of the given variable node class and all nodes with
    label 'bipartite' == 1 are replaced by instances of the given factor node
    class.
    All new nodes in the generated factor graph get a label 'origin',
    which indicated the label of the origin node of the origin graph.
    The generated factor graph is returned.

    Positional arguments:
    graph -- the origin graph used for conversion
    vnode -- variable node class used instead of all origin variable nodes.
    fnode -- factor node class used instead of all origin factor nodes

    Keyword arguments:
    bipartite -- boolean if given graph is already bipartite

    """
    mapping = dict(zip(graph, graph))
    fgraph = FactorGraph()

    if bipartite:
        vn = [n for (n, d) in graph.nodes(data=True) if d['bipartite'] == 0]
        fn = [n for (n, d) in graph.nodes(data=True) if d['bipartite'] == 1]

        obj_box = [vnode(i) for i in range(len(vn))]
        mapping.update((n, obj_box.pop()) for n in vn)
        obj_box = [fnode(i, None) for i in range(len(fn))]
        mapping.update((n, obj_box.pop()) for n in fn)
        graph = nx.relabel_nodes(graph, mapping)  # Returns a copy of 'graph'.

        # Build factor graph
        fgraph.set_nodes(graph.nodes())
        fgraph.set_edges(graph.edges())
    else:
        obj_box = [vnode(i) for i in range(graph.number_of_nodes())]
        mapping.update((n, obj_box.pop()) for n in graph.nodes())
        graph = nx.relabel_nodes(graph, mapping)  # Returns a copy of 'graph'.

        # Build factor graph
        fgraph.set_nodes(graph.nodes())
        i = list(range(graph.number_of_edges()))
        for e in graph.edges_iter():
            n = fnode(i.pop(), None)
            fgraph.set_node(n)
            fgraph.set_edges([(e[0], n), (n, e[1])])

    # Node attribute to identify original node
    origin = {v: k for k, v in mapping.items()}
    nx.set_node_attributes(fgraph, 'origin', origin)

    return fgraph
