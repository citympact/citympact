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
                "detail_div"
            ).find_element(By.CLASS_NAME, vote_class)
        except:
            self.fail("Unable to find the upvote_button element to click on.");

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
        for vote_class in ["upvote_button", "downvote_button"]:
            self.browser.get(WEBAPP_URL)
            vote_elt = self.get_project_first_vote_elt(vote_class)

            # Making sure the newly vote is displayed as an active class on the
            # elt:
            try:
                self.scrollToElement(vote_elt)
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


    def test_petition_sign(self):
        """
        Testing that signing a petition as anonymous user redirects to the
        login page.
        """
        self.browser.get(WEBAPP_URL)


        sign_petition_a = self.browser.find_element(
            By.CSS_SELECTOR, ".detail_div:first-child .sign_petition_div a")
        self.scrollToElement(sign_petition_a)
        sign_petition_a.click()

        try:
            WebDriverWait(self.browser, 2.5).until(lambda browser:
                "accounts/login" in browser.current_url
            )
        except TimeoutException as e:
            self.fail("A click on the signature button should redirect to " \
                + "the login page as this test did not authenticate " \
                + "beforehand.");




    def test_add_petition(self):
        """
        Testing that clickon on add a petition as anonymous user redirects to
        the login page.
        """
        self.browser.get(WEBAPP_URL)

        a = self.browser.find_element(By.CSS_SELECTOR, "#new_petition")
        self.scrollToElement(a)
        a.click();

        try:
            WebDriverWait(self.browser, 2.5).until(lambda browser:
                "accounts/login" in browser.current_url
            )
        except TimeoutException as e:
            self.fail("A click on the signature button should redirect to " \
                + "the login page as this test did not authenticate " \
                + "beforehand.");

    def todo_test_logged_add_petition(self):
        # FixMe: add a test that covers the login and the petition creation
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

        def inputPrefixInSearchBar(text):
            # First, resetting the search bar:
            search_input.clear()
            self.browser.find_element(
                By.CSS_SELECTOR, "body").click()
            try:
                WebDriverWait(self.browser, 2.5).until(EC.invisibility_of_element_located((By.CSS_SELECTOR, ".suggestions-dropdown")))
            except TimeoutException as e:
                self.fail("The suggestions did not disappear.")

            # Second, inputting the query (and waiting for the response)
            for c in text[0:3]:
                search_input.send_keys(c)
                # Mimicking the user keyboard stroke latency - also giving us
                # some time for ajax RTT:
                time.sleep(0.150)
            try:
                WebDriverWait(self.browser, 2.5).until(lambda browser:
                    len(_parent_element(search_input).find_element(
                        By.CSS_SELECTOR,
                        ".suggestions-dropdown"
                    ).find_elements(By.CSS_SELECTOR, "ul>li>a"))>0
                )
            except TimeoutException as e:
                self.fail("No suggestion displayed under the search bar.");


        self.browser.get(WEBAPP_URL)
        search_input = self.browser.find_element(
            By.CSS_SELECTOR, "#search-input")

        petitionTitles = [h2.text for h2 in self.browser.find_elements(By.CSS_SELECTOR, ".detail_div .sign_petition_div+h2")]
        self.assertGreater(len(petitionTitles), 0)

        for  petitionTitle in petitionTitles:
            inputPrefixInSearchBar(petitionTitle)
            proposalsA = _parent_element(search_input).find_element(
                By.CSS_SELECTOR,
                ".suggestions-dropdown"
            ).find_elements(By.CSS_SELECTOR, "ul>li>a")
            proposalTitles = [a.text for a  in proposalsA]

            # Converting the list of choices into a string for quick assertion:
            self.assertIn(petitionTitle, str(proposalTitles))

            # Making sure the last proposal is a link to add a new petition:
            self.assertIn("Proposer une pétition", proposalsA[-1].text)
            self.assertIn("petition/add", proposalsA[-1].get_attribute("href"))


            # Making sure the selection circles back correctly
            for i in range(1 + len(proposalsA)):
                search_input.send_keys(Keys.DOWN)

            targetLi = _parent_element(proposalsA[0])
            try:
                WebDriverWait(self.browser, 2.5).until(lambda browser:
                    _has_class(targetLi, "active-suggestion")
                )
            except TimeoutException as e:
                self.fail("The keyboard DOWN-key selection did not work.");


        # Making sure the click works and redirects to the correct page:
        inputPrefixInSearchBar(petitionTitles[0])
        search_input.send_keys(Keys.DOWN)
        targetLi = _parent_element(_parent_element(search_input).find_element(
            By.CSS_SELECTOR,
            ".suggestions-dropdown"
        ).find_elements(By.CSS_SELECTOR, "ul>li>a")[0])
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

        import time; time.sleep(1)

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
