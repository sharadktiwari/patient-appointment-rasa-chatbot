from typing import Any, Text, Dict
from rasa_sdk.types import DomainDict
from rasa_sdk import Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.forms import FormValidationAction
import re

class PatientHistoryForm(FormValidationAction):
    '''
    Slots : appointment_by,name,gender,dob, contact,email, appointment_department, appointment_symptoms,appointment_dr_name,appointment_date,appointment_time
    Returns : Dispatcher and Slot Value (Success and Failed Message with Buttons (Exit))
    Process : values from slot to be validated -> condition we want value to fulfill -> Set value in slot
    '''
    def name(self) -> Text:
        return "validate_patient_history_form"

    def validate_fill_patient_history(self,slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict) -> Dict[Text, Any]:
        if slot_value=='yes':
            return {"fill_patient_history":'yes'}
        else:
            all_slots_of_patient_history_form = ["appointment_symptoms", "illness_duration", "ncdiseases", "medications"]
            
            set_slots = {slot:"nan" for slot in all_slots_of_patient_history_form}
            dispatcher.utter_message(text= "No problem, I understand!, But rest assured we have booked your appointment")
            return set_slots

    def validate_appointment_symptoms(self,slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,) -> Dict[Text, Any]:
        
        if slot_value and tracker.get_intent_of_latest_message() in ["pass_over","symptoms_developed"]:
            entities = {ents['value'] for ents in tracker.latest_message['entities'] if ents['entity']=='symptoms'}
            if slot_value == 'skip':
                message = "No problem, I understand!"
            elif len(entities)>0:
                message = f"Symptoms Detected - {', '.join(entities)}"
            else:
                message = "Sorry, I couldn't understand the symptoms"

            dispatcher.utter_message(text=message)
            return {"appointment_symptoms":slot_value,'detected_symptoms':list(entities)}
        else:
            dispatcher.utter_message(text="Sorry, I couldn't understand the symptoms. Can you please help me again ?")
            return {"appointment_symptoms":None}
        
        
    def validate_illness_duration(self,slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,) -> Dict[Text, Any]:
        
        if slot_value:
            message = "Got it!"
            dispatcher.utter_message(text=message)
            return {"illness_duration":slot_value}
        else:
            dispatcher.utter_message(text="Sorry, I couldn't get the duration. Can you please help me again ?")
            return {"illness_duration":None}
        

    def validate_medications(self,slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,) -> Dict[Text, Any]:
        
        if slot_value and tracker.get_intent_of_latest_message() in ["pass_over","current_medications"]:
            entities = {ents['value'] for ents in tracker.latest_message['entities'] if ents['entity']=='medication'}
            if slot_value == 'skip':
                message = "No problem, I understand!."
            elif len(entities)>0:
                message = f"I see, you are on the following medication - {', '.join(entities)}"
            else:
                message = "Sorry, I couldn't understand those medications. Can you please help me again ?"

            dispatcher.utter_message(text=message)
            return {"medications":slot_value,'detected_medications':list(entities)}
        else:
            dispatcher.utter_message(text="Sorry, I couldn't understand those medications. Can you please help me again ?")
            return {"medications":None}
        

    def validate_ncdiseases(self,slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,) -> Dict[Text, Any]:
        
        if slot_value:
            message = "Got it!"
            dispatcher.utter_message(text=message)
            if slot_value == 'skip':
                return {"ncdiseases":slot_value, "medications":'skip'}
            else:
                return {"ncdiseases":slot_value}
        else:
            dispatcher.utter_message(text="Sorry, I couldn't understand those NCDs. Can you please help me again ?")
            return {"ncdiseases":None}
        




