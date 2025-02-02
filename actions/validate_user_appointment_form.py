from typing import Any, Text, Dict
from rasa_sdk.types import DomainDict
from rasa_sdk import Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.forms import FormValidationAction
import re
from database.CRUD import dboperations

class UserAppointmentForm(FormValidationAction):
    '''
    Slots : appointment_by,name,gender,dob, contact,email, appointment_department, appointment_symptoms,appointment_dr_name,appointment_date,appointment_time
    Returns : Dispatcher and Slot Value (Success and Failed Message with Buttons (Exit))
    Process : values from slot to be validated -> condition we want value to fulfill -> Set value in slot
    '''
    def name(self) -> Text:
        return "validate_user_appointment_form"
    

    def validate_clinic_location(self,slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,) -> Dict[Text, Any]:
        
        slot_value = re.findall(r'[0-9]{1,20}',slot_value)

        if len(slot_value)>0 :
            message = "Alright!"
            dispatcher.utter_message(text=message)
            return {"clinic_location":slot_value[0]}
        else:
            dispatcher.utter_message(text="Sorry, I couldn't pick that location. Can you please help me again ?")
            return {"clinic_location":None}


    def validate_visit_type(self,slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,) -> Dict[Text, Any]:
        if slot_value == 'new_patient' or slot_value == 'follow_up':
            visitType = {'new_patient': 'first', 'follow_up': 'follow up'}
            message = f"I see, this is your {visitType[slot_value]} visit to the Dr."
            dispatcher.utter_message(text=message)
            return {"visit_type":slot_value}
        else:
            dispatcher.utter_message(text="Sorry, I couldn't understand the purpose of your visit. Can you please help me again ?")
            return {"visit_type":None}


    def validate_appointment_date(self,slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,) -> Dict[Text, Any]:
        slot_value = re.findall(r'[0-9]{2}/[0-9]{2}/[0-9]{4}',slot_value)
        if len(slot_value)>0:                
            # message = f"So, What Time?"
            # dispatcher.utter_message(text=message)
            return {"appointment_date":slot_value[0]}
        else:
            dispatcher.utter_message(text="Sorry, that is not in correct format as I was expecting. Can you try that again, please ?")
            return {"appointment_date":None}


    def validate_appointment_time(self,slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,) -> Dict[Text, Any]:
        slot_value = re.findall(r'[0-9]{2}-[0-9]{2}',slot_value)
        if len(slot_value)>0:           
            contact = tracker.get_slot('contact')
            name = tracker.get_slot('name')
            if name and contact:
                check_user = dboperations.check_user_presence({"name":name,"contact":contact})
                if check_user['status_code']==200:
                    return {"appointment_time":slot_value[0],"dob":check_user['data']['dob'],"gender":check_user['data']['gender']}
            return {"appointment_time":slot_value[0]}
        else:
            dispatcher.utter_message(text="Sorry, that is not in correct format as I was expecting. Can you try that again, please ?")
            return {"appointment_time":None}


    def validate_name(self,slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,) -> Dict[Text, Any]:
        if slot_value:
            message = f"Welcome {slot_value.title()}😀!"
            dispatcher.utter_message(text=message)
            contact = tracker.get_slot('contact')
            if contact:
                check_user = dboperations.check_user_presence({"name":slot_value,"contact":contact})
                if check_user['status_code']==200:
                    return {"name":slot_value,"dob":check_user['data']['dob'],"gender":check_user['data']['gender']}
            return {"name":slot_value}
        else:
            dispatcher.utter_message(text="Sorry, couldn't get your name. Can you try that again, please ?")
            return {"name":None}


    def validate_dob(self,slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,) -> Dict[Text, Any]:

        # slot_value = re.findall(r'[0-9]{2}/[0-9]{2}/[0-9]{2,4}',slot_value)
        slot_value =re.findall(r"([0123]{1}[\d]{1}\/[01]{1}[\d]{1}\/[12]{1}[90]{1}[\d]{2}|[0123]{1}[\d]{1}\/[01]{1}[\d]{1}\/[\d]{2})\b",slot_value)

        if len(slot_value)>0:
            try:
                if len(slot_value[0]) ==10:
                    import datetime
                    if datetime.datetime.strptime(slot_value[0],"%d/%m/%Y") > datetime.datetime.now():
                        message = "Sorry, that is not in correct format as I was expecting. Can you try that again, please ?"
                        dispatcher.utter_message(text=message)
                        return {"dob":None}

                    message = "Got it....."
                    dispatcher.utter_message(text=message)
                    return {"dob":slot_value[0]}
                else:
                    message = "Sorry, that is not in correct format as I was expecting. Can you try that again, please ?"
                    dispatcher.utter_message(text=message)
                    return {"dob":None}
            except:
                message = "Sorry, that is not in correct format as I was expecting. Can you try that again, please ?"
                dispatcher.utter_message(text=message)
                return {"dob":None}
        else:
            dispatcher.utter_message(text="Sorry, that is not in correct format as I was expecting. Can you try that again, please [DD/MM/YYYY] ?")
            return {"dob":None}
        

    def validate_gender(self,slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,) -> Dict[Text, Any]:
        if slot_value:
            return {"gender":slot_value}
        else:
            dispatcher.utter_message(text="Sorry, I didn't get you. can you try that again, please ?")
            return {"gender":[]}
        

    def validate_contact(self,slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,) -> Dict[Text, Any]:
        
        slot_value = re.findall(r'[0-9-+\s]{10,18}',slot_value)
        
        if len(slot_value)>0:
            check_user = dboperations.check_user_presence({"name":tracker.get_slot('name'),"contact":slot_value[0]})
            if check_user['status_code']==200:
                return {"contact":check_user['data']['contact'],"dob":check_user['data']['dob'],"gender":check_user['data']['gender']}
            else:
                return {"contact":slot_value[0]}
        else:
            dispatcher.utter_message(text="Sorry, that seems to be an incorrect contact number. Can you try that again, please ?")
            return {"contact":None}





