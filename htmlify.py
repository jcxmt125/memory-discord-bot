import random
from pathlib import Path
def makePage(text, filename="", description = "This is an automatically generated webpage.", title = "Auto gen. page"):

    for i in range(len(text)):
        if text[i][-1] == "\n":
            text[i] = "                " + text[i][:-1] + "<br>\n"

    if filename == "":
        filename = str(random.randint(1,1000000))
    
    if Path(filename).is_file():
        filename += str(random.randint(1,1000))

    #I mean the chances of there being a file with the same name are pretty slim.
    #TODO make this actually check the cloud storage this will likely upload to.

    with open(filename+".html", 'w', encoding="UTF-8") as rsl:
        toWrite = ""

        toWrite += """<!DOCTYPE html>\n
    <meta charset="UTF-8">\n
    <meta name="viewport" content="width=device-width, initial-scale=1.0">\n"""
        
        toWrite += f"""<meta name="description" content="{description}">\n"""

        toWrite += """<head>\n"""

        toWrite += f"<title>{title}</title>\n"

        ##Maybe I should make the font variable.

        toWrite += """<link rel="preconnect" href="https://fonts.googleapis.com">\n
        <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n
        <link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans+KR:wght@300&display=swap" rel="stylesheet">\n
        <style>\n
          body {\n
            font-family: 'IBM Plex Sans KR', sans-serif;;\n
            padding: 10px;\n
            line-height: 200%;\n
          }\n
        </style>\n
        </head>\n
        <body style="background-color:#202020;color:#F0F0F0">\n"""
        
        for j in text:
            toWrite += j

        toWrite += """</body>\n
    </html>"""

        rsl.write(toWrite)
    
    return(filename+".html")

    #I'll probably want to path.unlink the HTML file in the actual bot code just so it doesn't clutter things up too much.
    
if __name__ == "__main__":
    with open("source.txt", 'r', encoding="UTF-8") as src:
        fulltext = src.readlines()
        makePage(fulltext)