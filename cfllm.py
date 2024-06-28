import requests
from dotenv import load_dotenv
import os

#Please don't forget this line ever again in the future-
load_dotenv()

#This will error out if no env variables are set!!
CLOUDFLARE_AI_GATEWAY_SLUG = os.getenv("CLOUDFLARE_AI_GATEWAY_SLUG")
CLOUDFLARE_USER_ID = os.getenv("CLOUDFLARE_USER_ID")
CLOUDFLARE_AI_API_KEY = os.getenv("CLOUDFLARE_AI_API_KEY")

API_BASE_URL = "https://gateway.ai.cloudflare.com/v1/"+CLOUDFLARE_USER_ID+"/"+CLOUDFLARE_AI_GATEWAY_SLUG+"/workers-ai/"

headers = {"Authorization": "Bearer "+CLOUDFLARE_AI_API_KEY}

def run(model, inputs):
    input = { "stream": True, "messages": inputs }
    response = requests.post(f"{API_BASE_URL}{model}", headers=headers, json=input)
    return response

selectedModel = "@cf/meta/llama-3-8b-instruct"

#streamed response
#TODO make this not error out for single token responses
def llmrequest(syst, prompt):
    inputs = [
    { "role": "system", "content": syst }
    ]

    inputs.append({ "role": "user", "content": prompt })

    plaintext = ""
    fullresp = ""

    output = run(selectedModel, inputs)
    
    for line in output:  
        if line:  # Is it actually a new line?
            # Handle each line of the response (text generation)
            plaintext += line.decode("utf-8")        

    while plaintext.find('"response":') != -1:
        whereis = plaintext.find('"response":')
        plaintext = plaintext[whereis+12:]
        whereto = plaintext.find('"')
        fullresp += plaintext[:whereto]
    
    if fullresp[-1] == fullresp[-2]:
        fullresp = fullresp[:-1]

    while fullresp[0] == " ":
        fullresp = fullresp[1:]

    return(True, str(fullresp))

#run but not streamed
def nsrun(model, inputs):
    input = { "messages": inputs }
    response = requests.post(f"{API_BASE_URL}{model}", headers=headers, json=input)
    return response

#TODO for the whole thing: make error handling just in case cloudflare AI freaks out
#It has happened and AI gateway even seems to cache errors which is very weird...

#non-streamed response (useful for very short expected responses (like single token level short) (the stream one seems to error out for that))
def nsllmreq(syst, prompt):
    
    inputs = [
    { "role": "system", "content": syst }
    ]

    inputs.append({ "role": "user", "content": prompt })

    output = nsrun(selectedModel, inputs).json()

    return output['result']['response']

if __name__ == "__main__":

    print(nsllmreq("You are a helpful assistant. Respond with short messages.", "Why do humans live on?"))
