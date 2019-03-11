# importing libraries numpy and pandas for data storage and processing
import numpy as np
import pandas as pd
from graphics import *
win = GraphWin("test", 1000, 1000)

radius = 10
length = 30

def add_points(*pts):
    final = Point(0,0)
    for pt in pts:
        final.x += pt.x
        final.y += pt.y
    return final

def multiply_point(point, value):
    x = point.x * value
    y = point.y * value
    return Point(x,y)

def print_node(data, center):
    # Making the circle
    cir = Circle(center, radius)
    cir.draw(win)

    # Inserting text
    message = Text(center, data)
    message.draw(win)

# Print / or \. start gives the center of the circle to start from
# Function returns the coordinate to the next node
def print_line(right, start):

    one_by_root_two = 1/(2**0.5)
    unit_vector_right = Point(one_by_root_two, one_by_root_two)
    unit_vector_left = Point(-1 * one_by_root_two, one_by_root_two)
    spacing_right = multiply_point(point=unit_vector_right, value=radius+1)
    spacing_left = multiply_point(point=unit_vector_left, value=radius+1)

    if right:
        # TODO: Print \ of constant length with starting coordinate start + spacing_right
        start = add_points(start, spacing_right)
        end = add_points(start, multiply_point(point=unit_vector_right, value=length))
        next_center =  add_points(end, spacing_right)

    else:
        # TODO: Print \ of constant length with starting coordinate start + spacing_right
        start = add_points(start, spacing_left)
        end = add_points(start, multiply_point(point=unit_vector_left, value=length))
        next_center = add_points(end, spacing_left)
    line = Line(start, end)
    line.draw(win)

    return  next_center

# Printing the complete tree(node list) based on nid using recursion
def print_tree(tree, root_id=1, center=Point(win.getWidth()/2,radius + 1)):
    # Capturing the root
    root_node = next(element for element in tree if element.nid == root_id)

    # printing the node as nid
    print_node(root_node.nid, center)

    # Check if the tree has root == leaf
    if root_node.right == 0:
        return

    # Now print the right child tree
    center_right = print_line(right=True, start=center)
    print_tree(tree=tree, root_id=root_node.right, center=center_right)

    # Now print the left child tree
    center_left = print_line(right=False, start=center)
    print_tree(tree=tree, root_id=root_node.left, center=center_left)
# function to check if a split is worth it
def worthy(parent_df, left_child_df, right_child_df):
    flag = False
    gain = np.var(parent_df["output"]) - (len(left_child_df["output"])*np.var(left_child_df["output"]) - len(right_child_df["output"])*np.var(right_child_df["output"]))/(len(parent_df["output"]))
    if gain > limit_percentage * np.var(parent_df["output"]):
        flag = True
    return flag

# condition_True takes dataframe(df) and condition to split(split_condition) ,and returns final data-frame if the condition is True in df
def condition_True(df, split_condition):
    new_df = df[eval(split_condition)]
    return new_df


# condition_false takes dataframe(df) and condition to split(split_condition) ,and returns final data-frame if the condition is false in df
def condition_false(df, split_condition):
    #new_split_condition = "!(" + split_condition + ")"
    #.print(df)
    condition_str=split_condition
    x=eval(condition_str)
    x=1-x
    bool_list = list(map(bool,x))
    
    
    #new_split_condition="not"+" "+split_condition
    new_df = df[bool_list]

    return new_df
#function to take take two lists or series and return the weighted variance
def wt_variance(ser1,ser2):
    return (len(ser1)*np.var(ser1)+len(ser2)*np.var(ser2))/(len(ser1)+len(ser2))

# convention is left -> false and right -> True
def make_nodes(parent_node):

    global no_of_nodes

    # first, the left and right dataframes
    df_right = condition_True(df=parent_node.data.df, split_condition=parent_node.data.split_condition)
    df_left = condition_false(df=parent_node.data.df, split_condition=parent_node.data.split_condition)

    # Checking if the split is worthy
    worthy_split = worthy(parent_df=parent_node.data.df, left_child_df=df_left, right_child_df=df_right)

    if not worthy_split:
        parent_node.right = 0
        parent_node.left = 0
        return None,None

    # making the node-data
    right_node_data = Node_data(df=df_right)
    left_node_data = Node_data(df=df_left)

    # assigning new node ids
    no_of_nodes += 1
    right_nid = no_of_nodes
    no_of_nodes += 1
    left_nid = no_of_nodes

    # Assigning the parent's left and right child id
    parent_node.right = right_nid
    parent_node.left = left_nid

    # making the left and right nodes
    right_node = Node(nid=right_nid, data=right_node_data)
    left_node = Node(nid=left_nid, data=left_node_data)

    return left_node, right_node

# function to make the tree out of a data-set
def make_tree(dataset):

    global no_of_nodes

    # variable to store node list
    nodes = []

    # Making root node
    no_of_nodes += 1
    root_node_data = Node_data(df=dataset)
    root_node = Node(nid=no_of_nodes, data=root_node_data)
    nodes.append(root_node)

    # Initializing the parent to be root
    parent = root_node
    while True:

        # Storing the children after split
        
        left_child, right_child = make_nodes(parent_node=parent)

        if right_child == None:
            # Meaning parent is a leaf
            nodes[nodes.index(parent)].left = 0
            nodes[nodes.index(parent)].right = 0
            
            while True:
                # Check if the leaf is right child
                parent_from_right = next((x for x in nodes if x.right == parent.nid), None)
                if parent_from_right == None:
                    # If parent is left child, make the new parent to check, parent of parent
                    parent = next((x for x in nodes if x.left == parent.nid),None)
                    if parent.nid == 1:
                        return nodes
                else:
                    # If parent is right child, make the sibling parent 
                    parent = next((x for x in nodes if x.nid == parent_from_right.left),None)
                    break
        else:
            nodes.append(right_child)
            nodes.append(left_child)
            parent = right_child

no_of_nodes = 0
limit_percentage = 0.05

# declaring class to store node data for the tree
class Node_data():

    # df stores the data-set at this point and split_condition stores the condition to split as a string
    def __init__(self, df, split_condition = "", mean = 0):
        # initialising the variables
        self.df = df
        self.split_condition = self.make_split_condition(df=df)
        self.mean = np.mean(df["output"])

    # make_split_condition takes the dataframe and returns the best split condition
    def make_split_condition(self, df):
        condition_list = ["X1", 0]
        condition = ''
        attributes = list(df.columns.values)
        attributes.remove("output")
        min_var = np.var(df["output"])
        #print(min_var)
        for column in attributes:
            df_current = df.loc[:, [column, 'output']]
            df_current = df_current.sort_values(column)

            for element in df_current[column].unique()[1:]:
                ser1 = df_current[df_current[column] < element]["output"]
                ser2 = df_current[df_current[column] >= element]["output"]
                curr_var = wt_variance(ser1, ser2)
                if curr_var < min_var:
                    condition_list[0] = column
                    condition_list[1] = element
                    min_var = curr_var
            #print(min_var)
        condition += "df[\'%s\']<%.2f" % (condition_list[0], condition_list[1])

        return condition


# declaring node class
class Node():

    # nid stores id of the node, data is object of the Node_Data class, left stores id of the left child, and right stores id of the right child
    # -1 indicates uninitialised, 0 indicates leaf
    def __init__(self, nid, data, left=-1, right=-1):
        # initialising the variables
        self.nid = nid
        self.data = data
        self.left = left
        self.right = right

data = pd.read_csv("train.csv")
tree = make_tree(data)
print_tree(tree)
win.getMouse()
'''test_node_data=Node_data(df=data)
test_node=Node(nid=1,data=test_node_data)
test_node.data.split_condition
'''