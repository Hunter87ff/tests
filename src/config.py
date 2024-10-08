import os, random, string, requests, psutil
from pymongo import MongoClient
from dotenv import load_dotenv
load_dotenv()


development = os.getenv("DEV_env")
event_date = "2024-10-08"
db = MongoClient(os.getenv("MONGO_URI"))["Database"]
tokendb = db.get_collection("tickets")
userdb =db.get_collection("users")
configdbc = dict(db.get_collection("config").find_one({"id":87}))
authToken = os.getenv("AUTH_TOKEN")
erl = configdbc.get("erl")


def delete_unused_tickets():
    tokendb.delete_many({"status": "valid"})
    log("Deleted all unused tickets")

def delete_used_tickets():
    tokendb.delete_many({"status": "used"})
    log("Deleted all used tickets")

def delete_all_tickets():
    tokendb.delete_many({})
    log("Deleted all tickets")
    
def log(message:str):
    obj = {"content" : message}
    requests.post(erl, json=obj)


class Ticket:
    def __init__(self, obj:dict) -> None:
        self.name = obj.get("name")
        self.email = obj.get("email")
        self.token = obj.get("token") or self.get_token()
        self.status = obj.get("status") or "valid"
        self.valid = self.status == "valid"


    def get_token(self):
        token = ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))
        if not tokendb.find_one({"token": token}):
            return token
        return self.get_token()


    def save(self):
        ticket = Ticket(self.json)
        tokendb.insert_one(self.json)
        if event: event.add_ticket(ticket)
        print("Updated ticket: ", ticket.token)
        
        return self


    @property
    def json(self):
        return {
            "name": self.name,
            "email": self.email,
            "token": self.token,
            "status": self.status
        }

class Event:
    def __init__(self) -> None:
        self.date = event_date
        self._tickets = dict()

    @property
    def tickets(self):
        if self._tickets:return self._tickets
        ticks = tokendb.find({})
        self._tickets = {tick.get("token"): Ticket(tick) for tick in ticks} # mo
        del ticks
        return self._tickets
    
    def update_ticket(self, token:str, status:str):
        self._tickets[token].status = status
        tokendb.update_one({"token": token}, {"$set": {"status": status}})
        return self

    def add_ticket(self, ticket:Ticket):
        self._tickets[ticket.token] = ticket
        return self
    
    @property
    def tickSold(self):
        return len(self.tickets)
    

class Admin:
    def __init__(self, obj:dict) -> None:
        self.username = obj.get("name")
        self.password = obj.get("password")
        self.email = obj.get("email")
        self.token = obj.get("token") or "invalid"

    def to_dict(self):
        return {
            "name": self.username,
            "email": self.email,
            "password": self.password,
            "token": self.token
        }

def is_manager(token:str=None) -> bool | Admin:
    data = userdb.find_one({"token": token or "invalid"})
    if data:return Admin(data)
    return False

def system():
    cpu_usage = psutil.cpu_percent()
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    detail = f"""
    ```
    Total RAM : {memory.total / (1024**3):.2f} GB
    CPU Cores : {psutil.cpu_count(logical=False)}
    CPU Usage : {cpu_usage}%
    RAM Usage : {memory.used//10**6} MB({memory.percent}%) | {psutil.Process(os.getpid()).memory_info().rss//2**20}MB
    Total Disk: {disk.total//10**9} GB
    Disk Usage: {disk.used//10**9} GB({disk.percent}%)
    ```
    """
    return detail

event = Event()