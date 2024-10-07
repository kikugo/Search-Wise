import unittest
from src.scraping.scraper import scrape_course_listings, scrape_course_details

class TestScraping(unittest.TestCase):
    def test_scrape_course_listings(self):
        courses = scrape_course_listings(num_pages=1)
        self.assertTrue(len(courses) > 0)
        self.assertTrue('title' in courses[0])
        self.assertTrue('url' in courses[0])

    def test_scrape_course_details(self):
        course = {'url': 'https://courses.analyticsvidhya.com/courses/getting-started-with-decision-trees'}
        detailed_course = scrape_course_details(course)
        self.assertTrue('full_description' in detailed_course)
        self.assertTrue('curriculum' in detailed_course)

if __name__ == '__main__':
    unittest.main()