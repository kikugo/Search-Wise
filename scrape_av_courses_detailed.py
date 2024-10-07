import requests
from bs4 import BeautifulSoup
import json
import time
import logging
import re
from requests.adapters import HTTPAdapter
from urllib3.util import Retry

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def load_courses(file_path='av_courses.json'):
    with open(file_path, 'r') as f:
        return json.load(f)

def get_session():
    session = requests.Session()
    retry = Retry(total=5, backoff_factor=0.1, status_forcelist=[500, 502, 503, 504])
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    return session

def scrape_course_details(course, session):
    try:
        logging.info(f"Scraping course details: {course['url']}")
        response = session.get(course['url'], timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        
        details = {}
        
        # Full description
        description = soup.find('div', class_='section__content')
        details['full_description'] = description.text.strip() if description else course.get('full_description', "No description found")
        
        # Course curriculum
        curriculum = soup.find_all('span', class_='course-curriculum__chapter-lesson')
        details['curriculum'] = [lesson.text.strip() for lesson in curriculum] if curriculum else []
        
        # Update num_lessons based on curriculum
        details['num_lessons'] = len(details['curriculum']) if details['curriculum'] else course.get('num_lessons', "Not specified")
        
        # Course metadata (difficulty, time, rating)
        metadata = soup.find('ul', class_='text-icon__list section__body')
        if metadata:
            metadata_items = metadata.find_all('li', class_='text-icon__list-item')
            for item in metadata_items:
                icon = item.find('i')
                if icon and 'fa-signal' in icon.get('class', []):
                    details['difficulty'] = item.find('h4').text.strip()
                elif icon and 'fa-clock-o' in icon.get('class', []):
                    details['estimated_time'] = item.find('h4').text.strip()
                elif icon and 'fa-star' in icon.get('class', []):
                    details['rating'] = item.find('h4').text.strip()
        
        # Key takeaways
        takeaways = soup.find('h3', string=re.compile('Key Takeaways'))
        if takeaways:
            takeaways_list = takeaways.find_next('ul')
            details['key_takeaways'] = [li.text.strip() for li in takeaways_list.find_all('li')] if takeaways_list else []
        else:
            details['key_takeaways'] = []
        
        # Instructor info
        instructor = soup.find('h3', string=re.compile('About the Instructor'))
        details['instructor_info'] = instructor.find_next('div', class_='section__body').text.strip() if instructor else "Not specified"
        
        return details
    
    except Exception as e:
        logging.error(f"Error scraping course details for {course['url']}: {e}")
        return {}

def scrape_all_course_details(courses):
    session = get_session()
    detailed_courses = []
    for course in courses:
        time.sleep(2)  # Be respectful with request frequency
        course_details = scrape_course_details(course, session)
        updated_course = {**course, **course_details}
        detailed_courses.append(updated_course)
    
    return detailed_courses

if __name__ == "__main__":
    # Load existing course data
    courses = load_courses()
    logging.info(f"Loaded {len(courses)} courses from av_courses.json")
    
    # Scrape detailed information for each course
    detailed_courses = scrape_all_course_details(courses)
    
    # Save the detailed course information
    with open('av_courses_detailed.json', 'w', encoding='utf-8') as f:
        json.dump(detailed_courses, f, ensure_ascii=False, indent=2)
    
    logging.info(f"Scraped details for {len(detailed_courses)} courses and saved to av_courses_detailed.json")