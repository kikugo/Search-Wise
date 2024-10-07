import json
import torch
import pickle
import logging
from sentence_transformers import SentenceTransformer, util
from typing import List, Dict, Any
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class SmartSearchTool:
    def __init__(self, data_file: str):
        self.model = SentenceTransformer('distilbert-base-nli-stsb-mean-tokens')
        self.courses = self.load_courses(data_file)
        self.course_embeddings = self.load_or_compute_embeddings()
        self.vectorizer = TfidfVectorizer(stop_words='english')
        self.tfidf_matrix = self.vectorizer.fit_transform([course['title'] + ' ' + course.get('full_description', '') for course in self.courses])
        self.all_words = set(word for course in self.courses for word in course['title'].lower().split())

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

    def get_autocomplete_suggestions(self, partial_query: str, max_suggestions: int = 5) -> List[str]:
        partial_query = partial_query.lower()
        return sorted([word for word in self.all_words if word.startswith(partial_query)])[:max_suggestions]

    def extract_keywords(self, text: str, num_keywords: int = 5) -> List[str]:
        tfidf = self.vectorizer.transform([text])
        feature_names = self.vectorizer.get_feature_names_out()
        sorted_indices = tfidf.data.argsort()[-num_keywords:][::-1]
        return [feature_names[i] for i in sorted_indices]

    def cluster_results(self, results: List[Dict[str, Any]], num_clusters: int = 3) -> List[Dict[str, Any]]:
        if len(results) < num_clusters:
            return results

        vectors = self.tfidf_matrix[[self.courses.index(r['course']) for r in results]]
        kmeans = KMeans(n_clusters=num_clusters)
        kmeans.fit(vectors)
        
        for result, cluster in zip(results, kmeans.labels_):
            result['cluster'] = int(cluster)
        
        return results

    def search(self, query: str) -> List[Dict[str, Any]]:
        query_embedding = self.model.encode(query, convert_to_tensor=True)
        cos_scores = util.cos_sim(query_embedding, self.course_embeddings)[0]
        top_results = torch.topk(cos_scores, k=len(self.courses))
        
        results = []
        for score, idx in zip(top_results[0], top_results[1]):
            course = self.courses[idx]
            results.append({
                'score': score.item(),
                'course': course,
                'keywords': self.extract_keywords(course.get('full_description', ''))
            })
        
        # Sort results by score in descending order
        results.sort(key=lambda x: x['score'], reverse=True)
        
        return results

    @staticmethod
    def parse_duration(duration_str: str) -> float:
        try:
            if 'Hour' in duration_str:
                return float(duration_str.split()[0])
            elif 'Mins' in duration_str:
                return float(duration_str.split()[0]) / 60
            return 0
        except ValueError:
            return 0

    @staticmethod
    def parse_rating(rating_str: str) -> float:
        try:
            return float(rating_str.split('/')[0])
        except ValueError:
            return 0

if __name__ == "__main__":
    search_tool = SmartSearchTool('data/av_courses_detailed.json')
    results = search_tool.search("machine learning")
    for result in results[:5]:
        print(f"Score: {result['score']:.4f}")
        print(f"Title: {result['course']['title']}")
        print(f"URL: {result['course']['url']}")
        print(f"Keywords: {', '.join(result['keywords'])}")
        print("---")