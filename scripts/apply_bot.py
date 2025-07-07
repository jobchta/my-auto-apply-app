import os
import time
from supabase import create_client, Client
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


# --- CONFIGURATION ---
SUPABASE_URL = os.environ.get("https://szdmjqgigwhtxpegvhvy.supabase.co")
SUPABASE_KEY = os.environ.get("eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InN6ZG1qcWdpZ3dodHhwZWd2aHZ5Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1MTg0NTc2MywiZXhwIjoyMDY3NDIxNzYzfQ.Hhw70MPW3457ugLWgoULisURIpaDPdA8P2i2e9D5Z6w")


# --- SCRIPT ---

def get_pending_application(supabase: Client):
    """Fetches the oldest pending application from the database."""
    try:
        # This query joins the applications, jobs, and profiles tables
        # to get all the necessary data in one call.
        response = supabase.table('applications').select('''
            id,
            jobs ( url ),
            profiles ( full_name, email, phone, resume_url )
        ''').eq('status', 'pending').order('created_at').limit(1).single().execute()
        return response.data
    except Exception:
        # This is expected when no pending jobs are found.
        return None

def update_application_status(supabase: Client, app_id: int, status: str, details: str = None):
    """Updates the status of an application in the database."""
    try:
        supabase.table('applications').update({
            'status': status,
            'details': details
        }).eq('id', app_id).execute()
        print(f"✅ Updated application {app_id} status to: {status}")
    except Exception as e:
        print(f"❌ Error updating status for app {app_id}: {e}")

def apply_to_greenhouse_job(driver, job_url: str, profile: dict):
    """Fills out a standard Greenhouse.io application form."""
    print(f"➡️ Navigating to Greenhouse job: {job_url}")
    driver.get(job_url)
    wait = WebDriverWait(driver, 15) # Wait up to 15 seconds for elements to appear

    # Fill out the main form fields
    wait.until(EC.presence_of_element_located((By.ID, 'first_name'))).send_keys(profile['full_name'].split(' ')[0])
    wait.until(EC.presence_of_element_located((By.ID, 'last_name'))).send_keys(profile['full_name'].split(' ')[-1])
    wait.until(EC.presence_of_element_located((By.ID, 'email'))).send_keys(profile['email'])
    wait.until(EC.presence_of_element_located((By.ID, 'phone'))).send_keys(profile['phone'])

    # This part is complex. Selenium can't easily handle OS file upload dialogs.
    # The simplest way to attach a resume is to send keys to the <input type="file"> element,
    # but this requires the file to be present on the GitHub Actions runner.
    # For now, we will log this step and skip submission.
    print(f"📄 Resume step: User resume is at URL '{profile['resume_url']}'. Manual upload would be needed.")

    print("✅ Form fields filled.")
    # To prevent actual submissions during testing, the submit button is not clicked.
    # To enable it, you would uncomment the following line:
    # wait.until(EC.element_to_be_clickable((By.ID, 'submit_app'))).click()
    # print("🚀 Application submitted!")
    time.sleep(2) # Pause to allow observation if not in headless mode

def main():
    print("--- Starting Apply Bot ---")
    if not all([SUPABASE_URL, SUPABASE_KEY]):
        print("❌ ERROR: Supabase credentials are not set in environment variables.")
        return

    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    application = get_pending_application(supabase)

    if not application:
        print("--- No pending applications found. Exiting. ---")
        return

    app_id = application['id']
    job_url = application.get('jobs', {}).get('url')
    profile = application.get('profiles')

    if not all([job_url, profile, profile.get('full_name'), profile.get('email')]):
        update_application_status(supabase, app_id, 'failed', 'Incomplete job or profile data.')
        return

    # Set up headless browser for cloud execution
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    
    driver = None
    try:
        service = ChromeService(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        
        # This bot is currently built only for Greenhouse jobs
        if 'boards.greenhouse.io' in job_url:
            apply_to_greenhouse_job(driver, job_url, profile)
            update_application_status(supabase, app_id, 'completed', 'Bot successfully filled form.')
        else:
            update_application_status(supabase, app_id, 'skipped', 'Not a Greenhouse URL.')
    except Exception as e:
        print(f"❌ An unexpected error occurred: {e}")
        update_application_status(supabase, app_id, 'failed', str(e))
    finally:
        if driver:
            driver.quit()
        print("--- Apply Bot Finished ---")

if __name__ == "__main__":
    main()