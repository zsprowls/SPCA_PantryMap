from playwright.sync_api import sync_playwright
import pandas as pd
import time
import json

def scrape_pantry_data():
    """Scrape pantry data from FeedMore WNY website."""
    with sync_playwright() as p:
        # Launch the browser
        browser = p.chromium.launch(headless=False)  # Set to True for production
        page = browser.new_page()
        
        try:
            print("Navigating to the page...")
            page.goto("https://www.feedmorewny.org/programs-services/find-food/pantry-locator/")
            time.sleep(3)  # Wait for page to load
            print("Please manually set the filters and click the search button in the browser window.")
            input("When you see the results, press Enter here to continue scraping...")
            print("Continuing with scraping...")
            
            # Wait for the page to be fully loaded
            page.wait_for_load_state("networkidle")
            time.sleep(5)  # Additional wait to ensure results are displayed
            
            pantries = []
            page_num = 1
            
            while True:
                print(f"Processing page {page_num}...")
                page.wait_for_selector(".results_entry", state="visible", timeout=60000)  # Updated selector
                pantry_elements = page.query_selector_all(".results_entry")
                print(f"Found {len(pantry_elements)} pantries on page {page_num}")
                
                for pantry in pantry_elements:
                    try:
                        # Get name from the left column
                        name = pantry.query_selector(".location_name").inner_text().strip()
                        
                        # Get address components from the center column
                        street = pantry.query_selector(".slp_result_street").inner_text().strip()
                        city_state_zip = pantry.query_selector(".slp_result_citystatezip").inner_text().strip()
                        address = f"{street}, {city_state_zip}"
                        
                        # Get phone number
                        try:
                            phone = pantry.query_selector(".slp_result_phone").inner_text().strip()
                        except:
                            phone = "N/A"
                            
                        # Get hours
                        try:
                            hours = pantry.query_selector(".slp_result_hours").inner_text().strip()
                        except:
                            hours = "N/A"
                            
                        pantries.append({
                            "name": name,
                            "address": address,
                            "phone": phone,
                            "hours": hours
                        })
                    except Exception as e:
                        print(f"Error processing pantry: {e}")
                        continue
                        
                try:
                    next_button = page.query_selector("button.next-page")
                    if not next_button or not next_button.is_enabled():
                        print("No more pages to process")
                        break
                    print("Clicking next page...")
                    next_button.click()
                    page.wait_for_load_state("networkidle")
                    time.sleep(1)
                    page_num += 1
                except:
                    print("No next page button found")
                    break
                    
            df = pd.DataFrame(pantries)
            df.to_csv("Map Data/pantry_locations.csv", index=False)
            with open("Map Data/pantry_locations.json", "w") as f:
                json.dump(pantries, f, indent=2)
            print(f"Successfully scraped {len(pantries)} pantries")
        except Exception as e:
            print(f"An error occurred: {e}")
        finally:
            browser.close()

if __name__ == "__main__":
    scrape_pantry_data() 