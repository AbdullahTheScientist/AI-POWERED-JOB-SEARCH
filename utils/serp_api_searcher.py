import json
import requests
from config import SERPAPI_API_KEY




import requests

# SerpDogAPI

class SerpApiSearcher:
    def search_jobs(self, keywords, location, platform=None, count=5, days_ago=5):
        try:
            url = "https://api.scrapingdog.com/google_jobs"
            api_key = "68031c85580e2c83a197311a"

            params = {
                "api_key": api_key,
                "query": f"{keywords} jobs in {location}",
                # "country": "us",
                "language": "en_us",
                "chips": f"date_posted:{days_ago}d"
            }

            response = requests.get(url, params=params)
            
            if response.status_code == 200:
                data = response.json()
                # return data
            # else:
            #     print(f"Request failed with status code: {response.status_code}")
            #     return []
            if "error" in data:
                print(f"ScrapingDog API error: {data['error']}")
                return []

            jobs = []
            if "jobs_results" in data:
                job_results = data["jobs_results"]

                for i, job in enumerate(job_results):
                    if i >= count:
                        break

                    title = job.get("title", "Unknown Title")
                    company = job.get("company_name", "Unknown Company")
                    location_name = job.get("location", "Unknown Location")
                    
                    description = job.get("description") or job.get("snippet", "No available description")

                    # Extract job type
                    job_type = "Not Specified"
                    if "detected_extensions" in job:
                        ext = job["detected_extensions"]
                        job_type = ext.get("schedule_type") or ext.get("employment_type", job_type)
            

                    # Apply URL
                    apply_url = None
                    if "apply_link" in job and "link" in job["apply_link"]:
                        apply_url = job["apply_link"]["link"]
                    elif "apply_options" in job and job["apply_options"]:
                        apply_url = job["apply_options"][0].get("link")
                    elif "job_id" in job and "related_links" in data:
                        for link in data.get("related_links", []):
                            if "apply" in link.get("text", "").lower():
                                apply_url = link.get("link")
                                break
                    if not apply_url and "job_id" in job:
                        apply_url = f"https://www.google.com/search?q={job['job_id']}"

                    date_posted = "Recent"
                    if "detected_extensions" in job and "posted_at" in job["detected_extensions"]:
                        date_posted = job["detected_extensions"]["posted_at"]

                    job_platform = job.get("via", "unknown")

                    if platform and platform.lower() != "all" and platform.lower() not in job_platform.lower():
                        continue

                    job_entry = {
                        "title": title,
                        "company": company,
                        "location": location_name,
                        "description": description,
                        "url": apply_url,
                        "apply_url": apply_url,
                        "date_posted": date_posted,
                        "platform": job_platform,
                        "job_type": job_type,
                        "is_real_job": True
                    }

                    jobs.append(job_entry)

                return jobs
            else:
                print("No job results found in response.")
                return []

        except Exception as e:
            print(f"ScrapingDog API error: {e}")
            return []

# # if __name__ == '__main__':
# #     search_query = "data scientist jobs in usa"
# #     location = 'us'
# #     job_count = 3
# #     days_ago =3
# #     jobs =[]
# #     serp_api_searcher = SerpApiSearcher()
# #     platform_jobs = serp_api_searcher.search_jobs(
# #                             keywords=search_query,
# #                             location=location,
# #                             # platform=platform,
# #                             count=job_count,
# #                             days_ago=days_ago
# #                             )
# #     jobs.extend(platform_jobs)

# #   jobs = []
                
# #                 if use_serp_api:
# #                     # Use SerpAPI to get real job listings
# #                     serp_api_searcher = resources["serp_api_searcher"]
# #                     for platform in selected_platforms:
# #                         try:
# #                             platform_jobs = serp_api_searcher.search_jobs(
# #                                 search_query,
# #                                 location,
# #                                 platform=platform,
# #                                 count=job_count,
# #                                 days_ago=days_ago
# #                             )
# #                             jobs.extend(platform_jobs)


# from config import SERPAPI_API_KEY

# class SerpApiSearcher:
#     """Search for real jobs using SerpAPI's Google Jobs search."""
    
#     def search_jobs(self, keywords, location, platform=None, count=5, days_ago=7):
#         """
#         Search for jobs using SerpAPI's Google Jobs API.
        
#         Args:
#             keywords (str): Job title or keywords to search for
#             location (str): Location for the job search
#             platform (str, optional): Specific platform to filter by
#             count (int): Maximum number of jobs to return
#             days_ago (int): Number of days ago to limit search results
            
#         Returns:
#             list: List of job dictionaries with details and direct links
#         """
#         if not SERPAPI_API_KEY:
#             print("SerpAPI key not configured. Returning empty results.")
#             return []
            

#         try:
#             # Base URL for SerpAPI Google Jobs
#             url = "https://serpapi.com/search"
            
#             # Prepare query parameters
#             query = f"{keywords} jobs in {location}"
#             if platform and platform.lower() != "all":
#                 query += f" {platform}"
                
#             params = {
#                 "engine": "google_jobs",
#                 "q": query,
#                 "api_key": SERPAPI_API_KEY,
#                 "hl": "en",
#                 "chips": f"date_posted:{days_ago}d"  # Add date filter
#             }
            
#             # Make API request
#             response = requests.get(url, params=params)
#             data = response.json()
            
#             # Check for API errors
#             if "error" in data:
#                 print(f"SerpAPI error: {data['error']}")
#                 return []
                
#             # Process job results
#             jobs = []
#             if "jobs_results" in data:
#                 job_results = data["jobs_results"]
                
#                 for i, job in enumerate(job_results):
#                     if i >= count:
#                         break
                    
#                     # Extract job details
#                     title = job.get("title", "Unknown Title")
#                     company = job.get("company_name", "Unknown Company")
#                     location_name = job.get("location", "Unknown Location")
                    
#                     # Get job description
#                     description = ""
#                     if "description" in job:
#                         description = job["description"]
#                     elif "snippet" in job:
#                         description = job["snippet"]
#                     else:
#                         description = "No description available"
                    
#                     # Extract job type information
#                     job_type = "Not specified"
#                     if "detected_extensions" in job:
#                         extensions = job["detected_extensions"]
#                         if "schedule_type" in extensions:
#                             job_type = extensions["schedule_type"]
#                         elif "employment_type" in extensions:
#                             job_type = extensions["employment_type"]
                    
#                     # Get apply link - SerpAPI provides direct application links
#                     apply_url = None
                    
#                     # Try to get the apply link from various possible locations
#                     if "apply_link" in job and "link" in job["apply_link"]:
#                         apply_url = job["apply_link"]["link"]
#                     elif "apply_options" in job and job["apply_options"]:
#                         apply_url = job["apply_options"][0].get("link")
#                     elif "job_id" in job and "related_links" in data:
#                         # Try to find in related links
#                         for link in data.get("related_links", []):
#                             if "apply" in link.get("text", "").lower():
#                                 apply_url = link.get("link")
#                                 break
                    
#                     # If still no apply URL, use job_id to create a Google Jobs link
#                     if not apply_url and "job_id" in job:
#                         apply_url = f"https://www.google.com/search?q={job['job_id']}"
                    
#                     # Get job date
#                     date_posted = "Recent"
#                     if "detected_extensions" in job and "posted_at" in job["detected_extensions"]:
#                         date_posted = job["detected_extensions"]["posted_at"]
                    
#                     # Determine platform from extensions or application options
#                     job_platform = job.get("via", "Unknown")
                    
#                     # Filter by platform if specified
#                     if platform and platform.lower() != "all" and platform.lower() not in job_platform.lower():
#                         continue
                    
#                     # Create job entry
#                     job_entry = {
#                         "title": title,
#                         "company": company,
#                         "location": location_name,
#                         "description": description,
#                         "url": apply_url,  # The direct application URL
#                         "apply_url": apply_url,  # Duplicate for consistency
#                         "date_posted": date_posted,
#                         "platform": job_platform,
#                         "job_type": job_type,  # Add job type information
#                         "is_real_job": True  # Flag to indicate this is a real job listing
#                     }
                    
#                     # Add job to results
#                     jobs.append(job_entry)
                
#             return jobs
            
#         except Exception as e:
#             print(f"SerpAPI search error: {e}")
#             return []