import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

def generate_audio(project_name, script):
    audio_files = []
    elevenlabs_api_key = os.getenv("ELEVEN_LABS_API_KEY")
    # voice_id = os.getenv("VOICE_ID")
    model_id = os.getenv('ELEVEN_MODEL_ID')  # Replace with your actual model ID


    # API endpoint
    url = f"https://api.elevenlabs.io/v1/text-to-speech/nPczCjzI2devNBz1zQrb"

    # Request headers
    headers = {
        "xi-api-key": elevenlabs_api_key,
        "Content-Type": "application/json",
    }

    for i, scene in enumerate(script):
        # Request body
        data = {
            "text": scene["phrase"],
            "model_id": model_id,  # Use the correct model ID
            "voice_settings": {
                "stability": 0.5,
                "similarity_boost": 0.5
            }
        }

        try:
            # Make the API request
            response = requests.post(url, json=data, headers=headers)
            response.raise_for_status()

            # Check if the content type is audio
            if 'audio/' in response.headers.get('Content-Type', ''):
                file_name = f"{project_name}_{i}.mp3"
                with open(f'audio/{file_name}', 'wb') as f:
                    f.write(response.content)

                audio_files.append(f'audio/{file_name}')
                print(f"Audio {i} saved successfully")
            else:
                print(f"Unexpected content type received for audio {i}: {response.headers.get('Content-Type')}")
                print(f"Response content: {response.text}")

        except requests.exceptions.RequestException as e:
            print(f"Failed to generate audio for scene {i}")
            print(f"Error: {str(e)}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"Status code: {e.response.status_code}")
                print(f"Response content: {e.response.text}")
            else:
                print("No response received from the server")
            return None
        
    return audio_files

# Test the function
if __name__ == "__main__":
    test_script = [{"phrase": "This is a test audio"}]
    result = generate_audio(test_script)
    print(f"Generated audio files: {result}")