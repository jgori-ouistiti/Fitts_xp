from tkinter import *
from tkinter import ttk
from tkinter import colorchooser
from tkinter import filedialog

from PIL import Image, ImageTk
import math
import json

root = Tk()
x_shift = 100
y_shift = 100
toolbar_width = 40

screen_width = root.winfo_screenwidth() - 2*x_shift
screen_height = root.winfo_screenheight() - 2*y_shift - toolbar_width

class MFrame(ttk.Frame):
    def __init__(self, root, title="Experiment editor"):
        ttk.Frame.__init__(self, root)
        
        self.master.title(title)
        
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
        
        #file name of the experiment (used in quick save)
        self.file_name = None
        
        #Menu part
        self.menuBar = Menu(root)
        
        self.fileMenu = Menu(self.menuBar)
        self.fileMenu.add_command(label = "Open", command = self.open_file)
        self.fileMenu.add_command(label = "Save", command = self.save_experiment)
        self.fileMenu.add_command(label = "Save as", command = self.save_experiment)
        self.fileMenu.add_command(label = "Exit", command = self.quitApp)
        self.menuBar.add_cascade(label = "File", menu = self.fileMenu)
        
        root.config(menu = self.menuBar)
        
        #Tools bar part
        self.tools  = Frame(self, bd = 1, relief = RAISED)
        
        
        self.rectangle_img = Image.open("images/square_button.png")
        self.rectangle_img = self.rectangle_img.resize((toolbar_width,toolbar_width))
        self.circle_img = Image.open("images/circle_button.png")
        self.circle_img = self.circle_img.resize((toolbar_width, toolbar_width))
        self.color_img  = Image.open("images/color_button.png")
        self.color_img  = self.color_img.resize((toolbar_width, toolbar_width))
        self.save_img   = Image.open("images/save_button.png")
        self.save_img   = self.save_img.resize((toolbar_width, toolbar_width))
        
        self.photo_rect = ImageTk.PhotoImage(self.rectangle_img)
        self.photo_circ = ImageTk.PhotoImage(self.circle_img)
        self.photo_color= ImageTk.PhotoImage(self.color_img)
        self.photo_save = ImageTk.PhotoImage(self.save_img)
        
        rectangle_button = Button(self.tools, image = self.photo_rect, relief = FLAT, command = self.set_rectangle_shape)
        circle_button    = Button(self.tools, image = self.photo_circ, relief = FLAT, command = self.set_circle_shape)
        color_button     = Button(self.tools, image = self.photo_color, relief = FLAT, command = self.new_color)
        save_button      = Button(self.tools, image = self.photo_save,  relief = FLAT, command = self.quick_save)
        
        circle_button   .pack(side=LEFT, padx = 2, pady=2)
        rectangle_button.pack(side=LEFT, padx = 2, pady=2)  
        color_button    .pack(side=LEFT, padx = 2, pady=2)
        save_button     .pack(side=LEFT, padx = 2, pady=2)
        
        self.tools.pack(side = TOP, fill = X)
        #self.tools.create_window(0,0,window = rectangle_button, anchor = NW)
        
        
        #Shape canvas part
        self.canvas = Canvas(self, width = screen_width, height = screen_height)
        self.canvas.pack(side = TOP)
        self.canvas.bind('<Button-1>', self.clicked)
        self.canvas.bind('<B1-Motion>', self.motion)
        self.canvas.bind('<ButtonRelease-1>', self.released)
        self.canvas.pack(side=TOP)
        
        #Binding shortcuts in both
        root.bind('<Key>', self.key_pressed)
        root.bind('<Control-Key-z>', self.undo)
        root.bind('<Control-Key-Z>', self.undo)
        root.bind('<Control-Key-s>', self.quick_save)
        root.bind('<Control-Key-S>', self.quick_save)
        root.bind('<Control-Key-o>', self.open_file)
        root.bind('<Control-Key-O>', self.open_file)
        
        self.pack(side=TOP, fill = X)
    
    def quitApp(self):
        #to do: "Do you want to save the work ?"
        root.destroy()
        
    def draw_circle(self, x, y, r, outline = None, fill = None, width = None):
        if outline == None:
            outline = self.outline
        if fill == None:
            fill = self.fill
        if width == None:
            width = self.width
        return self.canvas.create_oval(x - r, y - r, x + r, y + r, outline=outline, fill=fill, width=width)
    
    def draw_rectangle(self, x0, y0, x1, y1, outline = None, fill = None, width = None):
        if outline == None:
            outline = self.outline
        if fill == None:
            fill = self.fill
        if width == None:
            width = self.width
        return self.canvas.create_rectangle(x0, y0, x1, y1, outline=outline, fill=fill, width=width)
    
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
        if self.current_drawing == None:
            return
        if self.get_current_shape() == 'rectangle':
            self.drawings.append((self.current_drawing,{'shape':self.get_current_shape(),\
                                                        'x0':self.x0,\
                                                        'y0':self.y0,\
                                                        'x1':self.x1,\
                                                        'y1':self.y1,\
                                                        'border_color':self.outline,\
                                                        'fill_color':self.fill,\
                                                        'width':self.width}))
        if self.get_current_shape() == 'circle':
            self.drawings.append((self.current_drawing,{'shape':self.get_current_shape(),\
                                                        'x':self.x0,\
                                                        'y':self.y0,\
                                                        'r':self.sensibility * math.sqrt( (self.x1 - self.x0)**2 + (self.y1 - self.y0)**2 ),
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
        color = colorchooser.askcolor(title ="Choose color")
        self.fill = color[1]
        return color
        
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
            self.new_color()
            
        if event.keysym == 'a':
            print([k[1] for k in self.drawings])
            
    def save_experiment(self):
        #Ask a file name and path to save experiment in a json file
        print("Opening save file dialog...")
        f = filedialog.asksaveasfile(mode='w', defaultextension=".json")
        if f is None: # ask save as file dialog has been closed
            print("Abandon : save file dialog closed early")
            return
        print("Saving file as "+f.name+" ...")
        D = dict()
        for i in range(len(self.drawings)):
            D[i] = self.drawings[i][1]
        json_object = json.dumps(D, indent=4)
        f.write(json_object)
        f.close()
        self.file_name = f.name
        print("File saved !")
        return
        
    def quick_save(self, event=None):
        #Save directly if a file_name is already specified
        if self.file_name == None:
            return self.save_experiment()
        print("Saving as "+self.file_name+" ...")
        f = open(self.file_name, 'w')
        D = dict()
        for i in range(len(self.drawings)):
            D[i] = self.drawings[i][1]
        json_object = json.dumps(D, indent=4)
        f.write(json_object)
        f.close()
        print("File saved !")
        return
        
    def clear_all(self):
        while self.drawings != []:
            drawing = self.drawings.pop()
            self.canvas.delete(drawing[0])
        self.current_drawing = None
        
    def open_file(self, event=None):
        #clear actual drawings and open a file
        print("Opening open file dialog...")
        f_name = filedialog.askopenfilename(
            title = "Open a file",
            filetypes = (('json files', '*.json'), ('All files', '*.*')))
        if f_name == '': # ask open file dialog has been closed
            print("Abandon : open file dialog closed early")
            return
        f = open(f_name, 'r')
        data = json.load(f)
        print(data)
        self.clear_all()
        for id, fig in data.items():
            if fig['shape'] == 'rectangle':
                self.drawings.append((
                    #Draw element + adding to self.drawings 
                    self.draw_rectangle(
                        fig['x0'], 
                        fig['y0'], 
                        fig['x1'],
                        fig['y1'], 
                        outline = fig['border_color'], 
                        fill = fig['fill_color'], 
                        width = fig['width']),
                        
                    {'shape' : fig['shape'],
                    'x0': fig['x0'], 
                    'y0':fig['y0'], 
                    'x1':fig['x1'],
                    'y1':fig['y1'], 
                    'border_color' : fig['border_color'], 
                    'fill_color' : fig['fill_color'], 
                    'width' : fig['width']}))
            if fig['shape'] == 'circle':
                self.drawings.append((
                    #Draw element + adding to self.drawings 
                    self.draw_circle(
                    fig['x'], 
                    fig['y'], 
                    fig['r'], 
                    outline = fig['border_color'], 
                    fill = fig['fill_color'], 
                    width = fig['width']),
                    
                    {'shape' : fig['shape'],
                    'x': fig['x'], 
                    'y':fig['y'], 
                    'r':fig['r'],
                    'border_color' : fig['border_color'], 
                    'fill_color' : fig['fill_color'], 
                    'width' : fig['width']}))
        f.close()
        return

def main():
    frame = MFrame(root)
    root.geometry(f'{screen_width}x{screen_height}+{x_shift}+{y_shift}')
    root.mainloop()

if __name__ == '__main__':
    main()