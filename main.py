from BotFunctions import rmkt2sem, rmkt2semWep, isStatCorrect, isModCorrect
from semlar import Semlar
from weapons import weaponslist1, weaponslist2
import re
from datetime import timedelta
from time import sleep, time
from playsound import playsound
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec

from writer import Writer

options = Options()
options.headless = False
start_time = time()
weapons = weaponslist2()

# writing to .csv
writer = Writer("modlist.csv")

rmkt_driver = webdriver.Firefox(options=options)
rmkt_driver.get("https://riven.market/list/PC")
semlar = Semlar(options.headless)
print("Websites open")

for weapon in weapons:
    print("---Scanning " + weapon + "---")
    Select(rmkt_driver.find_element_by_id("list_limit")).select_by_value("200")  # Show 200 Rivens
    Select(rmkt_driver.find_element_by_id("list_recency")).select_by_value("7")  # <7 days
    Select(rmkt_driver.find_element_by_id("list_weapon")).select_by_visible_text(weapon)  # Weapon
    rmkt_driver.execute_script("loadList(1,'price','ASC')")  # price ascending

    # TODO: Zrobic zeby to gnojstwo dzialalo
    #WebDriverWait(rmkt_driver, 10).until(ec.presence_of_element_located((By.TAG_NAME, "center")))
    while True:
        rmkt_soup = BeautifulSoup(rmkt_driver.page_source, "lxml")
        loading = rmkt_soup.find_all("center")
        sleep(0.05)
        if not loading:  # if there is no "Loading" element
            break

    rmkt_list = rmkt_soup.find_all("div", class_="riven")
    for list_el in rmkt_list:
        wepid = list_el["id"]
        wepname = rmkt2semWep(list_el["data-weapon"])
        weptype = list_el["data-wtype"]
        modname = list_el["data-name"]
        modprice = list_el["data-price"]
        modage = list_el["data-age"]
        stat1, error1 = rmkt2sem(list_el["data-stat1"], weptype, wepname)
        stat2, error2 = rmkt2sem(list_el["data-stat2"], weptype, wepname)
        stat3, error3 = rmkt2sem(list_el["data-stat3"], weptype, wepname)
        stat4, error4 = rmkt2sem(list_el["data-stat4"], weptype, wepname)

        #TODO: try catch bo paszyjaja mi placze
        cont = False
        for error in [error1, error2, error3, error4]:
            if error != "":
                cont = True
                print(error+"\n"+" \""+list_el["data-stat1"]+"\""
                      " \""+list_el["data-stat2"]+"\""
                      " \""+list_el["data-stat3"]+"\""
                      " \""+list_el["data-stat4"]+"\"")
        if cont:
            continue

        statc = 0
        cond1 = True
        for stat in [stat1, stat2, stat3, stat4]:
            if not isStatCorrect(stat, weptype):
                cond1 = False
            if stat != "":
                statc += 1
        cond2 = (list_el["data-age"] == "new" or list_el["data-age"] == "> 1 day")
        cond3 = isModCorrect(stat1, stat2, stat3, stat4, statc)

        if cond1 and cond2 and cond3:
            semlar.checkStat(wepname, stat1, stat2, stat3, stat4)
            # write to csv
            writer.writerow(wepid, wepname, modname, modprice, semlar.rating, modage, semlar.sales, stat1, stat2, stat3, stat4)
    writer.writeempty()

rmkt_driver.quit()
semlar.quit()

print("---DONE---")
playsound("sound.wav")
time_elapsed = time() - start_time
print("Time Elapsed " + str(timedelta(seconds=time_elapsed)).split(".")[0])
