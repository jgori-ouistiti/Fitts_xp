from turtle import pos
import pygame
from drawable import *
from listener import *
from healthBar import *

#colors
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

class Game :
	def __init__(self, width, height, bg_color = WHITE):
		pygame.init()
		self.font = pygame.font.SysFont("aerial", 60)
		self.screen    = pygame.display.set_mode((width, height))
		pygame.display.set_caption("TEST CIBLES")
		self.width     = width
		self.height    = height
		self.listener  = dict() #Key = Listener object, value = boolean (True if listening, False if not listening) 
		self.drawables = dict() #Key = Drawable object, value = boolean (True if is on screen, False if not )
		self.bg_color  = bg_color
		self.running   = False
		self.barTime = HealthBar(5, posText=(50,50), posRect=(30,30))
		self.time = 100
		
	def draw(self):
		for d, v in self.drawables.items():
			if v:
				d.draw(self)

	def refreshScreen(self):
		self.screen.fill(self.bg_color)
		self.draw()
		pygame.display.update()
			
	def addDrawable(self, d):
		if (hasattr(d, "__len__")):
			for d_item in d:
				if isinstance(d_item, Drawable):
					self.listener.append(d_item)
				else:
					print("Warning : ",d_item," found but not drawable")
		elif (not isinstance(d, Drawable)):
			raise Exception("d is not drawable")
		else:
			self.drawables[d] = True
		
	def addListener(self, l):
		if (hasattr(l, "__len__")):
			for l_item in l:
				if isinstance(l_item, Listener):
					self.listener[l_item] = True
				else:
					print("Warning : ",l_item," found but not a listener")
		elif (not isinstance(l, Listener)):
			raise Exception("l is not a listener")
		else:
			self.listener[l] = True
		
	def removeDrawable(self, d):
		if (hasattr(d, "__len__")):
			for d_item in d:
				if d_item in self.drawables.keys():
					del self.drawables[d_item]
		elif d in self.drawables.keys():
			del self.drawables[d]
			
	def removeListener(self, l):
		if (hasattr(l, "__len__")):
			for l_item in l:
				if l_item in self.listener.keys():
					del self.listener[l_item]
		elif l in self.listener.keys():
			del self.listener[l]
			
	def addListenerDrawable(self, ld):
		if (hasattr(ld, "__len__")):
			for ld_item in ld:
				if (not isinstance(ld_item, Drawable) or not isinstance(ld_item, Listener)):
					print("Warning : ",l_item," found but not a listener or drawable")
				else:
					self.drawables[ld_item] = True
					self.listener[ld_item] = True
			return
		if (not isinstance(ld, Drawable) and not isinstance(ld, Listener)):
			raise Exception("ld is not a listener and not drawable")
		if (not isinstance(ld, Listener)):
			raise Exception("ld is not a listener")
		if (not isinstance(ld, Drawable)):
			raise Exception("ld is not drawable")
		self.drawables[ld] = True
		self.listener[ld] = True
		
	def removeListenerDrawable(self, ld):
		if ld in self.drawable.keys() and ld in self.listener.keys():
			del self.drawables[ld]
			del self.listener[ld]
		else:
			raise Exception("ld not in listener drawable")
			
	def hideDrawable(self, d):
		self.drawables[d] = False
	
	def hideListener(self, l):
		self.listener[l] = False
		
	def hideListenerDrawable(self, ld):
		self.hideDrawable(ld)
		self.hideListener(ld)
		
	def hideAllDrawable(self):
		for d in self.drawables.keys():
			self.drawables[d] = False
			
	def hideAllListener(self):
		for l in self.listener.keys():
			self.listener[l] = False
	
	def showAllDrawable(self):
		for d in self.drawables.keys():
			self.drawables[d] = True
			
	def showAllListener(self):
		for l in self.listener.keys():
			self.listener[l] = True
			
	def listen(self, event):
		for l, v in self.listener.items():
			if v:
				l.action(self, event)
			
	def menu(self, menu_title):
		if menu_title == "play":
			self.play()
		if menu_title == "pause":
			self.hideAllDrawable()
			self.hideAllListener()
			self.pauseMenu()
			
	def write_screen(self, mot,color, pos, booleen=True ):
		text = self.font.render(mot, booleen, color)
		text_rect = text.get_rect(center=pos)
		self.screen.blit(text, text_rect)
    
	def pauseMenu(self):
		self.refreshScreen()
		self.write_screen("PAUSE", BLACK, (self.width/2, self.height/2 - 30))
		self.write_screen("Press ESCAPE to continue", BLACK, (self.width/2, self.height/2 + 30))
		self.running = True
		while(self.running):
			pygame.display.update()
			ev = pygame.event.get()
			for event in ev:
				if event.type == pygame.KEYDOWN:
					if event.key == pygame.K_ESCAPE:
						self.running = False
						self.showAllDrawable()
						self.showAllListener()
						self.menu("play")
			
	
	def play(self):
		self.running = True
		self.addDrawable(self.barTime)
		pygame.time.set_timer(pygame.USEREVENT, 10) #Active pygame.USEREVENT toute les 10ms 
		while (self.running):
			self.refreshScreen()
			ev = pygame.event.get()
			for event in ev:
				self.listen(event)
				if event.type == pygame.QUIT:
					self.running = False
					
				#timer
				if event.type == pygame.USEREVENT:
					self.barTime.addSubTime(-0.01)
				
				if event.type == pygame.KEYDOWN:
					if event.key == pygame.K_ESCAPE:
						self.running = False
						self.menu("pause")
					
