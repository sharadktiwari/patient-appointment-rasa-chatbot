from typing import Text
from rasa_sdk.types import DomainDict
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet, ActiveLoop
from database.CRUD import dboperations
from datetime import datetime

class ActionRescheduleAppointment(Action):
    '''
    Slots : appointment_status, name, contact, reschedule_appointment, appointment_date, appointment_time,
    AVAILABLE_VALUES :  current_appointments, user_details, date_list, time_list
    Returns : Dispatcher (Success and Failed Message with Buttons (Show Other Services, Restart, Exit))
    Process : Data from slots -> Updation in an existing appointment in database
    '''
    def name(self) -> Text:
        return "action_reschedule_appointment"
    
    def run(self,dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict):
        try:
            app_status = tracker.get_slot('appointment_status')
            visit_id = tracker.get_slot('selected_appointment')

            if not (app_status and visit_id):
                buttons = [{"title": "Want me to show or reschedule another appointment", "payload": "/greet"},{"title": "No, that should be it!", "payload": "/goodbye"}]
                dispatcher.utter_message(text="Uhho 😞, I got lost. Please, let me help you again !!",buttons=buttons)
                return [ActiveLoop(None),SlotSet('appointment_status',None),SlotSet('selected_appointment',None),SlotSet('appointment_date',None),SlotSet('appointment_time',None)]

            insertion_time = datetime.now()
            if app_status == 'Rescheduled':
                app_date = tracker.get_slot('appointment_date')
                app_time = tracker.get_slot('appointment_time')

                result = dboperations.update_appointment(visit_id,datetime.strptime(app_date,'%d/%m/%Y'),app_time,insertion_time)

                if result['status_code']==200:
                    message = f"Thanks! Your appointment has been rescheduled for {app_date} at {app_time}"
                else:
                    message = result['data']
            
            else:
                result = dboperations.update_status(visit_id, 0, insertion_time)
                
                if result['status_code']==200:
                    message = f"OK ! Your appointment has been {app_status}"
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
        return [SlotSet("appointment_status",None), SlotSet('selected_appointment',None), SlotSet('appointment_date',None), SlotSet('appointment_time',None),SlotSet('clinic_location',None) ,ActiveLoop(None)]

