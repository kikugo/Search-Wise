import requests
from bs4 import BeautifulSoup
import json
import time

def scrape_analytics_vidhya_courses():
    base_url = "https://courses.analyticsvidhya.com/collections/free-courses"
    courses = []

    response = requests.get(base_url)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    course_links = soup.find_all('a', class_='course-card')
    
    for link in course_links:
        course_url = f"https://courses.analyticsvidhya.com{link['href']}"
        course_response = requests.get(course_url)
        course_soup = BeautifulSoup(course_response.content, 'html.parser')
        
        title = course_soup.find('h1', class_='course-title').text.strip()
        description = course_soup.find('div', class_='course-description').text.strip()
        
        curriculum_items = course_soup.find_all('div', class_='section-item')
        curriculum = [item.text.strip() for item in curriculum_items]
        
        course = {
            'title': title,
            'description': description,
            'curriculum': curriculum,
            'url': course_url
        }
        
        courses.append(course)
        time.sleep(1)  # Be respectful to the server
    
    return courses

def save_to_json(data, filename):
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    courses_data = scrape_analytics_vidhya_courses()
    save_to_json(courses_data, 'analytics_vidhya_courses.json')
    print(f"Scraped {len(courses_data)} courses and saved to analytics_vidhya_courses.json")
