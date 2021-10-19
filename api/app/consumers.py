from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer, JsonWebsocketConsumer
from app.models import *
from datetime import datetime



class GeneralConsumer(JsonWebsocketConsumer):

    def connect(self):
        self.room_group_name = 'general'

        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )

        self.accept()

    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )

    def receive_json(self, content):
        curr_user = self.scope['user']
        action = content['action']
        method = getattr(self, action)
        method(content['data'], curr_user)
        

    def send_json(self, content):
        curr_user = self.scope['user']
        cont = content['content']
        responded_users = content['responded_users']
        if responded_users == '__all__' or curr_user.id in set(responded_users):
            super().send(text_data=self.encode_json(cont))


    def notification(self, content, curr_user=None):
        notice = Notification.objects.get(id=content['notice_id'])
        # curr_user = self.scope['user']

        message = {
                'type': 'send_json',
                'content': {
                    'action': 'notification',
                    'data': {
                        'created_datetime': str(notice.created_datetime),
                        'text': notice.text,
                        'type': notice.type
                    }
                },
                'responded_users': [notice.user.id]
            }
            
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            message
        )

    
    def update_instance(self, content, curr_user=None):
        message = {
                'type': 'send_json',
                'content': {
                    'action': 'update_instance',
                    'data': {
                        'instance': content['instance']
                    }
                },
                'responded_users': content['responded_users']
            }
            
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            message
        )












