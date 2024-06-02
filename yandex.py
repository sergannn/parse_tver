from playwright.sync_api import sync_playwright
import csv
import time

def run(playwright):
    browser = playwright.chromium.launch(headless=False)  # Set headless=False to see the browser UI
    page = browser.new_page()

    def navigate_and_scroll():
        page.goto("https://yandex.ru/maps/1/a/search/Тверь,Пяторочка/")
        previous_content = []
        csv_file_path = 'output.csv'
         # Check if the CSV file exists and read existing data
        try:
            with open(csv_file_path, mode='r', encoding='utf-8') as file:
                reader = csv.reader(file)
                previous_content = [row for row in reader]
        except FileNotFoundError:
            pass  # Create a new file if it doesn't exist

        while True:  # Continuous scrolling
            page.evaluate("""() => {
                const container = document.querySelector('.scroll__container');
                if (container) {
                    container.scrollTop += 10;
                }
            }""")
            time.sleep(0.2)  # Adjust sleep duration as needed
            
            # Get the current content of elements
            current_content = [el for el in page.query_selector_all('li.search-snippet-view')]
            for li in current_content:
                coords = li.query_selector(".search-snippet-view__body").get_attribute('data-coordinates')
                address = li.query_selector(".search-business-snippet-view__address").inner_text()
                rating = li.query_selector(".business-rating-badge-view__rating-text").inner_text()
                print(coords)
                print(address)
                print(rating)
                if [coords, address, rating] not in previous_content:
                # Append new data to the CSV file
                    with open(csv_file_path, mode='a', encoding='utf-8', newline='') as file:
                        writer = csv.writer(file)
                        writer.writerow([coords, address, rating])
                
                # Update previous_content to include the new data
                    previous_content.append([coords, address, rating])
         # Optionally, sort the CSV file after appending new entries
            with open(csv_file_path, mode='r+', encoding='utf-8', newline='') as file:
                lines = file.readlines()
                lines.sort(key=lambda x: tuple(x.strip().split(',')))  # Sort based on coordinates, address, and rating
                file.seek(0)
                file.writelines(lines)
                file.truncate()

    navigate_and_scroll()

    browser.close()

with sync_playwright() as p:
    run(p)
