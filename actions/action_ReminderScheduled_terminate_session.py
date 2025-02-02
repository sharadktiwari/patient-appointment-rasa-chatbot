import datetime
from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import ReminderScheduled,BotUttered
from rasa_sdk import Action

class ActionSetReminderTerminateSession(Action):
    """Schedules a reminder, supplied with the last message's entities."""

    def name(self) -> Text:
        return "action_set_reminder_terminate_session"

    async def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        print("Inside Reminder")
        timeout = 1
        message = f"Session will Expire in {timeout} seconds"

        date = datetime.datetime.now() + datetime.timedelta(seconds=timeout)
        entities = tracker.latest_message.get("entities")
        print("Reminder set")
        reminder = ReminderScheduled(
            "reminder_terminate",
            trigger_date_time=date,
            entities=entities,
            name="terminate",
            kill_on_user_message=False,
        )
        dispatcher.utter_message(message, "From Dispatcher.")
        return [reminder, BotUttered(message)]