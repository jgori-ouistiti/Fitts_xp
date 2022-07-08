from cursor import *

class SensitiveCursor(Cursor):
    '''cursor with speed multiplicator (sensibility)'''
    
    def __init__(self, WIDTH, HEIGHT, dx_sens = 1, dy_sens = 1,cursorImage = 'class/cursor/cursor1.png', visible = True):
        super().__init__(WIDTH, HEIGHT, cursorImage = cursorImage, visible = visible)
        self.dx_sens = dx_sens
        self.dy_sens = dy_sens
        
    def move(self, dx, dy):
        # print('--DEBUG--')
        # print('self.x :',self.x)
        # print('dx :',dx)
        # print('self.dx_sens :',self.dx_sens)
        # print('self.WIDTH :',self.WIDTH)
        if self.x + (dx * self.dx_sens) > 0 and self.x + (dx * self.dx_sens) < self.WIDTH:
            self.x += (dx * self.dx_sens)
        if self.y + (dy * self.dy_sens) > 0 and self.y + (dy * self.dy_sens) < self.HEIGHT:
            self.y += (dy * self.dy_sens)
            
    def set_x_sensibility(self,dx_sens):
        self.dx_sens = dx_sens
        
    def set_y_sensibility(self,dy_sens):
        self.dy_sens = dy_sens
        
    def getSensibility(self):
        return (self.dx_sens, self.dy_sens)
        
    def invertX(self):
        '''Invert the X axe'''
        self.dx_sens = -self.dx_sens
        
    def invertY(self):
        '''Invert the Y axe'''
        self.dy_sens = -self.dy_sens
