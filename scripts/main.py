import datetime
import os
from pathlib import Path

from selenium.webdriver import Firefox
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
from selenium.webdriver.firefox.options import Options
from dotenv import load_dotenv


def get_full_schedule() -> dict:
    options = Options()
    load_dotenv()
    is_prod = os.getenv("ENV_NAME") == "Production"
    options.headless = is_prod
    binary = FirefoxBinary("/usr/bin/firefox" + "/firefox-bin" if is_prod else "")
    driver = Firefox(firefox_binary=binary, options=options)

    load_dotenv(os.path.join(Path(__file__).resolve().parent.parent, ".env"))

    PLAN_WEBSITE = "vplan.gymnasium-meine.de/mobil095"
    USERNAME = os.getenv("PLAN_USERNAME")
    PASSWORD = os.getenv("PLAN_PASSWORD")

    driver.get(f"https://{USERNAME}:{PASSWORD}@{PLAN_WEBSITE}/")
    driver.get(f"https://{PLAN_WEBSITE}/auswahlkl.html")

    number_of_classes = len(driver.find_elements(By.CSS_SELECTOR, ".mobilauswahlkl"))

    res = {}

    for i in range(number_of_classes):
        driver.get("https://vplan.gymnasium-meine.de/mobil095/auswahlkl.html")
        # Click on class in list
        driver.find_element(By.XPATH, f"/html/body/div[1]/div/ul/li[{i + 1}]/div/div/a").click()
        # Find all periods
        items = driver.find_elements(By.CSS_SELECTOR, ".liplanzeile")
        # Read date + class from title
        _, date, _, class_, *_ = driver.find_element(By.CSS_SELECTOR, "#planklkopf").text.split()
        if i == 0:
            # Convert date to DateTime
            res["date"] = datetime.datetime.strptime(date, "%d.%m.%Y")
            # Check when the plan was last updated
            _, _, date_l_up, hour_l_up = driver.find_element(By.CSS_SELECTOR, "#planklkopf2").text.split()
            # Convert last updated time to datetime
            res["last_updated"] = datetime.datetime.strptime(date_l_up[:-1] + " " + hour_l_up[:-1], "%d.%m.%Y %H:%M")
            # Find daily info box
            res["info"] = driver.find_element(By.CSS_SELECTOR, ".liinfozeile").text
        res[class_] = [item.text for item in items]

    driver.close()

    return res


def get_plan():
    new_schedule = get_full_schedule()
    return new_schedule
