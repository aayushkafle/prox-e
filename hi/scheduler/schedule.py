from icalendar import Calendar, Event, vDatetime, vCalAddress, vText
from datetime import datetime
import pytz
from pycouchdb.feedreader import BaseFeedReader
import pycouchdb

from credentials import userName, Password, URL

host = "http://" + userName + ":" + Password + "@" + URL + "/"

server = pycouchdb.Server(host)
print(server)
db = server.database("schedule")
print("Iamhere")

class Schedule(BaseFeedReader):
    def on_message(self, message):
        print("New change detected")
        if "seq" in message:
            last_seq = message["seq"]
            seq_file = open(".seq","w")
            seq_file.write(last_seq)
            seq_file.close()

        if not "deleted" in message:
            _part, _id = message["id"].split(":")
            if _part != "Calendar-Event":
                doc = db.get(message["id"])
                result = {}
                for key in doc:
                    if key not in ["_id", "_rev"]:
                        result[key] = doc[key]
                result["calendar-type"] = _part
                result["_id"] = "Calendar-Event:"+_id
                db.save(result)

if __name__ == "__main__":
    try:
        seq_file = open(".seq","r")
        last_seq = seq_file.read()
        seq_file.close()
        db.changes_feed(Schedule(), feed="continuous", heartbeat=1000, since=last_seq)
    
    except:
        db.changes_feed(Schedule(), feed="continuous", heartbeat=1000)
