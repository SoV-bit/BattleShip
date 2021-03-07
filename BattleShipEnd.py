from random import randint
#приветствую решил пройтись по коду сделать не большие коментарии
#Create by Константин )

class BoardException(Exception):
    pass


class BoardWrongShipException(BoardException):
    pass


class InputError(Exception):
    def __str__(self):
        return "Вы ввели не целое число"  # +


class BoardOutException(BoardException):
    def __str__(self):
        return "Вы вводете координаты за пределами доски"


class BoardUsedException(BoardException):
    def __str__(self):
        return "Вы уже стреляли в эту клетку"


class Dot:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):
        return (self.x == other.x) and (self.y == other.y)

    def __repr__(self):
        return f"Dot({self.x},{self.y})"


class Ship:
    def __init__(self, nose, width, direction):
        self.width = width
        self.nose = nose
        self.direction = direction
        self.live = width

    @property
    def dots(self):
        ship_dots = []
        for i in range(self.width):
            curs_x = self.nose.x
            curs_y = self.nose.y
            if self.direction == 0:
                curs_x += i
            elif self.direction == 1:
                curs_y += i
            ship_dots.append(Dot(curs_x, curs_y))
        return ship_dots

    def shooten(self, shot):
        return shot in self.dots

    @property
    def contour(self):
        ship_countour = []
        near = [
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1), (0, 0), (0, 1),
            (1, -1), (1, 0), (1, 1)
        ]
        for dot in self.dots:
            for dot_x, dot_y in near:
                if (Dot(dot.x + dot_x, dot.y + dot_y) not in self.dots) and (Dot(dot.x + dot_x, dot.y + dot_y) not in ship_countour):
                    ship_countour.append(Dot(dot.x + dot_x, dot.y + dot_y))
        return ship_countour


class Board:
    def __init__(self, hid=False, size=6, battle_front=[3, 2, 2, 1, 1, 1, 1]):
        self.memory = 0 #Небольшой костыль памяти как у рыбки Дори
        self.size = size
        self.battle_front = battle_front
        self.field = [[" "] * size for _ in range(size)]
        self.hid = hid
        self.busy = []
        self.ships = []
        self.counter_list = []

    def set_memory(self, mem):
        self.memory = mem  # Ура у него появилась память, если есть лучше способ хочу узнать

    @property
    def get_memory(self):
        return self.memory #Узнаем о чем помнит наша Дори

    def add_ship(self, ship):
        for dot in ship.dots:
            if self.out(dot) or dot in self.busy:
                raise BoardWrongShipException()
        for dot in ship.dots:
            self.field[dot.x][dot.y] = "■"
            self.busy.append(dot)
        for dot in ship.contour:
            if not self.out(dot) and dot not in self.busy:
                self.busy.append(dot)
        self.ships.append(ship)

    def __str__(self):
        s = "  |" #Сумашедший способ отображения доски, так же нитересны другие варианты
        for i in range(len(self.field)):
            if len(str(i + 1)) <= 1:
                s += " " + str(i + 1) + " |"
            else:
                s += " " + str(i + 1) + "|"
        for i, j in enumerate(self.field):
            if len(str(i + 1)) <= 1:
                s += f"\n{i + 1} | " + " | ".join(j) + " |"
            else:
                s += f"\n{i + 1}| " + " | ".join(j) + " |"
        if self.hid:
            s = s.replace("■", " ")
        return s

    def shot(self, dot):
        if self.out(dot):
            raise BoardOutException
        if dot in self.busy:
            raise BoardUsedException
        self.busy.append(dot)

        for ship in self.ships:
            if dot in ship.dots:
                ship.live -= 1
                self.field[dot.x][dot.y] = "*"
                if ship.live == 0:
                    print("Корабль уничтожен")
                    for d2 in ship.dots: #Если уничтожен то заменяем на крестики для визуализации
                        self.field[d2.x][d2.y] = "X"
                    for d2 in ship.contour:
                        if d2 in self.counter_list:
                            self.field[d2.x][d2.y] = "."
                            self.busy.append(d2)
                    self.battle_front.pop(self.battle_front.index(ship.width))
                    self.set_memory(0) #Тригер памяти на событие
                    return False
                else:
                    print("Корабль ранен!")
                    self.set_memory(1)#Тригер памяти на событие
                    return True
        self.field[dot.x][dot.y] = "."
        print("Мимо!")
        return False

    def begin(self):
        self.counter_list = self.busy #Запоминаем контуры кораблей для отображения после убийства
        self.busy = [] #Теперь заполняем стрельбу и контуры после убийства

    def out(self, dot):
        return not ((0 <= dot.x < self.size) and (0 <= dot.y < self.size))


class Player:
    def __init__(self, board, enemy):
        self.self_board = board
        self.enemy_board = enemy
        self.near = [] #Список для определения точек рядом
        self.smart = [] #Запоминаем куда стреляли

    def ask(self):
        raise NotImplementedError()

    def move(self):
        while True:
            try:
                target = self.ask()
                repeat = self.enemy_board.shot(target)
                return repeat
            except BoardException as e:
                print(e)


class AI(Player):
    def check(self,msh): # Сделал отдельно функцию проверки
        while True: #Ищет и уничтожает корабли
            if msh:
                if len(msh) >= 2:
                    if msh[0].x == msh[1].x:

                        ms = msh[randint(0, len(self.near) - 1)]
                        d = Dot(ms.x, ms.y + 1 - randint(0, 2))
                        if d in self.smart or self.self_board.out(d): #Кривой подход хотел добавить класс но не хватило времени додумать
                            continue
                        else:
                            break
                    else:

                        ms = msh[randint(0, len(self.near) - 1)]
                        d = Dot(ms.x + 1 - randint(0, 2), ms.y)
                        if d in self.smart or self.self_board.out(d):
                            continue
                        else:
                            break
                elif len(msh) == 1:

                    ms = msh[0]
                    d = Dot(ms.x + 1 - randint(0, 2), ms.y + 1 - randint(0, 2))
                    if d in self.smart or self.self_board.out(d):
                        continue
                    else:
                        break
            else:
                d = Dot(randint(0, self.self_board.size - 1), randint(0, self.self_board.size - 1)) #Не знаем куда стрелять
                break
        return d

    def ask(self):
        s = "" #Для оповещения о скором уничтожении корабля
        if self.enemy_board.get_memory == 0:  # Уничтожили?Стираем
            self.near = []
        d=self.check(self.near)
        for ship in self.enemy_board.ships:
            if d in ship.dots:
                if d not in self.near:
                    self.near.append(d)
                    self.smart.append(d)
        print(f"Ход компьютера: {d.x + 1},{d.y + 1}")
        for i in self.near:
            s += f"({i.x + 1},{i.y + 1}), "
        print("Я попал сюда: ", s)
        return d


class User(Player):
    def ask(self):
        while True:
            print("Ваш Ход ")
            print("Чтобы отобразить свою строку напишите show")  # Уже как то не до красоты извините (
            try:
                x = int(input("По x координате: "))
                if x == "show":  # Отображение своей доски, не очень интересно на неё все время смотреть
                    print("Ваша доска")
                    print(self.self_board)
                    continue
                else:
                    y = int(input("По y координате: "))
                    if y == "showmethemoney":
                        print("Доска вражины! Пора уничтожать!")
                        self.enemy_board.hid = not self.enemy_board.hid  # Небольшое шулерство, Тригер
                        continue
            except ValueError:
                print(self.enemy_board)
                print("!!!Нужно ввести целое!!!")
                continue
            return Dot(x - 1, y - 1)


class Game:
    def __init__(self):
        self.size = self.set_size()
        self.battle_front = self.set_battlefront()
        pl_b = self.random_board()
        ai_b = self.random_board()
        ai_b.hid = True
        self.ai = AI(ai_b, pl_b)
        self.pl = User(pl_b, ai_b)

    def set_size(self):#Настраиваем поле для интереса
        self.size = 6
        print("     Размер поля    ")
        print("   Одно целое число ")
        print("====================")
        size = input()
        try:
            size = int(size)
            if size < 3 or size > 50:
                print("!!!Не соблюдены условия!!!")
                print("!!!3 <", size, "< 50!!!")
            else:
                self.size = size
                print("Поле:  ", self.size, "x", self.size)
        except ValueError as e:
            print("!!Нужно ввести целое!!!")
            print("Поле:  ", self.size, "x", self.size)
        return self.size

    def set_battlefront(self): #Относительно быстрая расстановка кораблей учитывая если играть на большом поле
        self.battle_front = [3, 2, 2, 1, 1, 1, 1]
        tsize = int(self.size ** 2 / 3)
        temp_front = []
        while tsize > 0:
            try:
                print("====================")
                print("   Корабли должны   ")
                print("  Занимать не более ")
                print("  1/3 Площади поля  ")
                print("   Чтобы завершить  ")
                print("      Введите 0     ")
                print("У вас осталось", tsize, "Поле:", self.size, "x", self.size)
                print("Текущий флот", temp_front)
                print("====================")
                deck = int(input("Cколько палуб у корабля?"))
                if deck == 0:
                    if temp_front != []:
                        temp_front.sort(reverse=True)
                        self.battle_front = temp_front
                    break
                elif deck > self.size:
                    print("!!!Такой корабль не поместится на поле!!!")
                else:
                    amount = int(input("Сколько кораблей?"))
                    if tsize - deck * amount >=0:
                        tsize -= deck * amount
                        temp_front += ([deck] * amount)
                    else:
                        print("!!!Вы превысили ограничение поля на ",abs(tsize - deck * amount),"!!!")
            except ValueError as e:
                print("!!!Нужно ввести целое!!!")
                continue
        if temp_front != []:
            self.battle_front = temp_front
        return self.battle_front

    def try_board(self):
        board = Board(size=self.size, battle_front=self.battle_front)
        attempts = 0
        for l in self.battle_front:
            while True:
                attempts += 1
                if attempts > 500:
                    return None
                ship = Ship(Dot(randint(0, self.size), randint(0, self.size)), l, randint(0, 1)) #Может усуорит расстановку доски, есть варианты лучше?)
                try:
                    board.add_ship(ship)
                    break
                except BoardWrongShipException:
                    pass
        board.begin()
        print(f"Попыток сгенерировать поле {attempts}")
        return board

    def random_board(self):
        board = None
        while board is None:
            board = self.try_board()
        return board

    def greet(self):
        print("====================")
        print("   Приветсвуем вас  ")
        print(" в игре морской бой ")
        print("      на коленке    ")
        print("====================")
        print("  формат ввода: x y ")
        print("  x - номер строки  ")
        print("  y - номер столбца ")
        print("====================")

    def loop(self):
        self.pl.self_board.battle_front = self.pl.enemy_board.battle_front.copy()
        # Костыль без понятия как еще можно почему то ссылается на одну переменную, даже если сеты поставить в Board
        num = 0
        while True:
            print("Доска вражины")
            print(self.pl.enemy_board) #Исправил
            if num % 2 == 0:
                print("Ваш флот:  ", self.pl.self_board.battle_front)
                print("Флот Врага:", self.ai.self_board.battle_front)
                print("Ход Игрока")
                repeat = self.pl.move()
            else:
                print("Ход компьютера")
                repeat = self.ai.move()
            if repeat:
                num -= 1
            if not self.pl.enemy_board.battle_front:
                print("Игрок Победил")
                print(self.pl.enemy_board)
                print("Насколько было близко к поражениб")
                print(self.pl.self_board)
                break
            if not self.pl.self_board.battle_front:
                print("Комьютер Победил")
                print(self.ai.enemy_board)
                print("Ваши достижения")
                print(self.ai.self_board)
                break
            num += 1

    def start(self):
        self.greet()
        self.loop()


g = Game()
g.start()
