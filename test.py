import heapq
from typing import Any

if __name__ == "__main__":

    class Vertex:
        key: Any
        visited: bool
        distance: float
        color: str

        def __init__(self, key: Any):
            self.key = key
            self.visited = False
            self.parent = None
            self.distance = float("inf")

        def __lt__(self, other):
            return self.distance < other.distance

    Q = [
        Vertex("a"),
        Vertex("b"),
        Vertex("c"),
    ]

    for i in range(1, len(Q)):
        Q[i].distance = i

    Q.append(Vertex("d"))

    heapq.heapify(Q)

    for i in range(len(Q)):
        print(heapq.heappop(Q).distance)
