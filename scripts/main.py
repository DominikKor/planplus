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
        driver.find_element(By.XPATH, f"/html/body/div[1]/div/ul/li[{i + 1}]/div/div/a").click()
        items = driver.find_elements(By.CSS_SELECTOR, ".liplanzeile")
        class_ = driver.find_element(By.CSS_SELECTOR, "#planklkopf").text[-3:].strip()
        res[class_] = [item.text for item in items]

    driver.close()

    return res


def get_plan(refresh=False):
    if not refresh:
        data = {"5A": ["1. PH Zl APH2", "2. PH Zl APH2", "3. --- \nEN Frau Greunke fällt aus", "4. --- \nEN Frau Greunke fällt aus", "6. DE He A119", "7. DE He A119"], "5B": ["1. MU Bet BAula", "2. MU Bet BAula", "3. --- \nGE Herr Matthes fällt aus", "4. --- \nDE Frau Hackel fällt aus", "6. SP Pc Hall1", "7. SP Pc Hall1"], "5C": ["1. PH Ni A121", "2. PÄ Sc A121", "3. --- \nGE Frau Arenz fällt aus", "4. --- \nGE Frau Arenz fällt aus", "6. EN Ch A121", "7. DE Bs A121"], "5D": ["1. BI Fr ABI1", "2. BI Fr ABI1", "3. --- \nDE Frau Teufel fällt aus", "4. --- \nDE Frau Teufel fällt aus", "6. RE Du A126", "7. EN Pr A126"], "6A": ["1. MA Az A103", "2. MA Az A103", "3. EN Tf A103\nfür EN Frau Griesing", "4. EN Tf A103\nfür EN Frau Griesing", "6. SP Aw Hall2", "7. SP Aw Hall2", "8. CH Tr CCH1", "9. CH Tr CCH1"], "6B": ["1. BI Fi ABI2", "2. MA Grö A105", "3. DE St A105\nfür DE Frau Nachtwey", "4. EN Bet A105", "6. MU Bet BAula", "7. MU Bet BAula", "8. GE Ma A105"], "6C": ["1. EK Pr A106", "2. EN Kn A106", "3. DE Ha A106", "4. GE Lg A106", "6. RE Wi A106", "7. MA Pf A106", "8. MA Pf A106"], "6D": ["1. GE Ma A112", "2. GE Ma A112", "3. MA Bg A112", "4. MA Bg A112", "6. EN Lm A112", "7. PÄ RC A112", "8. PH Km APH1", "9. PH Km APH1"], "7A": ["1. EN Gg A101", "2. EN Gg A101", "3. DE Sr A101", "4. MA Sr A101", "5. FR7Sd Eb A113", "5. SN7Go Go A128", "5. SN7Ru Ru A204", "5. LA7Gg Gg A205", "7. GE Wi A101"], "7B": ["1. MA Grö A128", "2. DE He A128", "3. DE He A128", "4. MU Ma BMU1", "5. FR7Sd Eb A113", "5. SN7Go Go A128", "5. SN7Ru Ru A204", "5. LA7Gg Gg A205", "7. EN Fz A128"], "7C": ["1. MA Km A204", "2. MA Km A204", "3. DE Pc A204", "4. DE Pc A204", "5. FR7Sd Eb A113", "5. SN7Go Go A128", "5. SN7Ru Ru A204", "5. LA7Gg Gg A205", "7. GE Tf A204"], "7D": ["1. EN Go A205", "2. EN Go A205", "3. GE Ma A205\nfür SP Frau Tänzer", "4. DE He A205\nfür SP Frau Tänzer", "5. FR7Sd Eb A113", "5. SN7Go Go A128", "5. SN7Ru Ru A204", "5. LA7Gg Gg A205", "7. GE Ma A205"], "8A": ["1. --- \nKU Frau Korte fällt aus", "2. --- \nKU Frau Korte fällt aus", "3. SN8Bo Bo A211", "3. LA8Lü Lü A202", "3. FR8Gr Gr A201", "3. LA8Kg Kg B003", "3. SN8Go Kn A210\nfür SN Frau Gomez", "4. SN8Bo Bo A211", "4. LA8Lü Lü A202", "4. FR8Gr Gr A201", "4. LA8Kg Kg B003", "4. SN8Go Fr A210\nfür SN Frau Gomez", "5. EN Fz A210", "7. MA Zl A210"], "8B": ["1. DE Tf A211", "2. DE Tf A211", "3. SN8Bo Bo A211", "3. LA8Lü Lü A202", "3. FR8Gr Gr A201", "3. LA8Kg Kg B003", "3. SN8Go Kn A210\nfür SN Frau Gomez", "4. SN8Bo Bo A211", "4. LA8Lü Lü A202", "4. FR8Gr Gr A201", "4. LA8Kg Kg B003", "4. SN8Go Fr A210\nfür SN Frau Gomez", "5. RE Wi A211", "7. EN Lm A211"], "8C": ["1. --- \nCH Frau Dr. Kühn fällt aus", "2. EN Fz A201", "3. SN8Bo Bo A211", "3. LA8Lü Lü A202", "3. FR8Gr Gr A201", "3. LA8Kg Kg B003", "3. SN8Go Kn A210\nfür SN Frau Gomez", "4. SN8Bo Bo A211", "4. LA8Lü Lü A202", "4. FR8Gr Gr A201", "4. LA8Kg Kg B003", "4. SN8Go Fr A210\nfür SN Frau Gomez", "5. VF Grö A201\nstatt Fr (11.03.) St.6; DE Frau Tänzer fällt aus", "7. MA Grö A201"], "8D": ["1. SP Bo Hall2", "2. SP Bo Hall2", "3. SN8Bo Bo A211", "3. LA8Lü Lü A202", "3. FR8Gr Gr A201", "3. LA8Kg Kg B003", "3. SN8Go Kn A210\nfür SN Frau Gomez", "4. SN8Bo Bo A211", "4. LA8Lü Lü A202", "4. FR8Gr Gr A201", "4. LA8Kg Kg B003", "4. SN8Go Fr A210\nfür SN Frau Gomez", "5. EN Pr A202", "7. PH Km APH1"], "9A": ["1. --- \nSP Herr Andrew fällt aus", "2. --- \nSP Herr Andrew fällt aus", "3. PH Zl APH1", "4. PH Zl APH1", "5. EN Zi C001", "7. MA Bn C001"], "9B": ["1. EN Ge C002", "2. EN Ge C002", "3. DE Zi C002", "4. DE Zi C002", "5. KU Bs BKU2\nfür KU Frau Korte", "7. KU Ke BKU2"], "9C": ["1. DE Gr C003", "2. EN Zi C003", "3. MA Km C003\nfür BI Frau Fiedler", "4. BI Ha C003\nfür BI Frau Fiedler", "5. DE Gr C003", "7. RE Du C003"], "9D": ["1. DE Ha C004", "2. DE Ha C004", "3. BI Lg C004\nfür BI Frau Dr. Rosin", "4. BI Wi C004\nfür BI Frau Dr. Rosin", "5. EN Bet C004", "7. MA An C004", "8. SP Bo Hall1", "9. SP Bo Hall1"], "0A": ["1. DE Ht C005", "2. EN Lg C005", "3. PH Wm APH2\nstatt Mo (14.03.) St.1; SP Herr Andrew fällt aus", "4. PH Wm APH2\nstatt Mo (14.03.) St.2; SP Herr Andrew fällt aus", "6. FR10Eb Eb C005", "6. SN10Kg Kg C006", "6. SN10Ru Ru C101", "6. LA10St St C008", "7. FR10Eb Eb C005", "7. SN10Kg Kg C006", "7. SN10Ru Ru C101", "7. LA10St St C008", "8. EKbili10 Pr C004"], "0B": ["1. --- \nCH Herr Tröndle fällt aus", "2. CH Tr CCH2", "3. RE Zi C005\nfür RE Frau Duda", "4. RE Zi C005\nfür RE Frau Duda", "6. FR10Eb Eb C005", "6. SN10Kg Kg C006", "6. SN10Ru Ru C101", "6. LA10St St C008", "7. FR10Eb Eb C005", "7. SN10Kg Kg C006", "7. SN10Ru Ru C101", "7. LA10St St C008", "8. EKbili10 Pr C004"], "0C": ["1. --- \nDE Herr Gaus gehalten am Fr (25.02.) St.4", "2. DE Ga C008", "3. CH Kü CCH1", "4. CH Kü CCH1", "6. FR10Eb Eb C005", "6. SN10Kg Kg C006", "6. SN10Ru Ru C101", "6. LA10St St C008", "7. FR10Eb Eb C005", "7. SN10Kg Kg C006", "7. SN10Ru Ru C101", "7. LA10St St C008", "8. EKbili10 Pr C004"], "1A": ["1. --- \nma11A Frau Akeston fällt aus", "2. --- \nma11A Frau Akeston fällt aus", "3. en11A Ch C101", "4. en11A Ch C101", "6. KU11Dr Dr BKU1", "6. BI11Fe Fr ABI1", "7. KU11Dr Dr BKU1", "7. BI11Fe Fr ABI1", "8. re11A Wi C101", "9. re11A Wi C101"], "1B": ["3. ma11B Tr C102", "4. ma11B Vk C102\nfür MA Herr Tröndle", "6. KU11Dr Dr BKU1", "6. BI11Fe Fr ABI1", "7. KU11Dr Dr BKU1", "7. BI11Fe Fr ABI1", "8. de11B Ht C102", "9. de11B Ht C102"], "1C": ["1. ge11C Wi C103", "2. ge11C Wi C103", "3. ma11C Vk C103", "4. ma11C Vk C103", "6. KU11Dr Dr BKU1", "6. BI11Fe Fr ABI1", "7. KU11Dr Dr BKU1", "7. BI11Fe Fr ABI1", "8. po11C Ga C103", "9. po11C Ga C103"], "Q1": ["1. EK12 Bs A125", "1. IF12 Pf BIF2", "1. LA92 St A104", "1. MA12 Sr C105", "1. --- \nDE12 Frau Nachtwey fällt aus", "1. SN12 Kg A210", "1. --- \nBI12 Frau Dr. Rosin fällt aus", "2. EK12 Bs A125", "2. IF12 Pf BIF2", "2. LA92 St A104", "2. MA12 Sr C105", "2. --- \nDE12 Frau Nachtwey fällt aus", "2. SN12 Kg A210", "2. --- \nBI12 Frau Dr. Rosin fällt aus", "3. EK11 Bn A104", "3. EN11 Pr A113", "3. KU11 Fz BKU1", "3. MA11 Grö A122", "3. --- \nPO11 Frau Eisenblätter fällt aus", "3. --- \nCH11 Frau Akeston fällt aus", "4. EK11 Bn A104", "4. EN11 Pr A113", "4. KU11 Fz BKU1", "4. MA11 Grö A122", "4. --- \nPO11 Frau Eisenblätter fällt aus", "4. --- \nCH11 Frau Akeston fällt aus", "6. DE13 Gr A122", "6. EN13 Kn B003", "6. PH13 Beg APH2", "6. GE13 Ht A103", "6. --- \nBI13 Frau Dr. Kühn fällt aus", "7. DE13 Gr A122", "7. EN13 Kn B003", "7. PH13 Beg APH2", "7. GE13 Ht A103", "7. --- \nBI13 Frau Dr. Kühn fällt aus", "8. de18 Tf A212", "8. fr18 Sd C001", "8. ma181 Grö A112", "8. ma182 Beg A113", "8. ph18 Wm APH2", "9. de18 Tf A212", "9. fr18 Sd C001", "9. ma181 Grö A112", "9. ma182 Beg A113", "9. ph18 Wm APH2"], "Q2": ["1. DE02 Pc A215", "1. EN02 Ch B003", "1. KU02 Dr BKU1", "1. LA92 St B110", "1. MA02 Bg C007", "1. PH02 Wm APH1", "1. GE02 Lü A119", "1. CH Tr A213\nVORABI Chemie", "1. IF Lä A212\nVORABI Informatik", "2. DE02 Pc A215", "2. EN02 Ch B003", "2. KU02 Dr BKU1", "2. LA92 St B110", "2. MA02 Bg C007", "2. PH02 Wm APH1", "2. GE02 Lü A119", "2. CH No A213\nVORABI Chemie", "2. IF Lä A212\nVORABI Informatik", "3. BI01 No ABI1", "3. EK01 Bs A215", "3. GE01 Ht C104", "3. MA01 Pf B109", "3. PO01 Ga B110", "3. DE01 Lo A119", "3. CH Fr A213\nVORABI Chemie", "3. IF Dr A212\nVORABI Informatik", "4. BI01 No ABI1", "4. EK01 Bs A215", "4. GE01 Ht C104", "4. MA01 Pf B109", "4. PO01 Ga B110", "4. DE01 Lo A119", "4. CH Tr A213\nVORABI Chemie", "4. IF Lä A212\nVORABI Informatik", "5. CH Bn A213\nVORABI Chemie", "5. IF Kn A212\nVORABI Informatik", "6. DE03 Sr C104", "6. EK03 Wa C105", "6. EN03 Zi B109", "6. IF03 Lä BIF1", "6. RE03 Ni A215", "6. SN03 Bo A104", "6. --- \nCH03 Herr Tröndle fällt aus", "6. CH Tr A213\nVORABI Chemie", "6. IF Lä A212\nVORABI Informatik", "7. CH03 Tr CCH1", "7. DE03 Sr C104", "7. EK03 Wa C105", "7. EN03 Zi B109", "7. IF03 Lä BIF1", "7. RE03 Ni A215", "7. SN03 Bo A104", "8. de08 He A215", "8. en08 Lm A122", "8. fr98 Eb A125", "8. ma08 Li A101", "8. sn08 Ru C105", "9. de08 He A215", "9. en08 Lm A122", "9. fr98 Eb A125", "9. ma08 Li A101", "9. sn08 Ru C105"], "AG": []}
        return data
    new_schedule = get_full_schedule()
    return new_schedule
