from enum import Enum
import random

class VidTemp(Enum):
    Celsius = 'C'
    Fahrenheit = 'F'
    Kelvin = 'K'

def temp_generate():
    Goroda = ["Абакан","Сорск","Усть-Абакан","Таштып","Боград","Копьёво","Абаза","Черногорск"]
    temperatura = {gorod: round(random.randint(-40, 40), 1) for gorod in Goroda}
    return temperatura

def temp_convert_f_k(celsius,vidtemp):
    if vidtemp == VidTemp.Celsius:
        return celsius
    if vidtemp == VidTemp.Fahrenheit:
        return round(((1.8 * celsius)+ 32),1)
    if vidtemp == VidTemp.Kelvin:
        return round((celsius + 273.15),1)
    
def temp_po_gorodu(gorod, temperatura):
    celsius = temperatura[gorod]
    fahrenheit = temp_convert_f_k(celsius,VidTemp.Fahrenheit)
    kelvin = temp_convert_f_k(celsius,VidTemp.Kelvin)
    return f"{celsius}{VidTemp.Celsius.value}, {fahrenheit}{VidTemp.Fahrenheit.value} , {kelvin}{VidTemp.Kelvin.value}"

def filter_gorods(temperatura, znak):
    if znak == '+':
        return list(filter(lambda s: s[1] > 0,temperatura.items()))
    if znak == '-':
         return list(filter(lambda s: s[1] < 0,temperatura.items()))
    
def sort_gorods(temperatura,vidsortirovki):
    if vidsortirovki == 'В':
        return sorted(temperatura.items(), key = lambda s: s[1])
    if vidsortirovki == 'У':
        return sorted(temperatura.items(), key = lambda s: s[1],reverse=True)
        
temperaturka = temp_generate()
Goroda = ["Абакан","Сорск","Усть-Абакан","Таштып","Боград","Копьёво","Абаза","Черногорск"]

print(f"список городов о погоде которых можно узнать: {Goroda}")
gorod = input("Введите город для которого необходимо узнать погоду: ")
print(f"Погода в {gorod}: {temp_po_gorodu(gorod,temperaturka)}")

znak = input("\n По какому знаку фильтровать города? Введите '+' или '-': ")
filtergorod = filter_gorods(temperaturka,znak)
if znak == '+':
    print(f"Города с погодой больше нуля: {filtergorod}")
if znak == '-':
    print(f"Города с погодой меньше нуля: {filtergorod}")

vidsortirovki = input("\n Как осортировать города? Введите 'В' (По возрастанию) или 'У' (По убыванию): ")
filtergorod = sort_gorods(temperaturka,vidsortirovki)
if vidsortirovki == 'В':
    print(f"Сортировка по возрастанию: {filtergorod}")
if vidsortirovki == 'У':
    print(f"Сортировка по убыванию: {filtergorod}")
# F = 1,8 C + 32
# K=C + 273.15
