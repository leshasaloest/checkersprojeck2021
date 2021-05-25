from tkinter import *
import img
from tkinter import messagebox


def get_row_col_from_mouse(event):
    global row, col
    x, y = event.x, event.y
    row = y // SQUARE_SIZE
    col = x // SQUARE_SIZE


def on_closing():
    if messagebox.askokcancel("Quit", "Do you want to quit?"):
        root.destroy()


class Board:
    def __init__(self):
        self.board = []
        self.black_left = self.white_left = 12
        self.black_kings = self.white_kings = 0
        self.create_board()

    def create_board(self):
        for row in range(ROWS):
            self.board.append([])
            for col in range(COLS):
                if col % 2 == ((row + 1) % 2):
                    if row < 3:
                        self.board[row].append(Piece(row, col, 'black'))
                    elif row > 4:
                        self.board[row].append(Piece(row, col, 'white'))
                    else:
                        self.board[row].append(0)
                else:
                    self.board[row].append(0)

    def draw_field(self, canvas):
        for row in range(ROWS):
            for col in range(row % 2, COLS, 2):
                canvas.create_rectangle(row*SQUARE_SIZE, col*SQUARE_SIZE, (row+1)*SQUARE_SIZE, (col+1)*SQUARE_SIZE, fill='white')

    def draw(self, can):
        self.draw_field(can)
        for row in range(ROWS):
            for col in range(COLS):
                piece = self.board[row][col]
                if piece != 0:
                    piece.draw(can)

    def move(self, piece, row, col):
            self.board[piece.row][piece.col], self.board[row][col] = self.board[row][col], self.board[piece.row][piece.col]
            piece.move(row, col)

            if row == ROWS - 1 or row == 0:
                piece.make_king()
                if piece.color == 'black':
                    self.black_kings += 1
                else:
                    self.white_kings += 1

    def get_piece(self, row, col):
        return self.board[row][col]

    def winner(self):
        if self.white_left <= 0:
            return 'white'
        elif self.black_left <= 0:
            return 'black'

        return None

    def get_valid_moves(self, piece):
        moves = {}
        left = piece.col - 1
        right = piece.col + 1
        row = piece.row
        if piece.color == 'white' and not piece.king:
            moves.update(self._traverse_left(row - 1, max(row - 3, -1), -1, piece.color, left))
            moves.update(self._traverse_right(row - 1, max(row - 3, -1), -1, piece.color, right))
        if piece.color == 'black' and not piece.king:
            moves.update(self._traverse_left(row + 1, min(row + 3, ROWS), 1, piece.color, left))
            moves.update(self._traverse_right(row + 1, min(row + 3, ROWS), 1, piece.color, right))
        return moves

    def _traverse_left(self, start, stop, step, color, left, skipped=[]):
        moves = {}
        last = []
        for r in range(start, stop, step):
            if left < 0:
                break

            current = self.board[r][left]
            if current == 0:
                if skipped and not last:
                    break
                elif skipped:
                    moves[(r, left)] = last + skipped
                else:
                    moves[(r, left)] = last

                if last:
                    if step == -1:
                        row = max(r - 3, 0)
                    else:
                        row = min(r + 3, ROWS)
                    moves.update(self._traverse_left(r + step, row, step, color, left - 1, skipped=last))
                    moves.update(self._traverse_right(r + step, row, step, color, left + 1, skipped=last))
                break
            elif current.color == color:
                break
            else:
                last = [current]

            left -= 1
        return moves

    def _traverse_right(self, start, stop, step, color, right, skipped=[]):
        moves = {}
        last = []
        for r in range(start, stop, step):
            if right >= COLS:
                break

            current = self.board[r][right]
            if current == 0:
                if skipped and not last:
                    break
                elif skipped:
                    moves[(r, right)] = last + skipped
                else:
                    moves[(r, right)] = last

                if last:
                    if step == -1:
                        row = max(r - 3, 0)
                    else:
                        row = min(r + 3, ROWS)
                    moves.update(self._traverse_left(r + step, row, step, color, right - 1, skipped=last))
                    moves.update(self._traverse_right(r + step, row, step, color, right + 1, skipped=last))
                break
            elif current.color == color:
                break
            else:
                last = [current]

            right += 1

        return moves

    def remove(self, pieces):
        for piece in pieces:
            self.board[piece.row][piece.col] = 0
            if piece != 0:
                if piece.color == 'white':
                    self.white_left -= 1
                else:
                    self.black_left -= 1


class Piece:
    def __init__(self, row, col, color):
        self.row = row
        self.col = col
        self.color = color
        self.king = False
        self.x = 0
        self.y = 0
        self.calc_pos()

    def calc_pos(self):
        self.x = SQUARE_SIZE * self.col + SQUARE_SIZE // 2
        self.y = SQUARE_SIZE * self.row + SQUARE_SIZE // 2

    def make_king(self):
        self.king = True

    def draw(self, can):
        if self.color == 'black':
            image = 'im3'
            if self.king:
                image = 'im4'
        if self.color == 'white':
            image = 'im1'
            if self.king:
                image = 'im2'
        can.create_image(self.x, self.y, image=img.get(image))

    def move(self, row, col):
        self.row = row
        self.col = col
        self.calc_pos()

    def __repr__(self):
        return self.color


class Game:
    def __init__(self, can, root):
        self._init()
        self.can = can
        self.root = root
        self.exist = True

    def update(self):
        if self.exist:
            self.can.delete('all')
            self.board.draw(self.can)
            self.draw_valid_moves(self.valid_moves)
            self.can.update()

    def _init(self):
        self.selected = None
        self.board = Board()
        self.turn = 'white'
        self.valid_moves = {}

    def winner(self):
        return self.board.winner()

    def reset(self):
        self._init()

    def select(self, row, col):
        if self.selected:
            result = self._move(row, col)
            if not result:
                self.selected = None
                self.select(row, col)

        piece = self.board.get_piece(row, col)
        if piece != 0 and piece.color == self.turn:
            self.selected = piece
            self.valid_moves = self.board.get_valid_moves(piece)
            return True

        return False

    def _move(self, row, col):
        piece = self.board.get_piece(row, col)
        if self.selected and piece == 0 and (row, col) in self.valid_moves:
            self.board.move(self.selected, row, col)
            skipped = self.valid_moves[(row, col)]
            if skipped:
                self.board.remove(skipped)
            self.change_turn()
        else:
            return False

        return True

    def draw_valid_moves(self, moves):
        for move in moves:
            row, col = move
            self.can.create_rectangle(col*SQUARE_SIZE, row*SQUARE_SIZE,(col+1)*SQUARE_SIZE, (row+1)*SQUARE_SIZE, outline='green',width=5)

    def change_turn(self):
        self.valid_moves = {}
        if self.turn == 'white':
            self.turn = 'black'
        else:
            self.turn = 'white'

    def exitgame(self, event = None):
        answer = messagebox.askokcancel("Quit", "Do you want to quit?")
        if answer:
            self.exist = False
            self.root.destroy()


if __name__ == '__main__':
    WIDTH, HEIGHT = 800, 800
    ROWS, COLS = 8, 8
    SQUARE_SIZE = WIDTH // COLS
    root = Tk()
    canvas = Canvas(root, width=WIDTH, height=HEIGHT, bg='black')
    canvas.pack()
    canvas.bind('<Button-1>', get_row_col_from_mouse)
    row = col = 0
    g = Game(canvas, root)
    root.bind('<Escape>', g.exitgame)
    root.protocol("WM_DELETE_WINDOW", g.exitgame)
    while g.exist:
        if g.winner() != None:
            print(g.winner())
            g.exist = False
        g.select(row, col)
        g.update()