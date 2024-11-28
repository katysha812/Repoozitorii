from enum import Enum
class Pizza: #класс пиццы
    def init(self):
        self.name = None #название пиццы
        self.dough = [] #тесто
        self.sauce = [] #соусы
        self.cheese = [] #сыры
        self.toppings = [] #добавки
        
        
#метод для строкового представления объекта
    def str(self):

        return f"Пицца {self.name}: (тесто={self.dough}, соусы={self.sauce}, сыры={self.cheese}, добавки={self.toppings})"

class Dough(Enum): #перечисление видов теста
    THIN = "тонкое"
    THICK = "толстое"
    STANDART = "стандартное"
    XRUSTIACHEE = "хрустящее"

class Sauce(Enum): #перечисление видов соуса
    TOMATO = "томатный"
    CREAM = "сливочный"
    CHESNOCHNII = "чесночный"
    BARBEQ = "барбекю"
    FIRMENNII = "фирменный"


class Cheese(Enum): #перечисление видов сыра
    MOZZARELLA = "моцарелла"
    PARMESAN = "пармезан"
    KAMAMBERR = "камамбер"
    CHEDDER = "чеддер"
    SULUGUNI = "сулугуни"
    BRU = "бри"
    MAASDAM = "маасдам"
    GAUDA = "гауда"
    FETA = "фета"

class Topping(Enum): #перечисление видов добавок
    MUSHROOMS = "грибы"
    OLIVKI = "оливки"
    OPEREZ = "острый перец"
    SPEREZ = "сладкий перец"
    BECON = "бекон"
    KAPERCI = "каперсы"
    ANANASI = "ананасы"
    KOLBASKI = "колбаски"
    SOSIGIES = "сосиски"
    KURIZA = "курица"
    MASLINI = "маслины"
    VETCHINA = "ветчина"


class PizzaBuilder: #класс постройщика пицц
    def init(self):
        self.pizza = Pizza() #пицца для настройки

    def set_name(self, name): #установить название пиццы
            self.pizza.name = name
            return self #обязательно нужно вернуть текущий экземпляр

#PizzaBuilder
    def build_dough(self, dough): #выбрать тесто для пиццы
        self.pizza.dough.extend(dough)
        return self
    
    def build_sauce(self, sauce): #выбрать соус
        self.pizza.sauce.extend(sauce)
        return self
    
    def build_cheese(self, cheese): #выбрать сыр
        self.pizza.cheese.extend(cheese)
        return self
    
    def build_toppings(self, toppings): #прибавить добавок
        self.pizza.toppings.extend(toppings)
        return self
    
    def bake(self): #запечь пиццу (вернуть объект пиццы)
        return self.pizza
    
#создание настройщика пицц
builder = PizzaBuilder()

#запекаем пиццу

pizza = (builder.set_name("4 сыра")
.build_sauce([Sauce.CREAM.value])
.build_cheese([Cheese.MOZZARELLA.value, Cheese.MAASDAM.value, Cheese.FETA.value, Cheese.KAMAMBERR.value])
.build_dough([Dough.THICK.value])
.build_toppings([Topping.KAPERCI.value, Topping.MASLINI.value])
.bake()
)
print(pizza)