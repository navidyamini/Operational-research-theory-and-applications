import random
import math
import operator


# generating uniform traffic matrix, in which the traffic sent from any source to
# any destination is a uniform random variable in the range [0.5;1.5],
def generating_traffic_matrix(min, max, node):
    tsd = [[0 for x in range(node)] for y in range(node)]
    for i in range(node):
        for j in range(node):
            if j != i:
                tsd[i][j] = random.uniform(min, max)
    # print tsd
    return tsd


# add the traffic between i and j with traffic between j and i
def bidirectional_creator(tm, node):
    btm = [[0 for x in range(node)] for y in range(node)]
    for i in range(node):
        for j in range(i):
            btm[j][i] = tm[i][j] + tm[j][i]
    return btm


def creating_flow_vector(tsd, node):
    fv = []
    for i in range(node):
        for j in range(node):
            fv.append([tsd[i][j], i, j])
    # sorting flow vector
    fv.sort(reverse=True)
    return fv


def bidirectional_flow_vector_creator(fv, node):
    bfv = []
    for i in range(node):
        for j in range(node):
            if fv[i][j] != 0:
                bfv.append([fv[i][j], i, j])
    bfv.sort(reverse=True)
    return bfv


# sum all the traffic of node n
def total_nodes_traffic_calculator(bfw, node):
    tnt = []
    for n in range(node):
        sum_node_traffic = 0
        for i in range(len(bfw)):
            if (bfw[i][1] == n or bfw[i][2] == n):
                sum_node_traffic += bfw[i][0]
        tnt.append([sum_node_traffic, n])
    tnt.sort(reverse=True)
    return tnt


def get_place(topology, size, deltas):
    while deltas >= 0:
        # look at each place of the manhatan
        for i in range(size):
            for j in range(size):
                free_neighbors = []
                # check if this place is free
                if topology[i][j] == -1:

                    # check all the neighbors
                    # right
                    if topology[i][(j + 1) % size] == -1:
                        free_neighbors.append([i, (j + 1) % size])
                    # left
                    if topology[i][(j + size - 1) % size] == -1:
                        free_neighbors.append([i, (j + size - 1) % size])
                    # down
                    if topology[(i + 1) % size][j] == -1:
                        free_neighbors.append([(i + 1) % size, j])
                    # up
                    if topology[(i + size - 1) % size][j] == -1:
                        free_neighbors.append([(i + size - 1) % size, j])
                    if deltas == len(free_neighbors):
                        return i, j, free_neighbors
                    if i == (size - 1) and j == (size - 1):
                        deltas -= 1


def manhatan_creator(tnt, bfv, node, deltas):
    # type: (object, object, object, object) -> object
    # at the beginning all the nodes in side our topology is equal to -1. it means that, that place is empty and we
    # are going to replace -1 with 0 to 15 node's numbers.
    size = int(math.sqrt(node))
    topology = [[-1 for x in range(size)] for y in range(size)]
    placed_node = []
    counter = 0
    while len(placed_node) != node:
        current_node = tnt[counter][1]
        # first check that if we placed the node before or not
        if not (current_node in placed_node):
            # get the palce that we should put the node
            row_index, column_index, neighbors = get_place(topology, size, deltas)
            # fix the node in manhatan topology
            topology[row_index][column_index] = current_node
            placed_node.append(current_node)
            for i in range(len(neighbors)):
                flag = 0
                for j in range(len(bfv)):
                    if flag == 0:
                        # search the neighbor
                        if bfv[j][1] == current_node:
                            # get the potential neighbor
                            current_neighbor = bfv[j][2]
                            if not (current_neighbor in placed_node):
                                # get the palce of the neighbor
                                p = neighbors[i][0]  # raw
                                q = neighbors[i][1]  # column
                                topology[p][q] = current_neighbor
                                placed_node.append(current_neighbor)
                                flag = 1
                        if bfv[j][2] == current_node:
                            # get the potential neighbor
                            current_neighbor = bfv[j][1]
                            if not (current_neighbor in placed_node):
                                # get the palce of the neighbor
                                p = neighbors[i][0]  # raw
                                q = neighbors[i][1]  # column
                                topology[p][q] = current_neighbor
                                placed_node.append(current_neighbor)
                                flag = 1
                                # go to the next node for placing in topology
        counter += 1
    return topology


def sending_flows(keys, flow):
    # sending flows and adding the flows on every ij to find the fmax
    global flows
    for k in range(len(keys)):
        if keys[k] in flows:
            flows[keys[k]] += flow
        else:
            flows[keys[k]] = flow
    return


def line_checking(s2, d1, d2, keys, flow, size):
    # check if this is the neighbor
    if s2 == d2:
        sending_flows(keys, flow)
    # check if it is a right neighbor
    if (s2 + 1) % size == d2:
        keys.append(str(d1) + str(s2) + str(d1) + str(d2))
        sending_flows(keys, flow)
    # check if it is a right-right neighbor
    if (s2 + 2) % size == d2:
        # right
        keys.append(str(d1) + str(s2) + str(d1) + str((s2 + 1) % size))
        # right
        keys.append(str(d1) + str((s2 + 1) % size) + str(d1) + str(d2))
        sending_flows(keys, flow)
    # check if it is a left neighbor
    if (s2 + size - 1) % size == d2:
        keys.append(str(d1) + str(s2) + str(d1) + str(d2))
        sending_flows(keys, flow)
    return


def dictionary_creator(topology, size):
    manhatan_dict = dict()
    for i in range(size):
        for j in range(size):
            manhatan_dict[topology[i][j]] = [i, j]  # node_id, row, column
    return manhatan_dict


def route(fv, topology, node):
    size = int(math.sqrt(node))
    manhatan_dict = dictionary_creator(topology, size)

    # the key is the link i + j and the value is the flow:
    global flows
    flows.clear()
    for v in range(len(fv)):
        flow = fv[v][0]
        sid = fv[v][1]  # source_id
        did = fv[v][2]  # dest_id
        s1 = manhatan_dict[sid][0]  # row
        s2 = manhatan_dict[sid][1]  # column
        d1 = manhatan_dict[did][0]
        d2 = manhatan_dict[did][1]

        keys = []
        # check if we are in the same row
        if s1 == d1:
            line_checking(s2, d1, d2, keys, flow, size)
        # check if dest_id is one row below
        if (s1 + 1) % size == d1:
            # down
            keys.append(str(s1) + str(s2) + str(d1) + str(s2))
            line_checking(s2, d1, d2, keys, flow, size)
        # check if dest_id is two rows below
        if (s1 + 2) % size == d1:
            # down
            keys.append(str(s1) + str(s2) + str((s1 + 1) % size) + str(s2))
            # down
            keys.append(str((s1 + 1) % size) + str(s2) + str(d1) + str(s2))
            line_checking(s2, d1, d2, keys, flow, size)
        # check if dest_id is one row above
        if (s1 + size - 1) % size == d1:
            # up
            keys.append(str(s1) + str(s2) + str((s1 + size - 1) % size) + str(s2))
            line_checking(s2, d1, d2, keys, flow, size)

    return sorted(flows.items(), key=operator.itemgetter(1))


def copy_manhatan(ft, size):
    topology = [[0 for x in range(size)] for y in range(size)]
    for i in range(size):
        for j in range(size):
            topology[i][j] = ft[i][j]
    return topology

def probability(fmax,new_fmax,temperature):
    if new_fmax < fmax:
        return 1.0
    else:
        return math.exp((fmax - new_fmax) / temperature)

def simulating_annealing(fv,first_topology, node,fmax):

    size = int(math.sqrt(node))
    best_topology = first_topology

    #set initial temp
    temperature = 1000000
    #Cooling rate
    coolingrate = 0.003;
    best_fmax = fmax

    while temperature > 1:
        topology = first_topology
        manhatan_dic = dictionary_creator(topology, size)
        node1 = random.randint(0, nodes - 1)
        node2 = random.randint(0, nodes - 1)
        while node2 == node1:
            node2 = random.randint(0, nodes - 1)
        i1 = manhatan_dic[node1][0]
        j1 = manhatan_dic[node1][1]
        i2 = manhatan_dic[node2][0]
        j2 = manhatan_dic[node2][1]
        temp = topology[i1][j1]
        topology[i1][j1] = topology[i2][j2]
        topology[i2][j2] = temp
        sorted_flows = route(fv, topology, node)
        new_fmax = sorted_flows[len(sorted_flows) - 1][1]
        #probability to d ecide if we should accept the new one
        p = probability(fmax,new_fmax,temperature)
        rand = random.random()
        if p > rand:
            fmax = new_fmax
            first_topology = topology
        if fmax < best_fmax:
            best_fmax = fmax
            best_topology_= first_topology
        temperature *= 1 - coolingrate
    return best_fmax, best_topology


# main part starts from here

# minimum and maximum ranges for generating random number
minimum = 0.5
maximum = 1.5
simulations = []
flows = dict()

# getting all the data that we need from user
nodes = 16  # int(raw_input("Enter the number of nodes: "))
deltas = 4  # int(raw_input("\nEnter the number of delta: "))
number_of_simulation = 10000  # int(raw_input("\nEnter the number of simulations: "))

flows.clear()
traffic_matrix = generating_traffic_matrix(minimum, maximum, nodes)
bidirectional_traffic_matrix = bidirectional_creator(traffic_matrix, nodes)
flow_vector = creating_flow_vector(traffic_matrix, nodes)
bidirectional_flow_vector = bidirectional_flow_vector_creator(bidirectional_traffic_matrix, nodes)
total_nodes_traffic = total_nodes_traffic_calculator(bidirectional_flow_vector, nodes)
manhatan_topology = manhatan_creator(total_nodes_traffic, bidirectional_flow_vector, nodes, deltas)
sorted_flows = route(flow_vector, manhatan_topology, nodes)
fmax = sorted_flows[len(sorted_flows) - 1][1]
# printing the results
print "\nFirst Manhatan Topology"
for i in range(int(math.sqrt(nodes))):
    print manhatan_topology[i]
print "\nFirst fmax"
print str(fmax)

# caling simulating annealing function for finding better solution

#new_manhatan_topology =
Best_fmax , Best_topoloty = simulating_annealing(flow_vector,manhatan_topology, nodes,fmax)
print "\nBest Manhatan Topology"
for i in range(int(math.sqrt(nodes))):
    print Best_topoloty[i]
print "\nBest fmax"
print str(Best_fmax)