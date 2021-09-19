import csv
import random
import pickle
from time import sleep
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.keys import Keys


class CoursesCrawl:
    def __init__(self, link, username, password):
        self.username = username
        self.password = password
        self.link = link
        self.browser = webdriver.Chrome(executable_path='./chromedriver')
        self.get_link()

    def load_cookies(self):
        cookies = pickle.load(open("my_cookie.pkl", "rb"))
        for cookie in cookies:
            print(cookie)
            self.browser.add_cookie(cookie)
        self.browser.get(self.link)

    def save_cookies(self):
        pickle.dump(self.browser.get_cookies(), open("my_cookie.pkl", "wb"))

    def get_link(self):
        self.browser.get(self.link)
        sleep(2)
        self.login()

    def login(self):
        user_fd = self.browser.find_element_by_id('username')
        password_fd = self.browser.find_element_by_id('password')
        user_fd.send_keys(self.username)
        password_fd.send_keys(self.password)
        password_fd.send_keys(Keys.ENTER)

    def get_years(self, selector):
        selector = f"//div[contains(@data-depth, {selector})]"
        return self.browser.find_elements_by_xpath(selector)

    def get_semesters(self, parent, selector):
        selector = f"//div[contains(@data-depth, {selector})]"
        return parent.find_elements_by_xpath(selector)

    def get_categories(self, parent, selector, id):
        cates = []
        for i in range(1, 6):
            try:
                s = f"//div[contains(@data-depth, {selector}) and @data-categoryid={int(id) + i}]"
                cates.append(parent.find_element_by_xpath(s))
            except:
                pass
        return cates

    def crawl(self):
        while True:
            links = []
            years = self.get_years('1')
            semesters = self.get_semesters(years[1], '2')
            for semester in semesters:
                id = semester.get_attribute('data-categoryid')
                categories = self.get_categories(semester, '3', id)
                try:
                    for category in categories:
                        all_courses = category.find_element_by_tag_name(
                            'a')
                        links.append(all_courses.get_attribute('href'))
                except Exception as e:
                    print(e)
            with open('courses.csv', 'a') as csvfile:
                csvwriter = csv.writer(csvfile)
                for link in links:
                    self.browser.get(link)
                    courses_link = []
                    courses = self.browser.find_elements_by_xpath(
                        "//a[@class and contains(@href, 'course/view')]")
                    for course in courses:
                        courses_link.append(course.get_attribute('href'))
                    for cl in courses_link:
                        self.browser.get(cl)
                        cname = self.browser.find_element_by_class_name(
                            'coursename')
                        try:
                            tchs = [cname.text]
                            cteachers = self.browser.find_element_by_class_name('teachers').find_elements_by_tag_name(
                                'li'
                            )
                            for ct in cteachers:
                                tchs.append(ct.text)
                            csvwriter.writerow(tchs)
                        except:
                            tchs = [cname.text]
                            csvwriter.writerow(tchs)
            break
        sleep(1)
        self.browser.close()


if __name__ == '__main__':
    username = ''
    password = ''
    crawl_obj = CoursesCrawl(
        'https://courses.ctda.hcmus.edu.vn/login/index.php', username, password)
    crawl_obj.crawl()
