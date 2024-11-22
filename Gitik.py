# Создать список результатов полусеместровой аттестации и
# вывести все результаты с оценкой «хорошо» или выше.

# Сохраните всех неаттестованных студентов в отдельный список.

# Класс результат
# полусеместровой
# аттестации   
'''
class Attestatia:

    def __init__(self, name, group ,semestr,predmet,att):
        self.name = name  # Студент,
        self.group = group # группа
        self.semestr = semestr # семестр,
        self.predmet = predmet # предметы,
        self.att = att # аттестации

    def __str__(self):
        return f"Студент: {self.name}, группа {self.group} Семестр: {self.semestr}, предмет: {self.predmet}, оценка: {self.att}"
    

Savelov_Fizika = Attestatia("Савелов Алексей", "ИС(ВП)-52",2,"Физика",2)
Savelov_Istoria = Attestatia("Савелов Алексей", "ИС(ВП)-52",2,"История",3)
Veslouhova_Informatika = Attestatia("Веслоухова Наталья", "ИС(ПРО)-13",1,"Информатика",5)
Veslouhova_English = Attestatia("Веслоухова Наталья", "ИС(ПРО)-13",1,"Иностранный язык",4)
Marmeladovaova_Math = Attestatia("Мармеладова Маргарита", "ИС(АБД)-28",2,"Математика",4)
Egorov_Fizika = Attestatia("Егоров Никита", "ИС(ПТ)-11",2,"Физика",4)

list_att = [Savelov_Fizika, Savelov_Istoria, Veslouhova_Informatika, Veslouhova_English, Marmeladovaova_Math, Egorov_Fizika]

list_4or5 = list(filter(lambda s: s.att >= 4, list_att))
print("все результаты с оценкой «хорошо» или выше: ")
print("\n".join(map(str, list_4or5)))

list_neatt = list(filter(lambda s: s.att == 2, list_att))
print("все неаттестованные студенты: ")
print("\n".join(map(str, list_neatt)))

list1 = [letnyases2021, letnyases2022, letnyases2023, zimases2021, zimases2022]

ekz = list(map(lambda s: s.ekzamenov, list1))
#print(ekz)

avg = sum(ekz)/len(ekz)
print(f"Среднее значение: {avg}")

#вывести все сессии со средним количеством экзаменов и выше.
list2 = list(filter(lambda s: s.ekzamenov >= avg, list1))
print("Сессии со средним количеством экзаменов и выше: ")
print("\n".join(map(str, list2)))

#Сохранить все сессии с количеством зачётов от 1 до 3. 
list3 = list(filter(lambda s: 1 <= s.zachetov <= 3, list1))
print("Сессии с количеством зачётов от 1 до 3:")
print("\n".join(map(str, list3)))

'''

class Personaz:
    def __init__(self, name, monetki, keys, score, kolvopowerups):
        self.name = name
        self.monetki = monetki 
        self.keys = keys 
        self.score = score 
        self.kolvopowerups = kolvopowerups 

    def __str__(self):
        return f"Персонаж: {self.name}, монет собрано {self.monetki} ключей: {self.keys}, счет: {self.score}, power-ups использовано: {self.kolvopowerups}"
    
Jake = Personaz("Jake", 450, 3, 36789, 2)
Tricky = Personaz("Tricky", 1590, 1, 52025, 2)
Fresh = Personaz("Fresh", 390, 0, 5000, 8)
Yutani = Personaz("Yutani", 1800, 6, 25001, 5)
Frank = Personaz("Frank", 812, 1, 40200, 3)

List_personasiki = [Jake, Tricky, Fresh, Yutani, Frank]

money = list(map(lambda s: s.monetki, List_personasiki))
summa = sum(money)
print(f"Всего монет собрано: {summa}")

keys = list(map(lambda s: s.keys, List_personasiki))
avg = sum(keys)/len(keys)
print(f"Среднее значение ключей на персонажа: {int(avg)}")

score = list(map(lambda s: s.score, List_personasiki))
maxscore = max(score)
print(f"Максимальный счет: {maxscore}")

pu = list(map(lambda s: s.kolvopowerups , List_personasiki))
minpu = min(pu)
print(f"Персонаж с наименьшим кол-вом использованных power-ups: ")
list_min_pu = list(filter(lambda s: minpu == s.kolvopowerups, List_personasiki))
print("\n".join(map(str, list_min_pu)))

listm = list(filter(lambda s: s.monetki >= 1000, List_personasiki))
print("Собрали более 1000 монет: ")
print("\n".join(map(str, listm)))
print(f"Количество: {len(listm)}")