from typing import Text
from rasa_sdk.types import DomainDict
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
import datetime, pytz
from database.CRUD import dboperations
from rasa_sdk.events import FollowupAction


class ActionAskClinicLocation(Action):
    '''
    Slots : name, contact
    Returns : Dispatcher (Available Appointments to reschedule and Failed Message with Buttons (Show Other Services, Restart, Exit))
    Process : Data from slots -> Retrive data from database (user_id, name and contact -> appointment details (doctor id and name, date and time))
    '''

    def name(self) -> Text:
        return "action_ask_clinic_location"

    def run(self,dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict):
        buttons= [] 

        app_dr_contact = tracker.get_slot('dr_contact')
        location_data = dboperations.get_doc_locations(dr_contact = app_dr_contact)

        if location_data['status_code'] == 400:
            dispatcher.utter_message(text="I am not feeling very well today, please come back later")
            return [FollowupAction('action_deactivate_loop')]
        else:
            buttons = []
            message = 'Please select prefered clinic :- \n'
            for data in location_data['data']:
                title = data['loc_address'] 
                payload= f"Location - {str(data['loc_id'])}"  
                buttons.append({"title": title, "payload": payload})
            buttons.append({"title":"Restart","payload":"/restart_bot"})
            dispatcher.utter_message(text=message,buttons=buttons)
            return [] 
    

class ActionAskAppointmentDate(Action):
    '''
    Slots : appointment_dr_name, reschedule_appointment, active_loop
    Returns : Dispatcher (Doctor's Available Date list and Failed Message with Buttons (Show Other Services, Restart, Exit))
    Process : Data from slots -> Retrive data from database (dr_id -> doc_details (date and time))
    '''

    def name(self) -> Text:
        return "action_ask_appointment_date"
    
    def run(self,dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict):

        buttons= []
        loc_id = tracker.get_slot('clinic_location')

        if loc_id:
            appointment_day_data = dboperations.location_appointment_days(loc_id)
            
            if appointment_day_data['status_code'] == 400:
                dispatcher.utter_message(text='I am not feeling very well today, please come back later')
                return [FollowupAction('action_deactivate_loop')]
            
            appointment_time_data = dboperations.location_appointment_time(loc_id)
            
            if appointment_time_data['status_code'] == 400:
                dispatcher.utter_message(text='I am not feeling very well today, please come back later')
                return [FollowupAction('action_deactivate_loop')]
            
            ################################################################################################
            day_list = appointment_day_data['data']
            dates = []
            tday = datetime.date.today()
            twday=tday.weekday()
            for i in day_list:
                if i>twday:
                    diff = i-twday
                    a_date = tday+datetime.timedelta(days=diff)
                elif i<twday:
                    tweek = 7-twday
                    diff = tweek+i
                    a_date = tday+datetime.timedelta(days=diff)
                elif i==twday:
                    if datetime.time(hour=max([int(ts.split('-')[-1]) for ts in appointment_time_data['data']])-1,minute=30) <= datetime.datetime.now(pytz.timezone("Asia/Kolkata")).time():
                        continue
                    a_date = tday
                dates.append(a_date)
            
            dispatcher.utter_message(text="When would you like to book an appointment ?")
            dates.sort()
            for date in dates:
                dl = date.strftime("%d/%m/%Y")
                payload = "/appointment_info{\"date\":\"" + dl + "\"}"
                buttons.append({"title": f"{dl}", "payload": payload}) 

            if len(buttons) ==0:
                message = f"Sorry, no slots available for this week."
            else:
                message ="Dr. is available on 📅"
            buttons.append({"title":"Restart","payload":"/restart_bot"})
            dispatcher.utter_message(text=message,buttons=buttons)
            return []
        else:
            message = f"Uhho 😞, I got lost. Please, let me help you again !!"
            buttons = [{"title": "Yes, Please!!", "payload": "/restart_bot"},{"title": "No, that should be it!", "payload": "/goodbye"}]
            dispatcher.utter_message(text=message,buttons=buttons)
    

class ActionAskAppointmentTime(Action):
    '''
    Slots : appointment_date,  active_loop
    Returns : Dispatcher (Doctor's Available Time list and Failed Message with Buttons (Show Other Services, Restart, Exit))
    Process : Data from slots -> Retrive data from database (dr_id -> doc_details (date and time))
    '''

    def name(self) -> Text:
        return "action_ask_appointment_time"
    
    def run(self,dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict):

        buttons= []
        loc_id = tracker.get_slot('clinic_location')
        app_date = tracker.get_slot('appointment_date')

        if loc_id:
            appointment_time_data = dboperations.location_appointment_time(loc_id)
            
            if appointment_time_data['status_code'] == 400:
                dispatcher.utter_message(text='I am not feeling very well today, please come back later')
                return [FollowupAction('action_deactivate_loop')]
            
            ###################################################################################
            
            for tl in appointment_time_data['data']:
                if datetime.date.today() >= datetime.datetime.strptime(app_date,'%d/%m/%Y').date() and datetime.time(hour=int(tl.split('-')[-1])-1,minute=30) <= datetime.datetime.now(pytz.timezone("Asia/Kolkata")).time():
                    continue
                payload = "/appointment_info{\"time\":\"" + tl + "\"}"
                buttons.append({"title": f"{tl.title()}", "payload": payload})
            
            if not len(buttons):
                message = f"Sorry, Dr. isn't available on this date."
                dispatcher.utter_message(text=message)
                message = f"let me help you again !!"
                buttons = [{"title": "Yes, Please!!", "payload": "/restart_bot"},{"title": "No, that should be it!", "payload": "/goodbye"}]
                dispatcher.utter_message(text=message,buttons=buttons)
                return []
            
            message = f"So, What Time?"
            dispatcher.utter_message(text=message)
            
            if len(buttons)==1:
                message = f"Dr. is occupied for all other slots, except :-"
            else:
                message ="These are current available slots 🕐"
        
            buttons.append({"title":"Restart","payload":"/restart_bot"})
            dispatcher.utter_message(text=message,buttons=buttons)
            return []
        else:
            message = f"Uhho 😞, I got lost. Please, let me help you again !!"
            buttons = [{"title": "Yes, Please!!", "payload": "/restart_bot"},{"title": "No, that should be it!", "payload": "/goodbye"}]
            dispatcher.utter_message(text=message,buttons=buttons)


class ActionAskSelectedAppointment(Action):
    '''
    Slots : name, contact
    AVAILABLE_VALUES :  user_details, current_appointments
    Returns : Dispatcher (Available Appointments to reschedule and Failed Message with Buttons (Show Other Services, Restart, Exit))
    Process : Data from slots -> Retrive data from database (user_id, name and contact -> appointment details (doctor id and name, date and time))
    '''

    def name(self) -> Text:
        return "action_ask_selected_appointment"

    def run(self,dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict):
        buttons= []
        current_loop = tracker.active_loop.get("name") 
        app_contact = tracker.get_slot('contact')
        dr_contact = tracker.get_slot('dr_contact')
        
        current_appointments = dboperations.get_patient_appointments(dr_contact,app_contact,datetime.datetime.now())
        
        if current_appointments['status_code']==200:
            if current_loop == 'reschedule_appointment_form':
                message = 'These are your upcoming appointments with Dr.:- \n'
                for cur_apoint in current_appointments['data']:
                    payload= f"visit_id-{cur_apoint['visit_id']}, loc_id-{cur_apoint['loc_id']}"
                    show = f"""{cur_apoint['name'].title()}'s appointment at Clinic - ({cur_apoint['loc_address']}), on - ({cur_apoint['app_date'].strftime('%d/%m/%Y')}) between - ({cur_apoint['app_time_slot']})"""
                    buttons.append({"title": show, "payload": payload})
            else:
                message = 'These are your scheduled appointments with Dr.:- \n'
                for cur_apoint in current_appointments['data']:
                    payload= f"visit_id-{cur_apoint['visit_id']}"
                    show = f"""{cur_apoint['name'].title()}'s appointment at Clinic - ({cur_apoint['loc_address']}), on - ({cur_apoint['app_date'].strftime('%d/%m/%Y')}) between - ({cur_apoint['app_time_slot']})"""
                    buttons.append({"title": show, "payload": payload}) 
            buttons.append({"title":"Restart","payload":"/restart_bot"})
            dispatcher.utter_message(text=message,buttons=buttons)
            return []
        else:
            message = "You don't have appointment with Dr yet and Can I Help you with the appointments"
            buttons = [{"title": "Yes, Please!!", "payload": "/restart_bot"},{"title": "No, that should be it!", "payload": "/goodbye"}]
            dispatcher.utter_message(text=message,buttons=buttons)
            return []
