from abc import ABC, abstractmethod
# Интерфейс Стратегии
class SortStrategy(ABC):
    @abstractmethod
    def sort(self, data):
        pass

# Конкретная стратегия: сортировка пузырьком
class BubbleSort(SortStrategy):
    def sort(self, data):
        n = len(data)
        for i in range(n):
            for j in range(0, n-i-1):
                if data[j] > data[j+1]:
                    data[j], data[j+1] = data[j+1], data[j]
        return data

# Конкретная стратегия: сортировка выбором
class SelectionSort(SortStrategy):
    def sort(self, data):
        n = len(data)
        for i in range(n):
            min_idx = i
            for j in range(i+1, n):
                if data[j] < data[min_idx]:
                    min_idx = j
            data[i], data[min_idx] = data[min_idx], data[i]
        return data

# Контекст, который использует стратегию
class Sorter:
    def __init__(self, strategy: SortStrategy):
        self._strategy = strategy

    def set_strategy(self, strategy: SortStrategy):
        self._strategy = strategy

    def sort(self, data):
        return self._strategy.sort(data)

# Пример использования
data = [64, 25, 12, 22, 11]

sorter = Sorter(BubbleSort())
print("Bubble Sort:", sorter.sort(data.copy()))

sorter.set_strategy(SelectionSort())
print("Selection Sort:", sorter.sort(data.copy()))
