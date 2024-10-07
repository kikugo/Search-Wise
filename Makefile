.PHONY: scrape run_app install test clean

scrape:
	python -m src.scraping.scraper --pages 8 --detailed

run_app:
	streamlit run src/app/main.py

install:
	pip install -e .

test:
	python -m unittest discover tests

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -rf build dist *.egg-info