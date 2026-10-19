from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import time
import requests
from urllib.parse import urljoin
import re
import pandas
from webScraper import webScraper
from termcolor import colored

dances = {}
dances["smooth"] = ["Waltz", "Tango", "Foxtrot", "Vwaltz"]
dances["standard"] = ["Waltz", "Tango", "Vwaltz", "Foxtrot", "Quickstep"]
dances["rhythm"] = ["Chacha", "Rumba", "Swing", "Bolero", "Mambo"]
dances["latin"] = ["Samba", "Chacha", "Rumba", "Pasodoble", "Jive"]

dances_abbr = {}
dances_abbr["smooth"] = {"w" : "Waltz", "t" : "Tango", "f" : "Foxtrot", "v" : "Vwaltz"}
dances_abbr["standard"] = {"w" : "Waltz", "t" : "Tango", "v" : "Vwaltz", "f" : "Foxtrot", "q" : "Quickstep"}
dances_abbr["rhythm"] = {"c" : "Chacha", "r" : "Rumba", "s" : "Swing", "b" : "Bolero", "m" : "Mambo"}
dances_abbr["latin"] = {"s" : "Samba", "c" : "Chacha", "r" : "Rumba", "p" : "Pasodoble", "j" : "Jive"}

invigilations = ""
def check_elig(name, level, style, dance_list, ycn_table, invigilations, event_name):
   invigilation_str = ""
   for dance in dance_list:
      points = ycn_table[style][level][dance.lower()][0]
      if (points < 7):
         print(colored(f"Ok to dance {level} {style} {dance}", "green"))
      else:
         print(colored(f"Not ok to dance {level} {style} {dance} with {points} points", "red"))
         invigilation_str += f"\t{name} has {points} points in {level} {style} {dance}\n"
   if (invigilation_str):
      invigilations += f"{event_name}\n"
      invigilations += invigilation_str
   return invigilations


def parse_event_name(event_name):
   event_name = event_name.replace("Viennese Waltz", "Vwaltz")
   event_name = event_name.replace("Paso Doble", "Pasodoble")
   event_tokens = event_name.split(" ")
   print (event_tokens)
   level = event_tokens[0].lower()
   if level == "prechamp":
      level = "pre-champ"
   elif level == "open":
      level = "champ"
   elif level == "syllabus":
      level = "gold"
   style = event_tokens[1].lower()
   dances_tmp = [dance.title() for dance in event_tokens[2:]]

   dance_list = []
   for dance in dances_tmp:
      if dance in dances[style]:
         dance_list.append(dance)
      else:
         dance = dance.replace("sw", "s")
         print(dance)

         for abbr in dance:
            dance_list.append(dances_abbr[style][abbr.lower()])

   print(f"""
   level: {level}
   style: {style}
   dances: {dance_list}

""")
   return level, style, dance_list


def calc_ycn_streamlit(name):

   first = name.split(" ")[0]
   last = " ".join(name.split(" ")[1:])

   if (name ==  "Zeynep Deniz Lal"):
      first = "Zeynep Deniz"
      last =  "Lal"
   elif (name == "Skye Winters"):
      first = "Skye,Chase"
      last = "winters,oberg"

   webScraper_output = webScraper(first, last, True)

   smooth_data = webScraper_output[0]["smooth"]
   standard_data = webScraper_output[0]["standard"]
   rhythm_data = webScraper_output[0]["rhythm"]
   latin_data = webScraper_output[0]["latin"]

   smooth_df = pandas.DataFrame(smooth_data)
   standard_df = pandas.DataFrame(standard_data)
   rhythm_df = pandas.DataFrame(rhythm_data)
   latin_df = pandas.DataFrame(latin_data)

   data_frames = [smooth_df, standard_df, rhythm_df, latin_df]

   # Column labels
   for df in data_frames:
      df.columns = [
         "newcomer",
         "bronze",
         "silver",
         "gold",
         "novice",
         "prechamp",
         "champ",
      ]

   # Row labels
   smooth_df.index = ["Waltz", "Tango", "Foxtrot", "Vwaltz"]
   standard_df.index = ["Waltz", "Tango", "Vwaltz", "Foxtrot", "Quickstep"]
   rhythm_df.index = ["Chacha", "Rumba", "Swing", "Bolero", "Mambo"]
   latin_df.index = ["Samba", "Chacha", "Rumba", "Paso Doble", "Jive"]

   # print (smooth_df)
   # print(standard_df)

   return webScraper_output[0]

def calc_ycn_azure(name):
   if name == "Steven Test":
      return
   url = "https://ballroom-calc.azurewebsites.net/"
   first = name.split(" ")[0]
   last = name.split(" ")[1]

   driver = webdriver.Firefox()
   driver.implicitly_wait(10)
   driver.get(url)

   elem = driver.find_element(By.NAME, "first_name")
   elem.clear()
   elem.send_keys(first)

   elem = driver.find_element(By.NAME, "last_name")
   elem.clear()
   elem.send_keys(last)

   # submit form
   elem.submit()

   tableObtained = False
   while not tableObtained:
      try:
         driver.find_element(By.TAG_NAME, "table")
         tableObtained=True
      except:
         tableObtained = False


   html = driver.page_source
   tables = pandas.read_html(html)
   for table in range(len(tables)):
      df = tables[table]
      print(df)


   driver.close()

def calc_ycn(name):
   if name == "Steven Test":
      return
   url = "https://ballroom-calc.streamlit.app"
   first = name.split(" ")[0]
   last = name.split(" ")[1]

   driver = webdriver.Firefox()
   driver.implicitly_wait(10)
   driver.get(url)
   iframe = driver.find_element(By.CLASS_NAME, "_iframe_nim44_26")
   driver.switch_to.frame(iframe)

   elem = driver.find_element(By.ID, "text_input_1")
   elem.clear()
   elem.send_keys(first)

   elem = driver.find_element(By.ID, "text_input_2")
   elem.clear()
   elem.send_keys(last)

   # submit form
   driver.find_element(By.XPATH, "//button[@class='st-emotion-cache-15hul6a ef3psqc13']/div[@class='st-emotion-cache-12118b6 e1nzilvr5']").click()

   time.sleep(5)

   elem = driver.find_element(By.CSS_SELECTOR, "#bui3__anchor .eyeqlp53")
   elem.click()


   # html = driver.page_source
   # table= pandas.read_html(html)
   # print(table)
   driver.close()



def is_competitor_link(href):
    return href and "competitor" in href

URL = "https://carnegieclassic2024.web.app/competitors/"

# initiating the webdriver. Parameter includes the path of the webdriver.
driver = webdriver.Firefox()
driver.get(URL)

# this is just to ensure that the page is loaded
time.sleep(3)

html = driver.page_source

soup = BeautifulSoup(html, "html.parser")

competitor_entries = {}
for link in soup.find_all(href=is_competitor_link):
   href = link.get("href")
   fulllink= urljoin(URL, href)
   if (link.find_all("h3")):
      name = link.find_all("h3")[0].string
      if name == "Steven Test":
         continue
      print(name, fulllink)
      driver.implicitly_wait(30)
      driver.get(fulllink)
      driver.find_element(By.CLASS_NAME, "n-data-table-table") # wait until table is visible
      html = driver.page_source
      soup2 = BeautifulSoup(html, "html.parser")
      ycn_table = calc_ycn_streamlit(name)
      found_events = False
      for event in soup2.find_all(attrs={"data-col-key":"eventName"}):
         event_name = event.get_text()
         if event_name == "Event":
            continue
         print("eventname", event_name)
         level, style, dance_list = parse_event_name(event_name)
         found_events=True
         invigilations = check_elig(name, level, style, dance_list, ycn_table, invigilations, event_name)
      if not found_events:
         invigilations += f"{name} HAS NO ENTRIES\n"

      with open("invigilations.txt", "w") as f:
         f.write(invigilations)

driver.close()