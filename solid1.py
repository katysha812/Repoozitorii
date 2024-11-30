from enum import Enum

class PizzaType(Enum): #тип пиццы
    MARGARITA = 1,
    PEPPERONI = 2,

class OrderManager: #для управления заказами,
    def __init__(self):
        self.amount = 0.0 #сумма заказа

    def create_order(self): #создать заказ
        self.amount = 0.0 #сумма заказа
        print("Заказ пиццы создан")

    def get_amount(self):  # метод для получения суммы заказа
        return self.amount
    
class PriceCalculator: #для расчёта стоимости,
 
 def calculate_price(self, pizza_type): #высчитать цену
        if pizza_type == PizzaType.MARGARITA:
            return 10.0 
        elif pizza_type == PizzaType.PEPPERONI:
            return 12.50
        else:
            print("Неизвестный тип пиццы")
            return 0.00

class ReceiptPrinter: #для печати чеков.
    def print_receipt(self, amount): #печать чека
        print("Печать чека...")
        print(f"С вас: {amount}")


order = OrderManager()
order.create_order()

price_calc = PriceCalculator()
price = price_calc.calculate_price(PizzaType.MARGARITA)
order.amount = price

printer = ReceiptPrinter()
printer.print_receipt(order.get_amount())

'''
Проблема: класс PizzaOrder выполняет слишком много задач: создание
заказа, расчет стоимости и печать чека.
Задача: разделить обязанности на три отдельных класса:
OrderManager – для управления заказами,
PriceCalculator – для расчёта стоимости,
ReceiptPrinter – для печати чеков.
'''