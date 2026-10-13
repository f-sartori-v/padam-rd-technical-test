# Greedy construction of an edge-covering route

## Problem interpretation

I interpret the task as finding one continuous walk that traverses every required edge of an undirected weighted graph, while keeping the total traversal cost low. Repeated edges are allowed and the start and end vertices are unrestricted. This corresponds to an open postman formulation.

My implementation constructs an initial feasible route using greedy pairing, then extracts an Eulerian traversal. Simulated annealing is proposed future work and is not implemented in the submitted code.

## My approach

### Connectivity and degree checks

I build adjacency lists, count connected components containing edges and identify odd-degree vertices. Every original edge occurrence is counted, including parallel edges. Self-loops contribute two to the degree. Isolated vertices do not affect the edge-covering route.

For a connected undirected graph:

- With zero odd vertices, an Eulerian circuit can start at any vertex incident to an edge.
- With two odd vertices, an Eulerian trail must start at one odd vertex and end at the other.
- With more than two odd vertices, some edges must be repeated to obtain a single covering walk.

The implementation rejects disconnected edge sets and requires finite, nonnegative weights.

### Greedy pairing of odd vertices

When there are more than two odd vertices, I reserve the first two in vertex-ID order as endpoints. I process the remaining odd vertices in their existing order, pairing each unmatched vertex with the nearest available odd vertex.

Nearest means minimum weighted shortest-path distance in the graph. A Dijkstra search stops when the first available odd vertex is reached. The connecting path can pass through even-degree vertices.

This avoids building a complete distance graph between all odd vertices. It gives a fast initial solution, but neither the pairing nor the endpoint choice is guaranteed to be optimal.

### Path duplication and Eulerian traversal

For each selected pair, I recover a shortest path and duplicate its actual edges in a NetworkX multigraph. All original edge occurrences remain present. A separate simple graph retains only the cheapest parallel edge for shortest-path calculations.

Duplicating a path changes the parity of its two endpoints and preserves the parity of internal vertices. After augmentation, only the two reserved endpoints remain odd.

I then call `nx.eulerian_path` to extract an Eulerian traversal, following the Hierholzer approach. Every augmented edge is traversed once, so every original edge is covered at least once. The input graph is not modified. The returned format is `(u, v, weight, coordinates_u, coordinates_v)`.

```text
Check connectivity and identify odd vertices.
If there are zero or two odd vertices:
    Extract the Eulerian circuit or trail directly.
Otherwise:
    Reserve the first two odd vertices as endpoints.
    Pair each remaining odd vertex with its nearest unmatched partner.
    Duplicate the shortest paths connecting these pairs.
    Extract the Eulerian trail of the augmented multigraph.
Return the continuous covering walk.
```

## Results from my implementation

These figures come from the supplied local command-line runs. Route-construction times exclude parsing and plotting and are individual observations.

| Instance | Vertices | Edges | Odd vertices | Components | Original cost | Duplication cost | Total cost | Construction time |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| `paris_map` | 11,348 | 17,958 | 7,318 | 1 | 22,924 | 7,115 | 30,039 | 1.055 s |
| `hard_to_choose` | 35 | 595 | 0 | 1 | 1,200 | 0 | 1,200 | 0.020 s |
| `islands` | 60 | 760 | 40 | 3 | Not reported | Not applicable | No continuous route | Not reported |

For Paris, the greedy construction selects 3,658 pairs in 0.154 s, leaving two endpoints. The final walk contains 23,938 edge traversals. Duplication adds 31.04% to the original edge cost.

For `hard_to_choose`, all 595 edges are traversed without duplication. The cost of 1,200 is optimal under the stated interpretation, since every required edge must be traversed at least once.

For `islands`, a single continuous route is impossible using only the supplied edges. Separate routes or connecting travel would require a different output contract or additional input.

### Lower-bound interpretation

Let `W` be the sum of original edge weights and `D` the duplication cost. The route costs `W + D`, and `W` is a valid lower bound for nonnegative weights. The 31.04% excess for Paris is not a measured gap to the unknown optimum.

## Proposed improvements, not yet implemented

A natural next step is pair-exchange local search. Given pairs `(a, b)` and `(c, d)`, compare their cost with `(a, c), (b, d)` and `(a, d), (b, c)`, using shortest-path distances. Accept improving reconnections while preserving a valid pairing.

Endpoint moves would address the fixed endpoint choice. For example, if `s` is an endpoint and `(a, b)` a pair, replacing that pair with `(s, a)` makes `b` the new endpoint.

Simulated annealing could use these moves, accepting improvements and occasionally worsening moves with probability `exp(-delta / T)`. A decreasing temperature reduces that probability over time, while the best solution found is retained. Improvement is not guaranteed and should be evaluated over multiple seeds and time budgets.

Other options include multiple greedy starts, variable neighbourhood search and exact minimum-weight matching for smaller odd-vertex sets. An exact open-route formulation should choose the two endpoints jointly with the remaining pairs. For Paris, a complete distance graph on 7,318 odd vertices would contain 26,772,903 real-real pairs, motivating on-demand distances and restricted candidate neighbourhoods.

## Separate Codex-generated solution and benchmark

I used Codex to explore an independent solution as a comparison with my greedy construction. This implementation describes exact matching for small odd-vertex sets and a time-budgeted simulated-annealing heuristic for larger sets, followed by an Eulerian traversal.
Its code is not included in this submission.  It reports these Paris results across three seeds:

| Search budget | Reported route costs | Reported total solver time |
|---|---|---|
| 0 s, fallback only | 30,708; 30,708; 30,708 | 0.074–0.116 s |
| 0.25 s | 29,939; 29,952; 29,927 | 0.290–0.308 s |
| 1 s | 29,637; 29,621; 29,740 | 1.044–1.084 s |
| 3 s | 29,409; 29,354; 29,384 | 3.068–3.107 s |

The best reported cost, 29,354, is 685 below my observed cost of 30,039: a 2.28% reduction in total cost. Its duplication cost is 6,430 versus my 7,115: a 9.63% reduction. These are comparisons between separate runs, not controlled runtime comparisons. The document also reports cost 1,200 for `hard_to_choose` and rejection of `islands` as disconnected. It does not establish the optimal Paris cost.

These reported figures suggest that my greedy construction is a useful starting point and that an improvement phase can further reduce duplication. A controlled benchmark on the same machine, with consistent timing and independent route validation, would be needed to assess the improvement reliably.

## Complexity and limitations

Connectivity and degree calculations take `O(V + E)` time. For `k > 2` odd vertices, the construction performs `(k - 2) / 2` nearest-partner searches and reconstructs a shortest path for each pair. Each search can take `O((V + E) log(V + E))` time in the worst case, although nearest-partner searches can terminate much earlier.

Hierholzer traversal is linear in the augmented graph size with a suitable adjacency representation. Memory contains the graph, shortest-path search state, augmented edges and returned walk; no dense odd-vertex distance matrix is constructed.  The current optimisation limitations are greedy pairing, fixed endpoints and the absence of an improvement phase.