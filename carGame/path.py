from models import GameObject

class Path():
    def __init__(self, index, direction, name, nodes=[]):
        self.name = name
        self.index = index
        self.direction = direction
        self.path = []
        self.nodes = nodes
        for node in nodes:
            NewNode = Node(node)
            if nodes.index(node) -1 < 0:
                break
            else:
                NewNode.edges.append(NewNode.position, nodes[nodes.index(node) - 1])
            if nodes.index(node) + 1 > len(nodes):
                break
            else:
                node.edges.append(NewNode.position, nodes(nodes.index(node) + 1))
            self.path.append(NewNode)
        self.nodes = nodes
        self.start = self.nodes[0]
    def get_path(self):
        return self.path

    def set_path(self, path):
        self.path = path
     

class Node(GameObject):
    def __init__(self, position):
        self.position = position
        self.edges = []
        self.radius = 5