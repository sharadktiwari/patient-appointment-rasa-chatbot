from typing import Text
from rasa_sdk.types import DomainDict
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet,ActiveLoop
from database.CRUD import dboperations
from datetime import datetime

class ActionPatientHistory(Action):
    '''
    Slots : name, gender, dob, appointment_dr_name, appointment_date, appointment_time, contact, email
    Returns : Dispatcher (Success and Failed Message with Buttons (Show Other Services, Restart, Exit))
    Process : Data from slots -> Insertion of new appointment in database
    '''
    def name(self) -> Text:
        return "action_patient_history"
    
    def run(self,dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict):
        try:
            fill_patient_history = tracker.get_slot('fill_patient_history')
            app_sym = tracker.get_slot('appointment_symptoms')
            ill_dur = tracker.get_slot('illness_duration')
            ncd = tracker.get_slot('ncdiseases')
            meds = tracker.get_slot('medications')
            det_symp = tracker.get_slot('detected_symptoms')
            det_meds = tracker.get_slot('detected_medications')

            if app_sym== 'nan' or app_sym== 'skip':
                app_sym = None
            if ill_dur== 'nan' or ill_dur== 'skip':
                ill_dur = None
            if ncd== 'nan' or ncd== 'skip':
                ncd = None
            if meds== 'nan' or meds== 'skip':
                meds = None

            if not (app_sym or ill_dur or ncd or meds) or fill_patient_history == 'no':
                buttons = [{"title": "Want me to show or reschedule appointment", "payload": "/greet"},{"title": "No, that should be it!", "payload": "/goodbye"}]
                dispatcher.utter_message(buttons=buttons)
                return [ActiveLoop(None),SlotSet('patient_id',None),SlotSet('visit_id',None),SlotSet('detected_symptoms',None),SlotSet('detected_medications',None),
                        SlotSet('appointment_symptoms',None),SlotSet('illness_duration',None),SlotSet('medications',None),SlotSet('fill_patient_history',None),
                        SlotSet('ncdiseases',None),SlotSet('requested_slot',None)]

            patient_id = tracker.get_slot('patient_id')
            visit_id = tracker.get_slot('visit_id')

            insertion_time = datetime.now()

            ########################################################################################
            data = {'visit_id':visit_id,'symptoms':app_sym,'illness_duration':ill_dur,'ncd':ncd,'medications':meds}
            if det_symp:
                data['detected_symptoms'] = det_symp
            if det_meds:
                data['detected_medications'] = det_meds

            result = dboperations.fill_patient_history(patient_id,data,insertion_time)

            if result['status_code'] == 200 or result['status_code'] == 201:
                message = "Thanks for sharing the details!"
            else:
                message = "Uhho 😞, I got lost. But rest assured we have booked your appointment !!"

            dispatcher.utter_message(text= message)
            
            message = "Want me to help you reschedule or book another appointment ?"
            buttons = [{"title": "Yes, Please!!", "payload": "/greet"},{"title": "No, that should be it!", "payload": "/goodbye"}]
            dispatcher.utter_message(text= message,buttons=buttons)
            
        except Exception as e:
            print('Failed appointment (Exception) - ',e)
            message = "Uhho 😞, I got lost. But rest assured we have booked your appointment !!"
            buttons = [{"title": "Show my appointments", "payload": "/show_appointment"},{"title": "No, thanks!", "payload": "/goodbye"}]
            dispatcher.utter_message(text= message,buttons=buttons)
        return [SlotSet('appointment_symptoms',None),SlotSet('illness_duration',None),SlotSet('ncdiseases',None),SlotSet('medications',None),
                SlotSet('patient_id',None),SlotSet('visit_id',None),SlotSet('detected_symptoms',None),SlotSet('detected_medications',None),ActiveLoop(None)]
        