import time

from fake_useragent import UserAgent
from selenium.webdriver import Keys
from seleniumbase import Driver

from tgbot.config import get_db
from utils import LocalStorage


def get_random_chrome_user_agent():
    user_agent = UserAgent(browsers='chrome', os='windows', platforms='pc')
    return user_agent.random


def wait_for_element(driver, selector, timeout=5, retries=3, refresh=False):
    for i in range(retries):
        try:
            driver.wait_for_element(selector, timeout=timeout)
            print(f"Элемент {selector} найден на попытке {i + 1}")
            return driver.find_element(selector)
        except Exception as e:
            print(f"Попытка {i + 1}/{retries}: элемент {selector} не найден, повторяю...")
            if refresh:
                refresh_page(driver)
    print("Элемент не найден после всех попыток.")
    return None


def refresh_page(driver, sleep=1):
    driver.refresh()
    time.sleep(sleep)


def click_ok_and_confirm(driver, ok_selector, confirm_selector, code):
    if click_element(driver, ok_selector, element_name="OK"):
        if handle_invalid_code(driver):
            new_code = db.code()
            fill_text_field(driver, "input[placeholder='Please enter a redeem code']", new_code)
            return click_ok_and_confirm(driver, ok_selector, confirm_selector, new_code)

        if click_element(driver, confirm_selector, element_name="Confirm"):
            return True
        print("Кнопка Confirm не найдена, обновляем страницу.")
        refresh_page(driver)
        return reattempt_click(driver, ok_selector, confirm_selector, code)


def reattempt_click(driver, ok_selector, confirm_selector, code):
    fill_text_field(driver, "input[placeholder='Please enter a redeem code']", code)
    print("Код введен повторно.")

    if click_element(driver, ok_selector, element_name="OK после обновления"):
        return click_element(driver, confirm_selector, element_name="Confirm после повторного OK")
    return False


def click_element(driver, selector, element_name=""):
    try:
        driver.click(selector)
        print(f"Клик на элемент '{element_name}' выполнен.")
        return True
    except Exception as e:
        print(f"Элемент '{element_name}' не найден или не кликабелен.")
        return False


def fill_text_field(driver, selector, text, enter=False):
    field = wait_for_element(driver, selector, 1)
    if field:
        driver.type(selector, text)
        if enter:
            driver.send_keys(selector, Keys.ENTER)
            print("Клавиша Enter нажата.")
        return True
    else:
        print("Поле для ввода не найдено.")
        return False


def authorization(driver, account_and_password, db, ids, chang_id=False):
    if click_element(driver, "//div[text()='Sign In Midasbuy Account']", element_name="Sign In Midasbuy Account"):
        driver.switch_to.frame('login-iframe')
        if not fill_text_field(driver, "input[placeholder='Enter email to sign in or sign up']",
                               account_and_password[0]):
            return False
        click_element(driver, ".btn.comfirm-btn", element_name="Submit email")
        fill_text_field(driver, "input[placeholder='Enter password']",
                        account_and_password[1], enter=True)
        db.done_acc(ids, account_and_password)
        if chang_id:
            time.sleep(5)
            refresh_page(driver)
            click_element(driver, "//span/i[contains(@class,'i-midas:switch icon')]", element_name="Switch icon")
            return True
        return True


def active_code(ids, countus):
    start_time = time.time()
    db = get_db()
    account_and_password = db.acc_and_pass()
    print(f"ID {ids} выполняется с аккаунтом: {account_and_password[0]}")
    driver = Driver(browser="chrome", headless=True, uc=True, pls='none', block_images=True)
    driver.maximize_window()
    driver.get('https://www.midasbuy.com/midasbuy/bd/redeem/pubgm?utm_campaign=pubg_voucher&utm_source=faq')

    driver.add_cookie(
        {'httpOnly': False, 'name': 'select_cookie', 'path': '/', 'sameSite': 'None', 'secure': True, 'value': '1'})
    driver.add_cookie(
        {'httpOnly': False, 'name': 'cookie_control', 'path': '/', 'sameSite': 'None', 'secure': True, 'value': '1|1'})
    local_storage = LocalStorage(driver)
    # local_storage['signInAndSignUpEmail'] = account_and_password[0]
    local_storage['vip绑定拍脸_landingPop'] = '{"value":1,"saveTime":1735138643136}'
    local_storage['vip绑定拍脸_showtimes_landingPop'] = '{"value":1,"saveTime":1751299199000}'
    local_storage[
        'pubg-积分抽奖二期 拍脸配置 其他国家-20240125104017_landingPop'] = '{"value":1,"saveTime":1751299199000}'
    local_storage[
        'pubg-积分抽奖二期 拍脸配置 其他国家-20240125104017_showtimes_landingPop'] = '{"value":1,"saveTime":1751299199000}'
    refresh_page(driver, 2)
    # refresh_page(driver, 5)
    if not authorization(driver, account_and_password, db, ids):
        refresh_page(driver)
        authorization(driver, account_and_password, db, ids)
    time.sleep(1)
    refresh_page(driver)

    if not click_element(driver, "//span/i[contains(@class,'i-midas:switch icon')]", element_name="Switch icon"):
        authorization(driver, account_and_password, db, ids, chang_id=True)

    time.sleep(1)
    fill_text_field(driver, "input[placeholder='Enter Player ID']", text=ids, enter=True)

    if handle_invalid_id(driver, ids):
        print("ID некорректен, повторная попытка ввода.")

    print("ID верный, продолжаем активацию кода.")
    time.sleep(1)
    refresh_page(driver)
    code_entry_process(driver, db, countus, ids)

    print(f"Время выполнения скрипта: {time.time() - start_time:.2f} секунд")
    driver.quit()


def handle_invalid_code(driver):
    error_code = wait_for_element(driver, '//*[@id="root"]/div/div[7]/div[3]/div/div[2]/div[2]/div[1]/div[2]/div',
                                  timeout=2, retries=1)
    if error_code and "Redeem code is already used" in error_code.text:
        print("Код Битый")
        return True
    return False


def handle_invalid_id(driver, player_id):
    error_message = wait_for_element(driver, '//*[@id="root"]/div/div[5]/div[2]/div[1]/div/div[2]/div[2]/div',
                                     timeout=1, retries=1)
    if error_message and "Invalid Game ID" in error_message.text:
        print("Invalid Game ID найден, повторная попытка ввода ID.")
        time.sleep(1)
        fill_text_field(driver, "input[placeholder='Enter Player ID']", player_id, enter=True)
        time.sleep(1)
        error_message = wait_for_element(driver, '//*[@id="root"]/div/div[5]/div[2]/div[1]/div/div[2]/div[2]/div',
                                         timeout=2, retries=2)
        if error_message and "Invalid Game ID" in error_message.text:
            return True
        else:
            return False
    return False


def code_entry_process(driver, db, countus, ids):
    num_attempts = countus // 60
    for i in range(num_attempts):
        code = db.code_reservation()
        while True:
            fill_text_field(driver, "input[placeholder='Please enter a redeem code']", text=code)
            time.sleep(1)
            if click_ok_and_confirm(driver,
                                    "//div[contains(@class, 'redeem_modules_box default_box')]//div[contains(@class, 'Button_icon_text') and text()='OK']",
                                    "//div[contains(@class, 'PopConfirmRedeem')]//div[contains(@class, 'Button_icon') and text()='Confirm']",
                                    code=code):
                print(f"Зачислил UC  по заказу {ids}. {i}|{num_attempts}")
                if not click_element(driver,
                                     "//div[contains(@class, 'PurchaseContainer')]//div[contains(@class, 'Button_icon') and text()='Return to Shop']"):
                    driver.get(
                        'https://www.midasbuy.com/midasbuy/bd/redeem/pubgm?utm_campaign=pubg_voucher&utm_source=faq')
                else:
                    time.sleep(0.5)
                break
            else:
                refresh_page(driver)
                print("Процесс подтверждения не удался, перезагрузка страницы.")
