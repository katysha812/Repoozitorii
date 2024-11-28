class Pizza:
    def init(self):
        self.size = None
        self.cheese = None
        self.toppings = []

    def str(self):
        return f"Pizza(size={self.size}, cheese={self.cheese}, toppings={self.toppings})"


class PizzaBuilder:
    def init(self):
        self.pizza = Pizza()

    def set_size(self, size):
        self.pizza.size = size
        return self

    def add_cheese(self, cheese):
        self.pizza.cheese = cheese
        return self

    def add_topping(self, topping):
        self.pizza.toppings.append(topping)
        return self

    def build(self):
        return self.pizza


# Использование
builder = PizzaBuilder()
my_pizza = (builder
            .set_size("Large")
            .add_cheese("Mozzarella")
            .add_topping("Pepperoni")
            .add_topping("Mushrooms")
            .build())

print(my_pizza)
'''
### Объяснение кода:

1. Класс Pizza:
   - Этот класс представляет собой объект пиццы. Он имеет атрибуты 'size', 'cheese' и 'toppings', которые будут заполнены в процессе строения.
   - Метод 'str' переопределен для того, чтобы мы могли легко видеть, как выглядит пицца в текстовом виде.

2. Класс 'PizzaBuilder':
   - Этот класс используется для пошагового создания 'Pizza'.
   - В конструкторе класса мы создаём новый объект 'Pizza'.
   - Методы 'set_size', 'add_cheese' и 'add_topping' настраивают атрибуты пиццы. Все они возвращают 'self', что позволяет вызывать методы последовательно.
   - Метод 'build' возвращает готовую пиццу.

3. Использование:
   - Мы создаем объект 'PizzaBuilder' и используем его для настройки пиццы, указывая её размер, сыр и начинки.
   - В итоге вызываем метод 'build', который возвращает готовую пиццу, и выводим её на экран.

Паттерн "Builder" полезен, когда создаваемый объект имеет много параметров и мы хотим избежать сложности из-за большого количества конструкторов.

'''