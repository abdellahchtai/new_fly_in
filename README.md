*This project has been created as part of the 42 curriculum by abchtaib.*

---

# FLY-IN — Drone Zone Simulation

## Description

FLY-IN is a drone traffic simulation and visualization project. The goal is to route a fleet of drones from a **start zone** to an **end zone** through a network of interconnected zones, while respecting real-world-inspired constraints:

- Each **zone** has a maximum drone capacity (`max_drones`) and tracks how many drones are currently inside it (`curr_drones`).
- Each **connection** (edge between two zones) also has a maximum capacity and only allows a limited number of drones to pass through it simultaneously.
- A **restricted connection** acts as a transit corridor: a drone entering it is held for one simulation tick before being released into the next zone — it cannot be used again by another drone until it is free.

The simulation runs tick by tick (turn by turn). At each tick, every drone computes its optimal next step and moves if the path is available. The result is rendered in real time using **Pygame**, with smooth animation between positions.

---

## Algorithm Choices and Implementation Strategy

### Dijkstra's Algorithm

The core pathfinding algorithm used is **Dijkstra's shortest path algorithm**, applied at every tick for every drone individually.

**Why Dijkstra?**

The zone network is a **weighted directed graph** where:
- Nodes are zones.
- Edges are connections (`cnx`) between zones.
- Edge weights represent traversal cost (e.g., distance, congestion).

Dijkstra guarantees the **shortest path** from a source node to a target node in a graph with non-negative edge weights, making it the natural fit for this problem.

**Dynamic constraint filtering:**

Rather than running Dijkstra on the full graph, the algorithm filters out unavailable connections at query time:
- If a connection's `curr_cp` (current capacity) has reached `max_cp`, it is excluded from the graph for that tick.
- This means each drone always finds the shortest *available* path, adapting in real time to the current traffic state.

**Per-drone, per-tick execution:**

Dijkstra is re-run for every drone at every tick. This ensures that routing decisions always reflect the live state of the network — a connection saturated by one drone will be avoided by the next.

### Connection Capacity Enforcement

Connections between zones are not instantaneous — they are modeled as resources with limited capacity:

- `curr_cp` tracks how many drones are currently using the connection.
- Before a drone moves, the capacity is checked. If full, the drone waits.
- After a tick completes, connections no longer held by restricted drones have their `curr_cp` reset.

### Restricted Zones (Two-Tick Transit)

Connections marked as `restricted` require two ticks to cross:
- **Tick N:** The drone enters the connection. It is marked `in_cnx = True` and held at the midpoint visually.
- **Tick N+1:** The drone completes the crossing and arrives at the next zone.

This models real-world transit corridors where simultaneous occupation is controlled.

---

## Visual Representation

The simulation is rendered in real time using **Pygame**. The visualization is designed to make the simulation state immediately readable and to enhance understanding of the algorithm's decisions.

### Zone Display

Each zone is drawn as a **colored circle** on a 2D canvas:
- The zone's **name** and **type** are displayed above and below the circle.
- **`Max_dr`** shows the maximum drone capacity of the zone.
- **`Curr_dr`** shows how many drones are currently inside it, updating each tick.
- Zone colors are configurable via the data layer and fall back to yellow if invalid.
- **Connection lines** (edges) are drawn in black between connected zones.

### Drone Display with Smooth Animation

Drones are rendered as images (`drone.png`) overlaid on the canvas. Movement between ticks is **animated smoothly** rather than jumping instantly:

- Each drone stores a `prev_zone` (where it was last tick) and a `curr_zone` (where it is now).
- An `anim_progress` float (0.0 → 1.0) is advanced each frame using delta time from `clock.tick(60)`.
- The drone's screen position is linearly interpolated between its start and end position using this progress value.
- Drones crossing a **restricted connection** are displayed at the **midpoint** of the two zones during their transit tick, giving a clear visual cue that they are in transit.

### Controls

| Key / Action | Effect |
|---|---|
| `m` | Advance one simulation tick (disabled during animation) |
| `r` | To restart the simulation from the beginning|
| `Mouse drag` | Pan the map freely |
The turn counter is displayed in the top-left corner at all times.

---

## Instructions

### Requirements

- Python 3.10+
- Pygame

```bash
pip install pygame
```

### Running the Simulation

```bash
make run input_file= <name_of_the_map>
```

Make sure `drone.png` is present in the project root directory.

### Controls

- Press **m** to step through each simulation tick.
- Click **r** to restart the simulation.
- Close the window to exit.

### Project Structure

```
.
├── main.py            # Entry point
├── parsing.py         # Extracting clean data from the input file.
├── simulation.py      # Core simulation logic and tick management
├── render.py          # Pygame rendering and animation
├── algo.py            # Dijkstra's algorithm implementation
├── data.py            # Data models (Zone, Drone, Connection, etc.)
├── drone.png          # Drone sprite image
├── README.md          # Explanation of the project.
├── Makefile           # To run all the files automaticly.
```

---

## Resources

### Dijkstra's Algorithm

- [Dijkstra's Algorithm — Wikipedia](https://en.wikipedia.org/wiki/Dijkstra%27s_algorithm) — Formal definition, complexity analysis, and pseudocode.
- [Visualgo — Graph Shortest Paths](https://visualgo.net/en/sssp) — Interactive visual walkthrough of Dijkstra and related algorithms.
- [CS50 — Week 6: Graphs and Shortest Paths](https://cs50.harvard.edu/ai/2020/notes/0/) — Accessible lecture notes on graph search algorithms.
- [NetworkX Documentation](https://networkx.org/documentation/stable/reference/algorithms/shortest_paths.html) — Python graph library reference for shortest path implementations.

### Pygame

- [Pygame Official Documentation](https://www.pygame.org/docs/) — Full API reference.
- [Real Python — Pygame Primer](https://realpython.com/pygame-a-primer/) — Tutorial covering game loops, event handling, and rendering.

### AI Usage

AI (Claude by Anthropic) was used during the development of this project for the following tasks:

- **Understand the djikstra** — Understand the full mecanisme of the djikstra algo and take pratical exemple to see if this algo will work for this project or no
- **Writing this README** — structuring and drafting all sections according to the 42 curriculum requirements.
- **Documentation of the visual representation** The visualisation help the user to understand what happening in the back in a simple way.