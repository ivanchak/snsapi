#-*- encoding: utf-8 -*-

'''
    facebook
    
    We use python-facebook as the backend at present.
    It should be changed to invoke REST API directly later.
    '''

from ..snslog import SNSLog
logger = SNSLog
from ..snsbase import SNSBase
from .. import snstype
from ..utils import console_output
from .. import utils

from ..third import facebook

logger.debug("%s plugged!", __file__)

class FacebookStatusMessage(snstype.Message):
    platform = "FacebookStatus"
    def parse(self):
        self.ID.platform = self.platform
        self._parse(self.raw)

    def _parse(self, dct):
        self.ID.id = dct['id']
        
        self.parsed.time = utils.str2utc(dct['created_time'])
        self.parsed.username = dct['from']['name']
        self.parsed.userid = dct['from']['id']
        
        #When you share a status on facebook, your status is stored in the tag 'message' in the response of facebook timeline.
        #When your friends tag you in his/her status, you will see the message is stored in the tag 'description'. Here 'description' is what your friends wrote down.
        #Other messages like you being tagged in a photo are stored in a tag 'story'.
        #Thus, when there are no tag named 'message', we try to extract the 'description' or 'story' of that message to give meaningful information.
        try:
            self.parsed.text = dct['message']
        except:
            try:
                self.parsed.text = dct['description']
            except:
                self.parsed.text = dct['story']

class FacebookStatus(SNSBase):
    
    Message = FacebookStatusMessage
    
    def __init__(self, channel = None):
        super(FacebookStatus, self).__init__(channel)
        self.platform = self.__class__.__name__
        
        self.graph = facebook.GraphAPI(access_token = self.jsonconf['access_token'])
        #all we need is an access token given by facebook. There are several ways to get the access token. The most convenient way is to visit the Graph API explorer(http://developers.facebook.com/tools/explorer)
    
    @staticmethod
    def new_channel(full = False):
        c = SNSBase.new_channel(full)
        
        c['platform'] = 'FacebookStatus'
        c['app_key'] = ''
        c['app_secret'] = ''
        c['access_key'] = ''
        c['access_secret'] = ''
        
        return c
    
    def read_channel(self, channel):
        super(FacebookStatus, self).read_channel(channel)
    
    def auth(self):
        logger.info("Current implementation of Twitter does not use auth!")
    
    def home_timeline(self, count = 20):
        status_list = snstype.MessageList()
        try:
            statuses = self.graph.get_connections("me","feed")
            for s in statuses["data"]:
                status_list.append(self.Message(s,\
                                                self.jsonconf['platform'],\
                                                self.jsonconf['channel_name']))
        except Exception, e:
            logger.warning("Catch expection: %s", e)
        return status_list

    def update(self, text):
        text = self._cat(140, [(text, 1)])
        try:
            status = self.graph.put_object("me", "feed" , message = text)
            if status:
                return True
            else:
                return False
        except Exception, e:
            logger.warning('update Facebook failed: %s', str(e))
            return False
    
    def expire_after(self, token = None):
        # This platform does not have token expire issue. 
        return -1

