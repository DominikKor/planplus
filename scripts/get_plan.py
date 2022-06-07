import datetime
import logging
import os
from pathlib import Path

from dotenv import load_dotenv
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By


def get_full_schedule(last_changed: datetime.datetime = None) -> dict:
    load_dotenv(os.path.join(Path(__file__).resolve().parent.parent, ".env"))
    logger = logging.getLogger("scripts")

    plan_website = "vplan.gymnasium-meine.de/mobil095"
    username = os.getenv("PLAN_USERNAME")
    password = os.getenv("PLAN_PASSWORD")
    is_prod = os.getenv("ENV_NAME") == "Production"

    logger.debug(f"is_prod: {is_prod}")

    options = Options()

    if is_prod:
        options.binary_location = "/usr/bin/chromium-browser"
        options.add_argument("--no-sandbox")
        options.add_argument("--remote-debugging-port=9222")
        options.add_argument("--disable-dev-shm-using")
        options.add_argument("--headless")

    driver = Chrome(options=options)

    driver.get(f"https://{username}:{password}@{plan_website}/")
    driver.get(f"https://{plan_website}/auswahlkl.html")

    day_information = get_period_data_for_all_classes(driver, last_changed)

    driver.quit()

    return day_information


def check_if_web_element_contains_element_by_css_selector(element, css_selector: str) -> bool:
    try:
        element.find_element(By.CSS_SELECTOR, css_selector)
    except NoSuchElementException:
        return False
    else:
        return True


def get_period_data_for_all_classes(driver, last_changed, times_back=0, times_forward=0) -> dict:
    total_classes = len(driver.find_elements(By.CSS_SELECTOR, ".mobilauswahlkl"))
    results = {}

    for i in range(total_classes):
        # Click on class in list
        driver.find_element(By.XPATH, f"/html/body/div[1]/div/ul/li[{i + 1}]/div/div/a").click()

        for j in range(times_back):
            # Go back one day
            driver.find_element(By.XPATH, "/html/body/div[1]/div[1]/div/ul/li[1]/a").click()

        for j in range(times_forward):
            # Go forward one day
            driver.find_element(By.XPATH, "/html/body/div[1]/div[1]/div/ul/li[3]/a").click()

        # Find all periods
        items = driver.find_elements(By.CSS_SELECTOR, ".liplanzeile")

        # Find all periods where the room changed
        rooms_changed = get_changed_data_by_red_color(items, ".mobraum.mobgeaendert")

        # Find all periods where the subject changed
        subjects_changed = get_changed_data_by_red_color(items, ".mobfach.mobgeaendert")

        # Read date + class from title
        _, date, _, class_, *_ = driver.find_element(By.CSS_SELECTOR, "#planklkopf").text.split()
        if i == 0:
            results = get_daily_information(driver, date, last_changed)
            if not results["changed"]:
                return results
        results[class_] = [item.text for item in items]
        results[str(class_) + "rooms"] = rooms_changed
        results[str(class_) + "subjects"] = subjects_changed

        # Move back to class list
        driver.back()

    return results


def get_changed_data_by_red_color(items, css_selector: str) -> dict:
    results = {}
    for item in items:
        # True if data changed
        results[items.index(item)] = check_if_web_element_contains_element_by_css_selector(item, css_selector)

    return results


def get_daily_information(driver, date, last_changed) -> dict:
    logger = logging.getLogger("scripts")
    # Convert date to DateTime
    results = {"date": datetime.datetime.strptime(date, "%d.%m.%Y")}
    # Check when the plan was last changed
    _, _, date_l_up, hour_l_up = driver.find_element(By.CSS_SELECTOR, "#planklkopf2").text.split()
    # Convert last changed time to datetime
    results["last_changed"] = datetime.datetime.strptime(date_l_up[:-1] + " " + hour_l_up[:-1], "%d.%m.%Y %H:%M")
    if last_changed and results["last_changed"] == last_changed:
        logger.info("Plan data didn't change")
        return {"changed": False}
    results["changed"] = True
    # Find daily info box
    try:
        results["info"] = driver.find_element(By.CSS_SELECTOR, ".liinfozeile").text
    except NoSuchElementException:
        results["info"] = None

    return results
