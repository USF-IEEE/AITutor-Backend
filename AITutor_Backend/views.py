from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from asgiref.sync import sync_to_async
from .models import SessionModel, TutorEnvModel
import uuid

async def session_view(request):
    if request.method == "POST":            
        return JsonResponse({'msg': "42."})
    if request.method == "GET":
        # Handle the case where a session key is provided
        if 'session_key' in request.GET:

            session_key = request.GET.get('session_key', None)
            if not session_key:
                return JsonResponse({"error": "Session key missing from request."})
            # Since the ORM is not fully async, we use sync_to_async to interact with it
            session = await sync_to_async(SessionModel.objects.get)(session_id=session_key)
            # Further processing...
            if session: sync_to_async(session.save)()
            return JsonResponse({'session_key': session_key, 'response': 'Session exists. User input received.'})
        else:
            # Handle the case where no session key is provided
            new_session_key = str(uuid.uuid4())
            new_env_key = str(uuid.uuid4())
            # Use sync_to_async for database operations
            tutor_environment = await sync_to_async(TutorEnvModel.objects.create)(env_id=new_env_key)
            await sync_to_async(tutor_environment.save)()
            session = await sync_to_async(SessionModel.objects.create)(session_id=new_session_key, env_id=tutor_environment)
            await sync_to_async(session.save)()
            return JsonResponse({'session_key': new_session_key, 'response': 'New session created.'})
    else:
        return JsonResponse({'error': 'Invalid method'}, status=405)
