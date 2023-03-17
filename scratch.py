# МОРСКОЙ БОЙ

from random import randint

# ИСКЛЮЧЕНИЯ
class BoardException(Exception):
    pass

class BoardGoingOff(BoardException):
    def __str__(self):
        return "Выстрел вне поля!"


class BoardRepeat(BoardException):
    def __str__(self):
        return "В эту часть поля уже стреляли!"


class BoardWrongShipException(BoardException):
    pass


class Dot:  # класс точек
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):  # метод для сравнения двух объектов (точек)
        return self.x == other.x and self.y == other.y

    def __repr__(self):   # метод для вывода точек в консоль
        return f"({self.x}, {self.y})"


class Ship:   # класс корабля
    def __init__(self, bow_ship, leng, direction):   # аргументы: длина корабля, точка носа корабля, положение корабля
        self.bow_ship = bow_ship
        self.leng = leng
        self.direction = direction
        self.lives = leng

    @property
    def dots(self):     # метод dots - возвращает список всех точек корабля
        ship_dots = []
        for a in range(self.leng):
            a_x = self.bow_ship.x
            a_y = self.bow_ship.y

            if self.direction == 0:
                a_x += a

            elif self.direction == 1:
                a_y += a

            ship_dots.append(Dot(a_x, a_y))

        return ship_dots

    def shoot(self, sh):
        return sh in self.dots


class Board:    # класс доски
    def __init__(self, hid=False, size=6):
        self.size = size
        self.hid = hid

        self.count = 0

        self.pole = [["O"] * size for _ in range(size)]

        self.used = []
        self.ships = []

    def add_ship(self, ship):

        for d in ship.dots:
            if self.out(d) or d in self.used:
                raise BoardRepeat()
        for d in ship.dots:
            self.pole[d.x][d.y] = "■"
            self.used.append(d)

        self.ships.append(ship)
        self.contur(ship)

    def contur(self, ship, verb=False):  # класс контура вокруг корабля (список координат точек вокруг корабля)
        near = [
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1), (0, 0), (0, 1),
            (1, -1), (1, 0), (1, 1)
        ]
        for d in ship.dots:
            for dx, dy in near:
                cur = Dot(d.x + dx, d.y + dy)
                # self.pole[cur.x][cur.y] = '+' # тест контура корабля
                if not (self.out(cur)) and cur not in self.used:  #проверка что точка корабля не выходит за границы поля и что точка корабля не попадает на занятую ячейку
                    if verb:
                        self.pole[cur.x][cur.y] = "."
                    self.used.append(cur)

    def __str__(self):
        res = ""
        res += "  | 1 | 2 | 3 | 4 | 5 | 6 |"
        for i, row in enumerate(self.pole):
            res += f"\n{i + 1} | " + " | ".join(row) + " |"

        if self.hid:
            res = res.replace("■", "O")
        return res

    def out(self, d):   # проверка что точка не выходит за границы поля
        return not ((0 <= d.x < self.size) and (0 <= d.y < self.size))

# b = Board()
# b.contur(Ship(2, Dot(2, 3), 0))  # тест контура корабля
# b.add_ship(Ship(3, Dot(2, 3), 0)) # тест добавления корабля
# b.add_ship(Ship(2, Dot(0, 1), 1)) # тест добавления корабля
# print(b)
# print(b.used) # вывод списка использованных ячеек

    def shot(self, d):
        if self.out(d):  # если координаты точки выстрела за пределами доски
            raise BoardGoingOff()  # выбрасываем исключение что вышли за пределы доски

        if d in self.used:  # если координаты точки выстрела уже были
            raise BoardUsedException()  # выбрасываем исключение что эта точка уже была

        self.used.append(d) # пополняем список занятых точек доски точкой данного выстрела

        for ship in self.ships:  # для корабля в списке кораблей
            if d in ship.dots:  # если точка выстрела в списке точек корабля
                ship.lives -= 1  # уменьшаем количество жизней корабля
                self.pole[d.x][d.y] = 'X'  # ставим в эту точку 'X'
                if ship.lives == 0:  # если корабль уничтожен
                    self.count += 1  # увеличиваем счетчик подбитых кораблей на 1
                    self.contur(ship, verb=True)  # обводим контур подбитого корабля
                    print("Корабль уничтожен!")
                    return False  # возвращаем False (чтобы сказать, что дальше ход не нужно делать)
                else:
                    print("Корабль ранен!")
                    return True # возвращаем True (чтобы сказать, что нужно делать следующий ход)

        self.pole[d.x][d.y] = "."   # если не выполнены вышеуказанные условия (корабль не поражен) ставим на эту ячейку '.'
        print("Мимо!")
        return False  # возвращаем False (переход хода)

    def begin(self):   # этот метод обнуляет список занятых точек (ранее он содержал точки вокруг корабля)
        self.used = []


class Player:  # класс игрока
    def __init__(self, board, enemy):  # в качестве аргументов - доски: своя и противника
        self.board = board
        self.enemy = enemy

    def ask(self):  # метод ask не определяем
        raise NotImplementedError()  # чтобы сказать, что этот метод должен быть, но у потомков этого класса

    def move(self):
        while True:  # бесконечный цикл
            try:
                target = self.ask()  # просим игрока дать координаты
                repeat = self.enemy.shot(target)  # делаем выстрел по этим координатам
                return repeat # если выстрел прошел хорошо - возвращаем нужно ли повторить ход
            except BoardException as e:  # если выстрел прошел неудачно - выбрасываем исключение
                print(e)  # и печатаем его


class AI(Player):  # класс игрока-компьютера
    def ask(self):
        d = Dot(randint(0, 5), randint(0, 5))  # генерируем случайные точки с координатами от 0 до 5
        print(f"Ход компьютера: {d.x + 1} {d.y + 1}")  # пользователю показываем сгенерированные координаты x+1, y+1 (т.к. доски начинаются с '1')
        return d


class User(Player):
    def ask(self):
        while True:
            cords = input("Ваш ход: ").split()  # запрос координат, и преобразование их в список из введенных координат

            if len(cords) != 2: # если длина списка не равна 2
                print(" Введите 2 координаты! ")
                continue  # пропускаем оставшийся код в этой итерации

            x, y = cords  # присваиваем переменным x, у значения введенных координат (если корректно введены 2 координаты)

            if not (x.isdigit()) or not (y.isdigit()):  # проверяем, что введенные координаты являются числами
                print(" Введите числа! ")
                continue  # пропускаем оставшийся код в этой итерации

            x, y = int(x), int(y)  # приводим введенные координаты к целым числам

            return Dot(x - 1, y - 1)  # возвращаем точку с координатами x-1, y-1 (т.к. координаты точки - индексы значений списка)


class Game:  # класс игры
    def __init__(self, size=6):
        self.size = size
        pl = self.random_board()  # создаем доску игрока
        co = self.random_board()  # создаем доску компьютера
        co.hid = True  # доску компьютера скрываем

        self.ai = AI(co, pl)  # создаем игрока-комп
        self.us = User(pl, co)  # создаем игрока-пользователя

    def random_board(self):  # метод создания случайной доски
        board = None  # доска изначально = None
        while board is None:  # задаем бесконечный цикл
            board = self.random_place()  # в котором создаем случайную доску
        return board   #  возвращаем доску

    def random_place(self):  # метод  случайной расстановки кораблей
        lens = [3, 2, 2, 1, 1, 1, 1]  # задаем список длин кораблей
        board = Board(size=self.size)   # помещаем в переменную board результат вызова класса Board
        attempts = 0  # создаем счетчик количества попыток расставить корабли
        for l in lens:
            while True:  # запускаем бесконечный цикл
                attempts += 1  # увеличиваем счетчик количества попыток расставить корабли на 1
                if attempts > 2000:  # если количество попыток расстановки корабля превысило 2000
                    return None  # говорим что расстановка не удалась
                ship = Ship(Dot(randint(0, self.size), randint(0, self.size)), l, randint(0, 1))
                try:
                    board.add_ship(ship)  # добавляем созданный корабль в список кораблей
                    break
                except BoardRepeat:  # если ошибка - выбрасываем исключение
                    pass
        board.begin()   # обнуляем список занятых точек поля
        return board  # возвращаем доску

    def greet(self):
        print("-------------------")
        print("        ИГРА       ")
        print("     морской бой   ")
        print("-------------------")
        print(" формат ввода: x y ")
        print(" x - номер строки  ")
        print(" y - номер столбца ")

    def loop(self):  # метод игрового цикла
        num = 0   # счетчик номеров хода
        while True:
            print("-" * 20)
            print("Доска пользователя:")  # выводим доску пользователя
            print(self.us.board)
            print("-" * 20)
            print("Доска компьютера:")  # выводим доску компьютера
            print(self.ai.board)
            if num % 2 == 0:
                print("-" * 20)
                print("Ходит пользователь!")
                repeat = self.us.move()  # спрашиваем нужно ли повторить ход (если попали)
            else:
                print("-" * 20)
                print("Ходит компьютер!")
                repeat = self.ai.move()  # спрашиваем нужно ли повторить ход (если попали)
            if repeat:
                num -= 1  # если нужно повторить ход, уменьшаем счетчик ходов на 1 (чтобы ход остался у того же игрока)

            if self.ai.board.count == 7:  # если количество уничтоженных кораблей равно общему количеству кораблей на доске компьютера
                print("-" * 20)
                print("Пользователь выиграл!")
                break  # выход из цикла

            if self.us.board.count == 7:  # если количество уничтоженных кораблей равно общему количеству кораблей на доске пользователя
                print("-" * 20)
                print("Компьютер выиграл!")
                break  # выход из цикла
            num += 1

    def start(self):  # метод для старта заставки и игрового цикла
        self.greet()
        self.loop()


g = Game()
g.start()  # запуск игры