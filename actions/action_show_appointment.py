from typing import Text
from rasa_sdk.types import DomainDict
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet,ActiveLoop
from database.CRUD import dboperations
from datetime import datetime


class ActionShowAppointment(Action):
    '''
    Slots : appointment_status, name, contact, reschedule_appointment, appointment_date, appointment_time,
    AVAILABLE_VALUES :  current_appointments, user_details, date_list, time_list
    Returns : Dispatcher (Success and Failed Message with Buttons (Show Other Services, Restart, Exit))
    Process : Data from slots -> Updation in an existing appointment in database
    '''
    def name(self) -> Text:
        return "action_show_appointment"
    
    def run(self,dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict):
        try:
            visit_id = tracker.get_slot('selected_appointment')
            
            if not visit_id:
                buttons = [{"title": "Want me to book or reschedule appointment", "payload": "/greet"},{"title": "No, that should be it!", "payload": "/goodbye"}]
                dispatcher.utter_message(text="Uhho 😞, I got lost. Please, let me help you again !!",buttons=buttons)
                return [ActiveLoop(None),SlotSet('selected_appointment',None)]

            else:
                result = dboperations.get_appointment_details(visit_id)
                
                if result['status_code']==200:
                    message = f"""OK ! {result['data']['name'].title()} your {'New Patient' if result['data']['status']==1 else 'Follow Up'} \
                        appointment is scheduled with Dr. {result['data']['doc_name'].title()} on {result['data']['app_date'].strftime('%d/%m/%Y')} between \
                        {result['data']['app_time_slot']} at {result['data']['loc_address']}."""
                    dispatcher.utter_message(text= message)
                    if 'history' in result['data'].keys():
                        if 'detected_medications' in result['data']['history'].keys():
                            result['data']['history'].pop('detected_medications')
                        if 'detected_symptoms' in result['data']['history'].keys():
                            result['data']['history'].pop('detected_symptoms')
                        result['data']['history'].pop('visit_id')
                        message = ""
                        message_type = {'symptoms':"Patient is suffering from", 'illness_duration':"for", 'ncd':"Patient has following existing medical conditions", 'medications': "and has been advised to take following medicines"}
                        for k,v in result['data']['history'].items():
                            message += f"{message_type[k]} {v} "
                        dispatcher.utter_message(text= message)
                else:
                    message = result['data']
                    dispatcher.utter_message(text= message)

            message = "Want me to help you reschedule or book another appointment ?"
            buttons = [{"title": "Yes, Please!!", "payload": "/greet"},{"title": "No, that should be it!", "payload": "/goodbye"}]
            dispatcher.utter_message(text= message,buttons=buttons)
        
        except Exception as e:
            print('Failed Reschedule Appointment Form (Exception) - ',e)
            message = "Uhho 😞, I got lost. Please, let me help you again !!"
            buttons = [{"title": "Book appointment", "payload": "/greet"},{"title": "No, that should be it!", "payload": "/goodbye"}]
            dispatcher.utter_message(text= message,buttons=buttons)
        return [SlotSet('selected_appointment',None),ActiveLoop(None)]

