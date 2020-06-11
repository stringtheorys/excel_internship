"""Implementation of a priority queue using a binary heap"""

from __future__ import annotations

from enum import Enum, auto
from typing import List, Generic, TypeVar, Callable

T = TypeVar('T')


class Comparison(Enum):
    """
    Comparison types
    """
    GREATER = auto()
    EQUAL = auto()
    LESS = auto()


class PriorityQueue(Generic[T]):
    """
    A custom binary heap for the nodes of the branch and bound algorithm
    """

    queue: List[T] = []
    size: int = 0

    def __init__(self, comparator: Callable[[T, T], Comparison]):
        self.comparator = comparator

    def pop(self) -> T:
        """
        Remove top element from the queue

        :return: Top element of the queue
        """
        if self.size == 1:
            return self.queue.pop(0)

        root = self.queue[0]
        self.queue[0] = self.queue.pop(-1)

        pos = 0
        while True:
            left, right, largest = self.left(pos), self.right(pos), pos

            if left < self.size and self.comparator(self.queue[left], self.queue[pos]) == Comparison.GREATER:
                largest = left
            if right < self.size and self.comparator(self.queue[right], self.queue[pos]) == Comparison.GREATER:
                largest = right

            if largest == pos:
                break
            else:
                self.swap(pos, largest)
                pos = largest

        return root

    def push(self, data: T):
        """
        Pushes new element to the queue

        :param data: New element
        """
        self.queue.append(data)
        self.size += 1

        pos = self.size - 1
        parent = self.parent(pos)
        while pos > 0 and self.comparator(self.queue[parent], self.queue[pos]) == Comparison.GREATER:
            self.swap(pos, parent)

            pos = parent
            parent = self.parent(pos)

    def push_all(self, data: List[T]):
        """
        Pushes a list of element to the queue

        :param data: List of elements
        """
        for d in data:
            self.push(d)

    @staticmethod
    def parent(pos: int) -> int:
        """
        Position of the parent for an element

        :param pos: Element position
        :return: Parent element position
        """
        return (pos - 1) // 2

    @staticmethod
    def left(pos: int) -> int:
        """
        Position of the left to an element

        :param pos: Element position
        :return: Left element position
        """
        return 2 * pos + 1

    @staticmethod
    def right(pos: int) -> int:
        """
        Position of the right to an element

        :param pos: Element position
        :return: Right element position
        """
        return 2 * pos + 2

    def swap(self, child: int, parent: int):
        """
        Swap an child and parent element

        :param child: Child element position
        :param parent: Parent element position
        """
        temp = self.queue[child]
        self.queue[child] = self.queue[parent]
        self.queue[parent] = temp

    def __str__(self) -> str:
        """
        Converts the queue to a string

        :return: String representing the queue
        """

        return f"[{', '.join(self.queue)}]"
