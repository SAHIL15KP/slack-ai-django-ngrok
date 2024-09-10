import requests
import json
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import helpers
from pprint import pprint
import slacky
from .tasks import slack_message_task

SLACK_BOT_OAUTH_TOKEN = helpers.config('SLACK_BOT_OAUTH_TOKEN', default=None, cast=str)

@csrf_exempt
@require_POST
def slack_events_endpoint(request):
    json_data = {}
    try:
        json_data = json.loads(request.body.decode('utf-8'))
    except json.JSONDecodeError as e:
        print(f"JSON decode error: {e}")
        return HttpResponse("Invalid JSON", status=400)

    data_type = json_data.get('type')

    allowed_data_type = [
        'url_verification',
        'event_callback'
    ]

    if data_type not in allowed_data_type:
        return HttpResponse("not allowed", status=400)

    if data_type == "url_verification":
        challenge = json_data.get('challenge')
        if challenge is None:
            return HttpResponse("not allowed", status=400)
        return HttpResponse(challenge, status=200)

    elif data_type == "event_callback":
        event = json_data.get('event') or {}
        try:
            msg_text = event['blocks'][0]['elements'][0]['elements'][1]['text']
        except:
            msg_text = event.get('text')
        channel_id = event.get('channel')
        user_id = event.get('user')
        msg_ts = event.get('ts')
        thread_ts = event.get('thread_ts') or msg_ts
        slack_message_task.delay(msg_text, channel_id=channel_id, user_id=user_id, thread_ts=thread_ts)
        return HttpResponse("success", status=200)

    return HttpResponse("SUCCESS", status=200)