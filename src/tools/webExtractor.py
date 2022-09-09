import sys
sys.path.append('../class')
from cibleRect import *
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
import colors


URL = "https://fr.wikipedia.org/wiki/Wikip%C3%A9dia:Accueil_principal"

def extractPosition(url,WIDTH = 1080, HEIGHT = 1920, displayInfo = True):
    nbOfPos = 0
    if displayInfo:
        print("Collecting position from url :",url)
    options = Options()
    options.add_argument('--headless')
    options.add_argument("--width="+str(WIDTH))
    options.add_argument("--height="+str(HEIGHT))
    
    driver = webdriver.Firefox(options = options)
    driver.get(url)
    
    #elements = driver.find_elements(By.XPATH, '//button')
    #elements += driver.find_elements(By.XPATH, '//link')
    #elements = driver.find_elements_by_id("link")
    elements = driver.find_elements_by_xpath("//a[@href]") #On récupère tous les liens de la page
    cibles = []
    for element in elements:
        position = element.rect
        if position['x'] < 0 or position['y'] < 0 :
            continue
        if position['height'] <= 0 or position['width'] <= 0:
            continue
        if displayInfo :
            nbOfPos += 1
            print(position, 'url :', element.get_attribute("href"))
        cibles.append(position)
    if displayInfo :
        print("\nNumber of elements visible (relative to screen resolution) in the page :", nbOfPos)
    driver.quit()
    return cibles
    
def transformToTargets(positions, widthLimit, heightLimit, color=colors.BLACK, displayInfo = True):
    targets = []
    nbOfTar = 0
    for t in positions:
        if t['x'] > widthLimit or t['y'] > heightLimit :
            continue
        if displayInfo:
            print('Creating rectangular target with ', t)
        targets.append(CibleRect((int(t['x']),int(t['y'])), t['width'], t['height'], color))
        nbOfTar += 1
    if displayInfo : 
        print("Number of targets generated :",nbOfTar)
    return targets
    
def getTargetsFromUrl(url, widthLimit, heightLimit, color = colors.BLACK, displayInfo = True):
    positions = extractPosition(url, WIDTH = widthLimit, HEIGHT = heightLimit, displayInfo = displayInfo)
    targets = transformToTargets(positions, widthLimit, heightLimit, color, displayInfo)
    return targets
    
def main():
    targets = getTargetsFromUrl(URL)
    
if __name__ == '__main__':
    main()
