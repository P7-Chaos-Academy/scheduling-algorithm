import random
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import os

# Generate tasks with random costs (128, 512, or 1024) and timestamp values
random.seed()  # Use current time as seed for true randomness
base_time = datetime.now()

num_tasks = random.randint(8, 15)  # Random number of tasks between 8 and 15
tasks = []
for i in range(1, num_tasks + 1):
    task_id = f"T{i}"
    cost = random.choice([128, 512, 1024])
    value = (base_time + timedelta(seconds=random.randint(1, 100))).timestamp()  # random timestamp as value
    tasks.append((task_id, cost, value))

# Each node has a max capacity (e.g., available compute units)
nodes = {
    "nano1": 2000,
    "nano2": 2000,
    "nano3": 2000,
    "orin": 2000
}

# Simulate historical runtime tracking (this would come from your database)
# Units: seconds of runtime
node_historical_runtime = {
    "nano1": 0,  # Will be updated in real system from DB
    "nano2": 0,
    "nano3": 0,
    "orin": 0
}

def knapsack(tasks, capacity):
    n = len(tasks)
    dp = [[0] * (capacity + 1) for _ in range(n + 1)]

    for i in range(1, n + 1):
        cost = tasks[i-1][1]
        value = tasks[i-1][2]
        for w in range(1, capacity + 1):
            if cost <= w:
                dp[i][w] = max(value + dp[i-1][w-cost], dp[i-1][w])
            else:
                dp[i][w] = dp[i-1][w]

    # backtrack to get chosen tasks
    res = []
    w = capacity
    for i in range(n, 0, -1):
        if dp[i][w] != dp[i-1][w]:
            res.append(tasks[i-1])
            w -= tasks[i-1][1]
    return res

# Round-robin scheduling with fairness
# Sort tasks by value (descending) to prioritize high-value tasks
sorted_tasks = sorted(tasks, key=lambda t: t[2], reverse=True)

schedule = {node: [] for node in nodes.keys()}
node_usage = {node: 0 for node in nodes.keys()}  # Track current capacity usage
node_list = list(nodes.keys())

unscheduled = []

# Round-robin assignment with historical runtime consideration
for task in sorted_tasks:
    task_id, cost, value = task
    assigned = False
    
    # Try to assign to the node with the least TOTAL usage (current + historical)
    # This promotes long-term fairness across scheduling rounds
    # In production, node_historical_runtime would be fetched from database
    sorted_nodes = sorted(node_list, key=lambda n: node_usage[n] + node_historical_runtime[n])
    
    for node in sorted_nodes:
        if node_usage[node] + cost <= nodes[node]:
            # Assign task to this node
            schedule[node].append(task)
            node_usage[node] += cost
            assigned = True
            break
    
    if not assigned:
        unscheduled.append(task)

# Update historical runtime (in production, this would be written to database)
for node in nodes.keys():
    node_historical_runtime[node] += node_usage[node]

# Print results
print("=" * 70)
print("ROUND-ROBIN SCHEDULING RESULTS (WITH FAIRNESS)")
print("=" * 70)
for node in nodes.keys():
    tasks_in_node = schedule[node]
    total_cost = sum(t[1] for t in tasks_in_node)
    total_value = sum(t[2] for t in tasks_in_node)
    utilization = (total_cost / nodes[node]) * 100
    print(f"{node}: {[t[0] for t in tasks_in_node]}")
    print(f"  ├─ Tasks: {len(tasks_in_node)}")
    print(f"  ├─ Capacity: {total_cost}/{nodes[node]} ({utilization:.1f}%)")
    print(f"  ├─ Total Value: {total_value:.2f}")
    print(f"  └─ Historical Runtime: {node_historical_runtime[node]} units")
    print()

print(f"Unscheduled: {[t[0] for t in unscheduled]} ({len(unscheduled)} tasks)")
print("=" * 70)
print("\n💾 In production: Historical runtime would be persisted to database")

# Visualization
def visualize_schedule(schedule, nodes):
    fig, ax = plt.subplots(figsize=(12, 6))
    colors = plt.cm.tab10.colors
    
    node_names = list(nodes.keys())
    y_positions = {node: i for i, node in enumerate(node_names)}
    
    for node_idx, (node, tasks) in enumerate(schedule.items()):
        current_pos = 0
        for task in tasks:
            task_id, cost, value = task
            ax.barh(
                y_positions[node],
                cost,
                left=current_pos,
                height=0.6,
                color=colors[node_idx % len(colors)],
                edgecolor="black",
                linewidth=1.5
            )
            ax.text(
                current_pos + cost / 2,
                y_positions[node],
                f"{task_id}\n{cost}",
                ha="center",
                va="center",
                color="white",
                fontsize=9,
                fontweight="bold"
            )
            current_pos += cost
    
    ax.set_yticks(range(len(node_names)))
    ax.set_yticklabels(node_names)
    ax.set_xlabel("Capacity Used", fontsize=12)
    ax.set_ylabel("Nodes", fontsize=12)
    ax.set_title("Knapsack Task Scheduling Across 4 Nodes", fontsize=14, fontweight="bold")
    ax.grid(axis='x', alpha=0.3)
    
    plt.tight_layout()
    
    # Create outputs directory if it doesn't exist
    os.makedirs("outputs", exist_ok=True)
    output_path = "outputs/knapsack_schedule.png"
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    print(f"\n✅ Visualization saved to: {output_path}")
    plt.close()

visualize_schedule(schedule, nodes)