from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
import json


class Browser():
    def __init__(self):
        self.driver = webdriver.Firefox(executable_path=r'geckodriver.exe')
        self.driver.get("https://play.aidungeon.io/")
        with open("settings.json") as data:
            user_data = json.load(data)
        self.email = user_data["email"]
        self.password = user_data["password"]
        self.sign_in()

    def sign_in(self):
        email_field = self.driver.find_element_by_xpath("/html/body/div/div/div/div/div/div/div/div/div/div/div/div/div/div[2]/div[1]/input")
        email_field.send_keys(self.email)
        firstlogin_button = self.driver.find_element_by_xpath("/html/body/div/div/div/div/div/div/div/div/div/div/div/div/div/div[2]/div[2]")
        firstlogin_button.click()
        time.sleep(2)
        pass_field = self.driver.find_element_by_xpath("/html/body/div/div/div/div/div/div/div/div/div/div[2]/div/div[1]/div/div[2]/input")
        pass_field.send_keys(self.password)
        login_button = self.driver.find_element_by_xpath("/html/body/div/div/div/div/div/div/div/div/div/div[2]/div/div[1]/div/div[3]/div")
        login_button.click()

    def send_prompt(self, prompt):
        input_field = self.driver.find_element_by_xpath("/html/body/div/div/div/div/div/div/div/div/div/div/div/div[1]/div/div[3]/textarea")
        input_field.send_keys(prompt)
        input_field.send_keys(Keys.ENTER)

    def reset_game(self):
        elem = self.driver.find_element_by_xpath("/html/body/div/div/div/div/div/div/div/div/div/div/div/div[2]/div/div/div/div[3]/div/div/img")
        elem.click()
        self.driver.switch_to.alert.accept()
