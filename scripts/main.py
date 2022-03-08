from selenium.webdriver import Firefox, Keys
from selenium.webdriver.common.alert import Alert
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary


def get_full_schedule() -> dict:
    binary = FirefoxBinary("/home/droko/Downloads/firefox-66.0.5/firefox/firefox-bin")
    driver = Firefox(firefox_binary=binary)
    driver.get("https://vplan.gymnasium-meine.de/mobil095/")

    alert = Alert(driver)
    alert.send_keys("schueler" + Keys.TAB + "geheim")
    alert.accept()

    driver.get("https://vplan.gymnasium-meine.de/mobil095/auswahlkl.html")

    # NUMBER_OF_CLASSES = 5
    NUMBER_OF_CLASSES = len(driver.find_elements(By.CSS_SELECTOR, ".mobilauswahlkl"))

    res = {}

    for i in range(NUMBER_OF_CLASSES):
        driver.get("https://vplan.gymnasium-meine.de/mobil095/auswahlkl.html")
        driver.find_element(By.XPATH, f"/html/body/div[1]/div/ul/li[{i + 1}]/div/div/a").click()
        items = driver.find_elements(By.CSS_SELECTOR, ".liplanzeile")
        class_ = driver.find_element(By.CSS_SELECTOR, "#planklkopf").text[-2:]
        res[class_] = [item.text for item in items]

    driver.close()

    return res
