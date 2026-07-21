from playwright.sync_api import sync_playwright
import time
with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto("http://localhost:8501/compare")
    time.sleep(2)
    page.locator('input[type="file"]').nth(0).set_input_files(r"c:\Users\Joseph\Desktop\projects\CGPA_Calculator\p1.json")
    page.locator('input[type="file"]').nth(1).set_input_files(r"c:\Users\Joseph\Desktop\projects\CGPA_Calculator\p2.json")
    time.sleep(3)
    print("--- PAGE TEXT ---")
    print(page.inner_text("body"))
    browser.close()
