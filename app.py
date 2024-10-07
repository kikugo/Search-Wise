import streamlit as st
from search_tool import SmartSearchTool

@st.cache_resource
def load_search_tool():
    return SmartSearchTool('av_courses_detailed.json')

def main():
    st.title("Analytics Vidhya Course Search")
    
    search_tool = load_search_tool()
    
    st.sidebar.header("Filters")
    difficulty = st.sidebar.multiselect(
        "Difficulty",
        options=["Beginner", "Intermediate", "Advanced"],
        default=["Beginner", "Intermediate", "Advanced"]
    )
    
    is_free = st.sidebar.checkbox("Show only free courses", value=False)
    
    query = st.text_input("Enter your search query:")
    
    if query:
        results = search_tool.search(query)
        
        filtered_results = [
            result for result in results
            if result['course'].get('difficulty', 'Not specified') in difficulty
            and (not is_free or result['course'].get('is_free', False))
        ]
        
        st.write(f"Found {len(filtered_results)} results")
        
        for result in filtered_results:
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

if __name__ == "__main__":
    main()