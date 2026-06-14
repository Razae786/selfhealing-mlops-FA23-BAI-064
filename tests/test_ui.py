import os
import time
import pytest
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

BASE_URL = os.environ.get("BASE_URL", "http://localhost:5000")
SELENIUM_URL = os.environ.get("SELENIUM_URL", "http://localhost:4444/wd/hub")

def test_frontend_sentiment():
    # 1. Wait for Flask app to be fully ready
    for i in range(60):
        try:
            r = requests.get(f"{BASE_URL}/health", timeout=2)
            if r.status_code == 200:
                break
        except:
            pass
        time.sleep(2)
    else:
        pytest.fail("Flask app did not become ready in time")

    # 2. Wait for Selenium to be ready
    for i in range(60):
        try:
            r = requests.get(SELENIUM_URL.replace("/wd/hub", "/wd/hub/status"), timeout=2)
            if r.json().get("value", {}).get("ready"):
                break
        except:
            pass
        time.sleep(2)

    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")

    driver = webdriver.Remote(command_executor=SELENIUM_URL, options=options)
    try:
        driver.get(BASE_URL)
        wait = WebDriverWait(driver, 30)
        
        text_input = wait.until(EC.presence_of_element_located((By.ID, "text-input")))
        submit_btn = driver.find_element(By.ID, "submit-btn")
        result_output = driver.find_element(By.ID, "result-output")

        text_input.send_keys("This product is absolutely excellent and amazing")
        submit_btn.click()

        wait.until(lambda d: d.find_element(By.ID, "result-output").text.strip() != "")
        
        final_text = result_output.text
        assert "POSITIVE" in final_text or "NEGATIVE" in final_text or "Confidence" in final_text or "%" in final_text
    finally:
        driver.quit()
