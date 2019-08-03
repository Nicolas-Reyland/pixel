# Polygon handling for PiGUI
import matrix

stdout = False

def get_valid_positions(zone): # bruteforce

    (min_x, max_x), (min_y, max_y) = zone.rectangle()

    node_positions = zone.node_positions()
    valid_positions = []

    for y in range(min_y,max_y):
        for x in range(min_x,max_x):

            if point_in_polygon(node_positions, (x,y), length=max_x + 1):
                valid_positions.append((x,y))

    return valid_positions


def get_valid_positions_v2(zone): # jumping-rabbit-algorithm (line-equations, etc.)

    (min_x, max_x), (min_y, max_y) = zone.rectangle()

    nodes = zone.node_positions()
    valid_positions = []

    # build equations
    equations = []
    last_node = nodes[-1]
    for node in nodes:
        start, end = min(node[0], last_node[0]), max(node[0], last_node[0])
        #                 start-end x   line equation                         in case of ZeroDivisionError
        equations.append([(start, end), matrix.line_equation(last_node, node), max(node[1], last_node[1])])
        last_node = node

    # main loop
    for x in range(min_x, max_x):

        # starting point in or out of the shape ?
        inside = True # point_in_polygon(nodes, (min_x, min_y), length=max_x - min_x + 1)

        # get all equations that are in this column
        valid_equations = list(filter(lambda eq: eq[0][0] <= x <= eq[0][1], equations))

        # this is because of vertical lines
        while True: # more efficiant way to do that ?
            try:
                valid_equations = list(sorted(valid_equations, key=lambda eq: eq[1](x)))
                break
            except ZeroDivisionError:
                valid_equations2 = []
                for eq in valid_equations:
                    try:
                        eq[1](x)
                    except ZeroDivisionError:
                        eq = [eq[0], lambda x: eq[2], eq[2]]
                    valid_equations2.append(eq)
                valid_equations = valid_equations2[:]

        y = valid_equations[0][1](x)
        valid_equations.pop(0)

        # iterate through the equations
        for eq in valid_equations:

            # add valid positions
            if y == eq[1](x) and inside:
                valid_positions.append((x,int(y)))
            elif inside:
                valid_positions.extend( [(x,valid_y) for valid_y in range( int(y), min(int(eq[1](x)), max_y) )] )

            y = eq[1](x)
            inside = not inside
   
    return valid_positions


def get_valid_positions_v3(zone): # area-dodging algorithm
    pass
    # may be fun to implement
    # but I'm sure it's not quite as fast as the jumping-rabbit-algorithm




def point_in_polygon(nodes, position, length=1):

    # (position - position2)-line is parallel to the x-axis
    position2 = (position[0] + length, position[1])

    number_of_collisions = ray_cast_algorithm(nodes, position, position2)
    if stdout: print(number_of_collisions)

    # if the number_of_collisions is even, the point is not in the polygon
    # else (if odd), the point is in the polygon
    # if there are 0 collisions... point is not in polygon...
    if number_of_collisions == 0:
        return False
    else:
        return bool(number_of_collisions % 2)


def ray_cast_algorithm(nodes, position, position2): # to test: line equal to pos-pos2

    epsilon = 1e-9

    lines = []
    last_node = nodes[-1]
    for node in nodes:
        lines.append([last_node, node])
        last_node = node # [:]

    number_of_collisions = 0
    end_point_collisions = []

    for line_index,line in enumerate(lines):
        prev_line = lines[line_index-1]

        if stdout: print('doing line {} to {}'.format(line[0], line[1]))
        if stdout: print(f'[b] number of collisions: {number_of_collisions}')

        # end-point collision
        if position[1] == line[0][1]:
            if stdout: print('end-line collision catched !')

            if position[0] > line[0][0]:
                if stdout: print('wrong side')
                continue

            next_y, prev_y = line[1][1], prev_line[0][1]
            cur_y = position[1]

            if prev_y < cur_y > next_y or prev_y > cur_y < next_y:
                continue
                if stdout: print('not good')

            else:
                if stdout: print('good')
                number_of_collisions += 1
                continue

        elif position[1] == line[1][1]:
            if stdout: print('collision in next detected')
            continue

        # check if line in vertical
        if line[0][0] == line[1][0]:
            if stdout: print('line is vertical')
            # 'edges' of the vertical line
            min_max_y = (min(line[0][1], line[1][1]), max(line[0][1], line[1][1]))

            # check if line which is being checked is on the right side
            if line[0][0] > position[0]:

                # lambda collision
                if min_max_y[0] < position[1] and min_max_y[1] > position[1]:
                    number_of_collisions += 1
                    if stdout: print('touching vertical line')

            continue

        # check if lines are parallel (no intersection...)
        if matrix.slope(line[0], line[1]) == matrix.slope(position, position2):
            if stdout: print('line & position-line are parallel')
            continue

        # coordinates
        x1,y1 = position
        x2,y2 = position2
        x3,y3 = line[0]
        x4,y4 = line[1]
        # intersection point calculation
        px = ( (x1*y2-y1*x2)*(x3-x4)-(x1-x2)*(x3*y4-y3*x4) ) / ( (x1-x2)*(y3-y4)-(y1-y2)*(x3-x4) )
        py = ( (x1*y2-y1*x2)*(y3-y4)-(y1-y2)*(x3*y4-y3*x4) ) / ( (x1-x2)*(y3-y4)-(y1-y2)*(x3-x4) )
        # intersection coordinates
        intersection = (px,py)
        if stdout: print(f'intersection at {intersection}')

        if min(line[0][0], line[1][0]) > intersection[0]  or max(line[0][0], line[1][0]) < intersection[0]:
            # could do <= and >= (precision up to 1e-15, but should be enough like this)
            if stdout: print('intersection not on line')
            continue

        # distance which should be 0
        if stdout: print('position, intersection, position2 =',position, intersection, position2)
        if stdout: print(matrix.distance2d(position, intersection), matrix.distance2d(intersection, position2), matrix.distance2d(position, position2))
        distance_zero = matrix.distance2d(position, intersection) + matrix.distance2d(intersection, position2) - matrix.distance2d(position, position2)

        inter_vect = matrix.vector.normalize(matrix.vector.vector(line[0],line[1]))
        base_vect = matrix.vector.normalize(matrix.vector.vector(line[0], intersection))
        if stdout: print('inter, base =', inter_vect, base_vect)

        sign_vect = matrix.vector.multiplication(inter_vect, base_vect)

        if stdout: print(f'distance-zero: {distance_zero}, sign_vect: {sign_vect}')

        # check this distance AND if the direction of the source->intersection is the same as the source->base_coordinates
        if -epsilon < distance_zero < epsilon and sign_vect[0] > 0 and sign_vect[1] > 0:
            if stdout: print('collision at intersection verified')
            number_of_collisions += 1
        else:
            if stdout: print('collision at intersection canceled')


        if stdout: print(f'[a] number of collisions: {number_of_collisions}')

    
    if stdout: print(f'final: {number_of_collisions}, {end_point_collisions}')
    
    if len(end_point_collisions) == number_of_collisions and False:
        if stdout: print('only end-point collisions + not legal')
        number_of_collisions = 0

    return number_of_collisions


# - Smoothing Algotihms -
def chaikin(nodes, n=4):

    new_nodes = []
    for i in range(-1, len(nodes)-1):
        p_p1_vector = matrix.vector.vector(nodes[i], nodes[i+1])
        q = matrix.vector.multiplication_k(p_p1_vector, 1/n)
        r = matrix.vector.multiplication_k(p_p1_vector, (n-1)/n)
        q = matrix.vector.add(nodes[i], q)
        r = matrix.vector.add(nodes[i], r)
        new_nodes.append(q)
        new_nodes.append(r)
    
    return new_nodes

def PAEK(nodes): # Polygonial Approximation ... Kernel ...
    pass

def bezier(nodes):
    pass





