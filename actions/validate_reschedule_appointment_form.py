from typing import Any, Text, Dict
from rasa_sdk.types import DomainDict
from rasa_sdk import Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.forms import FormValidationAction
import re


class RescheduleAppointmentForm(FormValidationAction):
    '''
    Slots : appointment_status,name, contact, reschedule_appointment, appointment_date, appointment_time
    Returns : Dispatcher and Slot Value (Success and Failed Message with Buttons (Exit))
    Process : values from slot to be validated -> condition we want value to fulfill -> Set value in slot
    '''
    def name(self) -> Text:
        return "validate_reschedule_appointment_form"

    def validate_appointment_status(self,slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,) -> Dict[Text, Any]:
        if slot_value in ["Rescheduled","Canceled","Emergency"]:
            if slot_value == 'Rescheduled':
                message = "Please help me with the details to get it rescheduled"
                dispatcher.utter_message(text=message)
                return {'appointment_status':slot_value}
            else:
                message = "Alright, cancelling your Appointment"
                dispatcher.utter_message(text=message)
                return {'appointment_date':'1111/11/11','appointment_time':'11-11','appointment_status':slot_value}
        else:
            dispatcher.utter_message(text="Sorry, I couldn't understand that. Can you please help me again ?")
            return {'appointment_status':None}


    def validate_selected_appointment(self,slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,) -> Dict[Text, Any]:
        slot_value = re.findall(r"visit_id-([a-zA-Z0-9]{1,20}),\sloc_id-(\d{1,20})",slot_value)
        if len(slot_value)>0:
            message = "Alright!"
            dispatcher.utter_message(text=message)
            return {"selected_appointment":slot_value[0][0],'clinic_location':slot_value[0][1]}
        else:
            dispatcher.utter_message(text="Sorry, I guess that appointment no longer exists")
            return {"selected_appointment":None}
        

    def validate_contact(self,slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,) -> Dict[Text, Any]:
        
        slot_value = re.findall(r'[0-9-+\s]{10,18}',slot_value)

        if len(slot_value)>0:
            return {"contact":slot_value[0]}
        else:
            dispatcher.utter_message(text="Sorry, I couldn't understand your number. Can you please help me again ?")
            return {"contact":None}
        

    def validate_appointment_date(self,slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,) -> Dict[Text, Any]:
        slot_value = re.findall(r'[0-9]{2}/[0-9]{2}/[0-9]{4}',slot_value)
        if len(slot_value)>0:                
            message = f"Ok, when shall I get you booked ?"
            dispatcher.utter_message(text=message)
            return {"appointment_date":slot_value[0]}
        else:
            dispatcher.utter_message(text="Sorry, I couldn't understand the entered date. Can you please help me again ?")
            return {"appointment_date":None}


    def validate_appointment_time(self,slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,) -> Dict[Text, Any]:
        slot_value = re.findall(r'[0-9]{2}-[0-9]{2}',slot_value)
        if len(slot_value)>0:                
            return {"appointment_time":slot_value[0]}
        else:
            dispatcher.utter_message(text="Sorry, I couldn't understand the entered time. Can you please help me again ?")
            return {"appointment_time":None}
        
