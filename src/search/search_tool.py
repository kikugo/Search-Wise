import json
import torch
import pickle
import logging
import nltk
from nltk.corpus import wordnet
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from sentence_transformers import SentenceTransformer, util
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from typing import List, Dict, Any

# Download necessary NLTK data
nltk.download('wordnet', quiet=True)
nltk.download('punkt', quiet=True)
nltk.download('stopwords', quiet=True)

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

    def expand_query(self, query: str) -> str:
        expanded_terms = []
        for word in query.split():
            synonyms = wordnet.synsets(word)
            if synonyms:
                expanded_terms.extend([lemma.name() for lemma in synonyms[0].lemmas()])
            else:
                expanded_terms.append(word)
        return " ".join(set(expanded_terms))

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

    def search(self, query: str, filters: Dict[str, Any] = None, top_k: int = None) -> List[Dict[str, Any]]:
        expanded_query = self.expand_query(query)
        course_embeddings_list = self.course_embeddings.tolist()
        results = self._search(expanded_query, course_embeddings_list, self.courses, filters=filters)
        
        if filters:
            results = [r for r in results if self.apply_advanced_filters(r['course'], filters)]
        
        results.sort(key=lambda x: self.custom_rank(x['course'], x['score']), reverse=True)
        
        results = self.cluster_results(results)
        
        for result in results:
            result['keywords'] = self.extract_keywords(result['course'].get('full_description', ''))
        
        return results[:top_k] if top_k else results

    @staticmethod
    def _search(query: str, _course_embeddings: List[List[float]], _courses: List[Dict[str, Any]], top_k: int = None, filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        logging.info(f"Searching for query: {query}")
        logging.info(f"Number of courses: {len(_courses)}")
        logging.info(f"Number of embeddings: {len(_course_embeddings)}")
        
        model = SentenceTransformer('distilbert-base-nli-stsb-mean-tokens')
        query_embedding = model.encode(query, convert_to_tensor=True)
        course_embeddings = torch.tensor(_course_embeddings)
        cos_scores = util.cos_sim(query_embedding, course_embeddings)[0]
        top_results = torch.topk(cos_scores, k=len(_courses))
        
        results = []
        for score, idx in zip(top_results[0], top_results[1]):
            course = _courses[idx]
            results.append({
                'score': score.item(),
                'course': course
            })
        
        logging.info(f"Found {len(results)} results")
        return results

    def apply_advanced_filters(self, course: Dict[str, Any], filters: Dict[str, Any]) -> bool:
        if 'difficulty' in filters and filters['difficulty'] and course.get('difficulty') not in filters['difficulty']:
            return False
        if 'is_free' in filters and filters['is_free'] and not course.get('is_free', False):
            return False
        if 'min_rating' in filters and self.parse_rating(course.get('rating', '0')) < filters['min_rating']:
            return False
        if 'max_duration' in filters and self.parse_duration(course.get('estimated_time', '0')) > filters['max_duration']:
            return False
        if 'topics' in filters and not any(topic.lower() in course.get('title', '').lower() for topic in filters['topics']):
            return False
        return True

    def custom_rank(self, course: Dict[str, Any], relevance_score: float) -> float:
        rating_factor = self.parse_rating(course.get('rating', '0')) / 5
        popularity_factor = len(course.get('key_takeaways', [])) / 10  # Assuming more takeaways indicate popularity
        return (relevance_score * 0.6) + (rating_factor * 0.3) + (popularity_factor * 0.1)

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
    results = search_tool.search("machine learning for beginners", filters={'difficulty': ['Beginner'], 'is_free': True})
    for result in results[:5]:
        print(f"Score: {result['score']:.4f}")
        print(f"Title: {result['course']['title']}")
        print(f"URL: {result['course']['url']}")
        print(f"Cluster: {result['cluster']}")
        print(f"Keywords: {', '.join(result['keywords'])}")
        print("---")