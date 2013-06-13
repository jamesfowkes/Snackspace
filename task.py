class _task:
    def __init__(self, func, time, active):
        self.Function = func
        self._period = time
        self.Ticks = time
        self.Active = active            
    
    def Reload(self):
        self.Ticks = self._period
        
class TaskHandler:
            
    def __init__(self, parent):
        self._tasks = []
        self._parent = parent
    
    def addFunction(self, function, time, active = True):
        newTask = _task(function, time, active)
        self._tasks.append(newTask)
        
    def tick(self):
        for t in self._tasks:
            if t.Active and t.Ticks > 0:
                t.Ticks -= 1
                if t.Ticks == 0:
                    t.Reload()
                    t.Function()