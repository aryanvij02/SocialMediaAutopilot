# generate_srt.py
import os
from pathlib import Path
from openai import OpenAI
import srt

def generate_srt_from_audio_file(project_name, index, audio_file):
    # Set up OpenAI client
    client = OpenAI(api_key=os.getenv("OPEN_AI_API_KEY"))
    
    # Define file paths
    srt_file = f"audio/{project_name}_srt_{index}.srt"
    
    # Transcribe audio using Whisper
    try:
        with open(audio_file, "rb") as file:
            response = client.audio.transcriptions.create(
                model="whisper-1",
                file=file,
                response_format="srt"
            )
        
        # Parse the SRT content
        subtitle_generator = srt.parse(response)
        subtitles = list(subtitle_generator)
        
        # Write the SRT file
        with open(srt_file, 'w', encoding='utf-8') as f:
            f.write(srt.compose(subtitles))
        
        print(f"SRT file generated successfully: {srt_file}")
        return str(srt_file)
    
    except Exception as e:
        print(f"Error in generating SRT for {audio_file}: {str(e)}")
        return None

# Example usage
if __name__ == "__main__":
    audio_files = [
        "audio/audio_0.mp3",
        "audio/audio_1.mp3",
        "audio/audio_2.mp3",
        "audio/audio_3.mp3",
        "audio/audio_4.mp3",
        "audio/audio_5.mp3",
        "audio/audio_6.mp3"
    ]
    for index, audio_file in enumerate(audio_files):
        generate_srt_from_audio_file(index, audio_file)