from input import parse_cmd_line, parse_file
from graph import Graph
from time import perf_counter
from proposed_solution import graph_info, draw_path


def main():
    args = parse_cmd_line()
    vertices, edges = parse_file(args.in_file)
    print(f"#E={len(edges)}, #V={len(vertices)}", flush=True)
    graph = Graph(vertices, edges)
    odd_degrees, components = graph_info(graph)
    print("Number of odd nodes:", odd_degrees)
    print("Number of components:", components)

    if components > 1:
        print(f"Required edges must form a connected graph.")
        return
    else:
        first_start = perf_counter()
        print("Starting path solution", flush=True)
        path = draw_path(graph)
        print(f"Path found in {perf_counter() - first_start:.3f}s", flush=True)

        base_cost = sum(edge[2] for edge in graph.edges)
        total_cost = sum(edge[2] for edge in path)
        duplication_cost = total_cost - base_cost
        print("Traversed edges:", len(path))

        print(f"Sum of all current edges (Lower Bound): {base_cost:.2f}")
        print(f"Extra cost (duplication cost): {duplication_cost:.2f}")
        print(f"Total cost: {total_cost:.2f}")

        if base_cost > 0:
            print(f"Added: {100 * duplication_cost / base_cost:.2f}%")

    # Optional second solver: uncomment this block to run the benchmark.
    # from benchmark_solution import proposed_solution
    # try:
    #     diagnostics = {}
    #     path = proposed_solution(graph, method=args.method, time_limit=args.time_limit,
    #                              seed=args.seed, diagnostics=diagnostics)
    # except ValueError as error:
    #     raise SystemExit(f"No valid route: {error}") from error
    #
    # print("Solver:", diagnostics["method"], "(optimal)" if diagnostics["optimal"] else "(optimality not certified)")
    # print("Traversed edges:", len(path))
    # print("Value of path found:", sum(edge[2] for edge in path))
    # print("Lower bound:", diagnostics["lower_bound"])
    # print(f"Solver time: {diagnostics['seconds']:.3f} s")

    if args.plot_graph:
        graph.plot()
        graph.display_path(path=path)


if __name__ == "__main__":
    main()
