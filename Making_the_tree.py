# importing libraries numpy and pandas for data storage and processing
import numpy as np

min_leaf_size = 0
no_of_nodes = 0
limit_percentage = 0.001


def abs_error_of_data(array, value=-1):
    if value == -1:
        value = np.mean(array)
    error = 0
    for element in array:
        error += abs(element - value)
    return error


def mean_squared_error_of_data(array, value=-1):
    if value == -1:
        value = np.mean(array)
    error = 0
    for element in array:
        error += (element - value) ** 2
    return error


error_function = mean_squared_error_of_data


# declaring class to store node data for the tree
class NodeData:

    # df stores the data-set at this point and split_condition stores the condition to split as a string
    def __init__(self, df, split_condition="", mean=0):
        # initialising the variables
        self.df = df
        self.split_condition = self.make_split_condition(df=df)
        self.mean = np.mean(self.df[df.columns[-1]])

    # make_split_condition takes the data-frame and returns the best split condition
    def make_split_condition(self, df):
        global error_function
        attributes = list(df.columns.values)
        attributes.remove(df.columns[-1])
        output_values = df[df.columns[-1]]
        condition_list = [attributes[0], 0]
        min_var = error_function(output_values)

        for column in attributes:
            df_current = df.loc[:, [column, df.columns[-1]]]
            df_current = df_current.sort_values(column)

            for element in df_current[column].unique()[1:]:
                ser1 = df_current[df_current[column] < element][df.columns[-1]]
                ser2 = df_current[df_current[column] >= element][df.columns[-1]]
                curr_var = wt_variance(ser1, ser2)
                if curr_var < min_var:
                    condition_list[0] = column
                    condition_list[1] = element
                    min_var = curr_var
        condition = "df[\'%s\']<%.2f" % (condition_list[0], condition_list[1])

        return condition


# declaring node class
class Node:

    # nid stores id of the node, data is object of the NodeData class, left stores id of the left child, and right stores id of the right child
    # -1 indicates uninitialised, 0 indicates leaf
    def __init__(self, nid, data, left=-1, right=-1):
        # initialising the variables
        self.nid = nid
        self.data = data
        self.left = left
        self.right = right


# function to check if a split is worth it
def worthy(parent_df, left_child_df, right_child_df):
    global error_function
    flag = False
    left_child_size = len(left_child_df[left_child_df.columns[-1]])
    right_child_size = len(right_child_df[right_child_df.columns[-1]])
    if left_child_size >= min_leaf_size and right_child_size >= min_leaf_size:
        parent_error = error_function(parent_df[parent_df.columns[-1]])
        left_child_error = error_function(left_child_df[left_child_df.columns[-1]])
        right_child_error = error_function(right_child_df[right_child_df.columns[-1]])
        gain = parent_error - (left_child_size * left_child_error - right_child_size * right_child_error) / (
            len(parent_df[parent_df.columns[-1]]))
        if gain > limit_percentage * parent_error:
            flag = True
    return flag


# condition_true takes data-frame(df) and condition to split(split_condition) ,and returns final data-frame
def condition_true(df, split_condition):
    new_df = df[eval(split_condition)]
    return new_df


# condition_false takes data-frame(df) and condition to split(split_condition) ,and returns final data-frame
def condition_false(df, split_condition):
    # new_split_condition = "!(" + split_condition + ")"
    condition_str = split_condition.replace("<", ">=")
    new_df = df[eval(condition_str)]
    return new_df


# function to take take two lists or series and return the weighted variance
def wt_variance(ser1, ser2):
    global error_function
    return (len(ser1) * error_function(ser1) + len(ser2) * error_function(ser2)) / (len(ser1) + len(ser2))


# convention is left -> false and right -> True
def make_nodes(parent_node):
    global no_of_nodes

    # first, the left and right dataframes
    df_right = condition_true(df=parent_node.data.df, split_condition=parent_node.data.split_condition)
    df_left = condition_false(df=parent_node.data.df, split_condition=parent_node.data.split_condition)

    # Checking if the split is worthy
    worthy_split = worthy(parent_df=parent_node.data.df, left_child_df=df_left, right_child_df=df_right)

    if not worthy_split:
        parent_node.right = 0
        parent_node.left = 0
        return None, None

    # making the node-data
    right_node_data = NodeData(df=df_right)
    left_node_data = NodeData(df=df_left)

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
    root_node_data = NodeData(df=dataset)
    root_node = Node(nid=no_of_nodes, data=root_node_data)
    nodes.append(root_node)

    # Initializing the parent to be root
    parent = root_node
    while True:

        # Storing the children after split

        left_child, right_child = make_nodes(parent_node=parent)

        if right_child is None:
            # Meaning parent is a leaf
            nodes[nodes.index(parent)].left = 0
            nodes[nodes.index(parent)].right = 0

            while True:
                # Check if the leaf is right child
                parent_from_right = next((x for x in nodes if x.right == parent.nid), None)
                if parent_from_right is None:
                    if parent.nid is 1:
                        return nodes

                    # If parent is left child, make the new parent to check, parent of parent
                    parent = next((x for x in nodes if x.left == parent.nid), None)
                    if parent.nid == 1:
                        return nodes
                else:
                    # If parent is right child, make the sibling parent 
                    parent = next((x for x in nodes if x.nid == parent_from_right.left), None)
                    break
        else:
            nodes.append(right_child)
            nodes.append(left_child)
            parent = right_child
