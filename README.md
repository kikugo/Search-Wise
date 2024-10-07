---
title: Course Search AV
emoji: 🔍
colorFrom: blue
colorTo: green
sdk: streamlit
sdk_version: 1.21.0
app_file: app.py
pinned: false
---

# Course Compass

Course Compass is a smart search tool for online courses, featuring web scraping capabilities, a semantic search implementation, and an interactive Streamlit web application.

## Table of Contents

1. [Project Overview](#project-overview)
2. [Features](#features)
3. [Installation](#installation)
4. [Usage](#usage)
   - [Web Scraping](#web-scraping)
   - [Search Tool](#search-tool)
   - [Streamlit App](#streamlit-app)
5. [Project Structure](#project-structure)
6. [Technologies Used](#technologies-used)
7. [Future Improvements](#future-improvements)
8. [Contributing](#contributing)
9. [License](#license)

## Project Overview

Course Compass aims to create a user-friendly search interface for online courses. It consists of three main components:

1. Web scraping scripts to collect course data
2. A smart search tool using sentence transformers for semantic similarity
3. A Streamlit web application for users to search and filter courses

## Features

- Web scraping of online courses
- Smart search functionality using sentence transformers
- Interactive web interface with Streamlit
- Course filtering by difficulty and price (free/paid)
- Sorting options for search results
- Pagination of search results
- Data visualization of top search results

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/kikugo/Course_Compass_AV.git
   cd Course_Compass_AV
   ```

2. Create a virtual environment (optional but recommended):
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   ```

3. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

## Usage

### Web Scraping

To scrape the initial course data:

```
python scrape_av_courses.py
```

This will create or update the `av_courses.json` file with basic course information.

To scrape detailed course information:

```
python scrape_av_courses_detailed.py
```

This will create or update the `av_courses_detailed.json` file with comprehensive course details.

### Search Tool

The search tool is implemented in `search_tool.py`. You can use it directly in Python:

```python
from search_tool import SmartSearchTool

search_tool = SmartSearchTool('av_courses_detailed.json')
results = search_tool.search("machine learning for beginners")

for result in results:
    print(f"Score: {result['score']:.4f}")
    print(f"Title: {result['course']['title']}")
    print(f"URL: {result['course']['url']}")
    print("---")
```

### Streamlit App

To run the Streamlit app:

```
streamlit run app.py
```

This will start the web application. Open your browser and navigate to the URL provided in the terminal (usually `http://localhost:8501`).

## Project Structure

- `scrape_av_courses.py`: Script for initial course data scraping
- `scrape_av_courses_detailed.py`: Script for detailed course information scraping
- `search_tool.py`: Implementation of the smart search tool
- `app.py`: Streamlit web application
- `requirements.txt`: List of Python dependencies
- `av_courses.json`: Initial scraped course data
- `av_courses_detailed.json`: Detailed scraped course data

## Technologies Used

- Python 3.7+
- BeautifulSoup4 for web scraping
- Sentence Transformers for semantic search
- Streamlit for the web application
- Pandas and Altair for data manipulation and visualization

## Future Improvements

- Implement caching for search results to improve performance
- Add more advanced filtering options (e.g., by estimated time or rating range)
- Implement a user feedback mechanism for search results
- Add a feature to compare selected courses side-by-side
- Regularly update the course data through automated scraping

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is open source and available under the [MIT License](LICENSE).
