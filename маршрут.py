from abc import ABC, abstractmethod

class TravelStrategy(ABC): #абстрактный базовый класс всех стратегий

    @abstractmethod
    def travel(self, transportName, destination): pass #абстрактный метод отправки в путешествие

class BusTravel(TravelStrategy): #путешествие на автобусе

    def travel(self, transportName, destination): #едем на автобусе до destination
        print(f"Еду на автобусе: {transportName} до {destination}")
        
class SamokatTravel(TravelStrategy):
    def travel(self, transportName, destination): #летим на самокате до destination
        print(f"Лечу на самокате: {transportName} до {destination}")
        
class AirplaneTravel(TravelStrategy):
    def travel(self, transportName, destination): #летим на самолёте до destination
        print(f"Лечу на самолете: {transportName} до {destination}")

class TravelAgency: #туристическое агентство
    def __init__(self, strategy: TravelStrategy):
        self.strategy = strategy #задаём начальную стратегию (транспорт)

    def set_strategy(self, strategy: TravelStrategy):
        self.strategy = strategy #задаём новый транспорт

    def plan_trip(self, transportName, destination): #планируем путешествие на заданном транспорте
        self.strategy.travel(transportName, destination)

bus_travel = BusTravel() #создаём стратегию "автобус"
airplane_travel = AirplaneTravel() #создаём стратегию "самолёт"
samokat_travel = SamokatTravel() #создаём стратегию "самокат"

#отправляем туриста сначала на автобусе в Москву, а затем на самолёте в Токио

agency = TravelAgency(bus_travel) #создаём туристическое агентство
agency.plan_trip("Двухэтажный", "Москва") #задаём новый транспорт

agency.set_strategy(airplane_travel)

agency.plan_trip("Sukhoy Superjet", "Токио") #задаём новый транспорт

agency.set_strategy(samokat_travel)
agency.plan_trip("электронный", "сквера") #задаём новый транспорт