# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

from typing import List


class BookingDetails:
    def __init__(
        self,
        destination: str = None,
        origin: str = None,
        on_date: str = None,
        end_date: str = None,
        budget: str = None,
        unsupported_airports: List[str] = None,
    ):
        self.destination = destination
        self.origin = origin
        self.on_date = on_date
        self.end_date = end_date
        self.budget = budget
        self.unsupported_airports = unsupported_airports or []
