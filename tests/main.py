from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.action_chains import ActionChains

import time
import unittest

WEBAPP_URL = "http://127.0.0.1:8000/"

class TestStringMethods(unittest.TestCase):

    def setUp(self):
        options = webdriver.chrome.options.Options()
        options.add_argument('--headless')
        service = webdriver.chrome.service.Service("binaries/chromedriver")

        self.browser = webdriver.Chrome(service=service, options=options)
        self.browser.maximize_window()

    def get_project_first_vote_elt(self, vote_class):
        try:
            return self.browser.find_element(
                By.CLASS_NAME,
                "project-div"
            ).find_element(By.CLASS_NAME, vote_class)
        except:
            self.fail("Unable to find the upvote element to click on.");

    def test_project_votes(self):
        # Testing the upvoting and the downvoting on a project:
        for vote_class in ["upvote", "downvote"]:
            self.browser.get(WEBAPP_URL)
            vote_elt = self.get_project_first_vote_elt(vote_class)

            # Making sure the newly vote is displayed as an active class on the
            # elt:
            try:
                vote_elt.click()
                WebDriverWait(self.browser, 2.5).until(lambda browser:
                    vote_elt.get_attribute("class") == vote_class+" active-vote"
                )
            except TimeoutException as e:
                self.fail("The voted button did not switch to active");


            # Refreshing the page (still with the same session) and making sure
            # that the registred vote is still displayed:
            self.browser.refresh();
            vote_elt = self.get_project_first_vote_elt(vote_class)
            self.assertEqual(vote_elt.get_attribute("class"),
                vote_class+" active-vote")


    def scrollToElement(self, element):
        """ Helper function to scroll (and wait on) a given DOM element """

        page_y_offset = self.browser.execute_script("return window.pageYOffset")
        scroll_offset = element.location["y"] - page_y_offset
        self.browser.execute_script("window.scrollBy(0, arguments[0]);", scroll_offset)


        page_y_offset = self.browser.execute_script("return window.pageYOffset")
        window_height = self.browser.execute_script("return window.innerHeight")
        # Waiting that the windows bottom has at least reached the element
        # y-offset (by substracting the window height of the scrolling offset):
        WebDriverWait(self.browser, 2.5).until(lambda browser:
            browser.execute_script("return window.pageYOffset") >= \
                (scroll_offset - window_height)
        )
    def test_petition_five_star_vote(self):
        # Testing the 5-star voting on a petition:
        self.browser.get(WEBAPP_URL)


        first_project_stars = self.browser.find_elements(
            By.CSS_SELECTOR, ".petition:first-child .rating-stars>.vote-star")

        for i, star in enumerate(first_project_stars):
            self.scrollToElement(star)
            try:
                star.click()
                WebDriverWait(self.browser, 2.5).until(lambda browser:
                    "star-activated" in star.get_attribute("class")
                )
            except TimeoutException as e:
                self.fail("The voted star did not switch to active");
            # To do assert impact of the click on the frontend behaviour

        # Finally storing the definitive vote and refreshing the page to assert
        # that the vote is correctly displayed:
        finalStarIndex = 4
        star = first_project_stars[finalStarIndex]
        star.click();
        WebDriverWait(self.browser, 2.5).until(lambda browser:
            "star-activated" in star.get_attribute("class")
        )
        self.browser.refresh();

        first_project_stars = self.browser.find_elements(
            By.CSS_SELECTOR, ".petition:first-child .rating-stars>.vote-star")
        self.assertIn("star-activated", first_project_stars[finalStarIndex]\
            .get_attribute("class"))


    def tearDown(self):
        self.browser.quit()

if __name__ == "__main__":
    unittest.main(verbosity=2)
