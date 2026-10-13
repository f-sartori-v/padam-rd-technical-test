import heapq
import math
import time

import networkx as nx
from itertools import count

def draw_path(graph):
    """Return an edge-covering Eulerian walk after duplicating the chosen paths.

    Each returned edge is (u, v, weight, coordinates_u, coordinates_v).
    The input graph is not modified.
    """
    start, end, pairs, duplication_cost = identify_start_endpoint(graph)
    if start is None:
        return []

    augmented = nx.MultiGraph()
    shortest = nx.Graph()
    for u, v, weight, *_ in graph.edges:
        augmented.add_edge(u, v, weight=weight)
        if not shortest.has_edge(u, v) or weight < shortest[u][v]["weight"]:
            shortest.add_edge(u, v, weight=weight)

    # Duplicate actual shortest-path edges, not direct links between paired nodes.
    for u, v, _ in pairs:
        nodes = nx.shortest_path(shortest, u, v, weight="weight")
        for a, b in zip(nodes, nodes[1:]):
            augmented.add_edge(a, b, weight=shortest[a][b]["weight"])

    path = [
        (u, v, augmented[u][v][key]["weight"], graph.vertices[u], graph.vertices[v])
        for u, v, key in nx.eulerian_path(augmented, source=start, keys=True)
    ]
    return path


def graph_info(graph):
    """Return odd-degree vertex count and edge-bearing component count."""
    n = len(graph.vertices)
    adjacency = [[] for _ in range(n)]

    # Construct adjacent list
    for u, v, *_ in graph.edges:
        adjacency[u].append(v)
        adjacency[v].append(u)

    visited = set()
    components = 0

    # Identify connected components
    for start in range(n):
        if start in visited or not adjacency[start]:
            continue

        components += 1
        stack = [start]
        visited.add(start)

        while stack:
            u = stack.pop()

            for v in adjacency[u]:
                if v not in visited:
                    visited.add(v)
                    stack.append(v)

    odd_degrees = sum(len(neighbors) % 2 for neighbors in adjacency)
    return odd_degrees, components

def _nearest_endpoint_matching(original, odd, *, base_cost=0.0):
    """Accept a greedy pairing with the first two odd vertices as endpoints."""
    begin = time.monotonic()
    start, end = odd[:2]
    available = set(odd[2:])
    pairs = []

    # Visit odd vertices in their existing order and accept the nearest partner.
    for u in odd[2:]:
        if u not in available:
            continue
        available.remove(u)
        v, distance = _nearest_available_vertex(original, u, available)
        available.remove(v)
        a, b = sorted((u, v))
        pairs.append((a, b, distance))

    pairs.sort()
    duplication_cost = math.fsum(distance for _, _, distance in pairs)
    print(
        f"Nearest-node solution accepted: total={base_cost + duplication_cost:.2f}, "
        f"duplication={duplication_cost:.2f}, "
        f"pairs={len(pairs)}, time to find={time.monotonic() - begin:.3f}s",
        flush=True,
    )

    # TODO: Implement a heuristic to improve the initial pairing and endpoints.
    return start, end, pairs, duplication_cost


def _nearest_available_vertex(original, source, available):
    """Find the nearest available vertex by weighted graph distance."""
    queue = []
    counter = count()
    distances = {source: 0}

    heapq.heappush(queue, (0, next(counter), source))

    while queue:
        distance, _, u = heapq.heappop(queue)

        if distance > distances[u]:
            continue

        # The first available vertex reached has minimum distance.
        if u in available:
            return u, distance

        for v, data in original[u].items():
            candidate = distance + data["weight"]

            if candidate < distances.get(v, math.inf):
                distances[v] = candidate
                heapq.heappush(
                    queue, (candidate, next(counter), v)
                )

    raise ValueError("No available vertex is reachable.")


def identify_start_endpoint(graph):
    """
    Select the first two odd vertices as endpoints and greedily pair the rest.

    Assumes:
        - Undirected graph with nonnegative, finite weights.
        - graph.edges contains (u, v, weight, coord_u, coord_v).

    Returns:
        start, end, pairs, duplication_cost

        pairs contains (u, v, shortest_path_distance).
        For an Eulerian graph, start == end and pairs is empty.
    """

    n = len(graph.vertices)
    degrees = [0] * n
    original = nx.Graph()

    for u, v, weight, *_ in graph.edges:
        if not (0 <= u < n and 0 <= v < n):
            raise ValueError(f"Invalid vertex IDs: {(u, v)}")

        if not math.isfinite(weight) or weight < 0:
            raise ValueError("Weights must be finite and nonnegative.")

        # Count every original edge, including parallel edges.
        degrees[u] += 1
        degrees[v] += 1

        # For shortest paths, retain only the cheapest parallel edge.
        if (
            not original.has_edge(u, v)
            or weight < original[u][v]["weight"]
        ):
            original.add_edge(u, v, weight=weight)

    if original.number_of_nodes() == 0:
        return None, None, [], 0

    if not nx.is_connected(original):
        raise ValueError("Required edges must form a connected graph.")

    odd = [v for v, degree in enumerate(degrees) if degree % 2]
    k = len(odd)

    if k == 0:
        start = min(original.nodes)
        return start, start, [], 0

    if k == 2:
        return odd[0], odd[1], [], 0

    return _nearest_endpoint_matching(
        original,
        odd,
        base_cost=math.fsum(edge[2] for edge in graph.edges),
    )
