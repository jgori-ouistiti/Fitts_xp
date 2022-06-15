import tkinter as tk
from tkinter import colorchooser
import math

root = tk.Tk()
x_shift = 100
y_shift = 100

screen_width = root.winfo_screenwidth() - 2*x_shift
screen_height = root.winfo_screenheight() - 2*y_shift

class MFrame(tk.Frame):
    def __init__(self, root, title="Experiment editor"):
        super().__init__(root)
        
        self.master.title(title)
        self.pack(fill = tk.BOTH, expand = 1)
        self.canvas = tk.Canvas(self)
        self.canvas.pack(fill = tk.BOTH, expand = 1)
        
        self.shapes = [['circle', 'rectangle'],0]
        self.current_drawing = None
        self.outline = "#000"
        self.fill = "#fff"
        self.width = 2
        
        root.bind('<Button-1>', self.clicked)
        root.bind('<B1-Motion>', self.motion)
        root.bind('<ButtonRelease-1>', self.released)
        root.bind('<Key>', self.key_pressed)
        
    def draw_circle(self, x, y, r):
        return self.canvas.create_oval(x - r, y - r, x + r, y + r, outline=self.outline, fill=self.fill, width=self.width)
    
    def draw_rectangle(self, x0, y0, x1, y1):
        return self.canvas.create_rectangle(x0, y0, x1, y1, outline=self.outline, fill=self.fill, width=self.width)
    
    def clicked(self, event):
        self.x0 = event.x
        self.y0 = event.y
    
    def get_current_shape(self):
        return (self.shapes)[0][self.shapes[1]]
    
    def motion(self, event):
        if self.current_drawing != None:
            self.canvas.delete(self.current_drawing)
        self.x1 = event.x
        self.y1 = event.y
        if self.get_current_shape() == 'circle':
            r = math.sqrt((self.x1 - self.x0)**2 + (self.y1 - self.y0)**2)
            self.current_drawing = self.draw_circle(self.x0, self.y0, r)
        if self.get_current_shape() == 'rectangle':
            self.current_drawing = self.draw_rectangle(self.x0, self.y0, self.x1, self.y1)
        
    def released(self, event):
        self.current_drawing = None
        
    def next_shape(self):
        self.shapes[1] += 1
        if self.shapes[1] == len(self.shapes[0]):
            self.shapes[1] = 0
        return self.shapes[0][self.shapes[1]]
        
    def new_color(self):
        return colorchooser.askcolor(title ="Choose color")
        
    def key_pressed(self, event):
        if event.keysym == 'space':
            shp = self.next_shape()
            print("Selected shape : "+shp)
            return shp
        
        if event.keysym == 'c':
            print("Select new color")
            self.fill = self.new_color()[1]
            print("Color selected : ", self.fill)

def main():
    frame = MFrame(root)
    root.geometry(f'{screen_width}x{screen_height}+{x_shift}+{y_shift}')
    root.mainloop()

if __name__ == '__main__':
    main()