from random import randint
from pprint import pprint
from math import floor
import time


def timeit(function):
    def func(*args, **kwargs):
        time_start = time.perf_counter()
        result = function(*args, **kwargs)
        print(f"{function.__name__} used {time.perf_counter()-time_start:.5f} seconds.")
        return result

    return func


class BidirectionalBubbleSort:
    @staticmethod
    def bbs(array: list[int]) -> None:
        swapped: bool = True
        while swapped:
            swapped = False
            for index in range(len(array) - 1):
                if array[index] > array[index + 1]:
                    array[index + 1], array[index] = array[index], array[index + 1]
                    swapped = True
            for index in range(len(array) - 2, 0, -1):
                if array[index] < array[index - 1]:
                    array[index - 1], array[index] = array[index], array[index - 1]
                    swapped = True

    @staticmethod
    @timeit
    def benchmark():
        print("BidirectionalBubbleSort -> ", end="")
        original_array = RANDOM_ARRAY.copy()
        BidirectionalBubbleSort.bbs(original_array)
        assert original_array == ANSWER


class StoogeSort:
    @staticmethod
    def stooge_sort(array: list[int], start=0, end=None) -> None:
        if end == None:
            end = len(array) - 1
        if array[start] > array[end]:
            array[start], array[end] = array[end], array[start]
        if end - start + 1 > 2:
            divide = floor((end - start + 1) / 3)
            StoogeSort.stooge_sort(array, start, end - divide)
            StoogeSort.stooge_sort(array, start + divide, end)
            StoogeSort.stooge_sort(array, start, end - divide)

    @staticmethod
    @timeit
    def benchmark():
        print("StoogeSort -> ", end="")
        original_array = RANDOM_ARRAY.copy()
        StoogeSort.stooge_sort(original_array)
        assert original_array == ANSWER


class OddEvenSort:
    @staticmethod
    def odd_even_sort(array: list[int]) -> None:
        sorted: bool = False
        while not sorted:
            sorted = True
            for i in range(1, len(array) - 1, 2):
                if array[i] > array[i + 1]:
                    array[i], array[i + 1] = array[i + 1], array[i]
                    sorted = False
            for i in range(0, len(array) - 1, 2):
                if array[i] > array[i + 1]:
                    array[i], array[i + 1] = array[i + 1], array[i]
                    sorted = False

    @staticmethod
    @timeit
    def benchmark():
        print("OddEvenSort -> ", end="")
        original_array = RANDOM_ARRAY.copy()
        OddEvenSort.odd_even_sort(original_array)
        assert original_array == ANSWER


class BubbleSort:
    @staticmethod
    def bubblesort(array: list[int]) -> None:
        swapped: bool = True
        while swapped:
            swapped = False
            for index in range(len(array) - 1):
                if array[index] > array[index + 1]:
                    array[index], array[index + 1] = array[index + 1], array[index]
                    swapped = True

    @staticmethod
    @timeit
    def benchmark():
        print("BubbleSort -> ", end="")
        original_array = RANDOM_ARRAY.copy()
        BubbleSort.bubblesort(original_array)
        assert original_array == ANSWER


class QuickSort:
    @staticmethod
    def quicksort(array: list[int]) -> list[int]:
        if len(array) <= 1:
            return array

        left: list[int] = list()
        right: list[int] = list()
        mid: int = (len(array) - 1) // 2

        for index, element in enumerate(array):
            if index == mid:
                continue
            right.append(element) if element > array[mid] else left.append(element)
        return QuickSort.quicksort(left) + [array[mid]] + QuickSort.quicksort(right)

    @staticmethod
    @timeit
    def benchmark():
        print("QuickSort -> ", end="")
        original_array = RANDOM_ARRAY.copy()
        assert QuickSort.quicksort(original_array) == ANSWER


class QuickSort_Inplace:
    @staticmethod
    def partition(array: list[int], low: int, high: int) -> int:
        pivotElement = array[(low + high) // 2]
        left, right = low - 1, high + 1

        while True:
            left, right = left + 1, right - 1
            while array[left] < pivotElement:
                left += 1
            while array[right] > pivotElement:
                right -= 1
            if left >= right:
                return right
            array[left], array[right] = array[right], array[left]

    @staticmethod
    def quicksort(array: list[int], left, right):
        if right > left:
            r = QuickSort_Inplace.partition(array, left, right)
            QuickSort_Inplace.quicksort(array, left, r)
            QuickSort_Inplace.quicksort(array, r + 1, right)

    @staticmethod
    @timeit
    def benchmark():
        print("QuickSort (Inplace) -> ", end="")
        original_array = RANDOM_ARRAY.copy()
        QuickSort_Inplace.quicksort(original_array, 0, len(original_array) - 1)
        assert original_array == ANSWER


if __name__ == "__main__":
    for i in [10, 100, 1000, 10000]:
        RANDOM_ARRAY = [randint(-32768, 32768) for i in range(i)]
        ANSWER = sorted(RANDOM_ARRAY)
        print(f"Random Array Size is {len(RANDOM_ARRAY)}")
        QuickSort_Inplace().benchmark()
        QuickSort().benchmark()
        BubbleSort().benchmark()
        BidirectionalBubbleSort().benchmark()
        OddEvenSort().benchmark()
        StoogeSort().benchmark()
        print("=====")
