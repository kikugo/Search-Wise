import streamlit as st
from sentence_transformers import SentenceTransformer, util
import json
import torch
import pickle
from transformers import pipeline
from typing import List, Dict, Any
from functools import partial
import logging

logging.basicConfig(level=logging.INFO)

class SmartSearchTool:
    def __init__(self, data_file: str):
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.courses = self.load_courses(data_file)
        logging.info(f"Loaded {len(self.courses)} courses")
        self.course_embeddings = self.load_or_compute_embeddings()
        logging.info(f"Loaded embeddings with shape: {self.course_embeddings.shape}")

    def load_courses(self, data_file: str) -> List[Dict[str, Any]]:
        try:
            with open(data_file, 'r', encoding='utf-8') as f:
                courses = json.load(f)
            logging.info(f"Successfully loaded {len(courses)} courses from {data_file}")
            return courses
        except Exception as e:
            logging.error(f"Error loading courses from {data_file}: {str(e)}")
            return []

    def load_or_compute_embeddings(self) -> torch.Tensor:
        try:
            with open('data/course_embeddings.pkl', 'rb') as f:
                embeddings = pickle.load(f)
            logging.info("Successfully loaded pre-computed embeddings")
            return embeddings
        except FileNotFoundError:
            logging.info("Computing course embeddings...")
            embeddings = self.compute_course_embeddings()
            with open('data/course_embeddings.pkl', 'wb') as f:
                pickle.dump(embeddings, f)
            logging.info("Saved computed embeddings")
            return embeddings

    def compute_course_embeddings(self) -> torch.Tensor:
        texts = [f"{course['title']} {course.get('full_description', '')} {' '.join(course.get('key_takeaways', []))}" for course in self.courses]
        return self.model.encode(texts, convert_to_tensor=True)

    @staticmethod
    @st.cache_data(ttl=3600)
    def _search(query: str, _course_embeddings: List[List[float]], _courses: List[Dict[str, Any]], top_k: int = 5, filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        logging.info(f"Searching for query: {query}")
        logging.info(f"Number of courses: {len(_courses)}")
        logging.info(f"Number of embeddings: {len(_course_embeddings)}")
        
        model = SentenceTransformer('all-MiniLM-L6-v2')
        query_embedding = model.encode(query, convert_to_tensor=True)
        course_embeddings = torch.tensor(_course_embeddings)
        cos_scores = util.cos_sim(query_embedding, course_embeddings)[0]
        top_results = torch.topk(cos_scores, k=len(_courses))
        
        results = []
        for score, idx in zip(top_results[0], top_results[1]):
            course = _courses[idx]
            if filters:
                if 'difficulty' in filters and filters['difficulty'] and course.get('difficulty') not in filters['difficulty']:
                    continue
                if 'is_free' in filters and filters['is_free'] and not course.get('is_free', False):
                    continue
            results.append({
                'score': score.item(),
                'course': course
            })
            if len(results) == top_k:
                break
        
        logging.info(f"Found {len(results)} results")
        return results

    def search(self, query: str, top_k: int = 5, filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        course_embeddings_list = self.course_embeddings.tolist()
        return self._search(query, course_embeddings_list, self.courses, top_k, filters)



    def summarize_course(self, course: Dict[str, Any], max_length: int = 100) -> str:
        text = f"{course['title']}. {course.get('full_description', '')}"
        summary = self.summarizer(text, max_length=max_length, min_length=30, do_sample=False)
        return summary[0]['summary_text']

if __name__ == "__main__":
    search_tool = SmartSearchTool('data/av_courses_detailed.json')
    results = search_tool.search("machine learning for beginners", filters={'difficulty': ['Beginner'], 'is_free': True})
    for result in results:
        print(f"Score: {result['score']:.4f}")
        print(f"Title: {result['course']['title']}")
        print(f"URL: {result['course']['url']}")
        print("---")