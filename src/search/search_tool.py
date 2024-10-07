import streamlit as st
from sentence_transformers import SentenceTransformer, util
import json
import torch
import pickle
from transformers import pipeline
from typing import List, Dict, Any
from functools import partial

class SmartSearchTool:
    def __init__(self, data_file: str):
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.courses = self.load_courses(data_file)
        self.course_embeddings = self.load_or_compute_embeddings()
        self.summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

    def load_courses(self, data_file: str) -> List[Dict[str, Any]]:
        with open(data_file, 'r', encoding='utf-8') as f:
            return json.load(f)

    def load_or_compute_embeddings(self) -> torch.Tensor:
        try:
            with open('data/course_embeddings.pkl', 'rb') as f:
                return pickle.load(f)
        except FileNotFoundError:
            embeddings = self.compute_course_embeddings()
            with open('data/course_embeddings.pkl', 'wb') as f:
                pickle.dump(embeddings, f)
            return embeddings

    def compute_course_embeddings(self) -> torch.Tensor:
        texts = [f"{course['title']} {course.get('full_description', '')} {' '.join(course.get('key_takeaways', []))} {' '.join(course.get('curriculum', []))} {course.get('difficulty', '')} {course.get('instructor_info', '')}" for course in self.courses]
        return self.model.encode(texts, convert_to_tensor=True)

    @staticmethod
    @st.cache_data(ttl=3600)
    def _search(query: str, course_embeddings: torch.Tensor, courses: List[Dict[str, Any]], top_k: int = 5, filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        model = SentenceTransformer('all-MiniLM-L6-v2')
        query_embedding = model.encode(query, convert_to_tensor=True)
        cos_scores = util.cos_sim(query_embedding, course_embeddings)[0]
        top_results = torch.topk(cos_scores, k=len(courses))
        
        results = []
        for score, idx in zip(top_results[0], top_results[1]):
            course = courses[idx]
            if filters:
                if 'difficulty' in filters and course.get('difficulty') not in filters['difficulty']:
                    continue
                if 'is_free' in filters and course.get('is_free') != filters['is_free']:
                    continue
            results.append({
                'score': score.item(),
                'course': course
            })
            if len(results) == top_k:
                break
        
        return results

    def search(self, query: str, top_k: int = 5, filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        return self._search(query, self.course_embeddings, self.courses, top_k, filters)

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