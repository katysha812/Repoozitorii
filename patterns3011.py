from enum import Enum
class Computer: #класс Computer
    def __init__ (self):
        self.processor = None #Центральный процессор
        self.op = None #Оперативная память
        self.nacopitel = None #Накопитель
        self.videocard = None #Видеокарта
        self.komplekt = [] #Комплектующие
        
    def __str__(self):
        return f"Компьютер: (ЦП = {self.processor}, ОП = {self.op}, Накопитель = {self.nacopitel}, Видеокарта = {self.videocard}, Комплектующие = {self.komplekt})"
    
class Processor(Enum): #перечисление видов процессора
    AMDA67480OEM = "Процессор AMD A6-7480 OEM"
    AMDAthlonX4950OEM = "Процессор AMD Athlon X4 950 OEM"
    AMDA69500OEM = "Процессор AMD A6-9500 OEM"
    INTELCOREI310100FOEM = "Процессор Intel Core i3-10100F OEM"
    INTELCOREI59400FOEM = "Процессор Intel Core i5-9400F OEM"
    ANDRYZEN5500BOX = "Процессор AMD Ryzen 5 5500 BOX"

class Op(Enum): #перечисление видов оперативки
    SODIMMKINGSTONFURYIMPACT16GB = "Оперативная память SODIMM Kingston FURY Impact [KF432S20IBK2/16] 16 ГБ"
    SODIMMKINGSTONVALUERAM8GB = "Оперативная память SODIMM Kingston ValueRAM [KVR26S19S8/8] 8 ГБ"
    SODIMMAPACER4GB = "Оперативная память SODIMM Apacer [DV.04G2K.KAM] 4 ГБ"
    SODIMMSAMSUNG8GB = "Оперативная память SODIMM Samsung [M471A1K43DB1-CWE] 8 ГБ"

class Nacopitel(Enum): #перечисление видов накопителей
    SATAKINGSTONA400480GB = "480 ГБ 2.5'' SATA накопитель Kingston A400 [SA400S37/480G]"
    SATASAMSUNG870EVO500GB = "500 ГБ 2.5'' SATA накопитель Samsung 870 EVO [MZ-77E500BW]"
    SATAADATASU650256GB = "256 ГБ 2.5'' SATA накопитель ADATA SU650 [ASU650SS-256GT-R]"
    SATAAPACERAS350256GB = "256 ГБ 2.5'' SATA накопитель Apacer AS350 PANTHER [95.DB2A0.P100C]"

class Videocard(Enum): #перечисление видов видеокарт
    MSIGEFORCERTX4060 = "Видеокарта MSI GeForce RTX 4060 VENTUS 2X BLACK OC [GeForce RTX 4060 VENTUS 2X]"
    GIGABYTEGEFORCERTX4060 = "Видеокарта GIGABYTE GeForce RTX 4060 Ti EAGLE OC [GV-N406TEAGLE OC-8GD]"
    ASROCKINTELARCA580 = "Видеокарта ASRock Intel Arc A580 Challenger OC [A580 CL 8GO]"
    PALITGEFORCERTX3050 = "Видеокарта Palit GeForce RTX 3050 StormX [NE63050018P1-1070F]"

class Komplekt(Enum): #перечисление видов комплектующих
    MONITORVG27AQ1ABLACK = "27'' Монитор ASUS TUF Gaming VG27AQ1A черный"
    MONITORDF24N1BLACK = "23.8'' Монитор DEXP DF24N1 черный"
    KEYBOARDLOGITECHK120 = "Клавиатура проводная Logitech K120 [920-002506/22]"
    KEYBOARDMSIVIGORGK30 = "Клавиатура проводная MSI Vigor GK30"
    KEYBOARDADORGAMINGPATRON75 = "Клавиатура проводная+беспроводная ARDOR GAMING Patron 75 [AG-ZD-Pa83GY-P-HS-G-Sub]"
    MOUSEFURYBLACK = "Мышь проводная ARDOR GAMING Fury [ARD-FURY3327-BK] черный"
    MOUSELAMZUATLANTISBLUE = "Мышь беспроводная/проводная LAMZU Atlantis V2 BK MCU 1K голубой"

class ComputerBuilder:
    def __init__(self):
        self.computer = Computer()  
        
    def build_processor(self,processor):
        self.computer.processor = processor
        return self
        
    def build_op(self,op):
        self.computer.op = op
        return self
         
    def build_nacopitel(self,nacopitel):
        self.computer.nacopitel = nacopitel
        return self
         
    def build_videocard(self,videocard):
        self.computer.videocard = videocard
        return self
         
    def build_komplekt(self,komplekt):
        self.computer.komplekt.extend(komplekt)
        return self
         
    def sobratecompik(self):
        return self.computer

builder = ComputerBuilder()

computer = (builder.build_processor(Processor.AMDA69500OEM.value)
.build_nacopitel(Nacopitel.SATAKINGSTONA400480GB.value)
.build_op(Op.SODIMMSAMSUNG8GB.value)
.build_videocard(Videocard.GIGABYTEGEFORCERTX4060.value)
.build_komplekt([Komplekt.MONITORDF24N1BLACK.value,Komplekt.KEYBOARDLOGITECHK120.value,Komplekt.MOUSEFURYBLACK.value])
.sobratecompik()
)

print(computer)