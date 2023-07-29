import asyncio, discord, requests, sqlite3, datetime
from discord.errors import Forbidden
from fastapi import FastAPI
from fastapi.responses import HTMLResponse, Response
from datetime import timedelta
import 설정 as settings
import w
from flask import request, make_response


client = discord.Client()
app = FastAPI()


def get_kr_time():
    return datetime.datetime.now().strftime('%Y-%m-%d %H:%M')

def getip():
    return request.headers.get("CF-Connecting-IP", request.remote_addr)
    
def get_agent():
    return request.user_agent.string

def CuteAlertPage(title, desc, type):
    return '''
    <html>
        <head>
            <link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/gustavosmanc/cute-alert/style.css">
            <script src="https://cdn.jsdelivr.net/gh/gustavosmanc/cute-alert/cute-alert.js"></script>
            <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
        </head>
        <body>
            <script>
                cuteAlert({
                    type: "''' +  type + '''",
                    title: "''' +  title + '''",
                    message: "''' + desc + '''",
                    buttonText: "확인"
                })
            </script>
        </body>
    </html>
    '''

def is_expired(time):
    ServerTime = datetime.datetime.now()
    ExpireTime = datetime.datetime.strptime(time, '%Y-%m-%d %H:%M')
    if ((ExpireTime - ServerTime).total_seconds() > 0):
        return False
    else:
        return True

def get_expiretime(time):
    ServerTime = datetime.datetime.now()
    ExpireTime = datetime.datetime.strptime(time, '%Y-%m-%d %H:%M')
    if ((ExpireTime - ServerTime).total_seconds() > 0):
        how_long = (ExpireTime - ServerTime)
        days = how_long.days
        hours = how_long.seconds // 3600
        minutes = how_long.seconds // 60 - hours * 60
        return str(round(days)) + "일 " + str(round(hours)) + "시간 " + str(round(minutes)) + "분" 
    else:
        return False

def make_expiretime(days):
    ServerTime = datetime.datetime.now()
    ExpireTime_STR = (ServerTime + timedelta(days=days)).strftime('%Y-%m-%d %H:%M')
    return ExpireTime_STR

def add_time(now_days, add_days):
    ExpireTime = datetime.datetime.strptime(now_days, '%Y-%m-%d %H:%M')
    ExpireTime_STR = (ExpireTime + timedelta(days=add_days)).strftime('%Y-%m-%d %H:%M')
    return ExpireTime_STR

async def exchange_code(code, redirect_url):
    data = {
      'client_id': settings.client_id,
      'client_secret': settings.client_secret,
      'grant_type': 'authorization_code',
      'code': code,
      'redirect_uri': redirect_url
    }
    headers = {
      'Content-Type': 'application/x-www-form-urlencoded'
    }
    while True:
        r = requests.post(f"{settings.api_endpoint}/oauth2/token", data=data, headers=headers)
        if (r.status_code != 429):
            break

        limitinfo = r.json()
        await asyncio.sleep(limitinfo["retry_after"] + 2)
    return False if "error" in r.json() else r.json()

async def get_user_profile(token):
    header = {"Authorization" : token}
    res = requests.get("https://discordapp.com/api/v9/users/@me", headers=header)
    print(res.json())
    if (res.status_code != 200):
        return False
    else:
        return res.json()

def start_db():
    con = sqlite3.connect("database.db")
    cur = con.cursor()
    return con, cur

def is_guild(id):
    con,cur = start_db()
    cur.execute("SELECT * FROM guilds WHERE id == ?;", (id,))
    res = cur.fetchone()
    con.close()
    if (res == None):
        return False
    else:
        return True

def is_guild_valid(id):
    if not (str(id).isdigit()):
        return False
    if not is_guild(id):
        return False
    con,cur = start_db()
    cur.execute("SELECT * FROM guilds WHERE id == ?;", (id,))
    guild_info = cur.fetchone()
    expire_date = guild_info[3]
    con.close()
    if (is_expired(expire_date)):
        return False
    return True

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(client.start(settings.token))

@app.get("/Wave.js")
async def waveReturn():
    f = open("templates/Wave.js", "r", encoding="UTF-8")
    data = f.read()
    f.close()
    r = Response(content=data, media_type="text/javascript")
    return r


async def success():
    f = open("templates/success.html", "r", encoding="UTF-8")
    data = f.read()
    f.close()
    return HTMLResponse(data)

async def error(msg):
    f = open("templates/error.html", "r", encoding="UTF-8")
    data = f.read().replace("[ERROR_MSG]", msg)
    f.close()
    return HTMLResponse(data)

@app.get("/callback")
async def callback(code : str = None, state : str = None):

    exchange_res = await exchange_code(code, f"{settings.base_url}/callback")
    if (exchange_res == False):
        return await error(f"This is Boom.")
    user_info = await get_user_profile("Bearer " + exchange_res["access_token"])
    if (user_info == False):
        return await error("프로필 오류 발생, 총괄에게 문의.")
    guild = await client.fetch_guild(int(state))
    try:
        user = await guild.fetch_member(int(user_info["id"]))
    except:
        return await error(f"This is Boom")
    if user == None:
        return await error("먼저, 서버에 입장해주시길 바랍니다.")
    con, cur = start_db()
    cur.execute("INSERT INTO users VALUES(?, ?, ?);", (str(user_info["id"]), exchange_res["refresh_token"], int(state)))
    con.commit()
    cur.execute("SELECT * FROM guilds WHERE id == ?", (int(state),))
    roleid = cur.fetchone()[1]
    con.close()

    con, cur = start_db()
    cur.execute("SELECT * FROM guilds WHERE id == ?", (int(state),))
    webhook = str(cur.fetchone()[4])
    con.commit()
    con.close()

    role = guild.get_role(roleid)
    if role == None:
        return await error(f"`{guild.name}` 서버 세팅 오류발생.")
    try:
        await user.add_roles(role) 
    except:
        return await error(f"`{guild.name}` 서버 역할지급 오류 발생.") 
    try:
        pass

        
    except:
        pass


    try:
        if not webhook ==  "no": 
            w.send(webhook,f"{user.name}#{user.discriminator} ({user.id})" ,f"인증진행 완료.\n\n유저정보 : **{user.name}#{user.discriminator}**\n유저 아이디 : ({user.id})\n\n인증서버 : **{guild.name}**\n역할정보 : `{roleid}({role.name})`",f"<@{user.id}>")
    except:
        pass

    return await success() 
