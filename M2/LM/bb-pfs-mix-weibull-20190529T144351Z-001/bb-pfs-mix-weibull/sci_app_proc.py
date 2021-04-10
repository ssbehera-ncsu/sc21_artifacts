import simpy

class Scientific_App_Proc():
    def __init__(self, env, app, bb, pfs, sys_fail):
        self.env = env
        self.app = app
        self.app.set_sys_fail(sys_fail)
        self.exe = self.env.process(app.run(bb, pfs))

    def get_app(self):
        return self.app
    
    def get_exe(self):
        return self.exe
