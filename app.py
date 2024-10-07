import streamlit as st
import sys
import os
from typing import List, Dict, Any

# Add the project root to the Python path
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from src.search.search_tool import SmartSearchTool

@st.cache_resource
def load_search_tool():
    return SmartSearchTool('data/av_courses_detailed.json')

def get_autocomplete_suggestions(search_tool, partial_query):
    return search_tool.get_autocomplete_suggestions(partial_query)

def display_course_grid(results):
    # Create a 3-column layout
    cols = st.columns(3)
    
    for idx, result in enumerate(results):
        course = result['course']
        with cols[idx % 3]:
            with st.container():
                st.markdown(f"<h4 style='margin-bottom:0;'>{course['title']}</h4>", unsafe_allow_html=True)
                st.markdown(f"<p style='font-size:0.8em; margin-top:0;'>Score: {result['score']:.2f} | 🏆 {course.get('difficulty', 'N/A')} | ⏱️ {course.get('estimated_time', 'N/A')} | ⭐ {course.get('rating', 'N/A')}</p>", unsafe_allow_html=True)
                st.markdown(f"<p style='font-size:0.9em;'>{'🆓' if course.get('is_free', False) else '💰'} | 📚 {course.get('num_lessons', 'N/A')} lessons</p>", unsafe_allow_html=True)
                
                with st.expander("Details"):
                    st.write(course.get('full_description', 'No description available'))
                    st.write("**Key Takeaways:**")
                    for takeaway in course.get('key_takeaways', []):
                        st.write(f"• {takeaway}")
                
                st.markdown(f"[Go to course]({course['url']})", unsafe_allow_html=True)
            st.markdown("---")

def main():
    st.title("Analytics Vidhya Course Search")
    
    search_tool = load_search_tool()
    
    st.write(f"Loaded {len(search_tool.courses)} courses")
    
    if 'page_number' not in st.session_state:
        st.session_state.page_number = 0

    st.sidebar.header("Filters")
    difficulty = st.sidebar.multiselect(
        "Difficulty",
        options=["Beginner", "Intermediate", "Advanced"],
        default=[]
    )
    
    is_free = st.sidebar.checkbox("Show only free courses", value=False)
    
    min_rating = st.sidebar.slider("Minimum Rating", 0.0, 5.0, 0.0, 0.1)
    max_duration = st.sidebar.slider("Maximum Duration (hours)", 0, 100, 100)
    
    topics = st.sidebar.multiselect(
        "Topics",
        options=["Python", "Machine Learning", "Deep Learning", "Data Science", "AI"],
        default=[]
    )
    
    # Autocomplete
    query = st.text_input("Enter your search query:")
    if query:
        suggestions = get_autocomplete_suggestions(search_tool, query)
        if suggestions:
            selected_suggestion = st.selectbox("Did you mean:", [""] + suggestions)
            if selected_suggestion:
                query = selected_suggestion

    if query:
        filters = {
            'difficulty': difficulty,
            'is_free': is_free,
            'min_rating': min_rating,
            'max_duration': max_duration,
            'topics': topics
        }
        results = search_tool.search(query, filters=filters)
        
        st.write(f"Found {len(results)} results")
        
        if results:
            # Pagination
            results_per_page = 9  # Increased to fit 3x3 grid
            total_pages = (len(results) - 1) // results_per_page + 1
            page = st.selectbox("Page", range(1, total_pages + 1)) - 1
            
            start = page * results_per_page
            end = start + results_per_page
            
            display_course_grid(results[start:end])

            st.write(f"Page {page + 1} of {total_pages}")
        else:
            st.write("No results found. Please try a different query or adjust your filters.")

if __name__ == "__main__":
    main()