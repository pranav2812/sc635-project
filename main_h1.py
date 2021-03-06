#!/usr/bin/env python3

"""
Algorithm 1: Heuristic for MILC(MILC - H1).
Input: movement and communication graphs GM, GC, sensing locations VS, number of UAVs r, latency bound Lc
Output: subtours t 1, . . ., t k, MLP and schedule (st(v), sv v, ev v, st v) ∀v ∈ V S
"""

# G = {0: {1, 3, 4}, 1: {0, 4, 2}, 2: {1, 4, 5}, 3: {0, 1, 4, 7, 6}, 4: {0, 1, 2, 5, 8, 7, 6, 3},
#      5:{1,2,4,7,8}, 6:{3,4,7,10,9}, 7:{3,4,5,,8,11,10,9,6}, 8:{5,4,7,10,11}, 9:{}}


import numpy as np
from utils_h1 import min_latency, solve_tsp, split_tour, distGM, minmax_matching, mlp, plot_graph, list_to_str, com_to_str

# 8 -> SL, 0 -> BS

# Movement Graph
Gm = {8: [5], 5: [4, 8, 6], 6: [5], 4: [5, 3], 3: [4, 2], 2: [3, 1], 1: [2, 7, 0], 7: [1], 0: [1]}

# Communication Graph
Gc = {8: [5, 4, 6], 5: [8, 6], 6: [5, 8, 7], 4: [3, 8], 3: [4, 2], 2: [3, 1], 1: [2, 7, 0], 7: [1, 6], 0: [1]}

plot_graph(Gm, "Movement Graph")
plot_graph(Gc, "Communication Graph")

# Vs = [8, 4]  # List of SLs
Vs = 8  # SL for the graph
r = 3  # Maximum Number of UAVs
Lc = 4  # Maximum Latency
V0 = 0  # Base station Node

# Vs = [int(x) for x in input("List of sensing locations (space separated) : ").split(" ")]
Vs = [int(input("List of sensing locations : "))]
r = int(input("Maximum Number of UAVs : "))
Lc = int(input("Maximum Latency : "))

x = min_latency(Vs=Vs, v0=V0, num_uav=r, Gm=Gm, Gc=Gc)
for i in range(len(x)):
    if x[i][0] > Lc:
        print("This mission cannot be completed in given Latency bound. Please increase the bound or number of UAVs")
        exit()
for i in range(len(x)):
    print("=" * 100)
    print("sensing location : " + str(Vs[i]))
    print("time taken : " + str(x[i][0]))
    print("number of UAVs used : " + str(len(x[i][1])))
    print("route of information : " + list_to_str(x[i][1]))
    print("communication links used : " + com_to_str(x[i][1]))

exit()
optimal_path_in_points_idxs, optimal_path_in_sets_idxs, optimal_cost, distance_matrix = solve_tsp(Vs, Gm)
print(optimal_path_in_points_idxs, optimal_path_in_sets_idxs, optimal_cost)


def give_m1(Gm, Gc, Vs, r, Lc, V0):
    gammas = [float('inf') for v in range(len(Vs))]

    for num_uav in range(r, 0, -1):
        # All MLPs from all v ∈ Vs to the BS with i UAVs:
        dist_array = min_latency(Vs, V0, num_uav, Gm, Gc)

        for ii in range(len(Vs)):
            if dist_array[ii] <= Lc:
                gammas[ii] = num_uav

    if max(gammas) > r:
        print("Problem is infeasible!")
        return None

    new_Vs = [v for v in Vs if v not in Gc[V0]]
    gamma = max(new_Vs)
    k = r // gamma

    optimal_path_in_points_idxs, optimal_path_in_sets_idxs, optimal_cost, distance_matrix = solve_tsp(Vs, Gm)
    print("----")
    print(optimal_path_in_points_idxs, k, Lc)
    print(distance_matrix)
    exit()
    tour_array = split_tour(optimal_path_in_points_idxs, k, Lc, distance_matrix)

    for ii in range(1, k + 1):
        Ri = list(range((ii - 1) * gamma + 1, ii * gamma + 1))
        v_ = V0
        old_sv_array, old_ev_array, old_st_array, old_et_array = mlp(v_, V0, gammas[v_], Gm, Gc)
        stv_ = 0
        for v in tour_array[num_uav]:
            (sv_array, ev_array, st_array, et_array) = mlp(v, V0, gammas[v], Gm, Gc)

            num_rows = len(list(range(1, gammas[v])))
            num_cols = len(Ri)
            A = [[0 for i in range(num_cols)] for i in range(num_rows)]

            for ll in range(1, gammas[v]):
                for mm in Ri:
                    A[ll][mm] = stv_ + old_et_array[mm] + distGM(Gm, old_ev_array[mm] + sv_array[ll])

            M = minmax_matching(A)

            for mm in Ri:
                sv_array[mm] = sv_array[M[mm]]
                ev_array[mm] = ev_array[M[mm]]
                st_array[mm] = st_array[M[mm]]
                et_array[mm] = et_array[M[mm]]
            stv_ = stv_ + min([old_et_array[mm] + distGM(Gm, old_ev_array[mm], sv_array[mm]) for mm in Ri])
            v_ = v
            old_ev_array, old_et_array = ev_array, et_array


give_m1(Gm, Gc, Vs, r, Lc, V0)
