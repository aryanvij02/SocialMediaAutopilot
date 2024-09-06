from openai import OpenAI
import os
import requests
import json
import re

# Configuration
client = OpenAI(api_key=os.getenv("OPEN_AI_API_KEY"))

def generate_script(user_prompt):
    # Step 1: Generate script using GPT-4o
    response = client.chat.completions.create(
        model="gpt-4o",
        messages = [
            {
                "role": "system",
                "content": """You are an AI assistant that generates dialogue scripts in strict JSON format.
                Your output must be valid JSON that can be parsed programmatically.
                Do not include any text outside of the JSON structure.
                Ensure all property names and string values are enclosed in double quotes.
                Do not use single quotes in the JSON output."""
            },
            {
                "role": "user",
                "content": f'''      
                    You are an AI assistant tasked with creating a script for a short video based on a given topic or theme from a user's prompt provided below. 
                    Your output should be a JSON-formatted list of objects, where each object represents a scene in the video. Follow these guidelines:

                    Create 10-12 scenes in total.
                    
                    The end goal is to promote a specific product to a specific set of customers. 
                    The product involved automating PHONE CALLS with AI. Remember this please. All images and texts in script should be related to automating phone calls etc, don't talk about software systems. 
                    You should try to include these key aspects and features of the product succinctly and smartly. They shouldn't seem sales-like, but also should inform the customer
                        - Integrates with all your existing systems and CRM tools
                        - You will receive personal support at all times directly from the founder
                        - It has hundreds of custom voices and also voice cloning ability
                        - It can speak in 15 different languages
                        - It has texting and call workflows that allow you to forward calls and send text messages automatically during the call
                                        
                    Try to include maximum three features per video, picking the relevant ones.                        
                    
                    Talk about specific use cases of this product and how it can be helpful. 
                    
                    Your script must be engaging and start with a hook. It should immediately grab the viewer's attention.
                    
                    Each scene object should have two properties:

                    "phrase": A short sentence or phrase that will be spoken in the scene (15 words or less). Make sure the text you give is easy to covert to be spoken. 
                    "image_prompt": A detailed description of the image that should accompany the phrase (25 words or less). This should always be appropriate. 

                    Never say [VERTICAL] in the script. You are provided the relevant VERTICAL after the term VERTICAL in the prompt.
                    Ensure that the scenes flow logically from one to the next.
                    Use vivid, descriptive language for the image prompts to guide the image generation process. 
                    Each image prompt is indepenedent of one another. You cannot reference previous image prompts, as images will be generated separately and uniquely. 
                    Always fit the context of the scene and the overall theme of the video. The images really have to paint the picture of this overall script and story. 
                    If the user mentions the Name of their Product or Company or Service, you MUST make sure to include the Name in either the first or last scene for the image. 

                    Keep the overall tone and style consistent throughout the script.

                    Output your response in the following JSON format:
                    jsonCopy[
                    {{
                        "phrase": "String containing the spoken phrase for the first scene",
                        "image_prompt": "String describing the image for the first scene"
                    }},
                    {{
                        "phrase": "String containing the spoken phrase for the second scene",
                        "image_prompt": "String describing the image for the second scene"
                    }},
                    ...
                    ]
                    Do not include any explanations or additional text outside of the JSON structure. The output should be valid JSON that can be parsed programmatically.
                    Do not put 'json' before the returned json
                    ------------
                    
                    User Prompt: {user_prompt}
                '''
            }
        ]
    )
    content = response.choices[0].message.content.strip()
    try:
        return json.loads(content)
    except json.JSONDecodeError as e:
        print("JSON Decode Error:", e)
        print("Content received:", content)
        
        # Attempt to fix common JSON formatting issues
        try:
            # Remove any leading/trailing characters that aren't part of the JSON
            content = content.strip()
            if content.startswith('[') and content.endswith(']'):
                # Replace single quotes with double quotes
                content = content.replace("'", '"')
                # Ensure property names are in double quotes
                content = re.sub(r'(\w+):', r'"\1":', content)
                return json.loads(content)
        except Exception as fix_error:
            print("Failed to fix JSON:", fix_error)
        
        return None  # or handle the error as needed 
    
       
def generate_audio(script):
    # Step 2: Generate audio using ElevenLabs API
    audio_segments = []
    for item in script:
        for speaker, text in item.items():
            # This is a placeholder. You'll need to implement the actual API call to ElevenLabs
            audio_url = f"https://api.elevenlabs.io/v1/text-to-speech/{speaker}"
            response = requests.post(audio_url, json={"text": text}, headers={"xi-api-key": elevenlabs_api_key})
            audio_segments.append(AudioSegment.from_mp3(io.BytesIO(response.content)))
    
    # Combine audio segments with interruption
    final_audio = AudioSegment.empty()
    for i, segment in enumerate(audio_segments):
        if i == 5:  # User-3 interrupts Novi-3
            final_audio = final_audio.overlay(segment, position=len(final_audio) - 500)
        else:
            final_audio += segment
    
    return final_audio

def generate_subtitles(audio):
    # Step 3: Generate subtitles using Whisper
    model = whisper.load_model("base")
    result = model.transcribe(audio)
    return result["segments"]

def create_audiogram(audio, subtitles):
    # Step 4: Create audiogram
    # This is a placeholder. You'll need to implement the actual audiogram generation
    pass

def create_final_video(audio, audiogram, subtitles):
    # Step 5: Combine everything into a final video
    # This is a placeholder. You'll need to implement the actual video creation
    pass

def main(vertical):
    script = generate_script(vertical)
    print(script)

if __name__ == "__main__":
    final_video = generate_script("Create a video for an AI phone call receptionist that can automate answering the phone for your business, saving you time and money and improving customer satsifaction. It also fully integrates into your workflow. ")
    # print(f"Video for {vertical} has been generated successfully!")
    
    
    
    
