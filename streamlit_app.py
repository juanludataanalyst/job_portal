import streamlit as st
import pandas as pd

# Set page configuration
st.set_page_config(
    page_title="Job Portal",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Add title and description
st.title("Job Portal")
st.write("Browse available job opportunities and select positions you're interested in.")

# Sample job data
jobs_data = {
    "Title": [
        "Software Engineer", 
        "Data Scientist", 
        "Product Manager", 
        "UX Designer", 
        "DevOps Engineer",
        "Marketing Specialist",
        "Sales Representative",
        "Customer Support",
        "HR Manager",
        "Financial Analyst"
    ],
    "Company": [
        "Tech Co", 
        "Data Inc", 
        "Product Labs", 
        "Design Studio", 
        "Cloud Systems",
        "Marketing Pro",
        "Sales Force",
        "Support Hub",
        "People First",
        "Finance Group"
    ],
    "Location": [
        "Remote", 
        "New York", 
        "San Francisco", 
        "London", 
        "Berlin",
        "Toronto",
        "Sydney",
        "Singapore",
        "Paris",
        "Tokyo"
    ],
    "Type": [
        "Full-time",
        "Full-time",
        "Contract",
        "Part-time",
        "Full-time",
        "Full-time",
        "Commission",
        "Part-time",
        "Full-time",
        "Contract"
    ],
    "Salary": [
        "$120,000", 
        "$130,000", 
        "$140,000", 
        "$110,000", 
        "$125,000",
        "$80,000",
        "$70,000 + commission",
        "$55,000",
        "$95,000",
        "$105,000"
    ],
    "Experience": [
        "3+ years",
        "2+ years",
        "5+ years",
        "3+ years",
        "4+ years",
        "2+ years",
        "1+ years",
        "Entry level",
        "7+ years",
        "3+ years"
    ],
    "Posted": [
        "2023-04-01",
        "2023-04-03",
        "2023-04-05",
        "2023-04-07",
        "2023-04-10",
        "2023-04-12",
        "2023-04-15",
        "2023-04-18",
        "2023-04-20",
        "2023-04-22"
    ]
}

# Create dataframe
jobs_df = pd.DataFrame(jobs_data)

# Add sidebar filters
st.sidebar.header("Filter Jobs")

# Location filter
locations = ["All"] + sorted(jobs_df["Location"].unique().tolist())
selected_location = st.sidebar.selectbox("Location", locations)

# Job type filter
job_types = ["All"] + sorted(jobs_df["Type"].unique().tolist())
selected_type = st.sidebar.selectbox("Job Type", job_types)

# Experience level filter
experience_filter = st.sidebar.slider(
    "Experience (years)",
    0, 10, (0, 10)
)

# Apply filters
filtered_df = jobs_df.copy()

if selected_location != "All":
    filtered_df = filtered_df[filtered_df["Location"] == selected_location]

if selected_type != "All":
    filtered_df = filtered_df[filtered_df["Type"] == selected_type]

# Filter by experience (extract numeric value from experience string)
filtered_df["Experience_Numeric"] = filtered_df["Experience"].str.extract(r'(\d+)').fillna(0).astype(int)
filtered_df = filtered_df[
    (filtered_df["Experience_Numeric"] >= experience_filter[0]) & 
    (filtered_df["Experience_Numeric"] <= experience_filter[1])
]
filtered_df = filtered_df.drop(columns=["Experience_Numeric"])

# Display number of results
st.write(f"Showing {len(filtered_df)} of {len(jobs_df)} jobs")

# Display as interactive dataframe with selection
job_selection = st.dataframe(
    filtered_df,
    column_config={
        "Title": st.column_config.TextColumn("Job Title", width="medium"),
        "Company": st.column_config.TextColumn("Company", width="medium"),
        "Location": st.column_config.TextColumn("Location", width="small"),
        "Type": st.column_config.TextColumn("Job Type", width="small"),
        "Salary": st.column_config.TextColumn("Salary", width="small"),
        "Experience": st.column_config.TextColumn("Experience", width="small"),
        "Posted": st.column_config.DateColumn("Posted Date", format="MMM DD, YYYY", width="small"),
    },
    use_container_width=True,
    hide_index=True,
    selection_mode="multi-row",
    on_select="rerun"
)

# Show selected jobs
if hasattr(job_selection, 'selection') and job_selection.selection.rows:
    st.header("Selected Jobs")
    selected_indices = job_selection.selection.rows
    selected_jobs = filtered_df.iloc[selected_indices]
    
    st.dataframe(
        selected_jobs,
        use_container_width=True,
        hide_index=True
    )
    
    # Add application button for selected jobs
    if st.button("Apply for Selected Jobs"):
        st.success(f"Application submitted for {len(selected_indices)} jobs!")
        
        # Display application form (in a real app, this would be more sophisticated)
        with st.expander("Application Details", expanded=True):
            st.text_input("Full Name")
            st.text_input("Email")
            st.text_input("Phone")
            st.file_uploader("Upload Resume (PDF)", type=["pdf"])
            st.text_area("Cover Letter")
            if st.button("Submit Application"):
                st.success("Your application has been submitted successfully!")
else:
    st.info("Select jobs you're interested in by clicking on rows in the table above.")

# Add footer
st.markdown("---")
st.caption("Job Portal Demo - Built with Streamlit")