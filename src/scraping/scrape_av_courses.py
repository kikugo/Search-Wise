import requests
from bs4 import BeautifulSoup
import json
import time
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def scrape_course_listings(num_pages=8):
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

def save_to_json(data, filename='av_courses.json'):
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        logging.info(f"Data successfully saved to {filename}")
    except IOError as e:
        logging.error(f"Error saving data to {filename}: {e}")

if __name__ == "__main__":
    all_courses = scrape_course_listings()
    logging.info(f"Total courses scraped: {len(all_courses)}")
    save_to_json(all_courses)