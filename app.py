import streamlit as st
from search_tool import SmartSearchTool

@st.cache_resource
def load_search_tool():
    return SmartSearchTool('av_courses_detailed.json')

def main():
    st.title("Analytics Vidhya Course Search")
    
    search_tool = load_search_tool()
    
    query = st.text_input("Enter your search query:")
    
    # Add difficulty filter
    difficulties = ['All'] + list(set(course.get('difficulty', 'Not specified') for course in search_tool.courses))
    selected_difficulty = st.selectbox("Filter by difficulty:", difficulties)
    
    # Add price filter
    price_filter = st.radio("Filter by price:", ["All", "Free", "Paid"])
    
    if query:
        results = search_tool.search(query)
        
        # Apply filters
        filtered_results = [
            result for result in results
            if (selected_difficulty == 'All' or result['course'].get('difficulty') == selected_difficulty) and
            (price_filter == 'All' or 
             (price_filter == 'Free' and result['course'].get('is_free', False)) or 
             (price_filter == 'Paid' and not result['course'].get('is_free', True)))
        ]
        
        for result in filtered_results:
            course = result['course']
            st.subheader(course['title'])
            st.write(f"Relevance Score: {result['score']:.4f}")
            st.write(f"Difficulty: {course.get('difficulty', 'Not specified')}")
            st.write(f"Price: {'Free' if course.get('is_free', False) else 'Paid'}")
            st.write(f"Number of Lessons: {course.get('num_lessons', 'Not specified')}")
            st.write(f"Estimated Time: {course.get('estimated_time', 'Not specified')}")
            st.write(f"Rating: {course.get('rating', 'Not specified')}")
            
            with st.expander("Course Summary"):
                st.write(search_tool.summarize_course(course))
            
            with st.expander("Full Description"):
                st.write(course.get('full_description', 'No description available'))
            
            with st.expander("Key Takeaways"):
                for takeaway in course.get('key_takeaways', []):
                    st.write(f"- {takeaway}")
            
            with st.expander("Curriculum"):
                for lesson in course.get('curriculum', []):
                    st.write(f"- {lesson}")
            
            st.write(f"[Go to course]({course['url']})")
            st.write("---")

if __name__ == "__main__":
    main()