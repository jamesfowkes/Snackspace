from dbclient import DbClient
from task import TaskHandler
from time import sleep

class DBTester:

    def __init__(self):
        self.task_handler = TaskHandler(self)
        
        self.dbaccess = DbClient(True, self.task_handler)
        
    def start(self):
        while (1):
            sleep(0.001)
            self.task_handler.tick()
            
db = DBTester()

db.start()