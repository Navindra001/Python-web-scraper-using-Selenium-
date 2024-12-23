from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time
import csv
import os
# Set up Selenium WebDriver
def setup_driver():
    options = webdriver.ChromeOptions()
    options.add_argument('--start-maximized')
    options.add_argument('--disable-infobars')
    options.add_argument('--disable-notifications')
    driver = webdriver.Chrome(options=options)
    return driver

# Login function
def amazon_login(driver, email, password):
    driver.get("https://www.amazon.in")
    try:
        # Click on Sign-In
        sign_in_button = driver.find_element(By.ID, "nav-link-accountList")
        sign_in_button.click()
        
        # Enter Email
        email_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "ap_email"))
        )
        email_field.send_keys(email)
        email_field.send_keys(Keys.RETURN)

        # Enter Password
        password_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "ap_password"))
        )
        password_field.send_keys(password)
        password_field.send_keys(Keys.RETURN)

    except TimeoutException:
        print("Login failed. Check your credentials and internet connection.")
        driver.quit()
        exit()

# Scrape category data
def scrape_category(driver, category_url):
    driver.get(category_url)
    time.sleep(5)  # Wait for the page to load

    product_data = []

    for page in range(1, 4):  # Modify the range to scrape more pages if needed
        try:
            products = driver.find_elements(By.CSS_SELECTOR, ".zg-item-immersion")

            for product in products:
                try:
                    # Extract product details
                    name = product.find_element(By.CSS_SELECTOR, ".p13n-sc-truncated").text
                    price = product.find_element(By.CSS_SELECTOR, ".p13n-sc-price").text
                    rating = product.find_element(By.CSS_SELECTOR, ".a-icon-alt").text
                    image = product.find_element(By.CSS_SELECTOR, "img").get_attribute("src")

                    discount = None
                    try:
                        discount = product.find_element(By.CSS_SELECTOR, ".p13n-sc-discount").text
                    except NoSuchElementException:
                        pass

                    product_data.append({
                        "Name": name,
                        "Price": price,
                        "Rating": rating,
                        "Discount": discount,
                        "Image": image
                    })

                except NoSuchElementException:
                    continue

            # Navigate to the next page
            next_button = driver.find_element(By.CSS_SELECTOR, ".a-last a")
            next_button.click()
            time.sleep(10)

        except NoSuchElementException:
            print("End of pages for this category.")
            break

    return product_data

# Save data to CSV
def save_to_csv(data, filename):
    keys = data[0].keys() if data else []
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        writer.writerows(data)

# Main execution
def main():
    # Replace these with your Amazon credentials
    email = "your-email@example.com"
    password = "your-password"

    # Sample category URLs (you can add/remove URLs as needed)
    category_urls = [
        "https://www.amazon.in/gp/bestsellers/kitchen/ref=zg_bs_nav_kitchen_0",
        "https://www.amazon.in/gp/bestsellers/shoes/ref=zg_bs_nav_shoes_0",
        "https://www.amazon.in/gp/bestsellers/computers/ref=zg_bs_nav_computers_0",
        "https://www.amazon.in/gp/bestsellers/electronics/ref=zg_bs_nav_electronics_0",
    ]

    driver = setup_driver()
    amazon_login(driver, email, password)

    all_data = []

    for category_url in category_urls:
        print(f"Scraping category: {category_url}")
        category_data = scrape_category(driver, category_url)
        all_data.extend(category_data)

    driver.quit()

    # Save all data to CSV
    output_file = "amazon_best_sellers.csv"
    save_to_csv(all_data, output_file)
    print(f"Data saved to {output_file}")

if __name__ == "__main__":
    main()