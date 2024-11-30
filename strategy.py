from abc import ABC, abstractmethod

class AnimalStrategy(ABC): #абстрактный базовый класс всех стратегий

    @abstractmethod
    def povedenie(self, animalName): pass #абстрактный метод поведения


class MeowStrategy(AnimalStrategy): 

    def povedenie(self, animalName):
        print(f"я вижу что: {animalName} мяукает")
        
class FlyStrategy(AnimalStrategy):
    def povedenie(self, animalName):
        print(f"я вижу что: {animalName} летает")

class NachStrategy: #туристическое агентство
    def __init__(self, strategy: AnimalStrategy):
        self.strategy = strategy #задаём начальную стратегию (транспорт)

    def set_strategy(self, strategy: AnimalStrategy):
        self.strategy = strategy 

    def plan_strategy(self, animalName): 
        self.strategy.povedenie(animalName)

meow_strategy = MeowStrategy() #создаём стратегию 
fly_strategy = FlyStrategy() #создаём стратегию 

#отправляем туриста сначала на автобусе в Москву, а затем на самолёте в Токио

animal = NachStrategy(meow_strategy) #создаём туристическое агентство
animal.plan_strategy("кошечка") 

animal.set_strategy(fly_strategy)

animal.plan_strategy("синичка") 
