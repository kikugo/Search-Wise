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
    
    query = st.text_input("Enter your search query:")

    if query:
        # Perform initial search without filters
        initial_results = search_tool.search(query)
        
        # Apply filters to the initial results
        filtered_results = [
            result for result in initial_results
            if (not difficulty or result['course'].get('difficulty') in difficulty) and
               (not is_free or result['course'].get('is_free', False)) and
               (result['course'].get('rating', 0) >= min_rating) and
               (result['course'].get('estimated_time', 0) <= max_duration) and
               (not topics or any(topic.lower() in result['course'].get('title', '').lower() for topic in topics))
        ]
        
        st.write(f"Found {len(filtered_results)} results")
        
        if filtered_results:
            results_per_page = 9
            total_pages = (len(filtered_results) - 1) // results_per_page + 1
            page = st.selectbox("Page", range(1, total_pages + 1), index=0) - 1
            
            start = page * results_per_page
            end = start + results_per_page
            
            display_course_grid(filtered_results[start:end])

            st.write(f"Page {page + 1} of {total_pages}")
        else:
            st.write("No results found. Please try a different query or adjust your filters.")
    else:
        st.write("Enter a search query to find courses.")

if __name__ == "__main__":
    main()