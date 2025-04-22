import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import os

def fetch_remoteok_jobs(keyword):
    url = f"https://remoteok.com/remote-{keyword.replace(' ', '-')}-jobs"
    response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
    soup = BeautifulSoup(response.text, "html.parser")

    jobs = set()
    for div in soup.find_all("tr", class_="job"):
        try:
            title = div.find("h2").get_text(strip=True)
            company = div.find("h3").get_text(strip=True)
            link = "https://remoteok.com" + div["data-href"]
            jobs.add((title, company, link))
        except Exception:
            continue

    return jobs

def fetch_wwr_jobs(keyword):
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--user-agent=Mozilla/5.0")
    options.binary_location = "C:/Program Files (x86)/Google/Chrome/Application/chrome.exe"
    service = Service("C:/tools/chromedriver.exe")
    driver = webdriver.Chrome(service=service, options=options)

    url = f"https://weworkremotely.com/remote-jobs/search?term={keyword.replace(' ', '+')}"

    jobs = set()
    try:
        driver.get(url)
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "section.jobs"))
        )
        soup = BeautifulSoup(driver.page_source, "html.parser")
        job_sections = soup.select("section.jobs li:not(.view-all)")

        for job in job_sections:
            try:
                title = job.select_one("span.title").get_text(strip=True)
                company = job.select_one("span.company").get_text(strip=True)
                link = "https://weworkremotely.com" + job.find("a")["href"]
                jobs.add((title, company, link))
            except Exception:
                print("⚠️ Skipped malformed job entry")
                continue
    except Exception as e:
        print(f"❌ WWR Selenium Error: {e}")
    finally:
        driver.quit()

    return jobs

def main():
    print("💡 Script started")
    keywords = [
        "systems administrator",
        "system administrator",
        "sysadmin",
        "security engineer",
        "cloud security engineer",
        "infosec engineer",
        "information security",
        "IT administrator",
        "network engineer"
    ]
    all_jobs = set()

    for keyword in keywords:
        print(f"🔎 Searching RemoteOK for '{keyword}'...")
        all_jobs.update(fetch_remoteok_jobs(keyword))

        print(f"🔎 Searching WeWorkRemotely for '{keyword}' (via Selenium)...")
        all_jobs.update(fetch_wwr_jobs(keyword))

    print(f"✅ Processing {len(all_jobs)} unique jobs...")

    for title, company, link in all_jobs:
        print(f"""-----------------------------
📌 Title: {title}
🏢 Company: {company}
🔗 URL: {link}
""")

if __name__ == "__main__":
    main()
