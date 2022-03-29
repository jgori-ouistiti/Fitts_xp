from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By

URL = "https://fr.wikipedia.org/wiki/Wikip%C3%A9dia:Accueil_principal"

def extractPosition(url):
    options = Options()
    options.add_argument('--headless')
    driver = webdriver.Firefox(options = options)
    driver.get(url)
    
    #elements = driver.find_elements(By.XPATH, '//button')
    #elements += driver.find_elements(By.XPATH, '//link')
    #elements = driver.find_elements_by_id("link")
    elements = driver.find_elements_by_xpath("//a[@href]")
    cibles = []
    for element in elements:
        print(element.get_attribute("href"))
        position = element.rect
        print(position)
        if position['x'] < 0 or position['y'] < 0 :
            continue
        if position['height'] <= 0 or position['width'] <= 0:
            continue
        cibles.append(position)
    driver.quit()
    return cibles
    
def main():
    res = extractPosition(URL)
    print("Liste des cibles : ",res)
    
if __name__ == '__main__':
    main()
