import os, time, platform
from threading import Thread
from modules import config
with open("lava/application.yml", "r") as f1:content1= f1.read()
content = content1.replace("spot_id", f"{config.spot_id}").replace("spot_secret", f"{config.spot_secret}")
with open("lava/application.yml", "w") as f: f.write(content)

def lavalink():
    if platform.system() == "Windows":os.system("cd lava && java -jar Lavalink.jar > NUL 2>&1 &")
    else:os.system("cd lava && java -jar Lavalink.jar")    # > /dev/null 2>&1 &
Thread(target=lavalink).start()


time.sleep(5)
with open("lava/application.yml", "w") as f: f.write(content1.replace(config.spot_id, "spot_id").replace(config.spot_secret, "spot_secret"))
