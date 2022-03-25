
from game import *
import sys
sys.path.append('../tools')
import colors as Colors
import random

class Experiment :
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.game = Game(self.width, self.height)

        self.testTotale = 0

        # typeTarget : int (pour savoir quel disposition des targets on utilise)
        # nombreExp : int (pour savoir on repete combien de fois ce disposition des targets)
        # listTarget : list (c'est une liste des positions des targets)
        ## self.list : dict( typeTarget : [nombreExp, listTarget] )
        self.listTest = dict() 


    def addTest(self, nombre, typeTarget, listTarget): 
        """
            Permet d'ajouter/augmenter de nombre d'experience
        """
        if nombre > 0 : 
            self.testTotale += nombre
            if typeTarget in self.listTest : #si il existe, alors on augmente le nombre
                self.listTest[typeTarget][0] += nombre
            else : #sinon on va la creer, en la rajoutant dans le dictionnaire
                self.listTest[typeTarget] = [nombre, listTarget] 
        

    def menu(self):

        self.game.screen.fill(Colors.WHITE)
        pygame.display.update()  

        #self.game.write_screen()

        ev = pygame.event.get()
        for event in ev:
            if event.type == pygame.QUIT:
                self.game.quitApp()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE: 

                    key, value = random.choice(list(self.listTest))

                    if value[0] > 0 :
                        if value[0] == 1 : 
                            listTarget = self.listTest.pop(key)[1]
                        else : 
                            value[0] -= 1
                            listTarget = value[1]
                        self.game.addListenerDrawable(listTarget)
                        self.game.play('experiment', listTarget, showTime=False) 

                    



    def play(self):
        self.game.screen.fill(Colors.WHITE)
        pygame.display.update()  

        #self.game.write_screen()

        while(self.testTotale > 0):  
            ## Choose random a type of test
            key = random.choice(list(self.listTest))
            value = self.listTest[key]
            print("---- key(typeTarget) =", key, "||", "nombre =", value[0])

            if value[0] > 0 :
                if value[0] == 1 : 
                    # it is the last test of this type of target, 
                    # with 'pop', we delete it of the dictionary 
                    listTarget = self.listTest.pop(key)[1] 
                else : 
                    value[0] -= 1
                    listTarget = value[1]
                    
                    #ev = pygame.event.get()
                    #for event in ev:
                    #    if event.type == pygame.QUIT:
                    #        self.game.quitApp()
                    #    if event.type == pygame.KEYDOWN:
                    #        if event.key == pygame.K_ESCAPE:


                ## User have to do the test
                self.game.play('experiment', listTarget, showTime=False) #play effectue l'ajout des cibles dans Listener/Drawable
                self.testTotale -= 1

            if self.testTotale == 0:
                break 

        if self.testTotale == 0:
            print("FIN DE EXPERIENCE")          

    