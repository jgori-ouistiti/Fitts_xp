import tkinter as tk
from tkinter import colorchooser
from PIL import ImageTk, Image
import math

root = tk.Tk()
x_shift = 100
y_shift = 100
toolbar_width = 25

screen_width = root.winfo_screenwidth() - 2*x_shift
screen_height = root.winfo_screenheight() - 2*y_shift - toolbar_width

class MFrame(tk.Frame):
    def __init__(self, root, title="Experiment editor"):
        super().__init__(root)
        
        self.master.title(title)
        self.pack(fill = tk.BOTH, expand = 1)
        
        #List of different shapes followed by the index of the selected shape
        self.shapes = [['circle', 'rectangle'],0]
        self.shapes_ind = {self.shapes[0][k]:k for k in range(len(self.shapes[0]))}
        self.current_drawing = None
        self.outline = "#000"
        self.fill = "#fff"
        self.width = 2
        self.sensibility = 0.5 #used to making precise shapes while holding left mouse button and moving the mouse
        
        #List of all the shapes drawed on screen.
        self.drawings = []
        
        #Tools canvas part
        self.tools  = tk.Canvas(self, height = toolbar_width)
        sq_button_image = Image.open('images/square_button.png')
        sq_button_image = sq_button_image.resize((25,25), Image.Resampling.LANCZOS)
        rectangle_button = tk.Button(self.tools, image = ImageTk.PhotoImage(sq_button_image) , command = self.set_rectangle_shape, anchor = tk.W, borderwidth=0)
        self.tools.create_window(0,0,window = rectangle_button, anchor = tk.NW)
        self.tools.pack(fill = tk.BOTH)
        
        #Shape canvas part
        self.canvas = tk.Canvas(self)
        self.canvas.pack(fill = tk.BOTH, expand = 1)
        self.canvas.bind('<Button-1>', self.clicked)
        self.canvas.bind('<B1-Motion>', self.motion)
        self.canvas.bind('<ButtonRelease-1>', self.released)
        
        #Binding shortcuts in both
        root.bind('<Key>', self.key_pressed)
        root.bind('<Control-Key-z>', self.undo)
        root.bind('<Control-Key-Z>', self.undo)
        
    def draw_circle(self, x, y, r):
        return self.canvas.create_oval(x - r, y - r, x + r, y + r, outline=self.outline, fill=self.fill, width=self.width)
    
    def draw_rectangle(self, x0, y0, x1, y1):
        return self.canvas.create_rectangle(x0, y0, x1, y1, outline=self.outline, fill=self.fill, width=self.width)
    
    def undo(self, event):
        #delete the last item on the drawing list (shortcut CTRL-Z)
        if len(self.drawings) == 0:
            return
        drawing = self.drawings.pop()
        self.canvas.delete(drawing[0])
    
    def clicked(self, event):
        #called when using left mouse button
        self.x0 = event.x
        self.y0 = event.y
    
    def get_current_shape(self):
        return (self.shapes)[0][self.shapes[1]]
    
    def set_rectangle_shape(self):
        print("rectangle :",self.shapes)
        self.shapes[1] = self.shapes_ind['rectangle']
    
    def set_circle_shape(self):
        self.shapes[1] = self.shapes_ind['circle']
    
    def motion(self, event):
        #Drawing dynamically the current shape the user is drawing
        if self.current_drawing != None:
            self.canvas.delete(self.current_drawing)
        self.x1 = event.x
        self.y1 = event.y
        
        #circle case
        if self.get_current_shape() == 'circle':
            r = self.sensibility * math.sqrt( (self.x1 - self.x0)**2 + (self.y1 - self.y0)**2 )
            self.current_drawing = self.draw_circle(self.x0, self.y0, r)
        #rectangle case
        if self.get_current_shape() == 'rectangle':
            self.current_drawing = self.draw_rectangle(self.x0, self.y0, self.x1, self.y1)
        
    def released(self, event):
        #called when the user release left mouse button
        self.drawings.append((self.current_drawing,{'shape':self.get_current_shape(),\
                                                    'x0':self.x0,\
                                                    'y0':self.y0,\
                                                    'x1':self.x1,\
                                                    'x2':self.x1,\
                                                    'border_color':self.outline,\
                                                    'fill_color':self.fill,\
                                                    'width':self.width}))
        self.current_drawing = None
        
    def next_shape(self):
        #select the next shape in self.shapes[0]. (for now, called when pressing space bar)
        self.shapes[1] += 1
        if self.shapes[1] == len(self.shapes[0]):
            self.shapes[1] = 0
        return self.shapes[0][self.shapes[1]]
        
    def new_color(self):
        #change the fill color (for now, called when pressing C key)
        return colorchooser.askcolor(title ="Choose color")
        
    def key_pressed(self, event):
        #called each time a key is pressed
        
        #changing shape
        if event.keysym == 'space':
            shp = self.next_shape()
            print("Selected shape : "+shp)
            return shp
        
        #changing color
        if event.keysym == 'c':
            print("Select new color")
            self.fill = self.new_color()[1]
            print("Color selected : ", self.fill)
            
        if event.keysym == 'a':
            print([k[1] for k in self.drawings])

def main():
    frame = MFrame(root)
    root.geometry(f'{screen_width}x{screen_height}+{x_shift}+{y_shift}')
    root.mainloop()

if __name__ == '__main__':
    main()