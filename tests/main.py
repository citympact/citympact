import os
from PIL import Image, ImageDraw
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.action_chains import ActionChains

import time
import unittest

WEBAPP_URL = "http://127.0.0.1:8000"

# New petition representation:
testPetition = {
    "title": "New petiton from the test runner",
    "image": os.path.dirname(os.path.realpath(__file__)) \
        + "/binaries/testimage.jpg",
    "description": "This petition was actually filled by a test run."
}


def _parent_element(domElement):
    """
    Helper function to find the DOM-parent element of the provided elt.
    """
    return domElement.find_element(By.XPATH, "..")

def _has_class(domElement, className):
    """
    Helper function to test if the provided element has the provided class
    """
    return className in domElement.get_attribute('class').split(" ")

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

    def test_project_votes(self):
        """ Testing the upvoting and the downvoting on a project. """
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


    def test_petition_five_star_vote(self):
        """ Testing the 5-star voting on a petition """
        self.browser.get(WEBAPP_URL)


        first_project_stars = self.browser.find_elements(
            By.CSS_SELECTOR, ".petition:first-child .rating-stars>.vote-star")

        for i, star in enumerate(first_project_stars):
            self.scrollToElement(star)
            star.click()
            try:
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


    def test_add_petition(self):
        """ Testing the addition of a new petition """
        self.browser.get(WEBAPP_URL)

        allAElements = self.browser.find_elements(
            By.CSS_SELECTOR, "a")
        a = list(filter(lambda x: x.text.startswith("Lance une pétition"),
            allAElements))[0]

        self.scrollToElement(a)
        a.click();
        self.assertIn("petition/add", self.browser.current_url)

        self.addNewPetition(testPetition)
        # We should have been redirected to the home page:
        self.assertNotIn("petition/add", self.browser.current_url)

        # Asserting that the project was correctly added by searching its title:
        petitionH2 = self.findFirstPetitionH2ByText(testPetition["title"])

        self.assertTrue(petitionH2 is not None)

        # Making sur we have a valid confirmation message:
        alertDivs = self.browser.find_elements(
            By.CSS_SELECTOR, ".alert.alert-primary")
        self.assertTrue(len(alertDivs)>0)

    def test_search_bar(self):
        """ Testing the behaviour of the search bar """
        self.browser.get(WEBAPP_URL)

        # Making sure the petition was already saved, if not we quickly add it:
        if self.findFirstPetitionH2ByText(testPetition["title"]) is None:
            self.addNewPetition(testPetition)

        search_input = self.browser.find_element(
            By.CSS_SELECTOR, "#search-input")
        search_input.send_keys(testPetition["title"][0:3])


        proposalsA = _parent_element(search_input).find_element(
            By.CSS_SELECTOR,
            ".suggestions-dropdown"
        ).find_elements(By.CSS_SELECTOR, "ul>li>a")

        # Making sure the test petition is found in the list of proposals
        found_petition_offset = -1
        for i, proposalA in enumerate(proposalsA):
            if testPetition["title"] in proposalA.text:
                found_petition_offset = i
                break
        self.assertTrue(found_petition_offset>=0)

        # Making sure the last proposal is a link to add a new petition:
        self.assertIn("Propser une pétition", proposalsA[-1].text)
        self.assertIn("petition/add", proposalsA[-1].get_attribute("href"))

        # Testing the keyboard arrow selection and click behaviour:

        # Making sure the selection circles back correctly
        for i in range(1 + found_petition_offset + len(proposalsA)):
            search_input.send_keys(Keys.DOWN)

        targetLi = _parent_element(proposalsA[found_petition_offset])
        self.assertTrue(_has_class(targetLi, "active-suggestion"))

        # Making sure the click works and redirects to the correct page:
        targetLi.click()

        self.assertIn("/petition/", self.browser.current_url)

        # Making sure there is an integer petition id part in the url:
        petitionId = int(self.browser.current_url.split("/petition/")[-1])
        self.assertTrue(petitionId>=0)

    def findFirstPetitionH2ByText(self, petitionTitle):
        """
        Helper function to retrieve a petition title DOM element given content
        """
        allPetitionDiv = self.browser.find_elements(
            By.CSS_SELECTOR, ".petition")
        for petitionDiv in allPetitionDiv:
            h2Element = petitionDiv.find_elements(
                By.CSS_SELECTOR, "h2")[0]
            if h2Element.text == petitionTitle:
                return h2Element
        return None

    def addNewPetition(self, petition):
        """ Helper function to add a new petition """
        addPetitionURLSuffix = "/petition/add"
        if not addPetitionURLSuffix in self.browser.current_url:
            self.browser.get(WEBAPP_URL+addPetitionURLSuffix)

        # Creating the image in the binary/ adjacent folder:
        img = Image.new('RGB', (600, 800), color = 'white')
        d = ImageDraw.Draw(img)
        d.text((100,200), "Test image", fill=(0,0,0))
        img.save(petition["image"])

        for k,v in petition.items():
            inputOrTextarea = self.browser.find_elements(By.CSS_SELECTOR,
                "input[name=%s], textarea[name=%s]" % (k, k))[0]
            # FixMe: add robustness to the CSS selection (waiting for better FE)

            inputOrTextarea.send_keys(v)

        submitButton = self.browser.find_elements(By.CSS_SELECTOR, "input[type=submit]")[0]
        # FixMe: add robustness to the CSS selection (waiting for better FE)

        submitButton.click()


    def tearDown(self):
        self.browser.quit()

if __name__ == "__main__":
    unittest.main(verbosity=2)
