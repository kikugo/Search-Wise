import requests
from bs4 import BeautifulSoup
import json
import time
import logging
import concurrent.futures
from typing import List, Dict, Any

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def scrape_course_listings(num_pages: int = 8) -> List[Dict[str, Any]]:
    courses = []
    base_url = "https://courses.analyticsvidhya.com/collections?page="
    
    for page in range(1, num_pages + 1):
        try:
            logging.info(f"Scraping page {page}")
            response = requests.get(base_url + str(page))
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            course_cards = soup.find_all('li', class_='products__list-item')
            for card in course_cards:
                try:
                    title = card.find('h3').text.strip() if card.find('h3') else "No title found"
                    url = 'https://courses.analyticsvidhya.com' + card.find('a')['href'] if card.find('a') else "No URL found"
                    price_element = card.find('span', class_='course-card__price')
                    is_free = 'Free' in price_element.text if price_element else False
                    lessons_element = card.find('span', class_='course-card__lesson-count')
                    num_lessons = lessons_element.text.strip() if lessons_element else "No lesson count found"
                    
                    course = {
                        'title': title,
                        'url': url,
                        'is_free': is_free,
                        'num_lessons': num_lessons,
                    }
                    courses.append(course)
                    logging.info(f"Scraped course: {title}")
                except AttributeError as e:
                    logging.error(f"Error scraping a course on page {page}: {e}")
                except Exception as e:
                    logging.error(f"Unexpected error scraping a course on page {page}: {e}")
            
            time.sleep(2)
        
        except requests.RequestException as e:
            logging.error(f"Error scraping page {page}: {e}")
        except Exception as e:
            logging.error(f"Unexpected error on page {page}: {e}")
    
    return courses

def scrape_course_details(course: Dict[str, Any]) -> Dict[str, Any]:
    try:
        logging.info(f"Scraping course details: {course['url']}")
        response = requests.get(course['url'])
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        
        details = {}
        
        description = soup.find('div', class_='section__content')
        details['full_description'] = description.text.strip() if description else "No description found"
        
        curriculum = soup.find_all('span', class_='course-curriculum__chapter-lesson')
        details['curriculum'] = [lesson.text.strip() for lesson in curriculum] if curriculum else []
        
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
        
        takeaways = soup.find('h3', string='Key Takeaways')
        if takeaways:
            takeaways_list = takeaways.find_next('ul')
            details['key_takeaways'] = [li.text.strip() for li in takeaways_list.find_all('li')] if takeaways_list else []
        else:
            details['key_takeaways'] = []
        
        instructor = soup.find('h3', string='About the Instructor')
        details['instructor_info'] = instructor.find_next('div', class_='section__body').text.strip() if instructor else "Not specified"
        
        return {**course, **details}
    
    except Exception as e:
        logging.error(f"Error scraping course details for {course['url']}: {e}")
        return course

def save_to_json(data: List[Dict[str, Any]], filename: str = 'av_courses.json') -> None:
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        logging.info(f"Data successfully saved to {filename}")
    except IOError as e:
        logging.error(f"Error saving data to {filename}: {e}")

def main(num_pages: int = 8, detailed: bool = False) -> None:
    courses = scrape_course_listings(num_pages)
    
    if detailed:
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            detailed_courses = list(executor.map(scrape_course_details, courses))
        save_to_json(detailed_courses, 'data/av_courses_detailed.json')
    else:
        save_to_json(courses, 'data/av_courses.json')

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Scrape Analytics Vidhya courses")
    parser.add_argument("--pages", type=int, default=8, help="Number of pages to scrape")
    parser.add_argument("--detailed", action="store_true", help="Scrape detailed course information")
    args = parser.parse_args()
    
    main(args.pages, args.detailed)