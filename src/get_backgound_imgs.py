import requests
from io import BytesIO
from PIL import Image
import os
import random
import string
import yaml
from config import *

def download_random_image(url):
    response = requests.get(url)
    if response.status_code == 200:
        image_data = BytesIO(response.content)
        image = Image.open(image_data)
        return image
    else:
        return None

def save_image(image, output_directory):
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    filename = ''.join(random.choices(string.ascii_letters + string.digits, k=10)) + ".jpg"
    output_path = os.path.join(output_directory, filename)
    image.save(output_path)

if __name__ == '__main__':



    # Example Usage
    url = "https://source.unsplash.com/random"  # Replace with the desired image source URL
    output_directory = os.path.join(os.getcwd(),DATA_DIR,"backgrounds")  # Replace with the desired output directory

    # Download and save 5 random images
    for _ in range(N_BACKGROUNDS):
        image = download_random_image(url)
        if image:
            save_image(image, output_directory)
            print("Image saved successfully.")
        else:
            print("Failed to download the image.")



