# Specific tests
from dialogs.booking_dialog import BookingDialog
from config import DefaultConfig
from flight_booking_recognizer import FlightBookingRecognizer
import unittest

import aiounittest
from botbuilder.core import (
    TurnContext, 
    ConversationState, 
    MemoryStorage, 
)
from botbuilder.dialogs.prompts import (
    PromptOptions, 
)
from botbuilder.schema import Activity, ActivityTypes
from botbuilder.dialogs import DialogSet, DialogTurnStatus
from botbuilder.core.adapters import TestAdapter
from botbuilder.dialogs.prompts import TextPrompt

# test  luis configuration
class TestLuisConf(unittest.TestCase):
    def test_intent(self):
        rec = FlightBookingRecognizer(configuration=DefaultConfig)
        assert rec.is_configured
#test is_ambiguous
class TestBookingDialog(unittest.TestCase):
    def test_is_ambiguous(self):
        bd =  BookingDialog()
        ret = bd.is_ambiguous("Hello")
        assert ret
        ret = bd.is_ambiguous("2020-08-17")
        assert not ret
        
#test textprompt
class TextpromptTest(aiounittest.AsyncTestCase):
    async def test_extprompt(self):

        async def exec_test(turn_context:TurnContext):
            dialog_context = await dialogs.create_context(turn_context)
            results = await dialog_context.continue_dialog()
            if (results.status == DialogTurnStatus.Empty):
                options = PromptOptions(
                    prompt = Activity(
                        type = ActivityTypes.message, 
                        text = "What can I help you with today?"
                        )
                    )
                await dialog_context.prompt("textprompt", options)

            await conv_state.save_changes(turn_context)

        adapter = TestAdapter(exec_test)
        conv_state = ConversationState(MemoryStorage())
        dialogs_state = conv_state.create_property("dialog-state")
        dialogs = DialogSet(dialogs_state)
        dialogs.add(TextPrompt("textprompt"))
        await adapter.test('Hello', "What can I help you with today?")


       
        
                

