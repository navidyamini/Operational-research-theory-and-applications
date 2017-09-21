import random
import numpy

path =[]
path_found = 0
total_paths = 0
# generating uniform traffic matrix, in which the traffic sent from any source to
# any destination is a uniform random variable in the range [0.5;1.5],
def generating_traffic_matrix(min, max, node):
    #the case for which 10 % of traffic demands belongs to the high-traffic class
    tsd = [[0 for x in range(node)] for y in range(node)]
    for i in range(node):
        for j in range(node):
            if j != i:
                # with probability 0.1
                probability = (random.randint(1, 10))*0.1
                if (probability !=0.1):
                    tsd[i][j] = random.uniform(min, max)
                else:
                    tsd[i][j] = random.uniform(5, 15)
    return tsd


# by using this function, we create the vector that each elemnt on vector shows
# the traffic flow between node i and j
def creating_flow_vector(tsd, node):
    fv = []
    for i in range(node):
        for j in range(node):
            fv.append([tsd[i][j], i, j])
    # print fv
    return fv


# by using this function, we create bij matrix.( the links between i and j)
def bij_creator(fv, node, delta):
    bij = [[0 for x in range(node)] for j in range(node)]
    # check all flows to send
    for i in range(len(fv)):
        sum_photodiodes = [0 for x in range(node)]
        sum_lasers = [0 for x in range(node)]
        # update the sum of lightpaths in and out from node x
        for x in range(node):
            for y in range(node):
                sum_photodiodes[x] += bij[y][x]
                sum_lasers[x] += bij[x][y]
        if fv[i][0] != 0:
            # check all the lightpaths in and out of node i and node j
            if sum_lasers[fv[i][1]] < delta and sum_photodiodes[fv[i][2]] < delta:
                # create the link
                bij[fv[i][1]][fv[i][2]] = 1
            else:
                # no link created
                bij[fv[i][1]][fv[i][2]] = 0
    return bij


# multiplying traffic matrix with b_ij matrix. in b_ij matrix 0 means that there is no link between i and j
# by using this function we will set the flow that can pathing from that links to zero
def flow_matrix_creator(bij, tsd, node):
    fm = [[0 for x in range(node)] for j in range(node)]
    for i in range(node):
        for j in range(node):
            fm[i][j] = tsd[i][j] * bij[i][j]
    # print fm
    return fm


def make_route(i, d, visited, bij, node):
    global path_found
    global path
    visited.append(i)
    if bij[i][d] == 1:
        path.append([i, d])
        visited.append([d])
        path_found += 1
        return #(path, path_found)
    else:
        for j in range(node):
            if (j != i and not (j in visited)):
                if bij[i][j] == 1:
                    path.append([i, j])
                    visited.append([j])
                    if j == d:
                        path_found += 1
                        return# (path, path_found)

                    else:
                        return make_route(j, d, visited, bij, node)


def routes(node, fm, bij, tm):
    #path_found = 0
    global total_paths
    global path
    for s in range(node):
        for d in range(node):
            if s != d and bij[s][d] == 0:
                path = []
                total_paths += 1
                #path, path_found = make_route(s, d, path, [], bij, node)
                make_route(s, d, [], bij, node)
                for x in range(len(path)):
                    # update the new flows
                    fm[path[x][0]][path[x][1]] += tm[s][d]
    return fm

def fmax_calculator(nfm,node):
    fv = [[0 for x in range(node)] for j in range(node)]
    for i in range(node):
        for j in range(node):
            fv.append([nfm[i][j], i, j])  # [traffic flow of the link][i][j]
    fv.sort(reverse=True)
    return fv


# main part starts from here

# minimum and maximum ranges for generating random number
minimum = 0.5
maximum = 1.5
simulations = []
# geting all the data that we need from user
nodes = int(raw_input("Enter the number of nodes: "))
deltas = int(raw_input("\nEnter the number of delta: "))
number_of_simulation = int(raw_input("\nEnter the number of simulations: "))

while(len(simulations)<number_of_simulation):
    path_found = 0
    total_paths = 0

    traffic_matrix = generating_traffic_matrix(minimum, maximum, nodes)

    flow_vector = creating_flow_vector(traffic_matrix, nodes)
    # sorting flow vector
    flow_vector.sort(reverse=True)


    b_ij_matrix = bij_creator(flow_vector, nodes, deltas)

    flow_matrix = flow_matrix_creator(b_ij_matrix, traffic_matrix, nodes)

    new_flow_matrix = routes(nodes, flow_matrix, b_ij_matrix, traffic_matrix)

    f_vector = fmax_calculator(new_flow_matrix,nodes)

    if (path_found == total_paths):
        simulations.append(f_vector[0][0])
        average = numpy.mean(simulations)
        print str(average)

