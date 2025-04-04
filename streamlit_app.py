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

# Streamlit UI
st.title("Annotated Swimming Videos")

videos = list_videos()
if not videos:
    st.write("No videos found in the S3 bucket.")
else:
    selected_video = st.selectbox("Choose a video to view:", videos)
    video_url = get_video_url(selected_video)
    
    #st.write(f"Video URL: {video_url}")  # Debugging: Display the video URL
    st.video(video_url, format="video/mp4")  # Ensure correct format
    st.write(f"Video Source: {video_url}")
