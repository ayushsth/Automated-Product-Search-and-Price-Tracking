def run_comparison_script(prod_link, desirable_price, phone_no,first_name,last_name):
    import os
    import time
    import requests
    from selenium import webdriver
    from selenium.webdriver.firefox.service import Service
    from selenium.webdriver.firefox.options import Options
    from selenium.webdriver.common.by import By
    from flask import redirect,url_for
    from flask import flash

    import twilio
    from twilio.rest import Client

    twilio_sid="TWILIO SID"

    twilio_auth_token="TWILIO AUTH TOKEN"

    geckodriver_path = r'C:\geckodriver\geckodriver.exe'
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:137.0) Gecko/20100101 Firefox/137.0"

    service=Service(executable_path=geckodriver_path)
    options=Options()
    options.set_preference('general.useragent.override',user_agent)
    options.headless = True

    browser=webdriver.Firefox(service=service,options=options)
    browser.get(prod_link)

    try:
        prod_price=browser.find_element(By.CSS_SELECTOR,'span.pdp-price_type_normal')
        price_text = prod_price.text

        cleaned_price = price_text.replace("Rs. ", "").replace(",", "")

        price= int(cleaned_price)

        print(price)


        if price < desirable_price:
                client = Client(twilio_sid, twilio_auth_token)
                message = client.messages.create(
                    body=f"Dear {first_name} {last_name}.The price of the product is Rs. {price}. It's under your desirable price of Rs. {desirable_price}.",
                    from_="+1 YOUR TWILIO PHONE NO",
                    to=f"+977 {phone_no}"
                )

                return redirect(url_for('track'))
    except Exception as e:
        print(f"Error occurred: {e}")

    finally:
        browser.quit()
    
    return redirect(url_for('track'))
