import matplotlib.pyplot as plt
from dataclasses import dataclass, field
from typing import List, Optional
import random


# ------------------------
# Core Models
# ------------------------

@dataclass
class Task:
    id: str
    tokens: int
    assigned_node: Optional[str] = None
    start_time: Optional[float] = None
    end_time: Optional[float] = None

@dataclass
class Node:
    name: str
    speed: float           # tokens per second
    uptime: float          # how long the node will stay on (seconds)
    schedule: List[Task] = field(default_factory=list)

    def time_used(self):
        if not self.schedule:
            return 0
        return self.schedule[-1].end_time

    def remaining_time(self):
        return self.uptime - self.time_used()


# ------------------------
# Scheduler Framework
# ------------------------

class Scheduler:
    def __init__(self, nodes: List[Node], tasks: List[Task]):
        self.nodes = nodes
        self.tasks = tasks

    def run(self):
        """
        👇 Implement your scheduling algorithm here.
        For example:
        - sort tasks by size
        - assign based on node speed and remaining uptime
        - try combinations for max utilization
        """
        raise NotImplementedError("Implement your scheduling logic here!")

    def visualize(self):
        import os
        os.makedirs("outputs", exist_ok=True)
        
        fig, ax = plt.subplots(figsize=(12, 6))
        colors = plt.cm.tab10.colors

        # Plot each node at a fixed y position (0, 1, 2, 3 for 4 nodes)
        for i, node in enumerate(self.nodes):
            for task in node.schedule:
                ax.barh(
                    i,  # Use numeric position instead of node.name
                    task.end_time - task.start_time,
                    left=task.start_time,
                    color=colors[i % len(colors)],
                    edgecolor="black",
                    height=0.8
                )
                ax.text(
                    task.start_time + (task.end_time - task.start_time) / 2,
                    i,
                    task.id,
                    ha="center",
                    va="center",
                    color="white",
                    fontsize=8,
                    fontweight="bold"
                )

        # Set y-axis to show all node names
        ax.set_yticks(range(len(self.nodes)))
        ax.set_yticklabels([node.name for node in self.nodes])
        
        ax.set_xlabel("Time (seconds)", fontsize=12)
        ax.set_ylabel("Nodes", fontsize=12)
        ax.set_title("Task Scheduling Visualization (4 Nodes)", fontsize=14, fontweight="bold")
        ax.grid(axis='x', alpha=0.3, linestyle='--')
        
        plt.tight_layout()
        
        # Save to file instead of showing (works in headless environments)
        output_file = "outputs/schedule.png"
        plt.savefig(output_file, dpi=150, bbox_inches='tight')
        print(f"✓ Visualization saved to {output_file}")
        plt.close()


# ------------------------
# Example Simulation Setup
# ------------------------

def create_demo_data():
    nodes = [
        Node("nano1", speed=25, uptime=600),
        Node("nano2", speed=35, uptime=600),
        Node("nano3", speed=45, uptime=600),
        Node("orin", speed=80, uptime=900),
    ]

    # tasks = [Task(f"task{i}", tokens=random.randint(100, 1000)) for i in range(1, 11)]
    
    tasks = [
        Task("task1", tokens=500),
        Task("task2", tokens=300),
        Task("task3", tokens=700),
    ]
    return nodes, tasks


# ------------------------
# Example Custom Scheduler (Demo)
# ------------------------

class MyGreedyScheduler(Scheduler):
    def run(self):
        # Example heuristic: assign largest tasks first to fastest available node
        self.tasks.sort(key=lambda t: t.tokens, reverse=True)

        for task in self.tasks:
            best_node = None
            best_fit_time = float("inf")

            for node in self.nodes:
                est_time = task.tokens / node.speed
                if node.time_used() + est_time <= node.uptime:
                    remaining = node.uptime - (node.time_used() + est_time)
                    if remaining < best_fit_time:
                        best_fit_time = remaining
                        best_node = node

            if best_node:
                start = best_node.time_used()
                end = start + task.tokens / best_node.speed
                task.start_time, task.end_time = start, end
                task.assigned_node = best_node.name
                best_node.schedule.append(task)


# ------------------------
# Entrypoint
# ------------------------

if __name__ == "__main__":
    random.seed(42)
    nodes, tasks = create_demo_data()

    scheduler = MyGreedyScheduler(nodes, tasks)  # <- Replace with your algorithm
    scheduler.run()
    scheduler.visualize()
