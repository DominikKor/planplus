import json
from plan.models import Teacher

from selenium.webdriver import Firefox
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary


def get_teachers():
    binary = FirefoxBinary("/usr/bin/firefox")
    driver = Firefox(firefox_binary=binary)
    site = "https://gymnasium-meine.de/kollegium/"

    driver.get(site)
    teachers = driver.find_elements(By.CSS_SELECTOR, ".w-person-name")

    names = {}
    for teacher in teachers:
        try:
            short = teacher.text.split("(")[1][:-1]
        except IndexError:
            continue
        name = teacher.text.split(",")[0]
        names[short] = name

    print(names)

    driver.close()


def load_teachers_to_db(teachers_dict: dict):
    for k, v in teachers_dict.items():
        print(k, v)
        Teacher.objects.create(short_name=k, last_name=v)


with open("teachers.json") as file:
    teachers = json.loads(file.read())[0]

# get_teachers()
load_teachers_to_db(teachers)
