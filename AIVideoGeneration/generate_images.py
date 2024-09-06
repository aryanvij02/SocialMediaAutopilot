import os
import time
from openai import OpenAI
import requests
from dotenv import load_dotenv

load_dotenv()

def generate_image(project_name, script, max_retries=5, retry_delay=3):
    image_files = []
    # Initialize the OpenAI client
    client = OpenAI(api_key=os.getenv("OPEN_AI_API_KEY"))

    for i, item in enumerate(script):
        
        image_name = f"Images/{project_name}_{i}.png"
        image_prompt = "Make sure the image is vertical. Generate this: " + item["image_prompt"]

        for attempt in range(max_retries):
            try:
                # Generate the image
                response = client.images.generate(
                    model="dall-e-3",
                    prompt=image_prompt,
                    #This changes aspect ratio of the image
                    size="1024x1792",
                    quality="standard",
                    n=1,
                )

                # Get the image URL
                image_url = response.data[0].url

                # Download the image
                image_response = requests.get(image_url)
                if image_response.status_code == 200:
                    with open(image_name, "wb") as file:
                        file.write(image_response.content)
                    image_files.append(image_name)
                    print(f"{image_name} downloaded successfully.")
                    print(f"Image URL: {image_url}")
                    break  # Successfully generated and downloaded, exit retry loop
                else:
                    print(f"Failed to download the image. Status code: {image_response.status_code}")
            except Exception as e:
                error_message = str(e)
                if 'content_policy_violation' in error_message:
                    print(f"Content policy violation. Retrying with modified prompt. Attempt {attempt + 1}/{max_retries}")
                    # You might want to modify the prompt here to avoid the violation
                    modified_prompt = make_appropriate(script)
                    if modified_prompt:
                        image_prompt = "Make sure the image is vertical. Generate this: " + modified_prompt
                else:
                    print(f"An error occurred: {error_message}. Retrying. Attempt {attempt + 1}/{max_retries}")
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
        else:
            print(f"Failed to generate image after {max_retries} attempts.")

    return image_files

client = OpenAI(api_key=os.getenv("OPEN_AI_API_KEY"))
def make_appropriate(sentence):
    response = client.chat.completions.create(
        model="gpt-4o",
        messages = [
            {
                "role": "system",
                "content": "You are going to make any sentence appropriate"
            },
            {
                "role": "user",
                "content": f'''      
                    Please make the following sentence appropriate so it satisfies the content policy and doesn't violate it.
                    Only return the modified sentence
                    
                    Sentence: {sentence}
                '''
            }
        ]
    )
    content = response.choices[0].message.content.strip()
    # try:
    return content


if __name__ == "__main__":
    generate_image("Image_6",  [
    {
        "phrase": "Have you ever dreamed of running your own SaaS business?",
        "image_prompt": "An individual looking at a glowing laptop with futuristic graphics depicting business growth around them."
    },
    {
        "phrase": "Learn how to white-label and resell AI receptionists to car dealerships.",
        "image_prompt": "A sleek, modern car dealership with a friendly AI receptionist greeting a customer."
    },
    {
        "phrase": "White-labeling lets you brand the AI receptionists as your own product.",
        "image_prompt": "A professional showing a customized dashboard with their own logo and branding colors."
    },
    {
        "phrase": "Boost customer service by providing 24/7 support through AI technology.",
        "image_prompt": "A happy customer chatting with an AI receptionist on their smartphone at night."
    },
    {
        "phrase": "Easily integrate with existing dealership management systems.",
        "image_prompt": "A seamless connection graphic between an AI system and a dealership software."
    },
    {
        "phrase": "Automate appointments, follow-ups, and customer inquiries effortlessly.",
        "image_prompt": "A calendar filling up with scheduled car maintenance and sales appointments automatically."
    },
    {
        "phrase": "Minimize costs while maximizing customer satisfaction.",
        "image_prompt": "A graph showing decreased operational costs and increased customer satisfaction ratings."
    },
    {
        "phrase": "Stay ahead of competitors with cutting-edge AI solutions.",
        "image_prompt": "A car dealership standing out among others with advanced AI features."
    },
    {
        "phrase": "Ready to transform how car dealerships operate?",
        "image_prompt": "An excited car dealership owner shaking hands with an AI representative."
    },
    {
        "phrase": "Start your journey with us today and revolutionize customer service!",
        "image_prompt": "The logo of your SaaS business with a captivating background showing innovation and digital transformation."
    }
])