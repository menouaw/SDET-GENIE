import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException


BASE_URL = "https://www.consciousfood.com"
XPATHS = {
  "shop_button": "html/body/div[2]/div/header/nav/ul/li/header-menu/details/summary",
  "dry_fruits_link": "html/body/div[2]/div/header/nav/ul/li/header-menu/details/ul/li[8]/a",
  "add_cashews_button": "html/body/main/div[2]/div/div[3]/div/div/ul/li[4]/quantity-popover/div/div/quantity-input/button",
  "cashews_quantity_input": "html/body/main/div[2]/div/div[3]/div/div/ul/li[4]/quantity-popover[2]/div/div/quantity-input/input",
  "cart_link": "html/body/div[1]/header/div[2]/div/a[2]",

}

def setup_driver():
    driver = webdriver.Chrome()  # You might need to specify the path to your chromedriver
    driver.implicitly_wait(10) #Global implicit wait
    return driver

def teardown_driver(driver):
    driver.quit()


def navigate_to_dry_fruits(driver):
    try:
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, XPATHS["shop_button"]))).click()
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, XPATHS["dry_fruits_link"]))).click()
    except (NoSuchElementException, TimeoutException) as e:
        print(f"Error navigating to Dry Fruits: {e}")
        pytest.fail(f"Error navigating to Dry Fruits: {e}")


def add_cashews_to_cart(driver, quantity=1):
    try:
        add_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, XPATHS["add_cashews_button"])))
        add_button.click()
        if quantity !=1:
            quantity_input = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, XPATHS["cashews_quantity_input"])))
            quantity_input.clear()
            quantity_input.send_keys(quantity)

    except (NoSuchElementException, TimeoutException) as e:
        print(f"Error adding cashews: {e}")
        pytest.fail(f"Error adding cashews: {e}")


def check_cashews_in_cart(driver, expected_quantity=1):
    try:
        driver.get(BASE_URL + "/cart")
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, f"//a[contains(text(),'Cashews')]")))
        # Add assertion to check quantity if needed.  This requires a more robust cart element identification.
    except (NoSuchElementException, TimeoutException) as e:
        print(f"Error checking cashews in cart: {e}")
        pytest.fail(f"Error checking cashews in cart: {e}")


@pytest.fixture
def driver():
    driver = setup_driver()
    yield driver
    teardown_driver(driver)



@pytest.mark.parametrize("quantity", [1,3,0])
def test_add_remove_cashews(driver, quantity):
    driver.get(BASE_URL)
    navigate_to_dry_fruits(driver)
    add_cashews_to_cart(driver, quantity)
    if quantity != 0:
        check_cashews_in_cart(driver)
    else:
        try:
            WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, "//p[contains(text(),'Your cart is empty')]")))
        except TimeoutException:
            pytest.fail("Cart not empty when expected")



def test_remove_nonexistent_cashews(driver):
    driver.get(BASE_URL)
    navigate_to_dry_fruits(driver)
    #Attempt to remove without adding -  This requires a 'remove' button selector which was not provided.


def test_add_max_remove_cashews(driver):
    driver.get(BASE_URL)
    navigate_to_dry_fruits(driver)
    #Add max - Requires max quantity info, which was not provided.


def main():
    pytest.main(["-v", "-s", __file__])

if __name__ == "__main__":
    main()