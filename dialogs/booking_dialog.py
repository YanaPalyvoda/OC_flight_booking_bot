# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.


from botbuilder.core.bot_telemetry_client import TelemetryDataPointType
from botbuilder.dialogs import WaterfallDialog, WaterfallStepContext, DialogTurnResult
from botbuilder.dialogs.prompts import ConfirmPrompt, TextPrompt, PromptOptions
from botbuilder.core import MessageFactory, BotTelemetryClient, NullTelemetryClient
from .cancel_and_help_dialog import CancelAndHelpDialog
from .date_resolver_dialog import DateResolverDialog
from .end_date_resolver_dialog import EndDateResolverDialog
from botbuilder.applicationinsights import ApplicationInsightsTelemetryClient
from botbuilder.integration.applicationinsights.aiohttp import (AiohttpTelemetryProcessor,bot_telemetry_middleware)
from config import DefaultConfig
from datatypes_date_time.timex import Timex

class BookingDialog(CancelAndHelpDialog):
    def __init__(self, dialog_id: str = None,telemetry_client: BotTelemetryClient = NullTelemetryClient(),):
        super(BookingDialog, self).__init__(dialog_id or BookingDialog.__name__, telemetry_client)
        self.telemetry_client = telemetry_client
        text_prompt = TextPrompt(TextPrompt.__name__)
        text_prompt.telemetry_client = telemetry_client

        wf_dialog = WaterfallDialog(
                WaterfallDialog.__name__,
                [
                    self.destination_step,
                    self.origin_step,
                    self.on_date_step,
                    self.end_date_step,
                    self.budget_step,
                    self.confirm_step,
                    self.final_step,
                ],
            )
        wf_dialog.telemetry_client = telemetry_client
        self.add_dialog(text_prompt)
        self.add_dialog(ConfirmPrompt(ConfirmPrompt.__name__))
        self.add_dialog(DateResolverDialog(DateResolverDialog.__name__, self.telemetry_client))
        self.add_dialog(EndDateResolverDialog(EndDateResolverDialog.__name__, self.telemetry_client))
        self.add_dialog(wf_dialog)

        self.initial_dialog_id = WaterfallDialog.__name__

    async def destination_step(
        self, step_context: WaterfallStepContext
    ) -> DialogTurnResult:
        """
        If a destination city has not been provided, prompt for one.
        :param step_context:
        :return DialogTurnResult:
        """
        booking_details = step_context.options

        if booking_details.destination is None:
            return await step_context.prompt(
                TextPrompt.__name__,
                PromptOptions(
                    prompt=MessageFactory.text("To what city would you like to travel?")
                ),
            )  # pylint: disable=line-too-long,bad-continuation

        return await step_context.next(booking_details.destination)

    async def origin_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        """Prompt for origin city."""
        booking_details = step_context.options

        # Capture the response to the previous step's prompt
        booking_details.destination = step_context.result
        if booking_details.origin is None:
            return await step_context.prompt(
                TextPrompt.__name__,
                PromptOptions(
                    prompt=MessageFactory.text("From what city will you be travelling?")
                ),
            )  # pylint: disable=line-too-long,bad-continuation

        return await step_context.next(booking_details.origin)

    async def on_date_step(
        self, step_context: WaterfallStepContext
    ) -> DialogTurnResult:
        """
        If a travel date has not been provided, prompt for one.
        This will use the DATE_RESOLVER_DIALOG.
        :param step_context:
        :return DialogTurnResult:
        """
        booking_details = step_context.options

        # Capture the results of the previous step
        booking_details.origin = step_context.result
        if not booking_details.on_date or self.is_ambiguous(
            booking_details.on_date
        ):
            return await step_context.begin_dialog(
                DateResolverDialog.__name__, booking_details.on_date
            )  # pylint: disable=line-too-long

        return await step_context.next(booking_details.on_date)


    async def end_date_step(
        self, step_context: WaterfallStepContext
    ) -> DialogTurnResult:
        """
        If a return date has not been provided, prompt for one.
        This will use the END_DATE_RESOLVER_DIALOG.
        :param step_context:
        :return DialogTurnResult:
        """
        booking_details = step_context.options

        # Capture the results of the previous step
        booking_details.on_date = step_context.result
        if  not booking_details.end_date  or self.is_ambiguous(
            booking_details.end_date
        ):
            return await step_context.begin_dialog(
                EndDateResolverDialog.__name__, booking_details.end_date
            )  # pylint: disable=line-too-long

        return await step_context.next(booking_details.end_date)



    async def budget_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        """
        If budget has not been provided, prompt for one.
        :param step_context:
        :return DialogTurnResult:
        """
        booking_details = step_context.options

        # Capture the response to the previous step's prompt
        booking_details.end_date = step_context.result
        if booking_details.budget is None:
            return await step_context.prompt(
                TextPrompt.__name__,
                PromptOptions(
                    prompt=MessageFactory.text("What is your travel budget?")
                ),
            )  # pylint: disable=line-too-long,bad-continuation

        return await step_context.next(booking_details.budget)

    async def confirm_step(
        self, step_context: WaterfallStepContext 
        ) -> DialogTurnResult:
        """Confirm the information the user has provided."""
        booking_details = step_context.options
        # Capture the results of the previous step
        booking_details.budget = step_context.result
        msg = (
            f"Please confirm, I have you traveling to: { booking_details.destination } from: "
            f"{ booking_details.origin } departure on: { booking_details.on_date} return on: { booking_details.end_date} with a maximum budget of {booking_details.budget}."
        )
        # Offer a YES/NO prompt.
        return await step_context.prompt(
            ConfirmPrompt.__name__, PromptOptions(prompt=MessageFactory.text(msg))
        )


    async def final_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        """
        Complete the interaction and end the dialog.
        :param step_context:
        :return DialogTurnResult:
        """
        #INSTRUMENTATION_KEY = DefaultConfig.APPINSIGHTS_INSTRUMENTATION_KEY
        #TELEMETRY_CLIENT = ApplicationInsightsTelemetryClient(INSTRUMENTATION_KEY, telemetry_processor=AiohttpTelemetryProcessor(), client_queue_size=10)
        #self.telemetry_client = telemetry_client
        booking_details = step_context.options
        details_insights = {}
        details_insights['destination'] = booking_details.destination
        details_insights['origin'] = booking_details.origin
        details_insights['departure_date'] = booking_details.on_date
        details_insights['return_date'] = booking_details.end_date
        details_insights['budget'] = booking_details.budget
        #print(details_insights)
        if step_context.result:
            #booking_details = step_context.options
            #booking_details.budget = step_context.result
            self.telemetry_client.track_trace("OK",details_insights)   
            self.telemetry_client.flush()

            return await step_context.end_dialog(booking_details)
        else:    
              #record details to send to azure insights
            
            
            self.telemetry_client.track_trace("KO",details_insights,"CRITICAL")   
            self.telemetry_client.flush()
        
        return await step_context.end_dialog()   


    def is_ambiguous(self, timex: str) -> bool:
        timex_property = Timex(timex)
        return "definite" not in timex_property.types
