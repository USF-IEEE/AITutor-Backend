import json
import uuid
from django.http import JsonResponse, HttpResponseBadRequest
from asgiref.sync import sync_to_async
from django.views.decorators.csrf import csrf_exempt
from asgiref.sync import sync_to_async, async_to_sync
from AITutor_Backend.models import DatabaseManager
import uuid

def make_error_response(error_msg, sid, status=405):
    return JsonResponse(
        {"session_key":f"{sid}", 
         "success": False, 
         "resonse": {
        "error": error_msg
    }}, status=status)

def make_environment_response(environment_data, current_state, sid, status=200):
    environment_data = json.dumps(environment_data)
    def __get_response_obj(current_state, environment_data):
        if current_state == 0: return (True, {"prompt": environment_data})
        if current_state == 1: return (True, {"teaching": environment_data})
        if current_state == 2: return (True, {"guiding": environment_data})
        if current_state == 3: return (True, {"testing": environment_data})
        return (False, "Invalid state has occured. Try restarting the session.",)
    success, response_obj = __get_response_obj(current_state, environment_data)
    return JsonResponse(
        {"session_key":f"{sid}", 
         "success": success, 
         "resonse": {response_obj}
        }, 200) if success else make_error_response(response_obj, sid, )
   

def process_session_data(data):
    # Extract User Input:
        if not data["user_prompt"]: return (make_error_response)("No user prompt provided, ensure you are sending over the proper data.", data["session_key"])     
        # Further processing:
        db_manager =  DatabaseManager(session_id=data["session_key"])
        db_manager.load_tutor_env()
        environment_data, current_state = (db_manager.process_tutor_env)(data)
        # Save Enviornment State:
        db_manager.save_tutor_env()
        # Return Env Response:
        return make_environment_response(environment_data, current_state, data["session_key"])

def create_and_process_session_data(data):
    # Handle the case where no session key is provided
    session_key, db_manager = DatabaseManager.create_tutor_session()
    db_manager.load_tutor_env()
    environment_data, current_state = db_manager.process_tutor_env(data)
    # Save Enviornment State:
    db_manager.save_tutor_env()
    # Return Env Response:
    return make_environment_response(environment_data, current_state, session_key)

# TODO: Fix CSRF error
@csrf_exempt
def session_view(request):
    if request.method == "GET":            
        return JsonResponse({'msg': "42."})
    if request.method == "POST":
        raw_data = request.body.decode('utf-8')
        json_data = json.loads(raw_data)
        data = {
                "is_audio": json_data.get("is_audio", ""),
                "user_prompt": json_data.get("user_prompt", ""),
                "session_key": json_data.get("session_key", ""),
                # TODO: add more modalities e.g. files, audio, ...
            }
        # Handle the case where a session key is provided:
        if 'session_key' in data and data["session_key"]:
            return process_session_data(data)
        else:
            return create_and_process_session_data(data)
    else:
        return HttpResponseBadRequest('Invalid method')
