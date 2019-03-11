from graphics import *
win = GraphWin("test", 1000, 1000)

radius = 10
length = 10

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
        start = add_points(start, spacing_right)
        end = add_points(start, multiply_point(point=unit_vector_right, value=length))
        next_center =  add_points(end, spacing_right)

    else:
        start = add_points(start, spacing_left)
        end = add_points(start, multiply_point(point=unit_vector_left, value=length))
        next_center = add_points(end, spacing_left)
    line = Line(start, end)
    line.draw(win)

    return  next_center

# Printing the complete tree(node list) based on nid using recursion
def print_tree(tree, root_id=1, center=Point(win.getWidth()/2,radius + 1)):
    global length
    # Capturing the root
    root_node = next(element for element in tree if element.nid == root_id)

    # printing the node as nid
    print_node(root_node.nid, center)

    # Check if the tree has root == leaf
    if root_node.right == 0:
        return
    
    length /= 1.5
    # Now print the right child tree
    center_right = print_line(right=True, start=center)
    print_tree(tree=tree, root_id=root_node.right, center=center_right)

    # Now print the left child tree
    center_left = print_line(right=False, start=center)
    print_tree(tree=tree, root_id=root_node.left, center=center_left)