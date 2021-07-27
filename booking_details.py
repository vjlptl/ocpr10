# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.


class BookingDetails:
    def __init__(
        self,
        destination: str = None,
        origin: str = None,
        departure_date: str = None,
        return_date: str = None,
        budget: str = None
    ):
        self.destination = destination
        self.origin = origin
        self.departure_date = departure_date
        self.return_date = return_date
        self.budget = budget

