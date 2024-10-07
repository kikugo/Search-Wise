import unittest
from src.search.search_tool import SmartSearchTool

class TestSearch(unittest.TestCase):
    def setUp(self):
        self.search_tool = SmartSearchTool('data/av_courses_detailed.json')

    def test_search(self):
        results = self.search_tool.search("machine learning")
        self.assertEqual(len(results), 5)
        self.assertTrue('score' in results[0])
        self.assertTrue('course' in results[0])

    def test_search_with_filters(self):
        results = self.search_tool.search("python", filters={'difficulty': ['Beginner'], 'is_free': True})
        self.assertTrue(all(course['course'].get('difficulty') == 'Beginner' for course in results))
        self.assertTrue(all(course['course'].get('is_free') for course in results))

if __name__ == '__main__':
    unittest.main()