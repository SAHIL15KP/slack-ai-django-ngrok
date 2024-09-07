import json 
from django.http import HttpResponse 
from django.views.decorators.csrf import csrf_exempt 
from django.views.decorators.http import require_POST 
# Create your views here.
import helpers
import requests
SLACK_BOT_OAUTH_TOKEN = helpers.config('slack_bot_oauth_token',default=None , cast=str)

def send_message(message , channel_id=None):
    url = "https://slack.com/api/chat.postMessage"
    headers = {
    "Content-Type": "application/json; charset=utf-8",
    "Authorization": f"Bearer {SLACK_BOT_OAUTH_TOKEN}",
    "Accept":"application/json"
    }
    data = {
    "channel": f"{channel_id}",
    "text": message
}

    return requests.post(url , json=data , headers=headers)

@csrf_exempt
@require_POST
def slack_events_endpoint(request):
    json_data = {}
    try:
        json_data = json.loads(request.body.decode('utf-8'))
    except:
        pass

    data_type = json_data.get('type')

    print(data_type, json_data)
    allowed_data_type = [
        'url-verification',
        'event_callback'
    ]

    if data_type not in allowed_data_type:
        return HttpResponse("not allowed ", status = 400)  

    if data_type == "url_verification":
        challenge = json_data.get('challenge')
        if challenge is None:
            return HttpResponse("not allowed ", status=400)
        return HttpResponse(challenge, status=200)
    

    if data_type == "event_callback":
        event = json_data.get('event') or {}
        msg_text = event.get('text')
        channel_id = event.get('channel')
        # user_id = event.get('user')
        r=send_message(msg_text, channel_id=channel_id)
        return HttpResponse("success", status=r.status_code)

    return HttpResponse("SUCCESS", status=200)
