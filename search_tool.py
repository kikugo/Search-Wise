from sentence_transformers import SentenceTransformer, util
import json
import torch

class SmartSearchTool:
    def __init__(self, data_file):
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.courses = self.load_courses(data_file)
        self.course_embeddings = self.compute_course_embeddings()

    def load_courses(self, data_file):
        with open(data_file, 'r', encoding='utf-8') as f:
            return json.load(f)

    def compute_course_embeddings(self):
        texts = [f"{course['title']} {course.get('full_description', '')} {' '.join(course.get('key_takeaways', []))}" for course in self.courses]
        return self.model.encode(texts, convert_to_tensor=True)

    def search(self, query, top_k=5):
        query_embedding = self.model.encode(query, convert_to_tensor=True)
        cos_scores = util.cos_sim(query_embedding, self.course_embeddings)[0]
        top_results = torch.topk(cos_scores, k=top_k)
        
        results = []
        for score, idx in zip(top_results[0], top_results[1]):
            results.append({
                'score': score.item(),
                'course': self.courses[idx]
            })
        
        return results

if __name__ == "__main__":
    search_tool = SmartSearchTool('av_courses_detailed.json')
    results = search_tool.search("machine learning for beginners")
    for result in results:
        print(f"Score: {result['score']:.4f}")
        print(f"Title: {result['course']['title']}")
        print(f"URL: {result['course']['url']}")
        print("---")