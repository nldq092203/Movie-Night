from firebase_admin import storage
import uuid
import urllib.parse

def upload_to_firebase(file, folder='avatars'):
    """Uploads a file to Firebase Storage and returns the file's URL."""
    # Create a unique filename using UUID
    filename = f"{uuid.uuid4()}_{file.name}"

    # Get a reference to Firebase Storage bucket
    bucket = storage.bucket()

    # Create a reference for the file in a specific folder
    blob = bucket.blob(f'{folder}/{filename}')

    # Upload the file to Firebase
    blob.upload_from_file(file)

    # Make the file publicly accessible
    blob.make_public()

    # Return the public URL of the uploaded file
    return blob.public_url

def delete_from_firebase(file_path):
    """Deletes a file from Firebase Storage."""
    try:
        # Get a reference to Firebase Storage
        bucket = storage.bucket()

        # Decode the URL-encoded file path
        decoded_file_path = urllib.parse.unquote(file_path)

        # Create a reference to the file in the bucket
        blob = bucket.blob(decoded_file_path)

        # Delete the file from Firebase
        blob.delete()


        return True
    except Exception as e:
        print(f"Error deleting file from Firebase: {e}")
        return False