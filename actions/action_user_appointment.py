from typing import Text
from rasa_sdk.types import DomainDict
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet, ActiveLoop, ActionExecuted, FollowupAction
from database.CRUD import dboperations
from scripts.helper import generate_id
from datetime import datetime

class ActionUserAppointment(Action):
    '''
    Slots : name, gender, dob, appointment_dr_name, appointment_date, appointment_time, contact, email
    Returns : Dispatcher (Success and Failed Message with Buttons (Show Other Services, Restart, Exit))
    Process : Data from slots -> Insertion of new appointment in database
    '''
    def name(self) -> Text:
        return "action_user_appointment"
    
    def run(self,dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict):
        try:
            vi_ty = tracker.get_slot('visit_type')
            pa_name = tracker.get_slot('name')
            pa_gender = tracker.get_slot('gender')
            pa_dob = tracker.get_slot('dob')
            pa_contact = tracker.get_slot('contact')
            app_date = tracker.get_slot('appointment_date')
            app_time = tracker.get_slot('appointment_time')
            loc_id = tracker.get_slot('clinic_location')

            if not (pa_name and pa_contact and pa_dob and pa_gender and app_date and app_time and loc_id):
                buttons = [{"title": "Want me to show or book appointment", "payload": "/greet"},{"title": "No, that should be it!", "payload": "/goodbye"}]
                dispatcher.utter_message(text="Uhho 😞, I got lost. Please, let me help you again !!",buttons=buttons)
                return [ActiveLoop(None), SlotSet('clinic_location',None),SlotSet('visit_type',None),SlotSet('appointment_date',None),SlotSet('appointment_time',None)]

            patient_id = generate_id()
            visit_id = generate_id()
            insertion_time = datetime.now()

            #######################################################################################
            result = dboperations.fill_patient_data(
                {
                    "patient_id":patient_id,
                    "name": pa_name.lower(),
                    "dob": pa_dob,
                    "gender": pa_gender,
                    "contact": pa_contact,
                    "created_at": insertion_time
                    }
            )

            if result['status_code']!=400:
                patient_id = result['data']
                if result['status_code']==200:
                    message = f"I see, you are already registered with us : [ {pa_name.title()} and {pa_contact} ]."
                else:
                    message = "Got you registered"
                dispatcher.utter_message(text= message)
                
                result = dboperations.fill_appointment_data(
                    {
                        "visit_id": visit_id,
                        "patient_id":patient_id,
                        "loc_id": loc_id,
                        "app_date": datetime.strptime(app_date,'%d/%m/%Y'),
                        "app_time_slot": app_time,
                        "status": 2 if vi_ty== 'follow_up' else 1,
                        "created_at": insertion_time,
                        "updated_at": insertion_time
                        }
                )
                if result['status_code']!=400:
                    visit_id = result['data']
                    if result['status_code']==200:
                        message = f"An Appointment already Exists for {pa_name.title()}"
                        dispatcher.utter_message(text= message)
                        message = "Want me to help you reschedule or book another appointment ?"
                        buttons = [{"title": "Book appointment", "payload": "/greet"},{"title": "No, that should be it!", "payload": "/goodbye"}]
                        dispatcher.utter_message(text= message,buttons=buttons)
                    else:
                        # message = "Got your appointment scheduled with Dr."
                        # dispatcher.utter_message(text= message)
                        dispatcher.utter_message(text= f"""Dear, {pa_name.title()}, Your {' '.join(vi_ty.split('_'))} appointment has been set for date - {app_date} and Time - {app_time}""")
                            
                        return [SlotSet("visit_type",None), SlotSet("gender",None), SlotSet("dob",None), SlotSet("appointment_date",None),
                                SlotSet("appointment_time",None),SlotSet("patient_id",patient_id), SlotSet("visit_id",visit_id),SlotSet('clinic_location',None),
                                # ActionExecuted("action_listen"),
                                FollowupAction('patient_history_form'),ActiveLoop("patient_history_form")]
                else:
                    buttons = [{"title": "Book appointment", "payload": "/greet"},{"title": "No, that should be it!", "payload": "/goodbye"}]
                    dispatcher.utter_message(text= "Uhho 😞, I got lost. Please, let me help you again !!", buttons=buttons)
            else:
                buttons = [{"title": "Book appointment", "payload": "/greet"},{"title": "No, that should be it!", "payload": "/goodbye"}]
                dispatcher.utter_message(text= "Uhho 😞, I got lost. Please, let me help you again !!",buttons=buttons)

            
        except Exception as e:
            print('Failed appointment (Exception) - ',e)
            message = "Uhho 😞, I got lost. Please, let me help you again !!"
            buttons = [{"title": "Book appointment", "payload": "/greet"},{"title": "No, that should be it!", "payload": "/goodbye"}]
            dispatcher.utter_message(text= message,buttons=buttons)
        
        return [SlotSet("visit_type",None), SlotSet("gender",None), SlotSet("dob",None), SlotSet("appointment_date",None), SlotSet("patient_id",None),
                SlotSet("visit_id",None),SlotSet('clinic_location',None),SlotSet("appointment_time",None),ActiveLoop(None)]
        
        
        