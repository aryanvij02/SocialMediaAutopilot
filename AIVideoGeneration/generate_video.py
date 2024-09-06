from moviepy.editor import *
from moviepy.audio.io.AudioFileClip import AudioFileClip
import pysrt
import textwrap
from PIL import Image, ImageDraw
import numpy as np
import os
import shutil
from pathlib import Path
from glob import glob
import json
import base64
import subprocess

def render_frames_with_puppeteer(html_file, output_dir, duration, fps):
    try:
        subprocess.run([
            "node", 
            # "./render_frames.js", 
            "./AIVideoGeneration/render_frames.js", 

            html_file, 
            output_dir, 
            str(duration), 
            str(fps)
        ], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error running Puppeteer script: {e}")
        raise

def generate_html_template(image_path, subtitle_data, animation_type):
    with open(image_path, "rb") as image_file:
        encoded_image = base64.b64encode(image_file.read()).decode("utf-8")

    animations = {
        'zoom_in': '''
            @keyframes slowZoomIn {
                from { transform: scale(1); }
                to { transform: scale(1.05); }
            }
            #background { animation: slowZoomIn 30s ease-in-out forwards; }
        ''',
        'pan_right': '''
            @keyframes slowPanRight {
                from { background-position: 0% 50%; }
                to { background-position: 100% 50%; }
            }
            #background { animation: slowPanRight 35s linear forwards; }
        ''',
        'pan_down': '''
            @keyframes slowPanDown {
                from { background-position: 50% 0%; }
                to { background-position: 50% 100%; }
            }
            #background { animation: slowPanDown 35s linear forwards; }
        ''',
        'zoom_out': '''
            @keyframes slowZoomOut {
                from { transform: scale(1.05); }
                to { transform: scale(1); }
            }
            #background { animation: slowZoomOut 30s ease-in-out forwards; }
        '''
    }

    selected_animation = animations[animation_type]

    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Video Frame</title>
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@700&display=swap');
            body, html {{
                margin: 0;
                padding: 0;
                width: 100%;
                height: 100%;
                overflow: hidden;
            }}
            #background {{
                position: absolute;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background-image: url(data:image/png;base64,{encoded_image});
                background-size: cover;
                background-position: center;
            }}
            {selected_animation}
            #overlay {{
                position: absolute;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: rgba(0, 0, 0, 0.3);
            }}
            #content {{
                position: absolute;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                display: flex;
                justify-content: center;
                align-items: center;
                z-index: 1;
            }}
            #subtitle {{
                color: white;
                font-family: 'Roboto', sans-serif;
                font-size: 72px;
                font-weight: 700;
                text-align: center;
                padding: 20px;
                background: rgba(0, 0, 0, 0.5);
                border-radius: 10px;
                max-width: 80%;
                opacity: 0;
                transition: opacity 0.3s ease-in-out;
            }}
        </style>
    </head>
    <body>
        <div id="background"></div>
        <div id="overlay"></div>
        <div id="content">
            <div id="subtitle"></div>
        </div>
        <script>
            const subtitles = {json.dumps(subtitle_data)};
            const subtitleElement = document.getElementById('subtitle');

            function updateSubtitle(time) {{
                const currentSub = subtitles.find(sub => time >= sub.start && time < sub.end);
                
                if (currentSub) {{
                    subtitleElement.textContent = currentSub.text;
                    subtitleElement.style.opacity = 1;
                }} else {{
                    subtitleElement.style.opacity = 0;
                }}
            }}

            function update(time) {{
                updateSubtitle(time);
            }}
        </script>
    </body>
    </html>
    """
    return html_content

from moviepy.video.compositing.transitions import crossfadein
from moviepy.video.fx.all import fadeout, fadein

def generate_video(project_name, image_files, audio_files, srt_files):
    clips = []
    animation_types = ['zoom_in', 'pan_right', 'pan_down', 'zoom_out']
    for idx, (img, audio, srt) in enumerate(zip(image_files, audio_files, srt_files)):
        # Select animation type
        animation_type = animation_types[idx % len(animation_types)]

        # Load audio and get its duration
        audio_clip = AudioFileClip(audio)
        duration = audio_clip.duration

        # Parse SRT file
        subs = pysrt.open(srt)
        subtitle_data = [
            {
                'start': sub.start.seconds + sub.start.minutes * 60 + sub.start.hours * 3600,
                'end': sub.end.seconds + sub.end.minutes * 60 + sub.end.hours * 3600,
                'text': sub.text
            } for sub in subs
        ]

        # Generate HTML content with selected animation
        html_content = generate_html_template(img, subtitle_data, animation_type)

        # Create a directory for frames
        frame_dir = Path(f"./temp_frames_{project_name}_{idx}")
        frame_dir.mkdir(parents=True, exist_ok=True)

        # Save HTML content to a file
        html_file = frame_dir / "frame.html"
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(html_content)

        # Render frames using Puppeteer
        render_frames_with_puppeteer(str(html_file), str(frame_dir), duration, 30)  # 30 fps for smoother transitions

        # Get list of frame files
        frame_files = sorted(glob(os.path.join(frame_dir, "frame_*.png")))

        if not frame_files:
            raise FileNotFoundError(f"No frame files found in {frame_dir}")

        # Create video clip from rendered frames
        video_clip = ImageSequenceClip(frame_files, fps=30)

        # Set the audio of the clip
        video_clip = video_clip.set_audio(audio_clip)

        # Add fade in and fade out
        video_clip = video_clip.fadein(1).fadeout(1)

        clips.append(video_clip)
        
    final_clips = []
    for i in range(len(clips)):
        if i == 0:
            final_clips.append(clips[i])
        else:
            transition = crossfadein(clips[i], duration=0.5)
            final_clips.append(transition)

    # Concatenate all the clips with crossfade transitions
    final_clip = concatenate_videoclips(final_clips, method="compose")

    # Concatenate all the clips with crossfade
    project_dir = Path(f"./Videos/{project_name}")
    project_dir.mkdir(parents=True, exist_ok=True)
    
    output_file = project_dir / "video.mp4"
    # Write the result to a file
    final_clip.write_videofile(str(output_file), fps=30, codec='libx264', audio_codec='aac', threads=2, preset='ultrafast')

    # Close all clips to release resources
    final_clip.close()
    for clip in clips:
        clip.close()

    # Clean up frame directories
    for idx in range(len(image_files)):
        shutil.rmtree(f"./temp_frames_{project_name}_{idx}", ignore_errors=True)

    print(f"Video generated successfully: {output_file}")
    
    #Returns project directory, and the path to the output mp4 file. Ensure it is returned as a STRING
    return str(project_dir)

if __name__ == "__main__":
    # Test the function with sample data
    image_files = ["Images/Testing_0.png", "Images/Testing_1.png"]
    audio_files = ["audio/Testing_0.mp3", "audio/Testing_1.mp3"]
    srt_files = ["audio/Testing_srt_0.srt", "audio/Testing_srt_1.srt"]
    generate_video("test_project", image_files, audio_files, srt_files)