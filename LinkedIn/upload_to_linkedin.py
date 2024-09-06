import requests
import json


# API endpoints
REGISTER_UPLOAD_URL = "https://api.linkedin.com/v2/assets?action=registerUpload"
UGC_POSTS_URL = "https://api.linkedin.com/v2/ugcPosts"


def register_upload(headers, person_urn):
    data = {
        "registerUploadRequest": {
            "recipes": ["urn:li:digitalmediaRecipe:feedshare-video"],
            "owner": f"urn:li:person:{person_urn}",
            "serviceRelationships": [
                {
                    "relationshipType": "OWNER",
                    "identifier": "urn:li:userGeneratedContent"
                }
            ]
        }
    }
    response = requests.post(REGISTER_UPLOAD_URL, headers=headers, json=data)
    response.raise_for_status()
    return response.json()

def upload_video(access_token, upload_url, video_path):
    print(f"Uploading video from: {video_path}")
    print(f"Upload URL: {upload_url}")
    
    with open(video_path, 'rb') as video_file:
        files = {'file': ('video.mp4', video_file, 'video/mp4')}
        upload_headers = {
            "Authorization": f"Bearer {access_token}",
        }
        try:
            response = requests.post(upload_url, headers=upload_headers, files=files)
            print(f"Response status code: {response.status_code}")
            print(f"Response content: {response.content}")
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            print(f"Error during upload: {e}")
            print(f"Response content: {e.response.content if e.response else 'No response'}")
            raise
    return response

def create_video_share(person_urn, headers, asset, title, description):
    data = {
        "author": f"urn:li:person:{person_urn}",
        "lifecycleState": "PUBLISHED",
        "specificContent": {
            "com.linkedin.ugc.ShareContent": {
                "shareCommentary": {
                    "text": description
                },
                "shareMediaCategory": "VIDEO",
                "media": [
                    {
                        "status": "READY",
                        "description": {
                            "text": description
                        },
                        "media": asset,
                        "title": {
                            "text": title
                        }
                    }
                ]
            }
        },
        "visibility": {
            "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
        }
    }
    response = requests.post(UGC_POSTS_URL, headers=headers, json=data)
    response.raise_for_status()
    return response.json()

 
def upload_to_linkedin(video_details):
    person_urn = video_details['in_urn']
    # print(f"Person URN: {person_urn}")

    access_token = video_details['in_access_token']
    # print(f"Access Token: {access_token}")

    video_path = video_details['path']
    # print(f"Video Path: {video_path}")

    title = video_details['title']
    # print(f"Title: {title}")

    description = video_details['description']
    # print(f"Description: {description}")
    
    
    # Headers for all requests
    headers = {
        "Authorization": f"Bearer {access_token}",
        "X-Restli-Protocol-Version": "2.0.0",
        "Content-Type": "application/json"
    }
    
    try:
        # Step 1: Register the upload
        register_response = register_upload(headers, person_urn)
        upload_url = register_response['value']['uploadMechanism']['com.linkedin.digitalmedia.uploading.MediaUploadHttpRequest']['uploadUrl']
        asset = register_response['value']['asset']

        print(f"Upload URL: {upload_url}")
        print(f"Asset: {asset}")

        # Step 2: Upload the video
        upload_video(access_token, upload_url, video_path)

        # Step 3: Create the video share
        share_response = create_video_share(person_urn, headers, asset, title, description)
        print("Video shared successfully!")
        print(f"Share ID: {share_response['id']}")
        return True
    except Exception as e:
        print(f"An error occurred: {e}")
        return False
               
