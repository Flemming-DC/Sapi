
class DynRange():
    def __init__(self, limit: int|list) -> None:
        self.limit = limit if isinstance(limit, int) else len(limit)
        self._current = 0

    def __iter__(self):
        return self

    def __next__(self):
        if self._current >= self.limit:
            raise StopIteration
        result = self._current
        self._current += 1
        return result

# from typing import TypeVar, Iterator
# T = TypeVar['T']

# class LoopList(list[T]):

#     def __iter__(self) -> Iterator[T]:
#         return self

#     def __next__(self) -> T:
#         if self._current >= self.limit:
#             raise StopIteration
#         result = self._current
#         self._current += 1
#         return result



# this code
# m = 4
# for i in range(m):
#     if m < 8:
#         m += 1
#     print(i)

# A = [1, 2, 3, 4]
# for a in A:
#     if A[-1] < 8:
#         A.append(a)
#     print(a)



