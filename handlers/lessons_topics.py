TOPICS = {
    "beginner": {
        "ru": """📘 *Тема 1: Введение в Python*
Python — это язык программирования, который прост в изучении и мощен в использовании.

print("Привет, мир!")


📘 Тема 2: Переменные и типы данных
Переменные позволяют хранить значения и работать с ними в программе.

name = "Алия"
age = 18
height = 1.70
print(type(name), type(age), type(height))


📘 Тема 3: Условия
Оператор if используется для проверки условий.

if age >= 18:
    print("Совершеннолетний")
else:
    print("Несовершеннолетний")


""",

        "en": """📘 *Topic 1: Introduction to Python*

Python is a simple and powerful programming language.

print("Hello, world!")


📘 Topic 2: Variables and data types
Variables allow storing and processing values.

name = "Ali"
age = 18
height = 1.75
print(type(name), type(age), type(height))


📘 Topic 3: Conditions
The if statement is used for logical checks.

if age >= 18:
    print("Adult")
else:
    print("Minor")


""",

        "kz": """📘 *Тақырып 1: Python тіліне кіріспе*

Python — үйренуге оңай және қуатты тіл.

print("Сәлем, әлем!")


📘 Тақырып 2: Айнымалылар мен деректер түрлері
Айнымалылар мәліметтерді сақтауға және өңдеуге мүмкіндік береді.

name = "Алия"
age = 18
height = 1.65
print(type(name), type(age), type(height))


📘 Тақырып 3: Шарттар
if операторы логикалық тексерулерге қолданылады.

if age >= 18:
    print("Ересек")
else:
    print("Жасөспірім")


"""
    },

    "intermediate": {
        "ru": """📘 *Тема 1: Циклы*

Циклы позволяют выполнять код несколько раз.

for i in range(5):
    print(i)


📘 Тема 2: Функции
Функции позволяют структурировать код.

def greet(name):
    return f"Привет, {name}!"
print(greet("Алия"))


📘 Тема 3: Списки и словари

fruits = ["яблоко", "банан", "киви"]
prices = {"яблоко": 200, "банан": 150}
print(fruits[0], prices["банан"])


""",

        "en": """📘 *Topic 1: Loops*

Loops allow repeating blocks of code.

for i in range(5):
    print(i)


📘 Topic 2: Functions
Functions make code reusable.

def greet(name):
    return f"Hello, {name}!"
print(greet("Ali"))


📘 Topic 3: Lists and dictionaries

fruits = ["apple", "banana", "kiwi"]
prices = {"apple": 200, "banana": 150}
print(fruits[0], prices["banana"])


""",

        "kz": """📘 *Тақырып 1: Циклдер*

Циклдер кодты бірнеше рет орындауға мүмкіндік береді.

for i in range(5):
    print(i)


📘 Тақырып 2: Функциялар
Функциялар кодты құрылымдауға мүмкіндік береді.

def greet(name):
    return f"Сәлем, {name}!"
print(greet("Алия"))


📘 Тақырып 3: Тізімдер мен сөздіктер

fruits = ["алма", "банан", "киви"]
prices = {"алма": 200, "банан": 150}
print(fruits[0], prices["банан"])


"""
    },

    "advanced": {
        "ru": """📘 *Тема 1: Классы и объекты*

Классы позволяют создавать собственные типы данных.

class Person:
    def __init__(self, name):
        self.name = name
    def say_hi(self):
        print(f"Привет, я {self.name}")


📘 Тема 2: Работа с файлами

with open("data.txt", "w") as f:
    f.write("Привет, файл!")


📘 Тема 3: Исключения
Обработка ошибок делает код надёжнее.

try:
    x = int("abc")
except ValueError:
    print("Ошибка преобразования!")


""",

        "en": """📘 *Topic 1: Classes and objects*

Classes are used to create custom data types.

class Person:
    def __init__(self, name):
        self.name = name
    def say_hi(self):
        print(f"Hi, I'm {self.name}")


📘 Topic 2: Working with files

with open("data.txt", "w") as f:
    f.write("Hello, file!")


📘 Topic 3: Exceptions
Exception handling makes code safer.

try:
    x = int("abc")
except ValueError:
    print("Conversion error!")


""",

        "kz": """📘 *Тақырып 1: Кластар мен объектілер*

Кластар өз деректер түрлерін жасауға мүмкіндік береді.

class Person:
    def __init__(self, name):
        self.name = name
    def say_hi(self):
        print(f"Сәлем, мен {self.name}")


📘 Тақырып 2: Файлмен жұмыс

with open("data.txt", "w") as f:
    f.write("Сәлем, файл!")


📘 Тақырып 3: Ерекше жағдайлар
Қате өңдеу бағдарламаны сенімді етеді.

try:
    x = int("abc")
except ValueError:
    print("Қате түрлендіру!")


"""
    }
}
