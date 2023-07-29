import requests 
def send(url,title,discription,content):


    data = {
        "username" : "인증로그",
        "content" : content,
        "avatar_url" : "https://cdn.discordapp.com/attachments/935539200277753886/939050694168678400/888431241374879795.png"
        
    }


    data["embeds"] = [
        {
            "description" : discription,
            "title" : title,
    
        }
    ]

    result = requests.post(url, json = data)

    try:
        result.raise_for_status()
    except requests.exceptions.HTTPError as err:
        print(err)
    else:
        print("Payload delivered successfully, code {}.".format(result.status_code))

