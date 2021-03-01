import numpy as np
import pyxel

BOARD_SIZE = (20, 10)
TETRIMINOS = [
    # I
    [[[1, i] for i in range(4)],
        [[i, 1] for i in range(4)]] * 2,
    # O
    [[[0, 0], [0, 1], [1, 0], [1, 1]]] * 4,
    # T
    [[[0, 1]] + [[1, i] for i in range(3)],
        [[1, 2]] + [[i, 1] for i in range(3)],
        [[2, 1]] + [[1, i] for i in range(3)],
        [[1, 0]] + [[i, 1] for i in range(3)]],
    # J
    [[[0, 0]] + [[1, i] for i in range(3)],
        [[0, 2]] + [[i, 1] for i in range(3)],
        [[2, 2]] + [[1, i] for i in range(3)],
        [[2, 0]] + [[i, 1] for i in range(3)]],
    # L
    [[[0, 2]] + [[1, i] for i in range(3)],
        [[2, 2]] + [[i, 1] for i in range(3)],
        [[2, 0]] + [[1, i] for i in range(3)],
        [[0, 0]] + [[i, 1] for i in range(3)]],
    # S
    [[[0, 1], [0, 2], [1, 0], [1, 1]],
        [[0, 0], [1, 0], [1, 1], [2, 1]]] * 2,
    # Z
    [[[0, 0], [0, 1], [1, 1], [1, 2]],
        [[0, 1], [1, 0], [1, 1], [2, 0]]] * 2
]

REST_RANGE = 20


class Tetris:
    def __init__(self):
        pyxel.init(180, 160, fps=30, caption="Tetris")
        pyxel.load("assets/tetris.pyxres")
        self.setup()
        pyxel.run(self.update, self.draw)

    def setup(self):
        self.init_board()
        self.add_tetrimino()

        self.rest = False
        self.rest_frame_count = 0

    def init_board(self):
        self.board = np.zeros(BOARD_SIZE, dtype=np.int)

    def update(self):
        tetrimino_previous_position = self.tetrimino_position.copy()

        self.move_tetrimino(False)
        if pyxel.frame_count % 30 == 0:
            self.move_tetrimino(True)  # drop

        if self.rest:
            self.rest_frame_count += 1

            for tetrimino in TETRIMINOS[self.tetrimino_type][self.tetrimino_rotation]:
                if tetrimino[0] + self.tetrimino_position[0] + 1 >= BOARD_SIZE[0] or self.board[tetrimino[0]+self.tetrimino_position[0] + 1, tetrimino[1]+self.tetrimino_position[1]] != 0:
                    break
            else:
                self.rest = False
                self.rest_frame_count = 0

        if pyxel.btnp(pyxel.KEY_UP):
            for i in range(20):
                self.move_tetrimino(True)
            self.rest_frame_count = REST_RANGE

        if tetrimino_previous_position == self.tetrimino_position and self.rest_frame_count > REST_RANGE:
            self.save_board()
            self.rest = False
            self.rest_frame_count = 0
            self.add_tetrimino()

        if pyxel.btnp(pyxel.KEY_Q):  # or not self.check_gameover():
            pyxel.quit()

        if pyxel.btnp(pyxel.KEY_R):
            self.setup()

    def draw(self):
        pyxel.cls(6)
        pyxel.bltm(x=0, y=0, tm=0, u=0, v=0, w=16, h=21, colkey=2)

        for i in range(BOARD_SIZE[0]):
            for j in range(BOARD_SIZE[1]):
                if self.get_element(i, j) == None:
                    pass
                else:
                    #pyxel.rect(16 + 8 * j, 8 * i, 8, 8, 8 + int(self.get_element(i, j)))
                    pyxel.blt(x=16 + 8 * j, y=8 * i, img=0, u=0, v=8 *
                              (self.get_element(i, j) - 1), w=8, h=8, colkey=2)

        pyxel.text(120, 40, f"{pyxel.frame_count} {self.rest_frame_count}", 0)

        if self.check_gameover():
            pyxel.text(120, 32, "GAME OVER", 0)

    def check_gameover(self):
        mid = BOARD_SIZE[1] // 2
        if (self.board[0, mid-2:mid+2] == 0).all():
            return False
        return True

    def save_board(self):
        for tetrimino in TETRIMINOS[self.tetrimino_type][self.tetrimino_rotation]:
            self.board[tetrimino[0]+self.tetrimino_position[0], tetrimino[1] +
                       self.tetrimino_position[1]] = self.tetrimino_type + 1

        # 列を消す
        for i in range(BOARD_SIZE[0]):
            if (self.board[i] != 0).all():
                # 消した列より上を下に移動
                for j in reversed(range(i)):
                    self.board[j + 1] = self.board[j]

    def get_element(self, i, j):
        for tetrimino in TETRIMINOS[self.tetrimino_type][self.tetrimino_rotation]:
            if tetrimino[0]+self.tetrimino_position[0] == i and tetrimino[1]+self.tetrimino_position[1] == j:
                return self.tetrimino_type + 1

        return None if self.board[i, j] == 0 else self.board[i, j]

    def move_tetrimino(self, drop=True):
        self.tetrimino_next_rotation = self.tetrimino_rotation
        self.tetrimino_next_position = self.tetrimino_position.copy()

        # soft drop
        if drop or pyxel.btn(pyxel.KEY_DOWN):
            self.tetrimino_next_position = [
                self.tetrimino_position[0] + 1, self.tetrimino_position[1]]
            self.tetrimino_next_rotation = self.tetrimino_rotation
        else:
            if pyxel.btnp(pyxel.KEY_LEFT) or pyxel.btnp(pyxel.KEY_LEFT, hold=10, period=1):
                self.tetrimino_next_position = [
                    self.tetrimino_position[0], self.tetrimino_position[1]-1]
            elif pyxel.btnp(pyxel.KEY_RIGHT) or pyxel.btnp(pyxel.KEY_RIGHT, hold=10, period=1):
                self.tetrimino_next_position = [
                    self.tetrimino_position[0], self.tetrimino_position[1]+1]
            # rotate right
            if pyxel.btnp(pyxel.KEY_SPACE):
                self.tetrimino_next_position = [
                    self.tetrimino_position[0], self.tetrimino_position[1]]
                self.tetrimino_next_rotation = (
                    self.tetrimino_rotation + 1) % 4
            # rotate left
            elif pyxel.btnp(pyxel.KEY_SHIFT):
                self.tetrimino_next_position = [
                    self.tetrimino_position[0], self.tetrimino_position[1]]
                self.tetrimino_next_rotation = (
                    self.tetrimino_rotation - 1) % 4

        for tetrimino in TETRIMINOS[self.tetrimino_type][self.tetrimino_next_rotation]:
            if (tetrimino[0] + self.tetrimino_next_position[0] >= BOARD_SIZE[0] or tetrimino[1]+self.tetrimino_next_position[1] < 0 or tetrimino[1]+self.tetrimino_next_position[1] >= BOARD_SIZE[1] or self.board[tetrimino[0]+self.tetrimino_next_position[0], tetrimino[1]+self.tetrimino_next_position[1]] != 0):
                if not(tetrimino[1]+self.tetrimino_next_position[1] < 0 or tetrimino[1]+self.tetrimino_next_position[1] >= BOARD_SIZE[1]):
                    self.rest = True
                return

        self.tetrimino_position = self.tetrimino_next_position.copy()
        self.tetrimino_rotation = self.tetrimino_next_rotation

    def add_tetrimino(self):
        self.tetrimino_type = np.random.randint(7)  # 0-6
        self.tetrimino_position = [0, BOARD_SIZE[1] // 2 - 1]
        self.tetrimino_rotation = 0


Tetris()
