import datetime
import os
from pathlib import Path

from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver import Firefox
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
from selenium.webdriver.firefox.options import Options
from dotenv import load_dotenv
from selenium.webdriver.remote.webelement import WebElement


def get_full_schedule(last_changed: datetime.datetime = None) -> dict:
    options = Options()
    load_dotenv()
    is_prod = os.getenv("ENV_NAME") == "Production"
    options.headless = is_prod
    binary = FirefoxBinary("/usr/bin/firefox" + "/firefox-bin" if is_prod else "")
    driver = Firefox(firefox_binary=binary, options=options)

    load_dotenv(os.path.join(Path(__file__).resolve().parent.parent, ".env"))

    plan_website = "vplan.gymnasium-meine.de/mobil095"
    username = os.getenv("PLAN_USERNAME")
    password = os.getenv("PLAN_PASSWORD")

    driver.get(f"https://{username}:{password}@{plan_website}/")
    driver.get(f"https://{plan_website}/auswahlkl.html")

    day_information = get_period_data_for_all_classes(driver, last_changed)

    driver.close()

    return day_information


def check_if_web_element_contains_element_by_css_selector(element: WebElement, css_selector: str) -> bool:
    try:
        element.find_element(By.CSS_SELECTOR, css_selector)
    except NoSuchElementException:
        return False
    else:
        return True


def get_period_data_for_all_classes(driver, last_changed) -> dict:
    total_classes = len(driver.find_elements(By.CSS_SELECTOR, ".mobilauswahlkl"))
    results = {}

    for i in range(total_classes):
        driver.get("https://vplan.gymnasium-meine.de/mobil095/auswahlkl.html")
        # Click on class in list
        driver.find_element(By.XPATH, f"/html/body/div[1]/div/ul/li[{i + 1}]/div/div/a").click()
        # Go back one day
        # driver.find_element(By.XPATH, "/html/body/div[1]/div[1]/div/ul/li[1]/a").click()
        # Go forward one day
        # driver.find_element(By.XPATH, "/html/body/div[1]/div[1]/div/ul/li[3]/a").click()
        # Find all periods
        items = driver.find_elements(By.CSS_SELECTOR, ".liplanzeile")
        # Find all periods where the room changed
        rooms_changed = {}
        for item in items:
            # True if room changed
            rooms_changed[items.index(item)] = \
                check_if_web_element_contains_element_by_css_selector(item, ".mobraum.mobgeaendert")
        # Read date + class from title
        _, date, _, class_, *_ = driver.find_element(By.CSS_SELECTOR, "#planklkopf").text.split()
        if i == 0:
            results = get_daily_information(driver, date, last_changed)
        results[class_] = [item.text for item in items]
        results[str(class_) + "rooms"] = rooms_changed

    return results


def get_daily_information(driver, date, last_changed) -> dict:
    # Convert date to DateTime
    results = {"date": datetime.datetime.strptime(date, "%d.%m.%Y")}
    # Check when the plan was last changed
    _, _, date_l_up, hour_l_up = driver.find_element(By.CSS_SELECTOR, "#planklkopf2").text.split()
    # Convert last changed time to datetime
    results["last_changed"] = datetime.datetime.strptime(date_l_up[:-1] + " " + hour_l_up[:-1], "%d.%m.%Y %H:%M")
    if last_changed and results["last_changed"] == last_changed:
        driver.close()
        return {"changed": False}
    results["changed"] = True
    # Find daily info box
    try:
        results["info"] = driver.find_element(By.CSS_SELECTOR, ".liinfozeile").text
    except NoSuchElementException:
        results["info"] = None

    return results
