import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

CLOUDFLARE_AI_API_KEY = os.getenv("CLOUDFLARE_AI_API_KEY")

#This is probably fine (we might change the model later)
model = '@cf/stabilityai/stable-diffusion-xl-base-1.0'

#DON'T USE AI GATEWAY FOR THIS
#I HAVE NEVER KNOWN I COULD HATE AN IMAGE THAT MUCH
#(Context: It caches the image and sends it back for every single request, with no regards to the prompt)
url = "https://api.cloudflare.com/client/v4/accounts/" + os.getenv("CLOUDFLARE_USER_ID") + "/ai/run/" + model

headers = {
    "Authorization": f"Bearer {CLOUDFLARE_AI_API_KEY}",
}

def sdgen(prompt):

    data = {
        "prompt": prompt,
    }

    response = requests.post(url, headers=headers, data=json.dumps(data))

    #There might be some issues with this, but this is the easiest way I can think of...
    with open("output.png", "wb") as f:
        f.write(response.content)

    return

if __name__ == "__main__":
    sdgen("A serene lake scene featuring a lone duck floating effortlessly on the calm water, with serene surroundings and no distractions")