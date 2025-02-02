from typing import Any, Text, Dict
from rasa_sdk.types import DomainDict
from rasa_sdk import Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.forms import FormValidationAction
import re


class ShowAppointmentForm(FormValidationAction):
    '''
    Slots : appointment_status,name, contact, reschedule_appointment, appointment_date, appointment_time
    Returns : Dispatcher and Slot Value (Success and Failed Message with Buttons (Exit))
    Process : values from slot to be validated -> condition we want value to fulfill -> Set value in slot
    '''
    def name(self) -> Text:
        return "validate_show_appointment_form"

    def validate_selected_appointment(self,slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,) -> Dict[Text, Any]:
        slot_value = re.findall(r"[0-9]{1,20}",slot_value)
        if len(slot_value)>0:
            message = "Alright!"
            dispatcher.utter_message(text=message)
            return {"selected_appointment":slot_value[0]}
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
        
