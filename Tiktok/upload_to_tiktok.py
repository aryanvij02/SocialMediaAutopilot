# from Tiktok.access_token import access_token
# import requests
# import json


# # def upload_to_tiktok(video_details):
# #     refresh_token = video_details['tt_refresh_token']
# #     video_url = video_details['s3_url']
    
# #     # First, get the access token
# #     access_token_value, open_id = access_token(refresh_token)
    
# #     # Prepare the upload request
# #     url = "https://business-api.tiktok.com/open_api/v1.3/business/video/publish/"
    
# #     headers = {
# #         "Access-Token": access_token_value,
# #         "Content-Type": "application/json"
# #     }
    
# #     payload = {
# #         "business_id": open_id,
# #         "video_url": video_url,
# #         "post_info": {
# #             "caption": f"{video_details['title']} {video_details['hashtags']}",
# #             "disable_comment": False,
# #             "disable_duet": False,
# #             "disable_stitch": False
# #         }
# #     }
    
# #     # Make the upload request
# #     response = requests.post(url, headers=headers, data=json.dumps(payload))
    
# #     if response.status_code == 200:
# #         data = response.json()
# #         if data.get("code") == 0 and data.get("message") == "OK":
# #             print("Tiktok upload successful!")
# #             return True, True
# #         else:
# #             print("Failed TikTok")
# #             print(f"API error: {data.get('message')}")
# #             raise Exception(f"API error: {data.get('message')}")
# #     else:
# #         print("HTTP error:", response.status_code)
# #         raise Exception(f"HTTP error: {response.status_code}")

# def upload_to_tiktok(video_details):
#     def attempt_upload(refresh_token):
#         # Get the access token
#         access_token_value, open_id = access_token(refresh_token)
        
#         # Prepare the upload request
#         url = "https://business-api.tiktok.com/open_api/v1.3/business/video/publish/"
        
#         headers = {
#             "Access-Token": access_token_value,
#             "Content-Type": "application/json"
#         }
        
#         payload = {
#             "business_id": open_id,
#             "video_url": video_details['s3_url'],
#             "post_info": {
#                 "caption": f"{video_details['title']} {video_details['hashtags']}",
#                 "disable_comment": False,
#                 "disable_duet": False,
#                 "disable_stitch": False
#             }
#         }
        
#         # Make the upload request
#         response = requests.post(url, headers=headers, data=json.dumps(payload))
        
#         if response.status_code == 200:
#             data = response.json()
#             if data.get("code") == 0 and data.get("message") == "OK":
#                 print("TikTok upload successful!")
#                 return True
#             else:
#                 print("Failed TikTok")
#                 print(f"API error: {data.get('message')}")
#                 return False
#         else:
#             print("HTTP error:", response.status_code)
#             return False

#     # First attempt with the original refresh token
#     if attempt_upload(video_details['tt_refresh_token']):
#         return True, False

#     # If the first attempt fails due to rate limiting, try with the alternate account
#     else:
#         print("Attempting upload with alternate account...")
#         alternate_refresh_token = "rft.HIhT0DTM2viclZDGetMTD4NWCWwBtd3Nwi1BzuGESL1ZXGXURPDC6EuAth5N!6411.u1"  # The alternate account's refresh token (myaifrontdesk4@gmail.com)
#         if attempt_upload(alternate_refresh_token):
#             return True, True

#     # If both attempts fail, raise an exception
#     raise Exception("Failed to upload to TikTok with both accounts")

# # Example usage
# if __name__ == "__main__":
#     refresh_token = "rft.ySKKMj4o6Mp0ovmhwFrAge5y8ecRZYctj5DZx4EGVRAIjZACLkA6twgqfg7m!6362.u1"
#     video_url = "https://aisocialmediavideos.s3.amazonaws.com//inbound_1819/video.mp4"
#     video_details = {
#         "title": "Automate Client Bookings:",
#         "hashtags": "#AI #AutomateBookings #Automation"
#     }
    
#     try:
#         upload_result = upload_to_tiktok(refresh_token, video_url, video_details)
#         print(f"Upload successful. Response: {json.dumps(upload_result, indent=2)}")
#     except Exception as e:
#         print(f"Error: {str(e)}")


from Tiktok.access_token import access_token
import requests
import json

def upload_to_tiktok(video_details):
    def attempt_upload(refresh_token):
        try:
            # Get the access token
            access_token_value, open_id = access_token(refresh_token)
            
            # Prepare the upload request
            url = "https://business-api.tiktok.com/open_api/v1.3/business/video/publish/"
            
            headers = {
                "Access-Token": access_token_value,
                "Content-Type": "application/json"
            }
            
            payload = {
                "business_id": open_id,
                "video_url": video_details['s3_url'],
                "post_info": {
                    "caption": f"{video_details['title']} {video_details['hashtags']}",
                    "disable_comment": False,
                    "disable_duet": False,
                    "disable_stitch": False
                }
            }
            
            # Make the upload request
            response = requests.post(url, headers=headers, data=json.dumps(payload))
            
            response.raise_for_status()  # This will raise an HTTPError for bad responses
            
            data = response.json()
            if data.get("code") == 0 and data.get("message") == "OK":
                print("TikTok upload successful!")
                return True
            else:
                print("Failed TikTok")
                print(f"API error: {data.get('message')}")
                return False
        except requests.RequestException as e:
            print(f"HTTP error: {str(e)}")
            return False
        except json.JSONDecodeError as e:
            print(f"JSON parsing error: {str(e)}")
            return False
        except Exception as e:
            print(f"Unexpected error: {str(e)}")
            return False

    # First attempt with the original refresh token
    if attempt_upload(video_details['tt_refresh_token']):
        return True, False  # Success, no retry

    # If the first attempt fails, try with the alternate account
    print("Attempting upload with alternate account...")
    alternate_refresh_token = "rft.HIhT0DTM2viclZDGetMTD4NWCWwBtd3Nwi1BzuGESL1ZXGXURPDC6EuAth5N!6411.u1"  # The alternate account's refresh token (myaifrontdesk4@gmail.com)
    if attempt_upload(alternate_refresh_token):
        return True, True  # Success with retry

    # If both attempts fail, return False and False (failed, no successful retry)
    print("Failed to upload to TikTok with both accounts.")
    return False, False_slack

# Example usage
if __name__ == "__main__":
    video_details = {
        "tt_refresh_token": "rft.ySKKMj4o6Mp0ovmhwFrAge5y8ecRZYctj5DZx4EGVRAIjZACLkA6twgqfg7m!6362.u1",
        "s3_url": "https://aisocialmediavideos.s3.amazonaws.com//inbound_1819/video.mp4",
        "title": "Automate Client Bookings:",
        "hashtags": "#AI #AutomateBookings #Automation"
    }
    
    success, retry_done = upload_to_tiktok(video_details)
    if success:
        print(f"Upload successful. Used alternate account: {retry_done}")
    else:
        print(f"Upload failed. Retry attempted: {retry_done}")