from typing import Any, Text, Dict, List
import datetime
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import ConversationPaused , ConversationResumed, ReminderScheduled
class ActionReactToReminder(Action):
    """Reminds the user to call someone."""

    def name(self) -> Text:
        return "action_react_to_set_reminder_terminate_session"

    async def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        print("Inside action action_react_to_set_reminder_terminate_session")
        ##Time to Resume the Chatbot Again.
        date = datetime.datetime.now() + datetime.timedelta(minutes=0.5)
        message = "Uhho, where am I ? Looks like I'm lost"
        buttons = [{"title": "Take me back", "payload": "/greet"}]
        dispatcher.utter_message()
        reminder = ReminderScheduled(
            "reminder_resume_bot",
            trigger_date_time=date,            
            name="resume",
            kill_on_user_message=False,
        )

        return[ConversationPaused(),reminder]

class ActionReactToReminderResumeBot(Action):
    """Reminds the user to call someone."""

    def name(self) -> Text:
        return "action_react_to_reminder_resume_bot"

    async def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        print("Inside action action_react_to_reminder_resume_bot")       
        dispatcher.utter_message(f"Bot Resumed")

        return[ConversationResumed()]  