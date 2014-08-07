#! coding:utf-8
class MessageWrapper:
    def jsonWrapper(self,message,code):
        return "{'code':'%s','message':'%s'}" % (code,message)
    
