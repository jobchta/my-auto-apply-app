from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
import time

print("--- Starting Headless Selenium Test ---")

try:
    # Set up Chrome options for headless mode
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox") # Required for running in a GitHub Action
    options.add_argument("--disable-dev-shm-usage") # Overcomes limited resource problems
    options.add_argument("--start-maximized")
    
    # Initialize the driver
    service = ChromeService(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    
    print("✅ Headless browser opened successfully in the cloud.")
    
    # Go to Google
    driver.get("https://www.google.com")
    print(f"✅ Navigated to: {driver.title}")
    
except Exception as e:
    print(f"❌ An error occurred: {e}")
    
finally:
    # Close the browser
    if 'driver' in locals() and driver is not None:
        driver.quit()
        print("✅ Headless browser closed successfully.")
        
print("--- Headless Selenium Test Finished ---")