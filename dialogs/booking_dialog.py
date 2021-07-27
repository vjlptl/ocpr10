# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

from datatypes_date_time.timex import Timex

from botbuilder.dialogs import WaterfallDialog, WaterfallStepContext, DialogTurnResult, waterfall_dialog
from botbuilder.dialogs.prompts import ConfirmPrompt, TextPrompt, PromptOptions, text_prompt
from botbuilder.core import MessageFactory
from botbuilder.schema import InputHints
from .cancel_and_help_dialog import CancelAndHelpDialog
from .departure_date_resolver_dialog import DepartureDateResolverDialog
from .return_date_resolver_dialog import ReturnDateResolverDialog


class BookingDialog(CancelAndHelpDialog):
    def __init__(self, dialog_id: str = None):
        super(BookingDialog, self).__init__(dialog_id or BookingDialog.__name__)

        waterfall_dialog = WaterfallDialog(
            WaterfallDialog.__name__,
            [
                    self.destination_step,
                    self.origin_step,
                    self.departure_date_step,
                    self.return_date_step,
                    self.budget_step,
                    self.confirm_step,
                    self.final_step,
                ],
        )
        self.add_dialog(TextPrompt(TextPrompt.__name__))
        self.add_dialog(ConfirmPrompt(ConfirmPrompt.__name__))
        self.add_dialog(DepartureDateResolverDialog(DepartureDateResolverDialog.__name__))
        self.add_dialog(ReturnDateResolverDialog(ReturnDateResolverDialog.__name__))
        self.add_dialog(waterfall_dialog)

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
            booking_details.departure_date or check_date_dialog.check_date_past(
                booking_details.departure_date)
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
    
    async def budget_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        """
        If an origin city has not been provided, prompt for one.
        :param step_context:
        :return DialogTurnResult:
        """
        booking_details = step_context.options

        # Capture the response to the previous step's prompt
        booking_details.return_date = step_context.result
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
            f"Please confirm, I have you traveling for a { booking_details.budget } budget : "
            f"From { booking_details.origin } to { booking_details.destination } on { booking_details.departure_date }. "
            f"From { booking_details.destination } to { booking_details.origin } on { booking_details.return_date}. "
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
        if step_context.result:
            return await step_context.end_dialog(booking_details)

        return await step_context.end_dialog()

    def is_ambiguous(self, timex: str) -> bool:
        timex_property = Timex(timex)
        return "definite" not in timex_property.types
