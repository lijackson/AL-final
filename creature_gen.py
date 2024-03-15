import xml.etree.ElementTree as XMLTree
import random

CUBEDIM = 0.1
JROM = 4
SPAWN_H = 0.1

LIGHTING_ELEM = XMLTree.Element("light",{"diffuse": "1 1 1",
                                         "pos": "0 0 3",
                                         "dir": "0 -1 0"})

GEOM_ELEM = XMLTree.Element("geom", {"type": "plane",
                                     "size": "5 5 0.1",
                                     "rgba": "0 0 1 .5"})

DIR_TO_REL_POS = {
    -1: f"0 0 {SPAWN_H}", # default no offset just in case
    0: f"{CUBEDIM} 0 0",
    1: f"{-CUBEDIM} 0 0",
    2: f"0 {CUBEDIM} 0",
    3: f"0 {-CUBEDIM} 0",
    4: f"0 0 {CUBEDIM}",
    5: f"0 0 {-CUBEDIM}",
}
DIR_TO_JOINT_POS = {
    -1: "0 0 0", # default node
    0: f"{-CUBEDIM/2} 0 0",
    1: f"{CUBEDIM/2} 0 0",
    2: f"0 {-CUBEDIM/2} 0",
    3: f"0 {CUBEDIM/2} 0",
    4: f"0 0 {-CUBEDIM/2}",
    5: f"0 0 {CUBEDIM/2}",
}
DIR_TO_AXIS = { # fix because more than one axis?
    -1: "0 0 0", # default node
    0: "0 1 0",
    1: "0 1 0",
    2: "1 0 0",
    3: "1 0 0",
    4: "0 1 0",
    5: "0 1 0",
}
DIR_TO_RGBA = { # just stylistic to differentiate parts
    -1: "0 0 0 1", # default node
    0: "0.1 0.4 0.9 1",
    1: "0.6 0.2 0.5 1",
    2: "0.8 0.7 0.3 1",
    3: "0.2 0.7 0.3 1",
    4: "0.5 0.1 0.6 1",
    5: "0.8 0.4 0.9 1",
}

class Node:
    NID = 0
    name = ""
    id = None
    children = None
    dir = -1 # 0-5 depending on which face of the cube its attached to; -1 is no offset
    joint_attrs = None # (strength, offset, frequency)
    root_offset = [None,None,None] # total offset relative to the root node
    def __init__(self, dir, jointval = None, child_list = []):
        self.id = Node.NID
        Node.NID += 1

        self.name = "node"+str(self.id)
        self.children = []
        self.dir = dir
        if "type" in jointval:
            self.joint_attrs = jointval
            self.name = "rootnode"
        else:
            self.joint_attrs = {
                "type": "hinge",
                "strength": jointval["strength"],
                "frequency": jointval["frequency"],
                "offset": jointval["offset"],
                "pos": DIR_TO_JOINT_POS[dir],
                "range": f"{-JROM} {JROM}",
                "axis": DIR_TO_AXIS[dir],
            }
        for c in child_list:
            self.add_child(c)
        
    def add_child(self, cnode):
        self.children.append(cnode)

    def remove_child(self, cnode):
        self.children.remove(cnode)
    
    def get_joint_attr(self, attr):
        if attr not in self.joint_attrs:
            return None
        return self.joint_attrs[attr]

    def set_joint_attr(self, attr, val):
        if attr not in self.joint_attrs:
            return
        self.joint_attrs[attr] = val
        
def gen_rand_node(dir, stren_range, freq_range, offs_range):
    stren = random.randint(stren_range[0], stren_range[1])
    freq = random.randint(freq_range[0], freq_range[1])
    offs = random.randint(offs_range[0], offs_range[1])
    return Node(dir, {"strength":stren, "frequency":freq, "offset":offs})

def clone_node_tree(node):
    cloned_children = [clone_node_tree(child) for child in node.children]
    if "type" in node.joint_attrs and node.joint_attrs["type"] == "free":
        return Node(-1, {"type": "free"}, cloned_children)
    attrs = {
        "strength": node.joint_attrs["strength"],
        "frequency": node.joint_attrs["frequency"],
        "offset": node.joint_attrs["offset"]
    }
    cloned_node = Node(node.dir, attrs, cloned_children)
    
    return cloned_node

class Motor:
    def __init__(self, strength, offset, frequency, dir):
        self.strength = strength
        self.offset = offset
        self.frequency = frequency
        self.dir = dir

class Environment:
    root = None
    worldbody = None
    motor_elems = None
    motor_data = None
    def assemble(self, creature):
        self.motor_elems = []
        self.motor_data = {}
        self.assembleEnvironment()
        self.worldbody.append(self.assembleNode(creature))
        self.addMotors()

        return self.root

    def assembleEnvironment(self):
        self.root = XMLTree.Element("mujoco")
        timestep_elem = XMLTree.Element("option")
        timestep_elem.text = "timestep=0.1"
        self.root.append(timestep_elem)
        self.worldbody = XMLTree.Element("worldbody")
        self.root.append(self.worldbody)
        self.worldbody.append(LIGHTING_ELEM)
        self.worldbody.append(GEOM_ELEM)

    def assembleNode(self, node):
        assembled = XMLTree.Element("body", {"name": node.name,
                                             "pos": DIR_TO_REL_POS[node.dir],})
        pos_attrs = {
            "type": "box",
            "size": f"{CUBEDIM/2} {CUBEDIM/2} {CUBEDIM/2}",
            "rgba": DIR_TO_RGBA[node.dir]
        }
        node_geom = XMLTree.Element("geom", pos_attrs)
        assembled.append(node_geom)
        node_joint = self.createJoint(node)
        assembled.append(node_joint)
        for child in node.children:
            if child.id == node.id:
                print(f"RECURSION {child.id}")
                break
            XMLchild = self.assembleNode(child)
            assembled.append(XMLchild)
        return assembled

    def createJoint(self, node):
        # non movement joint
        if node.joint_attrs == None:
            return
        
        # is root
        if node.joint_attrs["type"] == "free":
            return XMLTree.Element("freejoint")
        
        joint_name = f"node{node.id}_joint"
        motor_name = f"node{node.id}_motor"
        motor_attrs = {
            "joint": joint_name,
            "name": motor_name
        }
        motor = XMLTree.Element("motor", motor_attrs)
        self.motor_elems.append(motor)
        self.motor_data[motor_name] = Motor(node.joint_attrs["strength"],
                                            node.joint_attrs["offset"],
                                            node.joint_attrs["frequency"],
                                            node.joint_attrs["axis"])

        joint_attrs = {
            "pos": DIR_TO_JOINT_POS[node.dir],
            "name": joint_name,
            "type": node.joint_attrs["type"],
            "limited": "true",
            "range": node.joint_attrs["range"],
            "axis": DIR_TO_AXIS[node.dir]
        }
        return XMLTree.Element("joint", joint_attrs)

    def addMotors(self):
        actuator = XMLTree.Element("actuator")
        self.root.append(actuator)
        for motor in self.motor_elems:
            actuator.append(motor)

def get_default_creature():
    return Node(-1, {"type": "free"}, [])

def get_test_creature():
    a1 = Node(0, {"strength": 5, "frequency":  5, "offset": 0}, [])
    a2 = Node(0, {"strength": 10, "frequency": 5, "offset": 45}, [a1])
    a3 = Node(0, {"strength": 15, "frequency": 5, "offset": 90}, [a2])
    b1 = Node(1, {"strength": 5, "frequency":  5, "offset": 180}, [])
    b2 = Node(1, {"strength": 10, "frequency": 5, "offset": 225}, [b1])
    b3 = Node(1, {"strength": 15, "frequency": 5, "offset": 270}, [b2])
    c1 = Node(2, {"strength": 5, "frequency":  5, "offset": 180}, [])
    c2 = Node(2, {"strength": 10, "frequency": 5, "offset": 225}, [c1])
    c3 = Node(2, {"strength": 15, "frequency": 5, "offset": 270}, [c2])
    d1 = Node(3, {"strength": 5, "frequency":  5, "offset": 0}, [])
    d2 = Node(3, {"strength": 10, "frequency": 5, "offset": 45}, [d1])
    d3 = Node(3, {"strength": 15, "frequency": 5, "offset": 90}, [d2])
    # e = Node(4, {"strength": 5, "frequency":   5, "offset": 0}, [])
    basic_creature = Node(-1, {"type": "free"}, [a3,b3,c3,d3])
    return basic_creature

if __name__ == "__main__":
    basic_creature = get_test_creature()

    env = Environment()
    env.assemble(basic_creature)
    print(XMLTree.tostring(env.root))
    print(env.motor_data)

