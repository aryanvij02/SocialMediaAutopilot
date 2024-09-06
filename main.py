import sys
import argparse 
import os
import time
import uuid
from DEPRECATED.video_content import videos
import json 
from importlib import import_module
import shutil
import re
import requests
from pathlib import Path
from LinkedIn.upload_to_linkedin import upload_to_linkedin
from Tiktok.upload_to_tiktok import upload_to_tiktok
from dynamoDB_management import add_to_dynamodb, update_dynamodb_item
# Add the AIGeneratedVideos directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'AIVideoGeneration'))
from AIVideoGeneration.main import main as ai_main

import subprocess
from openai import OpenAI
import random
from description_samples import DESCRIPTION_SAMPLE, DATA_LINKS
from pydantic import BaseModel
import boto3
from botocore.exceptions import ClientError
from dotenv import load_dotenv
import atexit
import signal

# Load environment variables from .env file
load_dotenv()


PROMPT_INDEX_FILE = 'prompt_index.txt'
DATA_TYPES = ['inbound']
# 'outbound', 'inbound', 'reseller'


tiktok_uploaded_count = 0
tiktok_failed_count = 0
tiktok_uploaded_links = []
youtube_uploaded_count = 0
youtube_failed_count = 0
youtube_uploaded_links = []

def get_prompt_index():
    if os.path.exists(PROMPT_INDEX_FILE):
        with open(PROMPT_INDEX_FILE, 'r') as f:
            return int(f.read().strip())
    return 0

def update_prompt_index(value):
    with open(PROMPT_INDEX_FILE, 'w') as f:
        f.write(str(value))

# Configuration
client = OpenAI(api_key=os.getenv("OPEN_AI_API_KEY"))

class ReturnedContent(BaseModel):
    title: str
    description: str
    hashtags: str
    
def generate_description(link, prompt, example_description):
    # Step 1: Generate script using GPT-4o
    response = client.beta.chat.completions.parse(
        model="gpt-4o-2024-08-06",
        messages = [
            {
                "role": "system",
                "content": "You are an AI assistant that generates data for video uploads."
            },
            {
                "role": "user",
                "content": f'''      
                    You will be given a prompt below that is used to generate a short 30-60 second video script. 
                    Your job is to generate an engaging title for the video, and an engaging description
                    For the title: It needs to be attention grabbing and relevant. It needs to be something people search, such as "Resell AI receptionists OR automate phone calls, etc etc"
                    For the description: It needs to be completely relevant to the prompt and the product. It should also follow the structure of the example provided. Max 200 words.
                    For all line breaks, do not use '\\n'
                    Use triple string quote and actually add "enters" = new lines. Not too many new lines. 
                    Also return 3-4 HASHTAGS with spaces between each hashtag. For example: #ClientEngagement #AIEmpowerment #SaaS #BusinessGrowth
                    
                    Return your response in this format as a JSON. 
                    Always return as a JSON only, nothing before or after. 
                    Do not give ```json before or after
                    Remember to double {{ }} for python!
                    {{     
                    "title": 'title',
                    "description": 'description',
                    "hashtags": 'hashtags'
                    }}
                    ------------
                    Prompt: {prompt}
                    Example: {example_description}
                '''
            }
        ],
        response_format=ReturnedContent
    )
    content = response.choices[0].message.parsed
    # content.strip()
    try:
        # print(content)
        # content_str = json.dumps(content)
        content_dict = content.model_dump()
        return content_dict
    # json.loads(content_str)
    except json.JSONDecodeError as e:
        print("JSON Decode Error:", e)
        print("Content received:", content)
        return None  # or handle the error as needed 

# def upload_failed_videos():
#     print("Entering upload_failed_videos function")
    
#     yt_failed_dir = 'Videos/yt_failed'
#     in_failed_dir = 'Videos/in_failed'
#     tt_failed_dir = 'Videos/tt_failed'

#     def process_directory(directory):
#         print(f"Checking directory: {directory}")
#         if not os.path.exists(directory):
#             print(f"The directory {directory} does not exist.")
#             return []
        
#         print(f"Directory {directory} exists. Checking contents.")
#         all_files = os.listdir(directory)
#         json_files = [f for f in all_files if f.endswith('.json')]
        
#         print(f"All files in directory: {all_files}")
#         print(f"JSON files in directory: {json_files}")
        
#         if not json_files:
#             print(f"No JSON files found in the directory {directory}.")
#             return []
        
#         print(f"Found {len(json_files)} JSON files. Attempting to process them.")
#         return json_files
    
#     yt_json_files = process_directory(yt_failed_dir)
#     in_json_files = process_directory(in_failed_dir)
#     tt_json_files = process_directory(tt_failed_dir)
    
#     # Create a dictionary to track upload success for each video
#     upload_status = {}
    
#     def process_files(json_files, failed_dir, upload_function, platform_name):
#         for file in json_files:
#             file_path = os.path.join(failed_dir, file)
            
#             if os.path.isfile(file_path):
#                 with open(file_path) as f:
#                     video_details = json.load(f)
                
#                 print(f"Uploading to {platform_name}, video found")
#                 success, url = upload_function(video_details)
                
#                 # Get the video directory path
#                 video_dir = Path(video_details['path']).parent
                
#                 if success:
#                     print(f"{platform_name} upload succeeded")
                    
#                     if platform_name == 'tiktok':
#                         update_dynamodb_item(video_details['name'], 'tiktok', video_details['tiktok_account'], True, url)
#                     elif platform_name == 'youtube':
#                         update_dynamodb_item(video_details['name'], 'youtube', video_details['email'], True, url)
                        
#                     os.remove(file_path)
                    
#                     # Update upload status
#                     if video_dir not in upload_status:
#                         upload_status[video_dir] = {"yt": False, "in": False, "tt": False}
#                     upload_status[video_dir][platform_name.lower()[:2]] = True
#                 else:
#                     print(f"{platform_name} upload failed")
            
#             else:
#                 print(f"{platform_name} file not found: {file_path}")
    
#     # Process Tiktok files
#     process_files(tt_json_files, tt_failed_dir, upload_to_tiktok, "tiktok")


#     # Process YouTube files
#     process_files(yt_json_files, yt_failed_dir, upload_to_youtube, "youtube")
    
#     # Process LinkedIn files
#     process_files(in_json_files, in_failed_dir, upload_to_linkedin, "LinkedIn")
    
    
    
#     # Check upload status and remove directories if appropriate
#     for video_dir, status in upload_status.items():
#         yt_success = status["yt"]
#         in_success = status["in"]
#         tt_success = status["tt"]
        
#         yt_file = os.path.join(yt_failed_dir, f"{video_dir.name}.json")
#         in_file = os.path.join(in_failed_dir, f"{video_dir.name}.json")
#         tt_file = os.path.join(tt_failed_dir, f"{video_dir.name}.json")
        
#         if (yt_success and in_success and tt_success) or \
#            (yt_success and in_success and not os.path.exists(tt_file)) or \
#            (yt_success and tt_success and not os.path.exists(in_file)) or \
#            (in_success and tt_success and not os.path.exists(yt_file)):
#             if os.path.exists(video_dir):
#                 shutil.rmtree(video_dir)
#                 print(f"Removed directory: {video_dir}")
#         else:
#             print(f"Kept directory: {video_dir} (YouTube: {yt_success}, LinkedIn: {in_success}, TikTok: {tt_success})")

#     print("Finished processing all files")
    
# def upload_failed_videos():
#     print("Entering upload_failed_videos function")
    
#     yt_failed_dir = 'Videos/yt_failed'
#     # in_failed_dir = 'Videos/in_failed'
#     tt_failed_dir = 'Videos/tt_failed'

#     def process_directory(directory):
#         print(f"Checking directory: {directory}")
#         if not os.path.exists(directory):
#             print(f"The directory {directory} does not exist.")
#             return []
        
#         print(f"Directory {directory} exists. Checking contents.")
#         all_files = os.listdir(directory)
#         json_files = [f for f in all_files if f.endswith('.json')]
        
#         print(f"All files in directory: {all_files}")
#         print(f"JSON files in directory: {json_files}")
        
#         if not json_files:
#             print(f"No JSON files found in the directory {directory}.")
#             return []
        
#         print(f"Found {len(json_files)} JSON files. Attempting to process them.")
#         return json_files
    
#     yt_json_files = process_directory(yt_failed_dir)
#     # in_json_files = process_directory(in_failed_dir)
#     tt_json_files = process_directory(tt_failed_dir)
    
#     # Create a dictionary to track upload success for each video
#     upload_status = {}
    
#     def process_files(json_files, failed_dir, upload_function, platform_name):
#         for file in json_files:
#             file_path = os.path.join(failed_dir, file)
            
#             if os.path.isfile(file_path):
#                 with open(file_path) as f:
#                     video_details = json.load(f)
                
#                 print(f"Uploading to {platform_name}, video found")
#                 print("Adding buffer of 5mins to avoid API rate limiting")
#                 time.sleep(300)
#                 success, yturl_or_tt_retry = upload_function(video_details)
                
#                 # Get the video directory path
#                 video_dir = Path(video_details['path']).parent
                
#                 if success:
#                     print(f"{platform_name} upload succeeded")
                    
#                     if platform_name == 'tiktok':
#                         tiktok_retry_account = "https://www.tiktok.com/@aifrontdesk3?is_from_webapp=1&sender_device=pc" # (myaifrontdesk4@gmail.com)
#                         if yturl_or_tt_retry: 
#                             update_dynamodb_item(video_details['name'], video_details['product'], tiktok_retry_account,'tiktok', True, tiktok_retry_account)
#                         else:
#                             update_dynamodb_item(video_details['name'], video_details['product'], video_details['tiktok_account'],'tiktok', True, video_details['tiktok_account'])
#                     elif platform_name == 'youtube':
#                         update_dynamodb_item(video_details['name'], video_details['product'], video_details['email'], 'youtube', True, yturl_or_tt_retry)
                        
#                     os.remove(file_path)
                    
#                     # Update upload status
#                     if video_dir not in upload_status:
#                         upload_status[video_dir] = {"yt": False, "tt": False}  # Removed "in": False
#                     upload_status[video_dir][platform_name.lower()[:2]] = True
#                 else:
#                     print(f"{platform_name} upload failed")
            
#             else:
#                 print(f"{platform_name} file not found: {file_path}")
    
#     # Process Tiktok files
#     process_files(tt_json_files, tt_failed_dir, upload_to_tiktok, "tiktok")

#     # Process YouTube files
#     process_files(yt_json_files, yt_failed_dir, upload_to_youtube, "youtube")
    
#     # Process LinkedIn files
#     # process_files(in_json_files, in_failed_dir, upload_to_linkedin, "LinkedIn")
    
#     # Check upload status and remove directories if appropriate
#     for video_dir, status in upload_status.items():
#         yt_success = status["yt"]
#         # in_success = status["in"]
#         tt_success = status["tt"]
        
#         yt_file = os.path.join(yt_failed_dir, f"{video_dir.name}.json")
#         # in_file = os.path.join(in_failed_dir, f"{video_dir.name}.json")
#         tt_file = os.path.join(tt_failed_dir, f"{video_dir.name}.json")
        
#         if (yt_success and tt_success) or \
#            (yt_success and not os.path.exists(tt_file)) or \
#            (tt_success and not os.path.exists(yt_file)):
#             if os.path.exists(video_dir):
#                 shutil.rmtree(video_dir)
#                 print(f"Removed directory: {video_dir}")
#         else:
#             print(f"Kept directory: {video_dir} (YouTube: {yt_success}, TikTok: {tt_success})")  # Removed LinkedIn

#     print("Finished processing all files")

def upload_failed_videos():
    print("Entering upload_failed_videos function")
    
    yt_failed_dir = 'Videos/yt_failed'
    tt_failed_dir = 'Videos/tt_failed'

    def process_directory(directory):
        print(f"Checking directory: {directory}")
        if not os.path.exists(directory):
            print(f"The directory {directory} does not exist.")
            return []
        
        print(f"Directory {directory} exists. Checking contents.")
        all_files = os.listdir(directory)
        json_files = [f for f in all_files if f.endswith('.json')]
        
        print(f"All files in directory: {all_files}")
        print(f"JSON files in directory: {json_files}")
        
        if not json_files:
            print(f"No JSON files found in the directory {directory}.")
            return []
        
        print(f"Found {len(json_files)} JSON files. Attempting to process them.")
        return json_files
    
    yt_json_files = process_directory(yt_failed_dir)
    tt_json_files = process_directory(tt_failed_dir)
    
    # Create a dictionary to track upload success for each video
    upload_status = {}
    
    def process_files(json_files, failed_dir, upload_function, platform_name):
        global tiktok_uploaded_count, tiktok_failed_count, youtube_uploaded_count, youtube_failed_count
        global tiktok_uploaded_links, youtube_uploaded_links
        
        for file in json_files:
            file_path = os.path.join(failed_dir, file)
            
            if os.path.isfile(file_path):
                with open(file_path) as f:
                    video_details = json.load(f)
                
                print(f"Uploading to {platform_name}, video found")
                print("Adding buffer of 5mins to avoid API rate limiting")
                # time.sleep(300)
                try:
                    success, yturl_or_tt_retry = upload_function(video_details)
                    
                    # Get the video directory path
                    video_dir = Path(video_details['path']).parent
                    
                    if success:
                        print(f"{platform_name} upload succeeded")
                        
                        if platform_name == 'tiktok':
                            tiktok_retry_account = "https://www.tiktok.com/@aifrontdesk3?is_from_webapp=1&sender_device=pc" # (myaifrontdesk4@gmail.com)
                            tiktok_uploaded_count += 1
                            if yturl_or_tt_retry:
                                tiktok_uploaded_links.append(tiktok_retry_account) 
                                update_dynamodb_item(video_details['name'], video_details['product'], tiktok_retry_account,'tiktok', True, tiktok_retry_account)
                            else:
                                tiktok_uploaded_links.append(video_details['tiktok_account']) 
                                update_dynamodb_item(video_details['name'], video_details['product'], video_details['tiktok_account'],'tiktok', True, video_details['tiktok_account'])
                        elif platform_name == 'youtube':
                            youtube_uploaded_count += 1
                            youtube_uploaded_links.append(yturl_or_tt_retry)
                            update_dynamodb_item(video_details['name'], video_details['product'], video_details['email'], 'youtube', True, yturl_or_tt_retry)
                            
                        os.remove(file_path)
                        
                        # Update upload status
                        if video_dir not in upload_status:
                            upload_status[video_dir] = {"yt": False, "tt": False}
                        upload_status[video_dir][platform_name.lower()[:2]] = True
                    else:
                        print(f"{platform_name} upload failed")
                except Exception as e:
                    print(f"Error uploading to {platform_name}: {str(e)}")
                    print(f"Skipping this file and continuing with the next one.")
            else:
                print(f"{platform_name} file not found: {file_path}")
    
    # Process Tiktok files
    process_files(tt_json_files, tt_failed_dir, upload_to_tiktok, "tiktok")

    # Process YouTube files
    process_files(yt_json_files, yt_failed_dir, upload_to_youtube, "youtube")
    
    # Check upload status and remove directories if appropriate
    for video_dir, status in upload_status.items():
        yt_success = status["yt"]
        tt_success = status["tt"]
        
        yt_file = os.path.join(yt_failed_dir, f"{video_dir.name}.json")
        tt_file = os.path.join(tt_failed_dir, f"{video_dir.name}.json")
        
        if (yt_success and tt_success) or \
           (yt_success and not os.path.exists(tt_file)) or \
           (tt_success and not os.path.exists(yt_file)):
            if os.path.exists(video_dir):
                shutil.rmtree(video_dir)
                print(f"Removed directory: {video_dir}")
        else:
            print(f"Kept directory: {video_dir} (YouTube: {yt_success}, TikTok: {tt_success})")

    print("Finished processing all files")

def upload_to_S3(project_dir):
    """Upload a file to an S3 bucket"""
    
    bucket = 'aisocialmediavideos'
    
    items = [os.path.join(project_dir, "video.mp4"), os.path.join(project_dir, "video_details.json")]
    s3_client = boto3.client(
        's3',
        aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
        aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
        region_name=os.getenv('AWS_DEFAULT_REGION')
    )
    
    for item in items:
        pattern = r'^(\.\/)?(\/)?Videos(?!\/failed)'
        item_name = re.sub(pattern, '', item)
        try:
            s3_client.upload_file(item, bucket, item_name, ExtraArgs={'ACL': 'public-read'})
            
        except ClientError as e:
            print("Failed S3 upload")
            print(e)
            return None, False
    print("Uploaded to S3 successfully")
    
    pattern_2 = r'^\/([^\/]+)\/'
    match = re.search(pattern_2, item_name)
    if match:
        extracted_name = match.group(1)
        url = f"https://{bucket}.s3.amazonaws.com//{extracted_name}/video.mp4"
        return url, True
    
    else:
        return None, False   
        
    
                
              
#Uploads videos to youtube directly!     
def upload_to_youtube(video_details):
    upload_script_path = os.path.join(os.path.dirname(__file__), 'Youtube2', 'upload.mjs')
    video_details_json = json.dumps(video_details)    
    try:    
        result = subprocess.run(['node', upload_script_path, video_details_json],
                            check=True, 
                            capture_output=True, 
                            text=True
                            )
        
        # Parse the output to find the video URL
        output_lines = result.stdout.split('\n')
        video_url = None
        for line in output_lines:
            try:
                data = json.loads(line)
                if data.get('status') == 'success':
                    video_url = data.get('videoUrl')
                    break
            except json.JSONDecodeError:
                continue
        
        if video_url:
            print(f"Upload successful. Video URL: {video_url}")
            return True, video_url
        else:
            print("Upload successful, but couldn't find video URL in the output.")
            return True, None
    
    except subprocess.CalledProcessError as e:
        print("Upload failed!")
        print("Error output:", e.stderr)
        return False, None      
# def upload_to_youtube(video_details):
#     upload_script_path = os.path.join(os.path.dirname(__file__), 'Youtube2', 'upload.mjs')
#     video_details_json = json.dumps(video_details)    
#     try:    
#         result = subprocess.run(['node', upload_script_path, video_details_json],
#                             check=True, 
#                             capture_output=True, 
#                             text=True
#                             )
        
#         print("Upload successful")
#         return True, result.stdout
    
#     except subprocess.CalledProcessError as e:
#             # The script returned a non-zero exit code
#             print("Upload failed!")
#             print("Error output:", e.stderr)
#             return False, e.stderr       
def send_slack_message(message):
    webhook_url = "https://hooks.slack.com/services/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"
    
    payload = {
        "text": message
    }
    
    response = requests.post(webhook_url, json=payload)
    
    if response.status_code == 200:
        print("Slack message sent successfully")
        return True
    else:
        print(f"Failed to send Slack message. Status code: {response.status_code}")
        return False     

def reinstall_package():
    try:
        result = subprocess.run(["node", "reinstall_package.js"], check=True)
        print("Package reinstalled successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Failed to reinstall package: {e}", file=sys.stderr)
        return False
    
def cleanup_and_save_progress(signum=None, frame=None, exception_occurred=False):
    global tiktok_uploaded_count, tiktok_failed_count, youtube_uploaded_count, youtube_failed_count
    global tiktok_uploaded_links, youtube_uploaded_links
    
    # Add a flag to ensure this function runs only once
    if hasattr(cleanup_and_save_progress, 'has_run'):
        return
    cleanup_and_save_progress.has_run = True
    
    print("Performing cleanup and saving progress...")
    
    if exception_occurred:
        slack_message = f'''
        Something went wrong, app has crashed.
        TikTok Successful Uploads: {tiktok_uploaded_count},
        TikTok Failed Uploads: {tiktok_failed_count},
        Youtube Successful Uploads: {youtube_uploaded_count},
        Youtube Failed Uploads: {youtube_failed_count},
        ----------------------------------------------
        TikTok Account Links: {tiktok_uploaded_links},
        Youtube Account Links: {youtube_uploaded_links}
        '''
    
    else:
        slack_message = f'''
        App ran successfully today!
        TikTok Successful Uploads: {tiktok_uploaded_count},
        TikTok Failed Uploads: {tiktok_failed_count},
        Youtube Successful Uploads: {youtube_uploaded_count},
        Youtube Failed Uploads: {youtube_failed_count},
        ----------------------------------------------
        TikTok Account Links: {tiktok_uploaded_links},
        Youtube Account Links: {youtube_uploaded_links}
        '''
    
    send_slack_message(slack_message)
    
    for data_type in DATA_TYPES:
        videos_dir = f'Videos'
        if os.path.exists(videos_dir):
            for project_dir in os.listdir(videos_dir):
                full_project_dir = os.path.join(videos_dir, project_dir)
                if os.path.isdir(full_project_dir):
                    video_details_path = os.path.join(full_project_dir, 'video_details.json')
                    if os.path.exists(video_details_path):
                        with open(video_details_path, 'r') as f:
                            video_details = json.load(f)
                        
                        #Youtube
                        yt_failed_dir = os.path.join('Videos', 'yt_failed')
                        os.makedirs(yt_failed_dir, exist_ok=True)
                        yt_failed_file_path = os.path.join(yt_failed_dir, f'{project_dir}_video_details.json')
                        with open(yt_failed_file_path, 'w') as json_file:
                            json.dump(video_details, json_file)
                            
                        #LinkedIn
                        # in_failed_dir = os.path.join('Videos', 'in_failed')
                        # os.makedirs(in_failed_dir, exist_ok=True)
                        # in_failed_file_path = os.path.join(in_failed_dir, f'{project_dir}_video_details.json')
                        # with open(in_failed_file_path, 'w') as json_file:
                        #     json.dump(video_details, json_file)
                            
                        #Tiktok
                        in_failed_dir = os.path.join('Videos', 'tt_failed')
                        os.makedirs(in_failed_dir, exist_ok=True)
                        in_failed_file_path = os.path.join(in_failed_dir, f'{project_dir}_video_details.json')
                        with open(in_failed_file_path, 'w') as json_file:
                            json.dump(video_details, json_file)
                        
                        print(f"Saved progress for {project_dir}")
    
    print("Cleanup completed.")
    if signum is not None:
        sys.exit(0)
        

def main():
    global tiktok_uploaded_count, tiktok_failed_count, youtube_uploaded_count, youtube_failed_count
    global tiktok_uploaded_links, youtube_uploaded_links
    
    curr_youtube_links = []

    try:
        exception_occured = False
        reinstall_result = reinstall_package()
        print(f"Package reinstall result: {reinstall_result}")

        print("Calling upload_failed_videos")
        try:
            upload_failed_videos()
        except Exception as e:
            print(f"Error in upload_failed_videos: {e}")
            print(f"Error type: {type(e)}")
            import traceback
            traceback.print_exc()
        
        prompt_index = get_prompt_index()
        print("Starting from prompt index " + str(prompt_index))

        for data_type in DATA_TYPES:
            print(f"\nProcessing {data_type.capitalize()} Data:")
            module = import_module(f'creds_and_content.{data_type}_info')
            
            credentials = getattr(module, f'{data_type}_credentials')
            prompts = getattr(module, f'{data_type}_prompts')
            
            daily_prompt = prompts[prompt_index]

            for i, credential in enumerate(credentials):
                vertical_list = getattr(module, f'{data_type}_verticals_{i+1}')
                
                # vertical_list = vertical_list[0]  # Note: This line might need revision based on your needs
                
                for vertical in vertical_list:
                    formatted_prompt = daily_prompt + vertical
                    
                    print("This is the prompt", formatted_prompt)
                    print("This is the vertical", vertical)
                    
                    example_description, data_links = DESCRIPTION_SAMPLE[data_type], DATA_LINKS[data_type]
                    description_info = generate_description(data_links, formatted_prompt, example_description) 
                    description_info['description'] = f"Link: {data_links} \n" + description_info['description']

                    name = f"{data_type}_{uuid.uuid4()}"
                    
                    project_dir = ai_main(name, formatted_prompt)
                    
                    if isinstance(project_dir, Path):
                        project_dir = str(project_dir)
                        
                    video_details = {
                        "name": name,
                        "path": os.path.join(project_dir, "video.mp4"),
                        "title": description_info['title'],
                        "description": description_info['description'],
                        "hashtags": description_info['hashtags'],
                        "email": credential['email'],
                        "pass": credential['password'],
                        "in_urn": credential['linkedin_urn'],
                        "in_access_token": credential['linkedin_access_token'],
                        "tt_refresh_token": credential['tiktok_refresh_token'],
                        "tiktok_account": credential['tiktok_account'],
                        "product": data_type
                    }
                        
                    data = {
                        'dir': project_dir,
                        'video_details': video_details
                    }
                    
                    with open(os.path.join(project_dir, 'video_details.json'), 'w') as json_file:
                        json.dump(video_details, json_file)
                        
                    url, s3_result = upload_to_S3(data['dir'])
                    
                    if s3_result:
                        data['video_details']['s3_url'] = url
                        with open(os.path.join(project_dir, 'video_details.json'), 'w') as json_file:
                            json.dump(data['video_details'], json_file) 
                        
                        dynamodb_result = add_to_dynamodb(data['video_details'])
                        
                        if dynamodb_result:
                            print("Saved successfully to DynamoDB")
                        else:
                            print("DynamoDB saving failed")
                        
                        # Immediate upload to TikTok
                        print("Uploading to TikTok")
                        tt_success, tiktok_retried = upload_to_tiktok(data['video_details'])
                        tiktok_retry_account = "https://www.tiktok.com/@aifrontdesk3?is_from_webapp=1&sender_device=pc"
                        
                        if not tt_success:
                            tiktok_failed_count += 1
                            tt_failed_dir = os.path.join('Videos', 'tt_failed')
                            os.makedirs(tt_failed_dir, exist_ok=True)
                            tt_failed_file_path = os.path.join(tt_failed_dir, f'{os.path.basename(project_dir)}_video_details.json')
                            with open(tt_failed_file_path, 'w') as json_file:
                                json.dump(data['video_details'], json_file)
                            update_dynamodb_item(data['video_details']['name'], video_details['product'], data['video_details']['tiktok_account'], 'tiktok', False, data['video_details']['tiktok_account'])
                        else:
                            tiktok_uploaded_count += 1
                            if tiktok_retried:
                                tiktok_uploaded_links.append(tiktok_retry_account)
                                update_dynamodb_item(data['video_details']['name'], video_details['product'], tiktok_retry_account, 'tiktok', True, tiktok_retry_account)
                            else:
                                tiktok_uploaded_links.append(data['video_details']['tiktok_account'])
                                update_dynamodb_item(data['video_details']['name'], video_details['product'], data['video_details']['tiktok_account'], 'tiktok', True, data['video_details']['tiktok_account'])
                        
                        # Immediate upload to YouTube
                        print("Uploading to YouTube")
                        yt_success, youtube_url = upload_to_youtube(data['video_details'])
                        
                        if not yt_success:
                            youtube_failed_count += 1
                            yt_failed_dir = os.path.join('Videos', 'yt_failed')
                            os.makedirs(yt_failed_dir, exist_ok=True)
                            yt_failed_file_path = os.path.join(yt_failed_dir, f'{os.path.basename(project_dir)}_video_details.json')
                            with open(yt_failed_file_path, 'w') as json_file:
                                json.dump(data['video_details'], json_file)
                            update_dynamodb_item(data['video_details']['name'], video_details['product'], data['video_details']['email'], 'youtube', False, youtube_url)
                        else:
                            youtube_uploaded_count += 1
                            youtube_uploaded_links.append(youtube_url)
                            curr_youtube_links.append(youtube_url)
                            update_dynamodb_item(data['video_details']['name'], video_details['product'], data['video_details']['email'], 'youtube', True, youtube_url)

                        # If both uploads are successful, remove the directory
                        if tt_success and yt_success:
                            shutil.rmtree(project_dir)
                    else:
                        print("S3 Upload Failed")
                        
            slack_message = f'''
            Videos uploaded for account: {credential['email']},
            TikTok Account URL: {data['video_details']['tiktok_account']},
            Youtube Video Links: {curr_youtube_links},
            '''
            send_slack_message()            
            

    # except Exception as e:
    #     print(f"An error occurred: {e}")
    #     exception_occured = True
    #     raise
           
# def main(): 
#     global tiktok_uploaded_count, tiktok_failed_count, youtube_uploaded_count, youtube_failed_count
#     global tiktok_uploaded_links, youtube_uploaded_links
    
#     try:
#         exception_occured = False
#         #Uninstall and reinstall youtube-video-uploader package
#         reinstall_result = reinstall_package()
#         print(f"Package reinstall result: {reinstall_result}")

#         print("Calling upload_failed_videos")
#         try:
#             upload_failed_videos()
#         except Exception as e:
#             print(f"Error in upload_failed_videos: {e}")
#             print(f"Error type: {type(e)}")
#             import traceback
#             traceback.print_exc()
        
#         prompt_index = get_prompt_index()
#         print("Starting from prompt index " + str(prompt_index))

#         for data_type in DATA_TYPES:
#             print(f"\nProcessing {data_type.capitalize()} Data:")
#             module = import_module(f'creds_and_content.{data_type}_info')
            
#             credentials = getattr(module, f'{data_type}_credentials')
#             prompts = getattr(module, f'{data_type}_prompts')
            
#             # Get the single prompt for the day
#             daily_prompt = prompts[prompt_index]

#             for i, credential in enumerate(credentials):
#                 vertical_list = getattr(module, f'{data_type}_verticals_{i+1}')
                
#                 ##DELETE THIS
#                 vertical_list = vertical_list[0]
#                 ###
                
#                 directories = []
                
#                 for vertical in vertical_list:
#                     formatted_prompt = daily_prompt + vertical
                    
#                     print("This is the prompt", formatted_prompt)
#                     print("This is the vertical", vertical)
                    
#                     # Generate description
#                     example_description, data_links = DESCRIPTION_SAMPLE[data_type], DATA_LINKS[data_type]
#                     description_info = generate_description(data_links, formatted_prompt, example_description) 
#                     description_info['description'] = f"Link: {data_links} \n" + description_info['description']

#                     # Generate file name
#                     name = f"{data_type}_{uuid.uuid4()}"
                    
#                     project_dir = ai_main(name, formatted_prompt)
                    
#                     if isinstance(project_dir, Path):
#                         project_dir = str(project_dir)
                        
#                     video_details = {
#                         "name": name,
#                         "path": os.path.join(project_dir, "video.mp4"),
#                         "title": description_info['title'],
#                         "description": description_info['description'],
#                         "hashtags": description_info['hashtags'],
#                         "email": credential['email'],
#                         "pass": credential['password'],
#                         "in_urn": credential['linkedin_urn'],
#                         "in_access_token": credential['linkedin_access_token'],
#                         "tt_refresh_token": credential['tiktok_refresh_token'],
#                         "tiktok_account": credential['tiktok_account'],
#                         "product": data_type
#                     }
                        
#                     data = {
#                         'dir': project_dir,
#                         'video_details': video_details
#                     }
                    
#                     with open(os.path.join(project_dir, 'video_details.json'), 'w') as json_file:
#                             json.dump(video_details, json_file)
                            
#                     #Upload vid + data to S3 bucket upon generation
#                     url, s3_result = upload_to_S3(data['dir'])
                    
                    
#                     if s3_result:
#                         #This is for subsequent uploading to Youtube/Tiktok/LinkedIn
#                         data['video_details']['s3_url'] = url
#                         #This is where we save that json file
#                         with open(os.path.join(project_dir, 'video_details.json'), 'w') as json_file:
#                             json.dump(data['video_details'], json_file) 
#                         directories.append(data)
                        
#                         #Once video is created and uploaded to S3, then we want to save data to dynamoDB
#                         dynamodb_result = add_to_dynamodb(data['video_details'])
                        
#                         if dynamodb_result:
#                             print("Saved successfully to DynamoDB")
#                         else:
#                             print("DynamoDB saving failed")
                        
#                     else:
#                         print("S3 Upload Failed")
                    
#                     ###DELETE THIS    
#                     # break
                
#                 #After generating videos for each credential, try uploading them one by one
#                 for data in directories:
#                     #Add a 5minute buffer between each upload to avoid rate limiting
#                     print("Starting 5 minute buffer")
#                     # time.sleep(300)
#                     print("Uploading to Tiktok")
#                     tt_success, tiktok_retried = upload_to_tiktok(data['video_details'])
#                     tiktok_retry_account = "https://www.tiktok.com/@aifrontdesk3?is_from_webapp=1&sender_device=pc" # (myaifrontdesk4@gmail.com)
                    

#                     # print("Uploading to LinkedIn")
#                     # in_success = upload_to_linkedin(data['video_details'])
                                
#                     print("Uploading to Youtube")
#                     yt_success, youtube_url = upload_to_youtube(data['video_details'])
                    
#                     #If the tiktok upload failed
#                     if not tt_success:
#                         tiktok_failed_count += 1
#                         tt_failed_dir = os.path.join('Videos', 'tt_failed')
#                         os.makedirs(tt_failed_dir, exist_ok=True)  # Ensure the directory exists

#                         tt_failed_file_path = os.path.join(tt_failed_dir, f'{os.path.basename(data["dir"])}_video_details.json')

#                         #Saves a json file with the video_details
#                         with open(tt_failed_file_path, 'w') as json_file:
#                             #This JSON still refers to the initial file path and video file
#                             json.dump(data['video_details'], json_file)
#                         update_dynamodb_item(data['video_details']['name'], video_details['product'], data['video_details']['tiktok_account'], 'tiktok', False, data['video_details']['tiktok_account'])
#                     else:
#                         tiktok_uploaded_count += 1
#                         if tiktok_retried:
#                             tiktok_uploaded_links.append(tiktok_retry_account)
#                             update_dynamodb_item(data['video_details']['name'], video_details['product'], tiktok_retry_account, 'tiktok', True, tiktok_retry_account)
#                         else:
#                             tiktok_uploaded_links.append(data['video_details']['tiktok_account'])
#                             update_dynamodb_item(data['video_details']['name'], video_details['product'], data['video_details']['tiktok_account'], 'tiktok', True, data['video_details']['tiktok_account'])

#                     #If the youtube upload failed
#                     if not yt_success:
#                         youtube_failed_count += 1
#                         yt_failed_dir = os.path.join('Videos', 'yt_failed')
#                         os.makedirs(yt_failed_dir, exist_ok=True)  # Ensure the directory exists

#                         yt_failed_file_path = os.path.join(yt_failed_dir, f'{os.path.basename(data["dir"])}_video_details.json')

#                         #Saves a json file with the video_details
#                         with open(yt_failed_file_path, 'w') as json_file:
#                             #This JSON still refers to the initial file path and video file
#                             json.dump(data['video_details'], json_file)
#                         update_dynamodb_item(data['video_details']['name'], video_details['product'], data['video_details']['email'], 'youtube', False, youtube_url)
#                     else:
#                         youtube_uploaded_count += 1
#                         youtube_uploaded_links.append(youtube_url)
#                         update_dynamodb_item(data['video_details']['name'], video_details['product'], data['video_details']['email'], 'youtube', True, youtube_url)

                    
#                     #If linkedin upload failed
#                     # if not in_success:
#                     #     in_failed_dir = os.path.join('Videos', 'in_failed')
#                     #     os.makedirs(in_failed_dir, exist_ok=True)  # Ensure the directory exists

#                     #     in_failed_file_path = os.path.join(in_failed_dir, f'{os.path.basename(data["dir"])}_video_details.json')

#                     #     #Saves a json file with the video_details
#                     #     with open(in_failed_file_path, 'w') as json_file:
#                     #         #This JSON still refers to the initial file path and video file
#                     #         json.dump(data['video_details'], json_file) 
                        
#                     #If the video has uploaded successfully to both places, delete the file directory 
                    
#                     if tt_success and yt_success:
#                         shutil.rmtree(data['dir'])
                
#                 ###DELETE THIS
#                 # break
#             # break
#         #####
            
            
        # Update the prompt index for the next day
        next_prompt_index = (prompt_index + 1) % len(prompts)
        update_prompt_index(next_prompt_index)
                
    # except Exception as e:
    #     exception_occured = True
    #     print(f"An error occurred: {e}")
        
    # finally:
    #     if exception_occured:
    #         cleanup_and_save_progress(None, None, True)
    #     else:
    #         cleanup_and_save_progress(None, None, False)
    
    except Exception as e:
        print(f"An error occurred: {e}")
        cleanup_and_save_progress(exception_occurred=True)
    else:
        cleanup_and_save_progress(exception_occurred=False)


                
if __name__ == "__main__":
    # Register the cleanup function to run at exit
    # atexit.register(cleanup_and_save_progress)

    # Register the cleanup function for SIGINT (Ctrl+C) and SIGTERM
    signal.signal(signal.SIGINT, lambda signum, frame: cleanup_and_save_progress(signum, frame, True))
    signal.signal(signal.SIGTERM, lambda signum, frame: cleanup_and_save_progress(signum, frame, True))

# Add argument parsing
    parser = argparse.ArgumentParser(description="Video upload script with retry functionality")
    parser.add_argument('--retry', action='store_true', help='Retry uploading failed videos only')
    args = parser.parse_args()

    # If --retry flag is provided, only run upload_failed_videos()
    if args.retry:
        print("Retrying failed video uploads...")
        reinstall_package()   
        upload_failed_videos()
    else:
        # Run the full main function if --retry is not provided
        main()    
    
    
    
    # video_details = {
    #             "path": "./Videos/inbound_3767/video.mp4",
    #             "title": "Never Miss a Call: AI Receptionist for Food Trucks",
    #             "description": "Link: https://www.myaifrontdesk.com/ \nRunning a food truck business and tired of missing calls after closing hours? Discover My AI Front Desk, the innovative virtual receptionist that ensures you never lose a customer. Specially designed for food truck owners, our AI answers calls 24/7, managing everything from scheduling to customer inquiries with ease. The AI receptionist is integrated seamlessly with your calendar, allowing it to set up appointments and respond to questions even when you're not available. Setting it up is a breeze; simply fill out a form and share your calendar. Within ten minutes, your AI front desk is rea  to handle all incoming calls without the hassle of technical integrations or lengthy onboarding. Elevate your customer service and watch your business thrive with My AI Front Desk, your trusty 24/7 call answering solution.", 
    #             "email": "videos@myaifrontdesk.com",
    #             "pass": "myaifrontdesk101$"
    #     }
    # # upload_to_youtube(video_details)
    # upload_to_S3("./Videos/inbound_3768")
    
    
    
    # def upload_failed_videos():
#     yt_success = False
#     in_success = False
    
#     print("Entering upload_failed_videos function")
#     yt_failed_dir = 'Videos/yt_failed'
    
#     print(f"Checking directory: {yt_failed_dir}")
#     if not os.path.exists(yt_failed_dir):
#         print(f"The directory {yt_failed_dir} does not exist.")
#         return
    
#     print(f"Directory {yt_failed_dir} exists. Checking contents.")
#     yt_all_files = os.listdir(yt_failed_dir)
#     yt_json_files = [f for f in yt_all_files if f.endswith('.json')]
    
#     print(f"All files in directory: {yt_all_files}")
#     print(f"JSON files in directory: {yt_json_files}")
    
#     if not yt_json_files:
#         print(f"No JSON files found in the directory {yt_all_files}.")
#         return
    
#     print(f"Found {len(yt_json_files)} JSON files. Attempting to process them.")
#     for file_name in yt_json_files:
#         file_path = os.path.join(yt_all_files, file_name)
#         if os.path.isfile(file_path):
#             # Process each file here
#             with open(file_path) as f:
#                 video_details = json.load(f)
                
#                 print("Uploading to youtube, video found")
#                 success, output = upload_to_youtube(video_details)
                
#                 #If the upload failed, try next
#                 if not success:
#                     print("Failed upload again")
#                     continue   
                
#                 #If the video has uploaded successfully, delete the file directory and the .json
#                 else:
#                     print("Succeeded upload")
#                     directory = Path(video_details['path']).parent
#                     #Removes the folder
#                     shutil.rmtree(directory)
#                     #Removes json in Videos/failed folder
#                     os.remove(file_path)
                    
#     # Code for processing files in 'in_failed' directory similar to 'yt_failed' directory
# in_failed_dir = 'Videos/in_failed'

# print(f"Checking directory: {in_failed_dir}")
# if not os.path.exists(in_failed_dir):
#     print(f"The directory {in_failed_dir} does not exist.")
#     return

# print(f"Directory {in_failed_dir} exists. Checking contents.")
# in_all_files = os.listdir(in_failed_dir)
# in_json_files = [f for f in in_all_files if f.endswith('.json')]

# print(f"All files in directory: {in_all_files}")
# print(f"JSON files in directory: {in_json_files}")

# if not in_json_files:
#     print(f"No JSON files found in the directory {in_all_files}.")
#     return

# print(f"Found {len(in_json_files)} JSON files. Attempting to process them.")
# for file_name in in_json_files:
#     file_path = os.path.join(in_failed_dir, file_name)
#     if os.path.isfile(file_path):
#         # Process each file here
#         with open(file_path) as f:
#             video_details = json.load(f)
            
#             print("Uploading to YouTube, video found")
#             success, output = upload_to_youtube(video_details)
            
#             # If the upload failed, try next
#             if not success:
#                 print("Failed upload again")
#                 continue   
            
#             # If the video has uploaded successfully, delete the file directory and the .json
#             else:
#                 print("Succeeded upload")
#                 directory = Path(video_details['path']).parent
#                 # Removes the folder
#                 shutil.rmtree(directory)
#                 # Removes json in Videos/in_failed folder
#                 os.remove(file_path)