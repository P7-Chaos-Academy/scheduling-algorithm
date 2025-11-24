import random
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import os

random.seed()
base_time = datetime.now()

num_tasks = random.randint(20, 40)
tasks = []
for i in range(1, num_tasks + 1):
    task_id = f"T{i}"
    cost = random.choice([128, 512, 1024])
    value = (base_time + timedelta(seconds=random.randint(1, 100))).timestamp()  # random timestamp as value
    tasks.append((task_id, cost, value))

nodes = {
    "nano1": {"speed": 25, "uptime": 300},
    "nano2": {"speed": 25, "uptime": 300},
    "nano3": {"speed": 25, "uptime": 300},
    "orin": {"speed":  25, "uptime": 100}
}

# Calculate effective capacity for each node
node_capacities = {
    node: info["speed"] * info["uptime"]
    for node, info in nodes.items()
}

# Simulate historical runtime tracking (this would come from your database)
# Units: seconds of runtime
node_historical_runtime = {
    "nano1": 0,  # Will be updated in real system from DB
    "nano2": 0,
    "nano3": 0,
    "orin": 0
}

# Capacity-proportional fair scheduling algorithm
# Goal: Maintain equal utilization percentage across all nodes
# Strategy: Always assign next task to the node with LOWEST current utilization %

schedule = {node: [] for node in nodes.keys()}
node_usage = {node: 0 for node in nodes.keys()}  # Track current capacity usage (tokens)
remaining_tasks = tasks[:]

print(f"\nNode Capacities:")
print(f"  nano1: {node_capacities['nano1']:,} tokens ({nodes['nano1']['speed']} tok/s × {nodes['nano1']['uptime']}s)")
print(f"  nano2: {node_capacities['nano2']:,} tokens ({nodes['nano2']['speed']} tok/s × {nodes['nano2']['uptime']}s)")
print(f"  nano3: {node_capacities['nano3']:,} tokens ({nodes['nano3']['speed']} tok/s × {nodes['nano3']['uptime']}s)")
print(f"  orin:  {node_capacities['orin']:,} tokens ({nodes['orin']['speed']} tok/s × {nodes['orin']['uptime']}s)")
print(f"  Total: {sum(node_capacities.values()):,} tokens\n")

# Assign tasks one at a time to maintain balanced utilization
while remaining_tasks:
    # Sort nodes by current utilization percentage (ascending)
    # Include historical runtime for long-term fairness
    node_list = sorted(
        nodes.keys(), 
        key=lambda n: (node_usage[n] + node_historical_runtime[n]) / node_capacities[n]
    )
    
    assigned = False
    
    # Try to assign to the node with lowest utilization
    for node in node_list:
        if not remaining_tasks:
            break
        
        # Calculate remaining capacity
        remaining_capacity = node_capacities[node] - node_usage[node]
        
        if remaining_capacity <= 0:
            continue  # Node is full
        
        # Find tasks that fit in remaining capacity
        fitting_tasks = [t for t in remaining_tasks if t[1] <= remaining_capacity]
        
        if not fitting_tasks:
            continue  # No tasks fit in this node
        
        # Simple greedy selection: pick the first task from fitting tasks
        # (fitting_tasks are already from remaining_tasks, sorted by value)
        best_task = fitting_tasks[0]
        
        schedule[node].append(best_task)
        node_usage[node] += best_task[1]
        remaining_tasks.remove(best_task)
        assigned = True
        break  # Re-evaluate which node has lowest utilization
    
    if not assigned:
        break  # No more tasks can be assigned

unscheduled = remaining_tasks

# Update historical runtime (in production, this would be written to database)
for node in nodes.keys():
    node_historical_runtime[node] += node_usage[node]

# Print results

for node in nodes.keys():
    tasks_in_node = schedule[node]
    total_cost = sum(t[1] for t in tasks_in_node)
    total_value = sum(t[2] for t in tasks_in_node)
    node_info = nodes[node]
    capacity = node_capacities[node]
    utilization = (total_cost / capacity) * 100
    # Calculate actual execution time
    execution_time = total_cost / node_info["speed"] if node_info["speed"] > 0 else 0
    
    print(f"{node} (speed={node_info['speed']} tokens/sec, uptime={node_info['uptime']}s):")
    print(f"  ├─ Tasks: {len(tasks_in_node)} → {[t[0] for t in tasks_in_node]}")
    print(f"  ├─ Tokens: {total_cost}/{capacity} ({utilization:.1f}% capacity)")
    print(f"  ├─ Execution Time: {execution_time:.1f}s / {node_info['uptime']}s available")
    print(f"  ├─ Total Value: {total_value:.2f}")
    print(f"  └─ Historical Runtime: {node_historical_runtime[node]} units")
    print()

print(f"Unscheduled: {[t[0] for t in unscheduled]} ({len(unscheduled)} tasks)")

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
    
    os.makedirs("outputs", exist_ok=True)
    output_path = "outputs/knapsack_schedule.png"
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()

visualize_schedule(schedule, nodes)