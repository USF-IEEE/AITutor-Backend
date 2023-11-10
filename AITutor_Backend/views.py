from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from asgiref.sync import sync_to_async
from .models import SessionModel, TutorEnvModel
import uuid

async def session_view(request):
    if request.method == "POST":
        if 'session_key' in request.POST:
            # Handle the case where a session key is provided
            session_key = request.POST.get('session_key', None)
            if not session_key:
                return JsonResponse({"error": "Session key missing from request."})
            # Since the ORM is not fully async, we use sync_to_async to interact with it
            session = await sync_to_async(SessionModel.objects.get)(session_id=session_key)
            # Further processing...
            if session: await session.save()
            return JsonResponse({'session_key': session_key, 'response': 'Session exists. User input received.'})
        else:
            # Handle the case where no session key is provided
            new_session_key = str(uuid.uuid4())
            # Use sync_to_async for database operations
            tutor_environment = await sync_to_async(TutorEnvModel.objects.create)()
            await tutor_environment.save()
            session = await sync_to_async(SessionModel.objects.create)(session_id=new_session_key, env_id=tutor_environment.env_id)
            await session.save()
            return JsonResponse({'session_key': new_session_key, 'response': 'New session created.'})
    if request.method == "GET":
        return JsonResponse({'msg': "42."})
    else:
        return JsonResponse({'error': 'Invalid method'}, status=405)
