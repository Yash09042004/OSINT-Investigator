#!/usr/bin/env python3
import sys
import json
import time
import os
from urllib.parse import urljoin, urlparse
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, WebDriverException

def sanitize_filename(url):
    """Create a safe filename from a URL"""
    parsed = urlparse(url)
    path = parsed.path.strip('/').replace('/', '_')
    if not path:
        path = 'homepage'
    # Limit length
    path = path[:50]
    return path

def discover_links(driver, base_url, max_links=4):
    """Discover internal links on the page"""
    discovered = []
    try:
        # Find all links
        links = driver.find_elements(By.TAG_NAME, 'a')
        base_domain = urlparse(base_url).netloc
        
        for link in links:
            try:
                href = link.get_attribute('href')
                if href and href.startswith('http'):
                    link_domain = urlparse(href).netloc
                    # Only internal links
                    if link_domain == base_domain and href != base_url:
                        if href not in discovered:
                            discovered.append(href)
                            if len(discovered) >= max_links:
                                break
            except:
                continue
    except Exception as e:
        print(f"Link discovery error: {e}")
    
    return discovered

def main():
    if len(sys.argv) < 2:
        print("Usage: runner.py <URL>")
        sys.exit(1)

    url = sys.argv[1]
    max_pages = 5  # Maximum pages to screenshot
    output_dir = "/out"
    
    print(f"Starting multi-page analysis of {url}...")

    # Set up Chrome options
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.binary_location = "/usr/bin/chromium"

    # Initialize driver
    service = Service("/usr/bin/chromedriver")
    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.set_page_load_timeout(20)

    all_logs = []
    screenshot_count = 0
    screenshot_manifest = []

    try:
        # Visit main page
        print(f"[1/{max_pages}] Visiting {url}...")
        driver.get(url)
        time.sleep(3)

        # Take screenshot of main page
        screenshot_name = f"screenshot_1_homepage.png"
        driver.save_screenshot(os.path.join(output_dir, screenshot_name))
        screenshot_count += 1
        screenshot_manifest.append({
            "number": 1,
            "url": url,
            "filename": screenshot_name,
            "type": "homepage"
        })
        print(f"  ✓ Screenshot saved: {screenshot_name}")

        # Collect logs from main page
        logs = driver.get_log("browser")
        for log in logs:
            all_logs.append({
                "page": url,
                "level": log["level"],
                "message": log["message"],
                "source": log.get("source", "unknown"),
                "timestamp": log["timestamp"]
            })

        # Discover links
        print("  Discovering internal links...")
        links = discover_links(driver, url, max_links=max_pages - 1)
        print(f"  Found {len(links)} internal links to explore")

        # Visit discovered links
        for idx, link_url in enumerate(links, start=2):
            if screenshot_count >= max_pages:
                break
            
            try:
                print(f"[{idx}/{max_pages}] Visiting {link_url}...")
                driver.get(link_url)
                time.sleep(2)

                # Take screenshot
                page_name = sanitize_filename(link_url)
                screenshot_name = f"screenshot_{idx}_{page_name}.png"
                driver.save_screenshot(os.path.join(output_dir, screenshot_name))
                screenshot_count += 1
                screenshot_manifest.append({
                    "number": idx,
                    "url": link_url,
                    "filename": screenshot_name,
                    "type": "internal_page"
                })
                print(f"  ✓ Screenshot saved: {screenshot_name}")

                # Collect logs
                logs = driver.get_log("browser")
                for log in logs:
                    all_logs.append({
                        "page": link_url,
                        "level": log["level"],
                        "message": log["message"],
                        "source": log.get("source", "unknown"),
                        "timestamp": log["timestamp"]
                    })

            except TimeoutException:
                print(f"  ✗ Page load timed out: {link_url}")
            except WebDriverException as e:
                print(f"  ✗ WebDriver error: {str(e)[:100]}")
            except Exception as e:
                print(f"  ✗ Error visiting {link_url}: {str(e)[:100]}")

        # Save all logs to JSON
        with open(os.path.join(output_dir, "console.json"), "w") as f:
            json.dump(all_logs, f, indent=2)
        print(f"\n✓ Logs saved ({len(all_logs)} entries)")

        # Save screenshot manifest
        with open(os.path.join(output_dir, "screenshots.json"), "w") as f:
            json.dump({
                "total_screenshots": screenshot_count,
                "base_url": url,
                "screenshots": screenshot_manifest
            }, f, indent=2)
        print(f"✓ Screenshot manifest saved")
        
        print(f"\n✅ Analysis complete: {screenshot_count} screenshots captured")

    except TimeoutException:
        print("Main page load timed out")
    except Exception as e:
        print(f"Fatal error: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    main()
