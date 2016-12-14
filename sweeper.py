from random import randrange
from math import log10

class Tile:
    def __init__(self):
        self.revealed = False
        self.flagged = False
        self.type = 0
        
    def __repr__(self):
        return "Tile()"

    def __eq__(self, other):
        if type(other) != type(self):
            return NotImplemented
        else:
            return True

    #Reveal a tile if it is not flagged, and return 0 since this isn't a bomb, thus it didn't explode
    def reveal(self):
        if not self.flagged:
            self.revealed = True
            
        return 0

    #Toggle flagged state if tile is not revealed
    def flag(self):
        if not self.revealed:
            if self.flagged:
                self.flagged = False
                return -1
            else:
                self.flagged = True
                return 1
        else:
            return 0

class Bomb(Tile):
    def __init__(self):
        super(Bomb, self).__init__()
        self.type = 1
        
    def __repr__(self):
        return "Bomb()"

    #Reveal tile and return 1 to designate game over if it is not flagged, else do nothing
    def reveal(self):
        if not self.flagged:
            self.revealed = True
            return 1

        return 0
            
    
class Board:
    def __init__(self, width=30, height=16, bombs=99):
        self.width = width
        self.height = height

        self.bomb_count = bombs
        self.bombs_remaining = bombs
        self.flagged = 0

        self.board = self.gen_board(width, height, bombs)

    def __repr__(self):
        return 'Board(width={}, height={}, bombs={})'.format(self.width, self.height, self.bomb_count)

    #Spit out a string representation of the board
    def __str__(self):
        height = self.height
        width = self.width
        board = [[None]*(width+3) for _ in range(height+3)]
        
        for y in range(height):
            for x in range(width):
                if (self.board[y][x].type == 1):
                    board[y+2][x+2] = '$'
                else:
                    board[y+2][x+2] = str(self.bombs_around(x, y))

        board[0] = '*'.rjust(int(log10(width))+2, ' ')
        board[1] = board[height+2] = ['*']*(width+4)
        for y in range(2, height+2):
            board[y][0] = str(y-2).rjust(int(log10(width))+1, '0')
            for x in [1, width+2]:
                board[y][x] = '*'

        return '\n'.join([''.join(board[i]) for i in range(height+3)])

    @property
    def display(self):
        height = self.height
        width = self.width
        board = [[None]*(width+3) for _ in range(height+3)]
        
        for y in range(height):
            for x in range(width):
                if self.board[y][x].revealed:
                    if (self.board[y][x].type == 1):
                        board[y+2][x+2] = '$'
                    else:
                        board[y+2][x+2] = str(self.bombs_around(x, y))
                else:
                    board[y+2][x+2] = '#'

        board[0] = '*'.rjust(int(log10(width))+2, ' ')
        board[1] = board[height+2] = ['*']*(width+4)
        for y in range(2, height+2):
            board[y][0] = str(y-2).rjust(int(log10(width))+1, '0')
            for x in [1, width+2]:
                board[y][x] = '*'

        return '\n'.join([''.join(board[i]) for i in range(height+3)])


    #return the number of bombs around a specified coordinate
    def bombs_around(self, x, y):
        count = 0
        for i in range(-1, 2):
            for j in range(-1, 2):
               if any((i, j)) and (0 <= y+i and y+i < self.height) and (0 <= x+j and x+j < self.width) and (self.board[y+i][x+j].type == 1):
                   count += 1
                   
        return count

    #return the number of flagged tile around a specified coordinate
    def flags_around(self, x, y):
        count = 0
        for i in range(-1, 2):
            for j in range(-1, 2):
               if any((i, j)) and (0 <= y+i and y+i < self.height) and (0 <= x+j and x+j < self.width) and (self.board[y+i][x+j].flagged):
                   count += 1
                   
        return count

    #Left click a tile
    def click(self, x, y):
        if (self.board[y][x].reveal()):
            for row in self.board:
                for cell in row:
                    if cell.type == 1:
                        cell.reveal()
            return 1
        
        elif self.board[y][x].revealed:
            around = self.bombs_around(x, y)
            if around == 0:
                self.cascade(x, y)
                
            return 0

    #Right click a tile
    def flag(self, x, y):
        result = self.board[y][x].flag()
        
        self.flagged += result
        self.bombs_remaining -= result

        return result

    #middle click
    def auto_click(self, x, y):
        results = []
        if self.board[y][x].revealed and self.flags_around(x, y) == self.bombs_around(x, y):
            for i in range(-1, 2):
                for j in range(-1, 2):
                    if any((i, j)) and (0 <= y+i and y+i < self.height) and (0 <= x+j and x+j < self.width):
                        results.append(self.click(x+j, y+i))

        return any(results)

    def cascade(self, x, y):
        for i in range(-1, 2):
            for j in range(-1, 2):
                if any((i, j)) and (0 <= y+i and y+i < self.height) and (0 <= x+j and x+j < self.width) and not self.board[y+i][x+j].revealed and self.board[y+i][x+j].type == 0: #Tile
                    self.click(x+j, y+i)

                
    @staticmethod
    def gen_board(width, height, bombs):
        assert width*height >= bombs, "There cannot be more bombs than tiles"

        count = 0
        coordinates = [(i, j) for i in range(width) for j in range(height)]
        board = [[None]*width for _ in range(height)]

        for _ in range(bombs):
            index = randrange(0, len(coordinates))
            x, y = coordinates.pop(index)

            board[y][x] = Bomb()

        for x, y in coordinates:
            board[y][x] = Tile()
        
        return board



            

