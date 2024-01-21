from random import randint
from typing import List, Optional

import big_o
import numpy as np


def generate_random_array(n: Optional[int] = 10, a: int = 0, b: int = 100) -> List[int]:
    return np.random.randint(a, b, n).tolist()


def generate_positive_integers(n: int = 1, min: int = 0, max: int = 10) -> List[int]:
    A = big_o.datagen.integers(n, min, max)
    return A


def swap(A: List[int], a: int, b: int):
    A[a], A[b] = A[b], A[a]


def partition(A: List[int], s: int, f: int) -> int:
    pivot = A[f]
    i = s - 1
    for j in range(s, f):
        if A[j] <= pivot:
            i += 1
            swap(A, i, j)
    swap(A, i + 1, f)
    return i + 1


def random_partition(A: List[int], s: int, f: int) -> int:
    p = randint(s, f)
    swap(A, p, f)
    return partition(A, s, f)
