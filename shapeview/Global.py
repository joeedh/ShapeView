import bpy

#this module is no longer used
class SVGlob:
    def __init__(self):
        self.timergen = 0
        self.is_rendering = False
        
    def startTimer(self, timerfunc):
        self.timergen += 1
        
        timergen = [self.timergen]
        def timer():
            if self.timergen != timergen[0]:
                print("Timer stop")
                return None
            timerfunc()
            return 0.1
        
        bpy.app.timers.register(timer)
    
    def stopTimers(self):
      self.timergen += 1


svglob = SVGlob()
