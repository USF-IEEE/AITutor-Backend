import json
import uuid
from django.http import JsonResponse, HttpResponseBadRequest
from asgiref.sync import sync_to_async
from django.views.decorators.csrf import csrf_exempt
from .models import SessionModel, TutorEnvModel

@sync_to_async
def create_tutor_environment():
    env_id = str(uuid.uuid4())
    tutor_environment = TutorEnvModel.objects.create(env_id=env_id)
    tutor_environment.save()
    return tutor_environment

@sync_to_async
def create_session(env_id):
    session_id = str(uuid.uuid4())
    session = SessionModel.objects.create(session_id=session_id, env_id=env_id)
    session.save()
    return session

@csrf_exempt
def session_view(request):
    if request.method == "GET":
        # Handle GET request
        return JsonResponse({'message': "this is a test message"})
    
    if request.method == "POST":
        try:
            # Get the raw JSON data from the request body
            raw_data = request.body.decode('utf-8')
            json_data = json.loads(raw_data)

            # Extract specific fields from the JSON data
            session_key = json_data.get('session_key', '')
            user_prompt = json_data.get('user_prompt', '')

            # Your processing logic here...

            return JsonResponse({'session_key': session_key, 'user_prompt': user_prompt, 'status': 'success', 'response': 'data to send back'})
        
        except json.JSONDecodeError as e:
            return JsonResponse({'error': 'Invalid JSON format'}, status=400)
        except Exception as e:
            return JsonResponse({'error': f'An error occurred: {str(e)}'}, status=500)

    else:
        return HttpResponseBadRequest('Invalid method')
