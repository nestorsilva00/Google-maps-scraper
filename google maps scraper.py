import time
from datetime import datetime
import re
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from random import randint
from win10toast import ToastNotifier
import pandas as pd
from selenium.common.exceptions import ElementClickInterceptedException
from timeit import default_timer as timer

class ScrapearGMaps:
    
    data = pd.DataFrame(columns=['name','category','address', 'timetable', 'website', 'phone_number', 'email', 'coordinates'])
    #worksheet = {}
    
    def __init__(self):
        
        self.driver = webdriver.Chrome()
        self.driver.maximize_window()
        
        now = datetime.now()
        today = now.strftime("%Y-%m-%d")

    def get_data(self): return self.data

    def set_data(self, new_data): self.data = new_data

    def push_notification(self, text):
        toaster = ToastNotifier()
        toaster.show_toast("Google Maps Scraper", text)

    def scroll_the_page(self, i):
        
        try:
            section_loading = WebDriverWait(self.driver, 120).until( \
        EC.presence_of_element_located((By.XPATH, "//div[contains(@class,'wo1ice-loading')]")))
            while True:
                print(len(WebDriverWait(self.driver, 120).until( \
                    EC.presence_of_all_elements_located((By.XPATH, "//div[contains(@class,'section-scrollbox')]//descendant::a")))))
                if i >= len(WebDriverWait(self.driver, 120).until( \
                    EC.presence_of_all_elements_located((By.XPATH, "//div[contains(@class,'section-scrollbox')]//descendant::a")))):
                    actions = ActionChains(self.driver)
                    actions.move_to_element(section_loading).perform()
                    time.sleep(randint(2,3))
                else:
                    break
        except:
            pass
        
    def get_geocoder(self, url_location): # gets geographical lat/long coordinates
        try:
            coords = re.search(r"!3d-?\d\d?\.\d{4,8}!4d-?\d\d?\.\d{4,8}",
                            url_location).group()
            coord = coords.split('!3d')[1]
            return tuple(coord.split('!4d'))
        except (TypeError, AttributeError):
            return ("", "")
        
    def get_name(self):
        try:
            #return self.driver.find_element_by_xpath("//h1[contains(@class,'header-title')]").text
            return WebDriverWait(self.driver, 2).until( \
                        EC.presence_of_element_located((By.XPATH, "//h1[contains(@class,'header-title')]//descendant::span"))).text
        except:
            return ""

    def get_category(self):
       try:
           #return self.driver.find_element_by_xpath("//h1[contains(@class,'header-title')]").text
           return WebDriverWait(self.driver, 2).until( \
                       EC.presence_of_element_located((By.XPATH, "//button[contains(@jsaction,'pane.rating.category')]"))).text
       except:
           return ""
            
    def get_address(self):
        try:
            #return self.driver.find_element_by_css_selector("[data-item-id='address']").text
            return WebDriverWait(self.driver, 2).until( \
                       EC.presence_of_element_located((By.XPATH, "//button[contains(@data-item-id,'address')]//div[contains(@class,'gm2-body-2')]"))).text
        except:
            return ""

    def get_phone(self):
        try:
            phone_number = self.driver.find_element_by_css_selector("[data-tooltip='Copiar el número de teléfono']").get_attribute("aria-label")
            return phone_number.replace("Teléfono: ", "")
        except:
            return ""
        
    def get_website(self):
        try:
            website = self.driver.find_element_by_css_selector("[data-item-id='authority']").get_attribute("aria-label")
            return website.replace("Sitio web: ", "")
        except:
            return ""

    def click_open_close_time(self):
        try:
            button = WebDriverWait(self.driver, 2).until( \
                       EC.element_to_be_clickable((By.XPATH, "//div//img[contains(@aria-label,'Horas')]")))
            button.click()            
        except Exception as e:
            print(e)
    
    def get_timetable(self):
        try:
            df_result = pd.DataFrame(columns=['day', 'open_time'])
            week_days = WebDriverWait(self.driver, 2).until( \
                       EC.presence_of_all_elements_located
                       ((By.XPATH, "//th//descendant::div")))
            week_days = list(filter(lambda a:week_days.index(a)%2==0, week_days))

            open_time = WebDriverWait(self.driver, 2).until( \
                       EC.presence_of_all_elements_located
                       ((By.XPATH, "//td//descendant::ul//li")))

            if(len(week_days)>=7 and len(open_time)>=7):
                for i in range(0,7):
                    day =week_days[i].get_attribute('innerHTML')
            
                    time= open_time[i].get_attribute('innerHTML')
            
                    df_result = df_result.append({'day': day, 'open_time':time}, ignore_index=True)
                
               
            
            return df_result
        except:
            return ""
    
    def scrape(self, query):
        try:
            query = query.replace(" ", "+")
            url = "https://www.google.es/maps/search/"+query+"/"
            self.driver.get(url)
                        
            time.sleep(randint(2,4))
            
            #element = self.driver.find_element_by_xpath("//button[.//span[text()='Acepto']]")
            #element.click()
            
            #time.sleep(3)
            while(True):
                try:
                    for i in range(0,20):
                        self.scroll_the_page(i)                
                        elements = WebDriverWait(self.driver, 120).until( \
                                EC.presence_of_all_elements_located((By.XPATH, "//div[contains(@class,'section-scrollbox')]//descendant::a")))
            
                        element = elements[i]
                                            
                        element.click()
                            
                        time.sleep(randint(2,3))
                            
                        self.click_open_close_time()

                        print("parkeo "+str(i))    
                        name = self.get_name()
                        print(name)
                        category = self.get_category()
                        print(category)
                        address = self.get_address()
                        print(address)
                        website = self.get_website()
                        print(website)
                        phone = self.get_phone()
                        print(phone)
                        time_table = self.get_timetable()
                        print(time_table)
                        coords = self.get_geocoder(self.driver.current_url)
                        print(coords)
                            

                        self.set_data(self.data.append({'name':name,'category':category,'address':address, 'timetable':time_table, 'website':website, 'phone_number':phone, 'coordinates':coords}, ignore_index=True))
                        
                        

                        go_back_button =  WebDriverWait(self.driver, 20).until( \
                                EC.presence_of_element_located((By.XPATH, "//button//span[contains(text(), 'Volver a los resultados')]")))
                        go_back_button.click()
                        time.sleep(randint(2,4))
              
                    
                    next_page = WebDriverWait(self.driver, 20).until( \
                                            EC.presence_of_element_located((By.XPATH, "//button[@aria-label='Página siguiente']")))
                    next_page.click()
                    time.sleep(randint(3,5))
                except ElementClickInterceptedException:
                    self.push_notification("Upss! Ha ocurrido un error")
                    break


                     
               
                
            
        except Exception as e:
            print(e)
        
        time.sleep(5)
        self.driver.quit()
        #self.data.to_excel(query+"_data.xls")
        self.data.to_csv(query+"_data.csv")
        self.push_notification("Ya ha terminado la extraccion de los datos de "+query.replace("+", " "))
        return(self.data)

start = timer()
start_time = datetime.now().time()
query = "restaurantes madrid españa"
gmaps = ScrapearGMaps()
print(gmaps.scrape(query))

end_time = datetime.now().time()
end = timer()
print("Tiempo de ejecución del programa: "+str(end - start))
print("Hora de inicio: "+str(start_time)+" - Hora de finalización: "+str(end_time))
