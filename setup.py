from setuptools import setup, find_packages

setup(
    name="course_compass",
    version="0.1",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "requests",
        "beautifulsoup4",
        "sentence-transformers",
        "streamlit",
        "torch",
    ],
    entry_points={
        "console_scripts": [
            "scrape_courses=src.scraping.scraper:main",
            "run_app=src.app.main:main",
        ],
    },
)