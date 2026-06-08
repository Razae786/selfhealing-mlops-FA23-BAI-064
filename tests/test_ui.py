import pytest, os, time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

BASE_URL = os.environ.get("BASE_URL", "http://localhost:5000")

def test_frontend_sentiment():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")

    driver = webdriver.Chrome(options=options)
    try:
        driver.get(BASE_URL)
        wait = WebDriverWait(driver, 20)
        text_input = wait.until(EC.presence_of_element_located((By.ID, "text-input")))
        text_input.send_keys("Spotlessly clean rooms with attentive staff.")
        driver.find_element(By.ID, "submit-btn").click()
        time.sleep(5)
        output_text = driver.find_element(By.ID, "result-output").text
        assert any(word in output_text for word in ["POSITIVE", "NEGATIVE", "Confidence"])
    finally:
        driver.quit()
