from generate_images import generate_image
from generate_script import generate_script
from generate_audio import generate_audio
from generate_srt import generate_srt_from_audio_file
from generate_video import generate_video

def main(project_name, prompt):
    script = generate_script(prompt)
    image_files = generate_image(project_name, script)
    audio_files = generate_audio(project_name, script)

    srt_files = []
    for index, audio_file in enumerate(audio_files):
        srt_file = generate_srt_from_audio_file(project_name, index, audio_file)
        if srt_file:
            srt_files.append(srt_file)
        else:
            print(f"Failed to generate SRT file for audio {index}.")
    
    if len(srt_files) == len(audio_files):
        project_dir = generate_video(project_name, image_files, audio_files, srt_files)
        return project_dir
    else:
        print("Some SRT files were not generated")

if __name__ == "__main__":
    project_name = input("Enter name of this project:")
    prompt = input("Enter your prompt: ")
    main(project_name, prompt)
    
        
        