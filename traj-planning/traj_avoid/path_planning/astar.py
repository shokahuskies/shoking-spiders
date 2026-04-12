import heapq
from typing import Dict, List, Optional, Set, Tuple

Vec2 = Tuple[float, float]
Cell = Tuple[int, int]

def world_to_cell(pos: Vec2, cell_size: float) -> Cell:
    return (int(pos[0] // cell_size), int(pos[1] // cell_size))

def cell_to_world(cell: Cell, cell_size: float) -> Vec2:
    return ((cell[0] + 0.5) * cell_size, (cell[1] + 0.5) * cell_size)

def neighbors8(c: Cell) -> List[Cell]:
    x, y = c
    return [
        (x+1, y), (x-1, y), (x, y+1), (x, y-1),
        (x+1, y+1), (x+1, y-1), (x-1, y+1), (x-1, y-1),
    ]

def heuristic(a: Cell, b: Cell) -> float:
    return max(abs(a[0]-b[0]), abs(a[1]-b[1]))

def build_unsafe_cells(other_preds: Dict[int, List[Vec2]], cell_size: float) -> Set[Cell]:
    unsafe: Set[Cell] = set()
    for preds in other_preds.values():
        for p in preds:
            c = world_to_cell(p, cell_size)
            unsafe.add(c)
            for nb in neighbors8(c):
                unsafe.add(nb)
    return unsafe

def astar_path(
    start: Cell,
    goal: Cell,
    unsafe: Set[Cell],
    bounds: Tuple[Cell, Cell],
    max_expansions: int,
) -> Optional[List[Cell]]:
    (xmin, ymin), (xmax, ymax) = bounds

    def in_bounds(c: Cell) -> bool:
        return xmin <= c[0] <= xmax and ymin <= c[1] <= ymax

    open_heap: List[Tuple[float, Cell]] = []
    heapq.heappush(open_heap, (0.0, start))

    came_from: Dict[Cell, Cell] = {}
    g_score: Dict[Cell, float] = {start: 0.0}

    expansions = 0
    while open_heap and expansions < max_expansions:
        _, current = heapq.heappop(open_heap)
        expansions += 1

        if current == goal:
            path = [current]
            while current in came_from:
                current = came_from[current]
                path.append(current)
            path.reverse()
            return path

        for nb in neighbors8(current):
            if not in_bounds(nb):
                continue
            if nb in unsafe and nb != goal:
                continue

            step_cost = 1.4 if (nb[0] != current[0] and nb[1] != current[1]) else 1.0
            tentative_g = g_score[current] + step_cost

            if nb not in g_score or tentative_g < g_score[nb]:
                came_from[nb] = current
                g_score[nb] = tentative_g
                f = tentative_g + heuristic(nb, goal)
                heapq.heappush(open_heap, (f, nb))

    return None
