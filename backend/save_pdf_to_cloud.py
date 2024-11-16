from google.cloud import storage
from google.oauth2 import service_account
import os

from const import BUCKET_NAME

# Configure Google Cloud Storage credentials
credentials = service_account.Credentials.from_service_account_file(
    os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
)
bucket_name = BUCKET_NAME

def upload_pdf_to_google_cloud(pdf_data, file_name):
    """Upload PDF data to Google Cloud Storage and return the public URL."""
    # Initialize a Google Cloud Storage client with the provided credentials
    client = storage.Client(credentials=credentials)
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(file_name)

    # Upload the PDF binary data to the bucket
    blob.upload_from_string(pdf_data, content_type='application/pdf')

    # Make the file publicly accessible and get the URL
    blob.make_public()
    return blob.public_url  # Return the public URL of the uploaded PDF