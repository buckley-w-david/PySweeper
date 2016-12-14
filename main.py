from tkinter import *
from PIL import Image

import sweeper
import configparser
import ImageTk as IMTK

class App(Tk):
    def __init__(self, *args, **kwargs):
        Tk.__init__(self, *args, **kwargs)
        self.title("PySweeper")
        self.resizable(0, 0)

        #Read the config and create game board with the set defaults
        self.config_file = config_file = configparser.ConfigParser()
        config_file.read('config.ini')
        self.mode = mode = IntVar()
        mode.set(int(config_file['config']['mode']))
        
        if (mode.get() == 0):
            self.tile_width = tile_width = 8
            self.tile_height = tile_height = 8
            self.mines = mines = 10
        elif (mode.get() == 1):
            self.tile_width = tile_width = 16
            self.tile_height = tile_height = 16
            self.mines = mines = 40
        elif (mode.get() == 2):
            self.tile_width = tile_width = 30
            self.tile_height = tile_height = 16
            self.mines = mines = 99
        else:
            self.tile_width = tile_width = int(config_file['custom']['width'])
            self.tile_height = tile_height = int(config_file['custom']['height'])
            self.mines = mines = int(config_file['custom']['mines'])

        self.board = sweeper.Board(tile_width, tile_height, mines)

        self.canvas = canvas = Canvas(self)
        self.canvas.bind('<ButtonPress-1>', self.left_press)
        self.canvas.bind('<ButtonPress-2>', self.middle_press)
        self.canvas.bind('<ButtonPress-3>', self.right_press)
        
        self.canvas.bind('<ButtonRelease-1>', self.left_release)
        self.canvas.bind('<ButtonRelease-2>', self.middle_release)
        self.canvas.bind('<ButtonRelease-3>', self.right_release)
        
        self.load_bitmap()
        self.add_menubar()
        self.create_gui()
        self.canvas.pack()
        self.running = True
        
    def add_menubar(self):
        #Create the menu bar
        self.menubar = Menu(self)        

        #Create the game menu
        self.game_menu = Menu(self.menubar, tearoff=0)
        self.game_menu.add_command(label="New", command=self.new, accelerator="F2")

        self.game_menu.add_separator()

        self.game_menu.add_radiobutton(label="Beginner", variable=self.mode, value=0, command=self.reload)
        self.game_menu.add_radiobutton(label="Intermediate", variable=self.mode, value=1, command=self.reload)
        self.game_menu.add_radiobutton(label="Expert", variable=self.mode, value=2, command=self.reload)
        self.game_menu.add_radiobutton(label="Custom...", variable=self.mode, value=3, command=self.set_custom)

        self.game_menu.add_separator()

        self.marks_check = IntVar()
        self.marks_check.set(0)
        self.marks = 0
        
        self.game_menu.add_radiobutton(label="Marks (?)", variable=self.marks_check, value=1, command=self.toggle_marks)
        self.game_menu.add_command(label="Best Times...", command=self.show_times)

        self.game_menu.add_separator()

        self.game_menu.add_command(label="Exit", command=self.exit_game)
        self.menubar.add_cascade(label="Game", menu=self.game_menu)

        #Add menu bar to window
        self.config(menu=self.menubar)

    def load_bitmap(self):
        self.PIL_image = im = Image.open("cloneskin.bmp")
        
#Rows of tiles
        self.revealed = [IMTK.PhotoImage(im.crop(((16*i), 0, (16*i)+16, 16))) for i in range(9)]
        self.tiles = [IMTK.PhotoImage(im.crop(((16*i), 16, (16*i)+16, 32))) for i in range(8)]
        self.numbers = [IMTK.PhotoImage(im.crop(((12*i), 33, (12*i)+11, 54))) for i in range(11)]
        self.faces = [IMTK.PhotoImage(im.crop(((27*i), 55, (27*i)+25, 81))) for i in range(5)]
        
        self.display_field = IMTK.PhotoImage(im.crop((28, 82, 69, 107)))
        self.blank_space = IMTK.PhotoImage(im.crop((0, 0, 14, 14)))
#Frame pieces
        self.top_left = IMTK.PhotoImage(im.crop((0, 82, 12, 93)))
        self.top_right = IMTK.PhotoImage(im.crop((15, 82, 27, 93)))

        self.middle_left = IMTK.PhotoImage(im.crop((0, 96, 12, 107)))
        self.middle_right = IMTK.PhotoImage(im.crop((15, 96, 27, 107)))

        self.bottom_left = IMTK.PhotoImage(im.crop((0, 110, 11, 122)))
        self.bottom_right = IMTK.PhotoImage(im.crop((15, 110, 27, 122)))

        self.top_slice = IMTK.PhotoImage(im.crop((13, 82, 14, 93)))
        
        self.upper_left_slice = IMTK.PhotoImage(im.crop((0, 94, 12, 95)))
        self.upper_right_slice = IMTK.PhotoImage(im.crop((15, 94, 27, 95)))
        
        self.middle_slice = IMTK.PhotoImage(im.crop((13, 96, 14, 107)))
        
        self.lower_left_slice = IMTK.PhotoImage(im.crop((0, 108, 12, 109)))
        self.lower_right_slice = IMTK.PhotoImage(im.crop((15, 108, 27, 109)))
        
        self.bottom_slice = IMTK.PhotoImage(im.crop((13, 110, 14, 122)))

    def create_gui(self):
        #Based on tile values, calculate and set window size
        self.width = 23 + 16*self.tile_width
        self.height = 66 + 16*self.tile_height
        
        self.geometry("{}x{}".format(self.width, self.height))
        self.canvas.configure(width=self.width, height=self.height)

        self.create_frame(self.canvas)
        self.create_field(self.canvas)

    def create_frame(self, canvas):
        canvas.create_image((0, 0), image=self.top_left, tag=('frame'), anchor=NW)
        canvas.create_image((self.width, 0), image=self.top_right, tag=('frame'), anchor=NE)
        canvas.create_image((0, self.height), image=self.bottom_left, tag=('frame'), anchor=SW)
        canvas.create_image((self.width, self.height), image=self.bottom_right, tag=('frame'), anchor=SE)

        canvas.create_image((0, self.top_left.height()+33), image=self.middle_left, tag=('frame'), anchor=NW)
        canvas.create_image((self.width, 33+self.top_left.height()), image=self.middle_right, tag=('frame'), anchor=NE)

        for i in range(self.width-self.bottom_right.width()-self.bottom_left.width()):
            canvas.create_image((i + self.bottom_left.width(), self.height), image=self.bottom_slice, tag=('frame'), anchor=SW)
            canvas.create_image((i + self.top_left.width(), 0), image=self.top_slice, tag=('frame'), anchor=NW)
            canvas.create_image((i + self.middle_left.width(), self.top_left.height()+33), image=self.middle_slice, tag=('frame'), anchor=NW)
            
        for i in range(33):
            canvas.create_image((0, i+self.top_left.height()), image=self.upper_left_slice, tag=('frame'), anchor=NW)
            canvas.create_image((self.width, i+self.top_left.height()), image=self.upper_right_slice, tag=('frame'), anchor=NE)
        for i in range(self.height-self.top_left.height()-33-self.middle_left.height()-self.bottom_left.height()):
            canvas.create_image((0, i+self.top_left.height()+33+self.middle_left.height()), image=self.lower_left_slice, anchor=NW)
            canvas.create_image((self.width, i+self.top_left.height()+33+self.middle_left.height()), image=self.lower_right_slice, anchor=NE)
    
    def create_field(self, canvas):
        self.draw_tiles(canvas)

        for i in [0, 14, 19]:
            for j in range(self.upper_left_slice.width(), self.width-self.upper_right_slice.width()-13):
                canvas.create_image((j, self.top_slice.height()+i), image=self.blank_space, tag=('frame'), anchor=NW)
        
        canvas.create_image((self.upper_left_slice.width()+5, self.top_slice.height()+4), image=self.display_field, tag=('frame'), anchor=NW)
        canvas.create_image((self.width-self.upper_right_slice.width()-5, self.top_slice.height()+4), image=self.display_field, tag=('frame'), anchor=NE)
        canvas.create_image((self.width//2, 28), image=self.faces[0], tag=('face'))

    def draw_tiles(self, canvas):
        self.starting_x = self.lower_left_slice.width()
        self.starting_y = self.top_slice.height()+33+self.middle_slice.height()
        self.field = {}
        
        for row in range(0, self.tile_height):
            for col in range(0, self.tile_width):
                x = self.starting_x+self.tiles[0].width()*col
                y = self.starting_y+self.tiles[0].height()*row
                cell = self.board.board[row][col]
                
                if cell.flagged:
                    cur_image = self.tiles[3]
                elif cell.revealed:
                    if cell.type:
                        cur_image = self.tiles[2]
                    else:
                        cur_image = self.revealed[self.board.bombs_around(col, row)]
                else:
                    cur_image = self.tiles[0]
                
                self.field[row, col] = canvas.create_image((x, y), image=cur_image, tag=('tile', 'row={}'.format(row), 'col={}'.format(col)), anchor=NW)


    def to_tile_space(self, coordinates):
        assert len(coordinates)==2, "coordinates must be passed in a tuple of form (x, y)"
        x, y = coordinates

        return ((x-self.lower_left_slice.width())//self.tiles[0].width(), (y-(self.top_slice.height()+33+self.middle_slice.height()))//self.tiles[0].height())

    def left_press(self, event):
        if (self.starting_x > event.x or event.x > self.width-self.lower_right_slice.width() or self.starting_y > event.y or event.y > self.height-self.bottom_slice.height() or not self.running):
            return
    def middle_press(self, event):
        if (self.starting_x > event.x or event.x > self.width-self.lower_right_slice.width() or self.starting_y > event.y or event.y > self.height-self.bottom_slice.height() or not self.running):
            return
    def right_press(self, event):
        if (self.starting_x > event.x or event.x > self.width-self.lower_right_slice.width() or self.starting_y > event.y or event.y > self.height-self.bottom_slice.height() or not self.running):
            return

    def left_release(self, event):
        if (self.starting_x > event.x or event.x > self.width-self.lower_right_slice.width() or self.starting_y > event.y or event.y > self.height-self.bottom_slice.height() or not self.running):
            return
        
        x, y = self.to_tile_space((event.x, event.y))
        result = self.board.click(x, y)
        self.canvas.delete("tile")
        self.draw_tiles(self.canvas)
        if result:
            abs_x = self.starting_x+self.tiles[0].width()*x
            abs_y = self.starting_y+self.tiles[0].height()*y
            self.field[y, x] = self.canvas.create_image((abs_x, abs_y), image=self.tiles[5], tag=('tile', 'row={}'.format(y), 'col={}'.format(x)), anchor=NW)
            self.running = False

        return result
        
    def middle_release(self, event):
        if (self.starting_x > event.x or event.x > self.width-self.lower_right_slice.width() or self.starting_y > event.y or event.y > self.height-self.bottom_slice.height() or not self.running):
            return
        
        x, y = self.to_tile_space((event.x, event.y))
        result = self.board.auto_click(x, y)
        self.canvas.delete("tile")
        self.draw_tiles(self.canvas)

        if result:
            self.running = False

        return result
        
        
    def right_release(self, event):
        if (self.starting_x > event.x or event.x > self.width-self.lower_right_slice.width() or self.starting_y > event.y or event.y > self.height-self.bottom_slice.height() or not self.running):
            return
        
        x, y = self.to_tile_space((event.x, event.y))
        abs_x = self.starting_x+self.tiles[0].width()*x
        abs_y = self.starting_y+self.tiles[0].height()*y

        result = self.board.flag(x, y)
        
        if result == -1:
            self.canvas.delete(self.field[y, x])
            cur_image = self.tiles[0]

            self.field[y, x] = self.canvas.create_image((abs_x, abs_y), image=cur_image, tag=('tile', 'row={}'.format(y), 'col={}'.format(x)), anchor=NW)

        elif result == 1:
            self.canvas.delete(self.field[y, x])
            cur_image = self.tiles[3]
            
            self.field[y, x] = self.canvas.create_image((abs_x, abs_y), image=cur_image, tag=('tile', 'row={}'.format(y), 'col={}'.format(x)), anchor=NW)
        

    def reload(self):
        self.config_file['config']['mode'] = str(self.mode.get())
        with open('config.ini', 'w') as f:
            self.config_file.write(f)
        
        if (self.mode.get() == 0):
            self.tile_width = tile_width = 8
            self.tile_height = tile_height = 8
            self.mines = mines = 10
        elif (self.mode.get() == 1):
            self.tile_width = tile_width = 16
            self.tile_height = tile_height = 16
            self.mines = mines = 40
        elif (self.mode.get() == 2):
            self.tile_width = tile_width = 30
            self.tile_height = tile_height = 16
            self.mines = mines = 99
        else:
            self.tile_width = tile_width = int(config_file['custom']['width'])
            self.tile_height = tile_height = int(config_file['custom']['height'])
            self.mines = mines = int(config_file['custom']['mines'])

        self.new()


#-----------Game Menu Methods-----------

    def new(self):
        self.board = sweeper.Board(self.tile_width, self.tile_height, self.mines)
        self.canvas.delete("all")
        self.create_gui()
        self.running = True
        
    def set_custom(self):
        pass
    
    def toggle_marks(self):
        if (self.marks == 1):
            self.marks = 0
            self.marks_check.set(0)
        else:
            self.marks = 1
            self.marks_check.set(1)
    def show_times(self):
        pass
    
    def exit_game(self):
        self.destroy()

#-----------\Game Menu Methods-----------'''

if __name__ == '__main__':
    app = App()
    app.mainloop()
