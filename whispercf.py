import requests
import os
from dotenv import load_dotenv

load_dotenv()

#We need to make it take a URL; Discord.py seems to be able to throw a URL in. (File management gets dizzy on a server-)
def cfwhisper(fileUrl):
  API_URL = "https://api.cloudflare.com/client/v4/accounts/" + os.getenv("CLOUDFLARE_USER_ID") + "/ai/run/@cf/openai/whisper"

  # Open the audio file in binary mode
  audio_data = requests.get(fileUrl)

  # Set headers with authorization token
  headers = {"Authorization": "Bearer "+os.getenv("CLOUDFLARE_AI_API_KEY")}

  # Send POST request with audio data
  response = requests.post(API_URL, headers=headers, data=audio_data)

  # Check for successful response
  if response.status_code == 200:
    return response.json()
  else:
    return False
  
if __name__ == "__main__":
  print(cfwhisper(input("url: ")))