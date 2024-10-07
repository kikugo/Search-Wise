# Course Compass

Course Compass is a smart search tool for online courses from Analytics Vidhya, featuring web scraping capabilities, a semantic search implementation, and an interactive Streamlit web application.

## Table of Contents

1. [Project Overview](#project-overview)
2. [Features](#features)
3. [Installation](#installation)
4. [Usage](#usage)
5. [Project Structure](#project-structure)
6. [Development](#development)
7. [Technologies Used](#technologies-used)
8. [Future Improvements](#future-improvements)
9. [Contributing](#contributing)
10. [License](#license)

## Project Overview

Course Compass aims to create a user-friendly search interface for Analytics Vidhya's online courses. It consists of three main components:

1. Web scraping scripts to collect course data
2. A smart search tool using sentence transformers for semantic similarity
3. A Streamlit web application for users to search and filter courses

## Features

- Web scraping of online courses from Analytics Vidhya
- Smart search functionality using sentence transformers
- Interactive web interface with Streamlit
- Course filtering by difficulty, price, rating, and duration
- Autocomplete suggestions for search queries
- Pagination of search results
- Data visualization of search results

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

4. Install the project in editable mode:
   ```
   pip install -e .
   ```

## Usage

The project includes a Makefile for common operations. Here are the available commands:

- Scrape course data:
  ```
  make scrape
  ```

- Run the Streamlit app:
  ```
  make run_app
  ```

- Run tests:
  ```
  make test
  ```

- Clean up generated files:
  ```
  make clean
  ```

## Project Structure

```
Course_Compass_AV/
├── data/
│   ├── av_courses.json
│   └── av_courses_detailed.json
├── src/
│   ├── app/
│   │   ├── __init__.py
│   │   └── main.py
│   ├── scraping/
│   │   ├── __init__.py
│   │   └── scraper.py
│   └── search/
│       ├── __init__.py
│       └── search_tool.py
├── tests/
│   ├── test_scraping.py
│   └── test_search.py
├── .gitignore
├── Makefile
├── README.md
├── requirements.txt
└── setup.py
```

## Development

To set up the development environment:

1. Install the project in editable mode:
   ```
   pip install -e .
   ```

2. Run tests:
   ```
   make test
   ```

3. To scrape fresh data:
   ```
   make scrape
   ```

4. To run the Streamlit app locally:
   ```
   make run_app
   ```

## Technologies Used

- Python 3.7+
- BeautifulSoup4 for web scraping
- Sentence Transformers for semantic search
- Streamlit for the web application
- Scikit-learn for TF-IDF vectorization and K-means clustering

## Future Improvements

- Implement caching for search results to improve performance
- Add more advanced filtering options
- Implement a user feedback mechanism for search results
- Add a feature to compare selected courses side-by-side
- Regularly update the course data through automated scraping

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is open source and available under the [MIT License](LICENSE).
