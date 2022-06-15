import tkinter as tk
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
        
        self.shape = 'circle'
        self.current_drawing = None
        
        root.bind('<Button-1>', self.clicked)
        root.bind('<B1-Motion>', self.motion)
        root.bind('<ButtonRelease-1>', self.released)
        
        
    def draw_circle(self, x, y, r, outline="#f11", fill = "#1f1", width = 2):
        return self.canvas.create_oval(x - r, y - r, x + r, y + r, outline=outline, fill=fill, width=width)
    
    def clicked(self, event):
        self.x0 = event.x
        self.y0 = event.y
    
    def motion(self, event):
        if self.current_drawing != None:
            self.canvas.delete(self.current_drawing)
        self.x1 = event.x
        self.y1 = event.y
        if self.shape == 'circle':
            r = math.sqrt((self.x1 - self.x0)**2 + (self.y1 - self.y0)**2)
            self.current_drawing = self.draw_circle(self.x0, self.y0, r)
        
    def released(self, event):
        self.current_drawing = None

def main():
    frame = MFrame(root)
    root.geometry(f'{screen_width}x{screen_height}+{x_shift}+{y_shift}')
    root.mainloop()

if __name__ == '__main__':
    main()