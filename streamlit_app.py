import streamlit as st
import boto3
from botocore.exceptions import NoCredentialsError

# AWS S3 Configuration from secrets.toml
AWS_ACCESS_KEY = st.secrets["aws"]["AWS_ACCESS_KEY"]
AWS_SECRET_KEY = st.secrets['aws']["AWS_SECRET_KEY"]
NON_ANNOTATED_BUCKET_NAME = st.secrets['aws']["NON_ANNOTATED_BUCKET_NAME"]
ANNOTATED_BUCKET_NAME = st.secrets['aws']["ANNOTATED_BUCKET_NAME"]
REGION_NAME = st.secrets['aws']["REGION_NAME"]

# Initialize S3 client
s3 = boto3.client(
    's3',
    aws_access_key_id=AWS_ACCESS_KEY,
    aws_secret_access_key=AWS_SECRET_KEY,
    region_name=REGION_NAME
)

def list_videos():
    try:
        response = s3.list_objects_v2(Bucket=NON_ANNOTATED_BUCKET_NAME)
        if 'Contents' in response:
            return [obj['Key'] for obj in response['Contents'] if obj['Key'].lower().endswith(('.mp4', '.avi', '.mov'))]
        return []
    except NoCredentialsError:
        st.error("AWS credentials not found.")
        return []
    

def get_video_url(video_key):
    # Generate a pre-signed URL for private S3 buckets
    return s3.generate_presigned_url(
        'get_object',
        Params={'Bucket': NON_ANNOTATED_BUCKET_NAME, 'Key': video_key},
        ExpiresIn=3600  # URL expires in 1 hour
    )

def list_annotated_videos():
    try:
        response = s3.list_objects_v2(Bucket=ANNOTATED_BUCKET_NAME)
        if 'Contents' in response:
            return [obj['Key'] for obj in response['Contents'] if obj['Key'].lower().endswith(('.mp4', '.avi', '.mov'))]
        return []
    except NoCredentialsError:
        st.error("AWS credentials not found.")
        return []
    
def load_video_from_s3(key):
    try:
        video_obj = s3.get_object(Bucket=ANNOTATED_BUCKET_NAME, Key=key)
        return video_obj['Body'].read()
    except Exception as e:
        st.error(f"Failed to load video: {e}")
        return None


st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Annotated Videos", "Video Viewer", "Author Bio"])

if page == "Annotated Videos":
    video_keys = list_annotated_videos()

    if video_keys:
        selected_video_key = st.selectbox("Select a video", video_keys)
        video_bytes = load_video_from_s3(selected_video_key)
        if video_bytes:
            st.video(video_bytes)
    else:
        st.write("No annotated videos found.")

    

elif page == "Video Viewer":
    videos = list_videos()
    if not videos:
        st.write("No videos found in the S3 bucket.")
    selected_video_1 = st.selectbox("Choose the first video to view:", videos, key="video1")
    video_url_1 = get_video_url(selected_video_1)
    st.video(video_url_1, format="video/mp4")

elif page == "Author Bio":
    st.title("Author Bio")
    st.write("""
    **Author:** John Doe  
    **Role:** Software Engineer and AI Enthusiast  
    **Description:** John specializes in developing AI-powered applications and cloud-based solutions.  
    This project is aimed at simplifying the annotation and review process for swimming videos.  
    """)
    st.write("Feel free to reach out for collaboration or feedback!")
