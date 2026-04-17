import tkinter as tk
from tkinter import messagebox
import heapq
import networkx as nx
import matplotlib.pyplot as plt

# ---------------- INITIAL DATA ----------------
cities = {
    "Chandigarh": [("Ambala", 45), ("Ludhiana", 90)],
    "Ambala": [("Delhi", 200), ("Patiala", 70)],
    "Ludhiana": [("Chandigarh", 90)],
    "Patiala": [("Delhi", 180)],
    "Delhi": []
}

heuristic_city = {
    "Chandigarh": 250,
    "Ambala": 200,
    "Ludhiana": 300,
    "Patiala": 180,
    "Delhi": 0
}

# ---------------- UTILS ----------------
def normalize_city_name(name):
    """Return title case, stripped name."""
    return name.strip().title()

def reconstruct_path(parent, start, goal):
    if goal not in parent and start != goal:
        return None
    path = []
    current = goal
    while current in parent:
        path.append(current)
        current = parent[current]
    path.append(start)
    return path[::-1]

def path_distance(path):
    if not path or len(path) < 2:
        return 0
    total = 0
    for i in range(len(path)-1):
        current = path[i]
        nxt = path[i+1]
        for neighbor, weight in cities[current]:
            if neighbor == nxt:
                total += weight
                break
    return total

# ---------------- ALGORITHMS ----------------
def bfs(start, goal):
    queue = [start]
    visited = {start}
    parent = {}
    while queue:
        current = queue.pop(0)
        if current == goal:
            break
        for neighbor, _ in cities[current]:
            if neighbor not in visited:
                visited.add(neighbor)
                parent[neighbor] = current
                queue.append(neighbor)
    return reconstruct_path(parent, start, goal)

def dfs(start, goal):
    stack = [start]
    visited = {start}
    parent = {}
    while stack:
        current = stack.pop()
        if current == goal:
            break
        for neighbor, _ in cities[current]:
            if neighbor not in visited:
                visited.add(neighbor)
                parent[neighbor] = current
                stack.append(neighbor)
    return reconstruct_path(parent, start, goal)

def best_first(start, goal):
    pq = [(heuristic_city[start], start)]
    visited = {start}
    parent = {}
    while pq:
        _, current = heapq.heappop(pq)
        if current == goal:
            break
        for neighbor, _ in cities[current]:
            if neighbor not in visited:
                visited.add(neighbor)
                parent[neighbor] = current
                heapq.heappush(pq, (heuristic_city.get(neighbor, 0), neighbor))
    return reconstruct_path(parent, start, goal)

# ---------------- GRAPH VISUAL ----------------
def draw_graph(path):
    G = nx.DiGraph()
    for city in cities:
        for neighbor, weight in cities[city]:
            G.add_edge(city, neighbor, weight=weight)
    pos = nx.spring_layout(G, seed=42)  # fixed seed for consistency
    colors = []
    for node in G.nodes():
        if node == path[0]:
            colors.append("green")
        elif node == path[-1]:
            colors.append("red")
        elif node in path:
            colors.append("yellow")
        else:
            colors.append("lightblue")
    nx.draw(G, pos, with_labels=True, node_color=colors, node_size=2000)
    edges = [(path[i], path[i+1]) for i in range(len(path)-1)]
    nx.draw_networkx_edges(G, pos, edgelist=edges, edge_color="red", width=3)
    labels = nx.get_edge_attributes(G, 'weight')
    nx.draw_networkx_edge_labels(G, pos, edge_labels=labels)
    plt.title("City Graph")
    plt.show()

# ---------------- GUI ----------------
class App:
    def __init__(self, root):
        self.root = root
        self.root.title("AI Pathfinding System")

        row = 0
        # Source / Destination
        tk.Label(root, text="Source City").grid(row=row, column=0, sticky="w", padx=5, pady=2)
        row += 1
        self.start_var = tk.StringVar(root)
        self.goal_var = tk.StringVar(root)
        self.start_menu = tk.OptionMenu(root, self.start_var, *cities.keys())
        self.start_menu.grid(row=row, column=0, padx=5, pady=2, sticky="ew")
        row += 1

        tk.Label(root, text="Destination City").grid(row=row, column=0, sticky="w", padx=5, pady=2)
        row += 1
        self.goal_menu = tk.OptionMenu(root, self.goal_var, *cities.keys())
        self.goal_menu.grid(row=row, column=0, padx=5, pady=2, sticky="ew")
        row += 1

        self.start_var.set(list(cities.keys())[0])
        self.goal_var.set(list(cities.keys())[1])

        # Algorithm buttons
        frame = tk.Frame(root)
        frame.grid(row=row, column=0, pady=10, sticky="ew")
        row += 1
        tk.Button(frame, text="BFS", command=lambda: self.run(bfs)).grid(row=0, column=0, padx=2)
        tk.Button(frame, text="DFS", command=lambda: self.run(dfs)).grid(row=0, column=1, padx=2)
        tk.Button(frame, text="Best First", command=lambda: self.run(best_first)).grid(row=0, column=2, padx=2)

        tk.Button(root, text="Compare All", command=self.compare).grid(row=row, column=0, pady=5)
        row += 1

        # Add city (with optional heuristic)
        tk.Label(root, text="Add New City").grid(row=row, column=0, sticky="w", padx=5, pady=2)
        row += 1
        tk.Label(root, text="City Name:").grid(row=row, column=0, sticky="w", padx=5)
        self.new_city = tk.Entry(root)
        self.new_city.grid(row=row, column=1, padx=5, pady=2, sticky="ew")
        row += 1
        tk.Label(root, text="Heuristic (optional):").grid(row=row, column=0, sticky="w", padx=5)
        self.heur_entry = tk.Entry(root)
        self.heur_entry.grid(row=row, column=1, padx=5, pady=2, sticky="ew")
        row += 1
        tk.Button(root, text="Add City", command=self.add_city).grid(row=row, column=0, columnspan=2, pady=2)
        row += 1

        # Add connection
        tk.Label(root, text="Add Connection").grid(row=row, column=0, sticky="w", padx=5, pady=2)
        row += 1
        tk.Label(root, text="From:").grid(row=row, column=0, sticky="w", padx=5)
        self.conn_from = tk.Entry(root)
        self.conn_from.grid(row=row, column=1, padx=5, pady=2, sticky="ew")
        row += 1
        tk.Label(root, text="To:").grid(row=row, column=0, sticky="w", padx=5)
        self.conn_to = tk.Entry(root)
        self.conn_to.grid(row=row, column=1, padx=5, pady=2, sticky="ew")
        row += 1
        tk.Label(root, text="Distance (km):").grid(row=row, column=0, sticky="w", padx=5)
        self.conn_dist = tk.Entry(root)
        self.conn_dist.grid(row=row, column=1, padx=5, pady=2, sticky="ew")
        row += 1
        self.bidir_var = tk.BooleanVar()
        tk.Checkbutton(root, text="Add reverse connection (bidirectional)", variable=self.bidir_var).grid(row=row, column=0, columnspan=2, sticky="w", padx=5)
        row += 1
        tk.Button(root, text="Add Connection", command=self.add_connection).grid(row=row, column=0, columnspan=2, pady=5)

        root.columnconfigure(1, weight=1)

    def update_dropdowns(self):
        city_list = list(cities.keys())
        menu = self.start_menu["menu"]
        menu.delete(0, "end")
        for city in city_list:
            menu.add_command(label=city, command=lambda value=city: self.start_var.set(value))
        menu = self.goal_menu["menu"]
        menu.delete(0, "end")
        for city in city_list:
            menu.add_command(label=city, command=lambda value=city: self.goal_var.set(value))

    def add_city(self):
        name = normalize_city_name(self.new_city.get())
        if not name:
            messagebox.showerror("Error", "City name cannot be empty")
            return
        if name in cities:
            messagebox.showerror("Error", f"{name} already exists")
            return

        # Heuristic handling
        heur_str = self.heur_entry.get().strip()
        if heur_str:
            try:
                heur = int(heur_str)
            except ValueError:
                messagebox.showerror("Error", "Heuristic must be an integer")
                return
        else:
            # Default: estimate as 0 (safe) or ask user? We'll use 0 as fallback.
            heur = 0

        cities[name] = []
        heuristic_city[name] = heur
        self.update_dropdowns()
        messagebox.showinfo("Success", f"{name} added with heuristic = {heur}")
        self.new_city.delete(0, tk.END)
        self.heur_entry.delete(0, tk.END)

    def add_connection(self):
        c1 = normalize_city_name(self.conn_from.get())
        c2 = normalize_city_name(self.conn_to.get())
        dist_str = self.conn_dist.get().strip()

        if not c1 or not c2 or not dist_str:
            messagebox.showerror("Error", "All fields are required")
            return
        try:
            dist = int(dist_str)
        except ValueError:
            messagebox.showerror("Error", "Distance must be an integer")
            return

        if c1 not in cities:
            messagebox.showerror("Error", f"{c1} does not exist")
            return
        if c2 not in cities:
            messagebox.showerror("Error", f"{c2} does not exist")
            return

        # Add forward connection
        cities[c1].append((c2, dist))
        msg = f"Connection {c1} → {c2} ({dist} km) added."

        # Add reverse if checkbox checked
        if self.bidir_var.get():
            cities[c2].append((c1, dist))
            msg += f"\nReverse connection {c2} → {c1} ({dist} km) also added."

        messagebox.showinfo("Success", msg)
        # Clear inputs
        self.conn_from.delete(0, tk.END)
        self.conn_to.delete(0, tk.END)
        self.conn_dist.delete(0, tk.END)
        self.bidir_var.set(False)

    def run(self, algo):
        start = normalize_city_name(self.start_var.get())
        goal = normalize_city_name(self.goal_var.get())

        path = algo(start, goal)
        if path is None:
            messagebox.showerror("No Path", 
                f"No route found from {start} to {goal}.\n"
                "Make sure there is a sequence of connections linking them.")
            return

        dist = path_distance(path)
        msg = f"Path: {' → '.join(path)}\nSteps: {len(path)-1}\nDistance: {dist} km"
        messagebox.showinfo("Path Found", msg)
        draw_graph(path)

    def compare(self):
        start = normalize_city_name(self.start_var.get())
        goal = normalize_city_name(self.goal_var.get())

        algos = {"BFS": bfs, "DFS": dfs, "Best First": best_first}
        results = []
        for name, algo in algos.items():
            path = algo(start, goal)
            if path is None:
                results.append(f"{name}: No path")
            else:
                steps = len(path) - 1
                dist = path_distance(path)
                results.append(f"{name}: {steps} steps, {dist} km")
        messagebox.showinfo("Algorithm Comparison", "\n".join(results))

# ---------------- RUN ----------------
if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
