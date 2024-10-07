import streamlit as st
import sys
import os

# Add the project root to the Python path
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from src.search.search_tool import SmartSearchTool

@st.cache_resource
def load_search_tool():
    return SmartSearchTool('data/av_courses_detailed.json')

def main():
    st.title("Analytics Vidhya Course Search")
    
    search_tool = load_search_tool()
    
    if 'page_number' not in st.session_state:
        st.session_state.page_number = 0

    st.sidebar.header("Filters")
    difficulty = st.sidebar.multiselect(
        "Difficulty",
        options=["Beginner", "Intermediate", "Advanced"],
        default=["Beginner", "Intermediate", "Advanced"]
    )
    
    is_free = st.sidebar.checkbox("Show only free courses", value=False)
    
    query = st.text_input("Enter your search query:")
    
    if query:
        filters = {
            'difficulty': difficulty,
            'is_free': is_free
        }
        results = search_tool.search(query, filters=filters)
        
        st.write(f"Found {len(results)} results")
        
        # Pagination
        results_per_page = 5
        start = st.session_state.page_number * results_per_page
        end = start + results_per_page

        for result in results[start:end]:
            course = result['course']
            st.subheader(course['title'])
            st.write(f"Relevance Score: {result['score']:.4f}")
            st.write(f"Difficulty: {course.get('difficulty', 'Not specified')}")
            st.write(f"Estimated Time: {course.get('estimated_time', 'Not specified')}")
            st.write(f"Rating: {course.get('rating', 'Not specified')}")
            st.write(f"Number of Lessons: {course.get('num_lessons', 'Not specified')}")
            st.write(f"Free: {'Yes' if course.get('is_free', False) else 'No'}")
            
            with st.expander("Course Description"):
                st.write(course.get('full_description', 'No description available'))
            
            with st.expander("Key Takeaways"):
                takeaways = course.get('key_takeaways', [])
                if takeaways:
                    for takeaway in takeaways:
                        st.write(f"• {takeaway}")
                else:
                    st.write("No key takeaways available")
            
            st.write(f"[Go to course]({course['url']})")
            st.write("---")

        # Pagination controls
        col1, col2, col3 = st.columns([1,1,1])
        if st.session_state.page_number > 0:
            if col1.button('Previous'):
                st.session_state.page_number -= 1
        if end < len(results):
            if col3.button('Next'):
                st.session_state.page_number += 1

        st.write(f"Page {st.session_state.page_number + 1} of {len(results) // results_per_page + 1}")

if __name__ == "__main__":
    main()