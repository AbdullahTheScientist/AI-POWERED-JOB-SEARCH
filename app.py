
import streamlit as st
import pandas as pd
import os
import json
import tempfile
import PyPDF2
import docx
from datetime import datetime, timedelta
# Import the UI utilities for improved display
from ui_utils import (
    format_job_description
)

# Import configuration
from config import COLORS, JOB_PLATFORMS

# Set page configuration with professional appearance
st.set_page_config(
    page_title="Professional Job Search Assistant",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded"
)


# Initialize tools and agents
@st.cache_resource
def load_resources():
    """Load and cache all required resources."""
    from utils.serp_api_searcher import SerpApiSearcher
    from agents.job_search_agent import JobSearchAgent
    
    job_search_agent = JobSearchAgent()
    serp_api_searcher = SerpApiSearcher()
    
    return {
        "job_search_agent": job_search_agent,
        "serp_api_searcher": serp_api_searcher,
    }

# Load resources
resources = load_resources()

# Application header with gradient using color palette
st.markdown(f"""
<div style='text-align:center; padding: 1.5rem 0; 
background: linear-gradient(90deg, {COLORS["primary"]}, {COLORS["secondary"]}, {COLORS["tertiary"]}); 
border-radius: 12px; margin-bottom: 2rem; box-shadow: 0 4px 12px rgba(0,0,0,0.1);'>
    <h1 style='color: white; font-size: 2.5rem; margin-bottom: 0.5rem; text-shadow: 1px 1px 3px rgba(0,0,0,0.3);'>
    Professional Job Search Assistant</h1>
    <p style='color: white; font-size: 1.2rem; font-weight: 500; margin: 0.5rem 2rem; text-shadow: 1px 1px 2px rgba(0,0,0,0.2);'>
    <span style='background-color: rgba(0,0,0,0.15); padding: 4px 12px; border-radius: 20px; margin: 0 5px;'>
    AI-powered job search</span> 
    <span style='background-color: rgba(0,0,0,0.15); padding: 4px 12px; border-radius: 20px; margin: 0 5px;'>
    Resume analysis</span> 
    <span style='background-color: rgba(0,0,0,0.15); padding: 4px 12px; border-radius: 20px; margin: 0 5px;'>
    Interview preparation</span>
    </p>
</div>
""", unsafe_allow_html=True)

if "job_results" not in st.session_state:
    st.session_state.job_results = []

# Create main navigation tabs
tabs = st.tabs([
    "🔍 Job Search"
])


# Tab 2: Job Search
with tabs[0]:
    st.header("Job Search")
    
    # Common job titles and locations
    common_job_titles = [
        "Data Scientist", "Software Engineer", "Product Manager", "Data Analyst",
        "Machine Learning Engineer", "Frontend Developer", "Backend Developer",
        "Full Stack Developer", "DevOps Engineer", "UX Designer", "AI Engineer",
        "Cloud Architect", "Database Administrator", "Project Manager", "Business Analyst",
        "Java Developer", "Python Developer", "React Developer", "Android Developer",
        "iOS Developer", "Node.js Developer", "Data Engineer", "Blockchain Developer",
        "Cybersecurity Analyst", "Quality Assurance Engineer"
    ]
    
    locations = [
        "Remote",
        "New York, NY", "San Francisco, CA", "Seattle, WA", "Austin, TX",
        "Boston, MA", "Chicago, IL", "Los Angeles, CA", "Atlanta, GA", "Denver, CO",
        "Bangalore, India", "Hyderabad, India", "Mumbai, India", "Delhi, India",
        "Pune, India", "Chennai, India", "London, UK", "Berlin, Germany", "Toronto, Canada"
    ]
    
    # Create search tabs
    search_tabs = st.tabs(["Custom Search"])
    

    # Custom Search Tab
    with search_tabs[0]:
        # Job search form
        with st.form("job_search_form"):
            st.subheader("Search Criteria")
            
            # Create a 2-column layout for job title and location
            col1, col2 = st.columns(2)
            
            with col1:
                keywords = st.selectbox("Job Title:", common_job_titles, key="job_titles")
            
            with col2:
                location = st.selectbox("Location:", locations, key="locations")
            
            # Advanced filters accordion
            with st.expander("Advanced Filters", expanded=False):
                # Job type selection
                job_types = ["Full-time", "Part-time", "Contract", "Internship", "Remote"]
                selected_job_types = st.multiselect("Job Types (optional):", job_types, key="job_types")
                
                # Experience level
                experience_level = st.select_slider(
                    "Years of experience:",
                    options=["0-1", "1-3", "3-5", "5-10", "10+"],
                    value="1-3",
                    key="experience_level"
                )
                
                # Recency filter
                recency = st.select_slider(
                    "Show jobs posted within:",
                    options=["1 day", "3 days", "1 week", "2 weeks", "1 month", "Any time"],
                    value="1 week",
                    key="recency"
                )
                
                # Platform selection
                selected_platforms = st.multiselect(
                    "Job Platforms:",
                    options=JOB_PLATFORMS,
                    default=JOB_PLATFORMS,
                    key="platforms"
                )
                
                # Number of results
                job_count = st.slider("Jobs per platform:", 3, 20, 5, key="job_count")
                
                # Use SerpAPI option
                use_serp_api = st.checkbox("Use SerpAPI for real job listings", value=True, key="use_serp_api")
            
            submit_search = st.form_submit_button("Search Jobs")
        
        # Execute job search
        if submit_search:
            # Build the search query including job types and experience
            search_query = keywords
            
            # Add job types to query if selected
            if selected_job_types:
                search_query += f" {' '.join(selected_job_types)}"
            
            # Add experience level to query if needed
            if experience_level != "1-3":  # If not default
                search_query += f" {experience_level} years"
            
            # Convert recency to days for API
            recency_days = {
                "1 day": 1, "3 days": 3, "1 week": 7,
                "2 weeks": 14, "1 month": 30, "Any time": 365
            }
            days_ago = recency_days.get(recency, 7)
            
            search_message = f"Searching for {search_query} jobs in {location}"
            search_message += f" posted within the last {recency}"
            if selected_job_types:
                search_message += f" ({', '.join(selected_job_types)})"
            
            with st.spinner(search_message):
                jobs = []
                
                if use_serp_api:
                    # Use SerpAPI to get real job listings
                    serp_api_searcher = resources["serp_api_searcher"]
                    for platform in selected_platforms:
                        try:
                            platform_jobs = serp_api_searcher.search_jobs(
                                search_query,
                                location,
                                platform=platform,
                                count=job_count,
                                days_ago=days_ago
                            )
                            jobs.extend(platform_jobs)
                        except Exception as e:
                            st.error(f"Error searching jobs on {platform}: {str(e)}")
                    
                    if not jobs:
                        st.warning("No jobs found via SerpAPI. Falling back to standard search.")
                        job_search_agent = resources["job_search_agent"]
                        try:
                            jobs = job_search_agent.search_jobs(
                                # st.session_state.resume_data,
                                search_query,
                                location=location,
                                platform=selected_platforms,
                                count=job_count
                            )
                        except Exception as e:
                            st.error(f"Error in job search: {str(e)}")
                else:
                    # Use standard job search
                    job_search_agent = resources["job_search_agent"]
                    try:
                        jobs = job_search_agent.search_jobs(
                            # st.session_state.resume_data,
                            search_query,
                            location,
                            platforms=selected_platforms,
                            count=job_count
                        )
                    except Exception as e:
                        st.error(f"Error in job search: {str(e)}")
                
                st.session_state.job_results = jobs
    
    # Display job results (common to both search methods)
    if st.session_state.job_results:
        total_jobs = len(st.session_state.job_results)
        st.subheader(f"Job Results ({total_jobs})")
        
        # Filter options
        col1, col2 = st.columns(2)
        with col1:
            # Sort options
            sort_option = st.selectbox(
                "Sort by:",
                ["Most Recent", "Relevance", "Company Name", "Location"],
                key="sort_option"
            )
        
        with col2:
            # Filter by platform
            filter_platform = st.selectbox(
                "Filter by platform:",
                ["All Platforms"] + JOB_PLATFORMS,
                key="filter_platform"
            )
        
        # Apply platform filter
        filtered_jobs = st.session_state.job_results
        if filter_platform != "All Platforms":
            filtered_jobs = [job for job in filtered_jobs if job.get("platform", "").lower() == filter_platform.lower()]
        
        # Sort jobs based on selection
        sorted_jobs = filtered_jobs.copy()
        # print(type(sorted_jobs))
        # for job in sorted_jobs:
        #     sorted_jobs = job['jobs_results']
        # print(sorted_jobs)
        if sort_option == "Most Recent":
            # Try to parse dates for sorting
            for job in sorted_jobs:
                if job.get("date_posted") and isinstance(job["date_posted"], str):
                    try:
                        if "hour" in job["date_posted"].lower():
                            hours = int(''.join(filter(str.isdigit, job["date_posted"].split()[0])))
                            job["sort_date"] = datetime.now() - timedelta(hours=hours)
                        elif "day" in job["date_posted"].lower():
                            days = int(''.join(filter(str.isdigit, job["date_posted"].split()[0])))
                            job["sort_date"] = datetime.now() - timedelta(days=days)
                        elif "week" in job["date_posted"].lower():
                            weeks = int(''.join(filter(str.isdigit, job["date_posted"].split()[0])))
                            job["sort_date"] = datetime.now() - timedelta(weeks=weeks)
                        elif "month" in job["date_posted"].lower():
                            months = int(''.join(filter(str.isdigit, job["date_posted"].split()[0])))
                            job["sort_date"] = datetime.now() - timedelta(days=30 * months)
                        else:
                            job["sort_date"] = datetime.now() - timedelta(days=365)
                    except (ValueError, IndexError):
                        job["sort_date"] = datetime.now() - timedelta(days=365)
                else:
                    job["sort_date"] = datetime.now() - timedelta(days=365)
            
            sorted_jobs.sort(key=lambda x: x.get("sort_date"), reverse=False)
        elif sort_option == "Company Name":
            sorted_jobs.sort(key=lambda x: x.get("company", "").lower())
        elif sort_option == "Location":
            sorted_jobs.sort(key=lambda x: x.get("location", "").lower())
         
        if not sorted_jobs:
            st.warning(f"No jobs found for the selected platform: {filter_platform}")
        else:
            # Create a dataframe for easier display
            job_df = pd.DataFrame([
                {
                    "Title": job["title"],
                    "Company": job["company"],
                    "Location": job.get("location", "Not specified"),
                    "Platform": job.get("platform", "Unknown"),
                    "Posted": job.get("date_posted", "Recent"),
                    "Job Type": job.get("job_type", ""),
                    "Real Job": "✓" if job.get("is_real_job", False) else "?"
                }
                for job in sorted_jobs
            ])
            
            # Display jobs in a dataframe with improved styling
            st.dataframe(
                job_df,
                use_container_width=True,
                column_config={
                    "Title": st.column_config.TextColumn("Job Title"),
                    "Real Job": st.column_config.TextColumn("Verified")
                },
                hide_index=True
            )
            
            # Job selection for detailed view
            if sorted_jobs:
                st.markdown("### Job Details")
                selected_index = st.selectbox(
                    "Select a job to view details:",
                    range(len(sorted_jobs)),
                    format_func=lambda i: f"{sorted_jobs[i]['title']} at {sorted_jobs[i]['company']}",
                    key="job_selection"
                )
                
                if selected_index is not None:
                    st.session_state.selected_job = sorted_jobs[selected_index]
                    selected_job = st.session_state.selected_job
                    
                    # Job title and company with professional styling
                    st.markdown(f"""
                    <div style='background: linear-gradient(90deg, {COLORS["primary"]}, {COLORS["secondary"]}); 
                    padding: 1rem; border-radius: 10px; margin-bottom: 1rem; box-shadow: 0 3px 10px rgba(0,0,0,0.2);'>
                        <h3 style='color: white; margin: 0; font-weight: 600; text-shadow: 1px 1px 3px rgba(0,0,0,0.3);'>{selected_job['title']}</h3>
                        <p style='color: white; font-size: 1.1rem; margin: 0.5rem 0 0 0; text-shadow: 1px 1px 2px rgba(0,0,0,0.2);'>{selected_job['company']}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Create columns for job details
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.markdown(f"""<div style="background-color: {COLORS["primary"]}; color: white; 
                        padding: 10px; border-radius: 8px; text-align: center; box-shadow: 0 2px 5px rgba(0,0,0,0.1);">
                        <p style="margin: 0; font-weight: bold; text-shadow: 1px 1px 2px rgba(0,0,0,0.2);">Location</p>
                        <p style="margin: 0; text-shadow: 1px 1px 2px rgba(0,0,0,0.1);">{selected_job.get('location', 'Not specified')}</p>
                        </div>""", unsafe_allow_html=True)
                    
                    with col2:
                        st.markdown(f"""<div style="background-color: {COLORS["primary"]}; color: white; 
                        padding: 10px; border-radius: 8px; text-align: center; box-shadow: 0 2px 5px rgba(0,0,0,0.1);">
                        <p style="margin: 0; font-weight: bold; text-shadow: 1px 1px 2px rgba(0,0,0,0.2);">Platform</p>
                        <p style="margin: 0; text-shadow: 1px 1px 2px rgba(0,0,0,0.1);">{selected_job.get('platform', 'Unknown')}</p>
                        </div>""", unsafe_allow_html=True)
                    
                    with col3:
                        st.markdown(f"""<div style="background-color: {COLORS["primary"]}; color: white; 
                        padding: 10px; border-radius: 8px; text-align: center; box-shadow: 0 2px 5px rgba(0,0,0,0.1);">
                        <p style="margin: 0; font-weight: bold; text-shadow: 1px 1px 2px rgba(0,0,0,0.2);">Posted</p>
                        <p style="margin: 0; text-shadow: 1px 1px 2px rgba(0,0,0,0.1);">{selected_job.get('date_posted', 'Recent')}</p>
                        </div>""", unsafe_allow_html=True)
                    
                    # Job type if available
                    if selected_job.get('job_type'):
                        st.markdown(f"""<div style="background-color: {COLORS["secondary"]}; color: white; 
                        padding: 8px 15px; border-radius: 20px; display: inline-block; margin: 10px 0; box-shadow: 0 2px 5px rgba(0,0,0,0.1);">
                        <span style="text-shadow: 1px 1px 1px rgba(0,0,0,0.2);">{selected_job.get('job_type')}</span></div>""", unsafe_allow_html=True)
                    
                    # Apply button
                    if selected_job.get('apply_url'):
                        apply_url = selected_job['apply_url']
                        is_real_job = selected_job.get('is_real_job', False)
                        
                        st.markdown(f"""
                        <div style="background-color: {COLORS["accent"]}; padding: 12px; 
                        border-radius: 6px; margin: 15px 0; text-align: center; box-shadow: 0 3px 8px rgba(0,0,0,0.15);">
                        <a href="{apply_url}" target="_blank" style="color: white; 
                        text-decoration: none; font-weight: bold; display: block; text-shadow: 1px 1px 2px rgba(0,0,0,0.2);">
                        {'➡️ Apply Now' if is_real_job else '➡️ View Job Details'}</a>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        if is_real_job:
                            st.success("This is a real job listing from a job search platform.")
                        else:
                            st.warning("This is a generated job listing for demonstration purposes.")
                    
                    # Job description
                    if selected_job.get('description'):
                        st.subheader("Job Description")
                        st.markdown(format_job_description(selected_job['description']), unsafe_allow_html=True)
                    else:
                        st.warning("No job description available.")