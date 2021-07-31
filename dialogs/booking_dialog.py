# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

from datatypes_date_time.timex import Timex

from botbuilder.dialogs import WaterfallDialog, WaterfallStepContext, DialogTurnResult
from botbuilder.dialogs.prompts import ConfirmPrompt, TextPrompt, PromptOptions
from botbuilder.core import MessageFactory, BotTelemetryClient, NullTelemetryClient
from botbuilder.schema import InputHints
from .cancel_and_help_dialog import CancelAndHelpDialog
#from .date_resolver_dialog import DateResolverDialog
from .departure_date_resolver_dialog import DepartureDateResolverDialog
from .return_date_resolver_dialog import ReturnDateResolverDialog
from applicationinsights import TelemetryClient

class BookingDialog(CancelAndHelpDialog):
    def __init__(
            self,
            dialog_id: str = None,
            telemetry_client: BotTelemetryClient = NullTelemetryClient(),
    ):
        super(BookingDialog, self).__init__(
            dialog_id or BookingDialog.__name__, telemetry_client
        )
        self.telemetry_client = telemetry_client
        text_prompt = TextPrompt(TextPrompt.__name__)
        text_prompt.telemetry_client = telemetry_client

        self.add_dialog(text_prompt)
        # self.add_dialog(ConfirmPrompt(ConfirmPrompt.__name__))
        self.add_dialog(DepartureDateResolverDialog(DepartureDateResolverDialog.__name__, self.telemetry_client))
        self.add_dialog(ReturnDateResolverDialog(ReturnDateResolverDialog.__name__, self.telemetry_client))
        self.add_dialog(
            WaterfallDialog(
                WaterfallDialog.__name__,
                [
                    self.destination_step,
                    self.origin_step,
                    # self.travel_date_step,
                    self.departure_date_step,
                    self.return_date_step,
                    self.budget_step,
                    # self.confirm_step,
                    self.final_step,

                ],
            )
        )

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
            message_text = "Where would you like to travel to?"
            prompt_message = MessageFactory.text(
                message_text, message_text, InputHints.expecting_input
            )
            return await step_context.prompt(
                TextPrompt.__name__, PromptOptions(prompt=prompt_message)
            )
        return await step_context.next(booking_details.destination)

    async def origin_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        """
        If an origin city has not been provided, prompt for one.
        :param step_context:
        :return DialogTurnResult:
        """
        booking_details = step_context.options

        # Capture the response to the previous step's prompt
        booking_details.destination = step_context.result
        if booking_details.origin is None:
            message_text = "From what city will you be travelling?"
            prompt_message = MessageFactory.text(
                message_text, message_text, InputHints.expecting_input
            )
            return await step_context.prompt(
                TextPrompt.__name__, PromptOptions(prompt=prompt_message)
            )
        return await step_context.next(booking_details.origin)

    async def departure_date_step(
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
        if not booking_details.departure_date or self.is_ambiguous(
            booking_details.departure_date
        ):
            return await step_context.begin_dialog(
                DepartureDateResolverDialog.__name__, booking_details.departure_date
            )
        return await step_context.next(booking_details.departure_date)

    async def return_date_step(
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
        booking_details.departure_date = step_context.result
        if not booking_details.return_date or self.is_ambiguous(
            booking_details.return_date
        ):
            return await step_context.begin_dialog(
                ReturnDateResolverDialog.__name__, booking_details.return_date
            )
        return await step_context.next(booking_details.return_date)

    async def budget_step(
            self, step_context: WaterfallStepContext
    ) -> DialogTurnResult:
        """
        If budget has not been provided, prompt for one.
        :param step_context:
        :return DialogTurnResult:
        """
        booking_details = step_context.options

        # Capture the response to the previous step's prompt
        booking_details.return_date = step_context.result
        #print("booking_dialog - 111")
        #print(booking_details.budget)
        if booking_details.budget is None:
            message_text = "What is your budget?"
            prompt_message = MessageFactory.text(
                message_text, message_text, InputHints.expecting_input
            )
            return await step_context.prompt(
                TextPrompt.__name__, PromptOptions(prompt=prompt_message)
            )
        return await step_context.next(booking_details.budget)

    async def confirm_step(
        self, step_context: WaterfallStepContext
    ) -> DialogTurnResult:
        """
        Confirm the information the user has provided.
        :param step_context:
        :return DialogTurnResult:
        """
        booking_details = step_context.options

        # Capture the results of the previous step
        booking_details.budget = step_context.result
        message_text = (
            f"Please confirm, I have you traveling on a { booking_details.budget } budget"
            f" from: {booking_details.departure_date} to: {booking_details.return_date} "
            f" to: { booking_details.destination } from: "
            f"{ booking_details.origin } ."
        )
        prompt_message = MessageFactory.text(
            message_text, message_text, InputHints.expecting_input
        )

        # Offer a YES/NO prompt.
        return await step_context.prompt(
            ConfirmPrompt.__name__, PromptOptions(prompt=prompt_message)
        )

    async def final_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        """
        Complete the interaction and end the dialog.
        :param step_context:
        :return DialogTurnResult:
        """
        booking_details = step_context.options
        properties = {}
        properties["destination"] = booking_details.destination
        properties["origin"] = booking_details.origin
        properties["departure_date"] = booking_details.departure_date
        properties["return_date"] = booking_details.return_date
        properties["budget"] = booking_details.budget

        #TEST
        if step_context.result is None:
            #print("FALSE")
            #from applicationinsights import TelemetryClient
            tc = TelemetryClient("ddd0b4c5-5455-4889-9310-098ae3050143")
            #tc.track_trace('FALSE ', {'1': '2'})
            tc.track_trace("Bad answer received", properties, "WARNING")
            tc.flush()
        else:
            #print("TRUE")
            #from applicationinsights import TelemetryClient
            tc = TelemetryClient("ddd0b4c5-5455-4889-9310-098ae3050143")
            #tc.track_trace('TRUE ', {'3': '4'})
            tc.track_trace("Good answer received", properties, "INFO")
            tc.flush()


        if step_context.result is None:
            self.telemetry_client.track_trace("Bad answer received", properties, "WARNING")
            self.telemetry_client.flush()
        else:
            self.telemetry_client.track_trace("Good answer received", properties, "INFO")
            self.telemetry_client.flush()

            booking_details = step_context.options
            booking_details.budget = step_context.result

            return await step_context.end_dialog(booking_details)

        return await step_context.end_dialog()

    def is_ambiguous(self, timex: str) -> bool:
        timex_property = Timex(timex)
        return "definite" not in timex_property.types
