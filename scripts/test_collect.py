import json
from backend.collectors.slurm import get_jobs, get_nodes
from backend.collectors.gpu import get_gpu_summary, get_gpu_processes


def main():
    print("==== JOBS ====")
    print(json.dumps(get_jobs(), indent=2, ensure_ascii=False))

    print("\n==== NODES ====")
    nodes = get_nodes()
    print(json.dumps(nodes, indent=2, ensure_ascii=False))

    gpu_nodes = []
    for node in nodes:
        gres = node.get("gres", "")
        if "gpu" in gres.lower():
            gpu_nodes.append(node["name"])

    print("\n==== GPU NODES ====")
    print(gpu_nodes)

    for node in gpu_nodes:
        print(f"\n==== {node} GPU SUMMARY ====")
        try:
            print(json.dumps(get_gpu_summary(node), indent=2, ensure_ascii=False))
        except Exception as e:
            print(f"[ERROR] get_gpu_summary({node}): {e}")

        print(f"\n==== {node} GPU PROCESSES ====")
        try:
            print(json.dumps(get_gpu_processes(node), indent=2, ensure_ascii=False))
        except Exception as e:
            print(f"[ERROR] get_gpu_processes({node}): {e}")


if __name__ == "__main__":
    main()