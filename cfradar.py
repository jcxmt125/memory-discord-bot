import requests
import datetime
import os

from dotenv import load_dotenv

load_dotenv()

CLOUDFLARE_RADAR_API_KEY = os.getenv("CLOUDFLARE_RADAR_API_KEY")


baseurl = "https://api.cloudflare.com/client/v4/accounts/"+os.getenv("CLOUDFLARE_USER_ID")+"/urlscanner/scan"

def httpsCheck(checkUrl):
    if checkUrl[0:5] == "http:" or checkUrl[0:6] == "https:":
        return True
    else:
        return False

def httpStrip(Url):
    if Url[0:6] == "https:":
        return Url[8:]
    elif Url[0:5] == "http:":
        return Url[7:]

def urlScan(scanUrl):
    
    try: #check preexist scans
        if httpsCheck(scanUrl):
            scanUrl = httpStrip(scanUrl)
        uuid = requests.get(baseurl+f"?page_hostname={scanUrl}", headers={"Authorization": "Bearer " + CLOUDFLARE_RADAR_API_KEY}).json()["result"]["tasks"][0]["uuid"]
        resultJson = requests.get(baseurl+"/"+uuid, headers={"Authorization": "Bearer " + CLOUDFLARE_RADAR_API_KEY}).json()
        verdict = resultJson["result"]["scan"]["verdicts"]["overall"]
        timeMade = resultJson["result"]["scan"]["task"]["time"][0:10]
        reportDate = datetime.datetime(year=int(timeMade[0:4]), month=int(timeMade[5:7]), day=int(timeMade[8:10]))
        if datetime.datetime.today() - datetime.timedelta(7) >= reportDate:
            raise Exception #report is older than 7 days
        return(verdict,timeMade)
    
    except: #start scan
        body = """{"url":""" + '''"''' + scanUrl + '''"''' + "}"
        return(requests.post(baseurl, headers={"Authorization": "Bearer " + CLOUDFLARE_RADAR_API_KEY}, data=body).json()["result"]["uuid"])
        
if __name__ == "__main__":
    #example.com is probably scanned recently already
    print(urlScan("https://example.com"))