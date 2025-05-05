def run_scrapping(prod_name, min_p, max_p):
    import os
    import requests
    import time
    from urllib.parse import urljoin
    from selenium import webdriver
    from selenium.webdriver.firefox.service import Service
    from selenium.webdriver.firefox.options import Options
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.common.exceptions import TimeoutException

    def check_url_exists(url):
        try:
            response = requests.get(url, stream=True, timeout=5)
            return response.status_code == 200
        except:
            return False

    def get_image_url(img_elem, browser):
        browser.execute_script("arguments[0].scrollIntoView(true);", img_elem)
        time.sleep(0.3)
        attributes = ['src', 'data-src', 'data-image-src']
        for attr in attributes:
            image_url = img_elem.get_attribute(attr)
            if image_url and image_url.strip():
                return urljoin("https:", image_url) if image_url.startswith("//") else image_url
        return None

    geckodriver_path = r'C:\geckodriver\geckodriver.exe'
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:137.0) Gecko/20100101 Firefox/137.0"

    service = Service(executable_path=geckodriver_path)
    options = Options()
    options.set_preference('general.useragent.override', user_agent)

    browser = webdriver.Firefox(service=service, options=options)
    browser.get('https://www.daraz.com.np/#?')

    search_box = browser.find_element(By.NAME, 'q')
    search_box.send_keys(prod_name)

    search_button = browser.find_element(By.XPATH, '/html/body/div[1]/div/div/div/div[2]/div/div[2]/div/form/div/div[2]/a')
    search_button.click()

    time.sleep(2)

    try:
        WebDriverWait(browser, 5).until(
            EC.any_of(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'div[data-qa-locator="product-item"]')),
                EC.presence_of_element_located((By.XPATH, '//div[contains(text(), "Sorry, we couldn’t find any results for")]'))
            )
        )

        try:
            browser.find_element(By.XPATH, '//div[contains(text(), "Sorry, we couldn’t find any results for")]')
            browser.quit()
            return "No products found"
        except:
            pass
    except TimeoutException:
        browser.quit()
        return "gibberish_search"

    WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'input[placeholder="Min"]'))).send_keys(min_p)
    WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'input[placeholder="Max"]'))).send_keys(max_p)

    price_button = browser.find_element(By.XPATH, '/html/body/div[4]/div/div[2]/div[1]/div/div[2]/div/div[5]/div[2]/div/button')
    price_button.click()

    time.sleep(2)
    results = []

    while True:
        time.sleep(3)
        products = browser.find_elements(By.CSS_SELECTOR, 'div[data-qa-locator="product-item"]')

        for product in products:
            try:
                title_elem = product.find_element(By.CSS_SELECTOR, 'div.RfADt > a')
                title = title_elem.get_attribute('title')
                link = title_elem.get_attribute('href')
                price = product.find_element(By.CSS_SELECTOR, 'div.aBrP0 > span.ooOxS').text
                
                img_elem = product.find_element(By.CSS_SELECTOR, 'img')
                image = get_image_url(img_elem, browser)

                if image and not image.startswith('https'):
                    image = 'https:' + image

                if image and image.endswith('.avif'):
                    jpg_image = image.replace('.avif', '.jpg')
                    png_image = image.replace('.avif', '.png')

                    if check_url_exists(jpg_image):
                        image = jpg_image
                    elif check_url_exists(png_image):
                        image = png_image
                    else:
                        image = "https://placehold.co/150x150?text=Image+Unavailable"

                results.append({'image': image, 'title': title, 'price': price, 'link': link})

            except Exception as e:
                print(f"Error processing product: {e}")
                continue

        try:
            next_button = browser.find_element(By.XPATH, '//li[@title="Next Page"]//button')
            if "disabled" in next_button.get_attribute("class") or not next_button.is_enabled():
                break
            next_button.click()
        except:
            break

    browser.quit()

    if not results:
        return "No products found"

    return results
