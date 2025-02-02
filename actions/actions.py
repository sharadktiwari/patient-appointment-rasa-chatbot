from typing import Any, Text, Dict, List
from rasa_sdk.types import DomainDict
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import UserUtteranceReverted,ConversationPaused, ActionReverted #, ActionExecuted, ReminderScheduled,Restarted
from rasa_sdk.events import SlotSet, ActiveLoop, FollowupAction
from database.CRUD import dboperations

# class ActionDefaultFallback(Action):
#     '''
#     Returns : Dispatcher (Please Enter Requested Input) if failed to define any intent or condition
#     Process : Continuous 10 fallbacks will pause the session
#     '''
#     def name(self) -> Text:
#             return "action_default_fallback"
#     def run(self, dispatcher, tracker: Tracker , domain: Dict[Text, Any]):
#         last_action  = ActionExecuted("action_default_fallback").get('name')
#         str(tracker.events)

#         ###Reminder to ResumeConversation After 30 seconds mins
#         date = datetime.datetime.now() + datetime.timedelta(seconds=.01)
#         reminder = ReminderScheduled(
#             "reminder_terminate",
#             trigger_date_time=date,            
#             name="ResumeSessionAfterFewTime",
#             kill_on_user_message=False,
#         )

#         print('last_action',last_action)
#         print('session_time', session_time)
#         session_time['last_action']=last_action
#         if last_action == "action_default_fallback":
#             message = "Please Enter Requested Input 🤔..."
#             dispatcher.utter_message(text=message)
#             session_time['counter']+=1            
#         else:
#             message = "Please Enter Requested Input 🤔..."
#             dispatcher.utter_message(text=message)
#             session_time['counter'] = 0        
            
#         if session_time['counter'] == 10:
#             dispatcher.utter_message(text=f"I guess, I'm not able to get you. Please, try booking the appointment again.")
#             session_time['counter'] = 0
#             session_time['same_intent_counter'] = 0
#             return[reminder, ConversationPaused(),ActiveLoop(None),Restarted()]
            
#         else:

#             message = "Please Enter Requested Input 🤔..."
#             # dispatcher.utter_message(text=message)
#             return [ConversationPaused(), UserUtteranceReverted()]

class ActionGreet(Action):
    '''
    Returns : Dispatcher (Greet Message with Buttons associated with logged in user)
    Process : Value from is_authenticated defines type of user, leads to portal selection
    '''
    def name(self) -> Text:
            return "action_greet"

    def run(self, dispatcher, tracker, domain):
        dr_contact = tracker.get_slot('dr_contact')
        if not dr_contact:
            dispatcher.utter_message(text="I am not feeling very well today, please come back later")
            return []
        
        result = dboperations.check_doc_presence(dr_contact)
        if result['status_code']==400:
            dispatcher.utter_message(text="I am not feeling very well today, please come back later")
            return []

        message = "How can I assist you ? :-"
        buttons = [{"title": "Schedule Appointment", "payload": "/make_appointment"},
                    {"title": "Modify Your Appointment", "payload": "/reschedule_appointment"},
                    {"title": "Show Appointments", "payload": "/show_appointment"}]
        dispatcher.utter_message(text=message,buttons=buttons)
        return []

class ActionOutOfScope(Action):
    '''
    Returns : Dispatcher (Out Of Scope Message)
    Process : Out of Scope intent triggers this action
    '''
    def name(self) -> Text:
            return "action_out_of_scope"
    def run(self, dispatcher, tracker, domain):

        message = "Oops, sorry - currently I can only help you with Booking or Rescheduling appointments."
        dispatcher.utter_message(text=message)
        return [ConversationPaused(),ActionReverted(), UserUtteranceReverted()]

class ActionIAmBot(Action):
    '''
    Returns : Dispatcher (I am bot Message)
    Process : I am bot intent triggers this action
    '''
    def name(self) -> Text:
            return "action_iamabot"
    def run(self, dispatcher, tracker, domain):

        message = "Namaste 🙏🏼, I am your Appointment Assistant. Here to help you with scheduling appointments with the Doc."
        dispatcher.utter_message(text=message)
        return [ConversationPaused(),ActionReverted(), UserUtteranceReverted()]

class ActionWellBeingNotWell(Action):
    '''
    Returns : Dispatcher (Wellbeing Message)
    Process : welbeing not well intent triggers this action
    '''
    def name(self) -> Text:
            return "action_wellbeing_not_well"
    def run(self, dispatcher, tracker, domain):

        message = "So sorry that you are not feeling very well today!."
        dispatcher.utter_message(text=message)
        return [ConversationPaused(),ActionReverted(), UserUtteranceReverted()]


class ActionWellBeingWell(Action):
    '''
    Returns : Dispatcher (wellbeing Message)
    Process : wellbeing well intent triggers this action
    '''
    def name(self) -> Text:
            return "action_wellbeing_well"
    def run(self, dispatcher, tracker, domain):

        message = "That makes me happy 🤗..."
        dispatcher.utter_message(text=message)
        return [ConversationPaused(),ActionReverted(), UserUtteranceReverted()]
    

class ActionRestart(Action):

  def name(self) -> Text:
      return "action_restart"

  async def run(
      self, dispatcher, tracker: Tracker, domain: Dict[Text, Any]
  ) -> List[Dict[Text, Any]]:       
        return [ActiveLoop(None), SlotSet('clinic_location',None),SlotSet('visit_type',None),SlotSet('patient_id',None),SlotSet('visit_id',None),SlotSet('detected_symptoms',None),
                SlotSet('appointment_date',None),SlotSet('appointment_time',None),SlotSet('name',None),SlotSet('dob',None),SlotSet('gender',None),SlotSet('contact',None),
                SlotSet('appointment_symptoms',None),SlotSet('illness_duration',None),SlotSet('medications',None),SlotSet('fill_patient_history',None),SlotSet('ncdiseases',None),
                SlotSet('appointment_status',None),SlotSet('selected_appointment',None),SlotSet('requested_slot',None),FollowupAction('action_greet')]


class ActionDeactivateLoop(Action):
    '''
    Process : Terminates the current loop
    '''
    def name(self) -> Text:
        return 'action_deactivate_loop'

    async def run(self,dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict):
        return [ActiveLoop(None), SlotSet('clinic_location',None),SlotSet('visit_type',None),SlotSet('patient_id',None),SlotSet('visit_id',None),SlotSet('detected_symptoms',None),
                SlotSet('appointment_date',None),SlotSet('appointment_time',None),SlotSet('name',None),SlotSet('dob',None),SlotSet('gender',None),SlotSet('appointment_symptoms',None),
                SlotSet('illness_duration',None),SlotSet('medications',None),SlotSet('fill_patient_history',None),SlotSet('ncdiseases',None),SlotSet('appointment_status',None),
                SlotSet('selected_appointment',None),SlotSet('requested_slot',None)]


# class ActionListen(Action):
#     '''
#     Rasa calls this action by default during user input
#     Process : 3 Continuous requests of slot will pause the session, same goes with 10 continuous intents.
#     '''
#     def name(self) -> Text:
#         return 'action_listen'

#     async def run(self,dispatcher: CollectingDispatcher,
#             tracker: Tracker,
#             domain: DomainDict):  
#         last_intent = tracker.get_intent_of_latest_message()
#         last_action  = ActionExecuted("action_default_fallback").get('name')
#         current_loop = tracker.active_loop.get("name") 
#         for trak_eve in tracker.events:
#             if trak_eve['event']=='slot' and trak_eve["name"]=='requested_slot':
#                 if session_time['last_slot'] == trak_eve['value']:
#                     session_time['slot_counter']+=1
#                 else:
#                     session_time['last_slot'] = trak_eve['value']
#                     session_time['slot_counter']=0


#         if last_action != "action_default_fallback":
#             session_time['counter']=0  

#         if last_intent == session_time['last_intent']:
#             session_time['same_intent_counter']+=1
#             session_time['last_intent'] = last_intent
#         else:
#             session_time['same_intent_counter']=0
#             session_time['last_intent'] = last_intent
#         if session_time['same_intent_counter'] == 10:    
#             session_time['same_intent_counter'] = 0
#             message = "I guess, I'm not able to get you. Please, try booking the appointment again."
#             dispatcher.utter_message(message)
#             return[ConversationPaused(),ActiveLoop(None)]
            
#         else:           
#             return []
        


