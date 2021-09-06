from random import randint

class BoardException (Exception):  # исключения
    pass
class BoardOutException(BoardException):
    def __str__(self):
        return 'Вы стреляете мимо доски!!! Улучшите свою точность!'
class BoardUsedException(BoardException):
    def __str__(self):
        return ('Два раза в цель снаряд не падает! Давайте новую точку!!!')
class BoardWrongShipException(BoardException):
    pass

class Dot:
    def __init__(self, x, y):
        self.x = x
        self.y = y
    def __eq__(self, other):
        return self.x == other.x and self.y == other.y
    def __repr__(self):
        return f'Dot({self.x},{self.y})'

class Ship:
    def __init__(self, bow, l, o):
        self.bow = bow #Расположение носа
        self.l = l #Длина коробля
        self.o = o #вертикаль или горизонталь
        self.lives = l #кол-во жизней

    @property
    def dots(self):
        ship_dots = []
        for i in range(self.l):  # цикл по длине корабля
            cur_x = self.bow.x  # координата у корабля
            cur_y = self.bow.y  # координата х корабля

            if self.o == 0: #если по горизонтали
                cur_x += i

            elif self.o == 1:  # если по вертикали
                cur_y += i

            ship_dots.append(Dot(cur_x, cur_y))
        return ship_dots  #точки корабля

    def shooten(self, shot):
        return shot in self.dots

class Board:
    def __init__(self, hid=False, size=6):
        self.hid = hid  #отображение (или нет) корабля
        self.size = size  # размер поля

        self.count = 0

        self.field = [['0'] * size for _ in range(size)]  # заполнение поля нулями

        self.ships = []  #клетки на которых корабли
        self.busy = []  #клетки на которые заняты либо выстрелом, либо кораблем

    def __str__(self):  # заполнение поля нумерацией
        res = ''
        res +='  | 1 | 2 | 3 | 4 | 5 | 6 | '
        for i, row in enumerate(self.field):
            res += f'\n{i+1} | ' + ' | '.join(row) + ' | '
        if self.hid:
            res = res.replace(" ■ ", " O ")
        return res

    def out(self, d):  # Проверка выхода за границы поля
        return not ((0 <= d.x < self.size) and (0 <= d.y < self.size))

    def contour(self, ship, verb=False):  # параметр verb нужен для того, чтобы ставить контур корабля в игре, а в самом начале делать этого не надо
        near = [
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1), (0, 0), (0, 1),
            (1, -1), (1, 0), (1, 1)
        ]
        for d in ship.dots:
            for dx, dy in near:
                cur = Dot(d.x + dx, d.y + dy)
                if not (self.out(cur)) and cur not in self.busy:
                    if verb:
                        self.field[cur.x][cur.y] = '.'
                    self.busy.append(cur)

    def add_ships(self, ship):  # ставим корабль на доску
        for d in ship.dots:
            if self.out(d) or d in self.busy:
                raise BoardWrongShipException()
        for d in ship.dots:
            self.field[d.x][d.y] = "■"
            self.busy.append(d)
            self.ships.append(ship)
            self.contour(ship)
    def shot(self,d): # производим выстрел
        if self.out(d):
            raise BoardOutException()
        if d in self.busy:
            raise BoardUsedException()
        self.busy.append(d)
        for ship in self.ships:
            if ship.shooten(d):
                ship.lives -= 1
                self.field[d.x][d.y] = 'X'
                if ship.lives == 0:
                    self.count += 1
                    self.contour(ship, verb=True)
                    print('Вы потопили корабль! Поздравляю!')
                    return False
                else:
                    print('Вы попали по кораблю! Осталось чуть-чуть и он будет потоплен!!!')
                    return True
        print('Вы промахнулись! Цельтесь лучше!')
        self.field[d.x][d.y] = '.'
        return False
    def begin(self):
        self.busy = []
    def defeat(self):
        return self.count == len(self.ships)
class Player:
    def __init__(self, board, enemy):
        self.board = board
        self.enemy = enemy

    def ask(self):
        raise NotImplementedError
    def move(self):
        while True:
            try:
                target = self.ask()
                repeat = self.enemy.shot(target)
                return repeat
            except BoardException as e:
                print(e)
class AI(Player):
    def ask(self):
        d = Dot(randint(0, 5), randint(0, 5))
        print(f'Компьтер выстрелил в: {d.x + 1} {d.y + 1}')
        return d
class User(Player):
    def ask(self):
        while True:
            cords = input('Ваш ход: ').split()

            if len(cords) != 2:
                print('Введите 2 координаты!')
                continue

            x, y = cords

            if not (x.isdigit()) or not (y.isdigit()):
                print('Введите числа!')
                continue

            x, y = int(x), int(y)

            return Dot(x-1, y-1)
class Game():
    def __init__(self, size=6):
        self.size = size
        pl = self.random_board()
        co = self.random_board()
        co.hid = True

        self.ai = AI(co, pl)
        self.user = User(pl, co)

    def try_board(self):
        lens = [3, 2, 2, 1, 1, 1, 1]
        board = Board(size=self.size)
        attempts = 0
        for l in lens:
            while True:
                attempts += 1
                if attempts > 1500:
                    return None
                ship = Ship(Dot(randint(0, self.size), randint(0, self.size)), l, randint(0, 1))
                try:
                    board.add_ships(ship)
                    break
                except BoardWrongShipException:
                    pass
        board.begin()
        return board
    def random_board(self):
        board = None
        while board is None:
            board = self.try_board()
        return board

    def greet(self):
        print('***************************')
        print('Приветствуем в Морском бою!')
        print('    Формат ввода: x y')
        print('     x - номер строки')
        print('    y - номер столбца')
        print('  Удачи на полях сражений!!!')

    def loop(self):
        num = 0
        while True:
            print("-" * 20)
            print("Доска пользователя:")
            print(self.user.board)
            print("-" * 20)
            print("Доска компьютера:")
            print(self.ai.board)
            print("-" * 20)
            if num % 2 == 0:
                print("Ходит пользователь!")
                repeat = self.user.move()
            else:
                print("Ходит компьютер!")
                repeat = self.ai.move()
            if repeat:
                num -= 1

            if self.ai.board.defeat():
                print("-" * 20)
                print("Пользователь выиграл!")
                break

            if self.user.board.defeat():
                print("-" * 20)
                print("Компьютер выиграл!")
                break
            num += 1
    def start(self):
        self.greet()
        self.loop()
g = Game()
g.start()









