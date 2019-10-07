# Copyright (C) 2019 Magenta ApS, http://magenta.dk.
# Contact: info@magenta.dk.
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.


import csv

from django.core.management.base import BaseCommand

from core.models import ActivityDetails, Section, Account


class Command(BaseCommand):
    help = """
    This script imports Accounts from the CBUR "Klassifikationer"
    spreadsheet.

    Currently this requires the sheet "Aktiviteter" be saved
    as "activities.csv" in the current directory.

    NOTE: This requires the Section models AND
    the ActivityDetails to have been populated first.
    """

    def add_arguments(self, parser):
        parser.add_arguments(
            "-p",
            "--path",
            type=str,
            help="set the path to read the activities.csv file",
        )

    def handle(self, *args, **options):
        with open("activities.csv") as csvfile:
            reader = csv.reader(csvfile)
            rows = [row for row in reader]
            for row in rows[1:]:
                activity_id = row[0]
                main_activity_section = row[4]
                supplementary_activity_section = row[5]
                paragraph = (
                    supplementary_activity_section
                    if supplementary_activity_section
                    else main_activity_section
                )
                main_activity = row[8]
                account_number = row[13]
                if (
                    not activity_id
                    or not (
                        main_activity_section or supplementary_activity_section
                    )
                    or not account_number
                    or not paragraph
                ):
                    continue

                # if no main activity column is present
                # we know the row is a main activity.
                if not main_activity:
                    try:
                        main_activity_details = ActivityDetails.objects.get(
                            activity_id=activity_id
                        )
                        supplementary_activity_details = None
                    except ActivityDetails.DoesNotExist:
                        print(
                            f"ActivityDetails with id: {activity_id}"
                            f" does not exist"
                        )
                        continue
                else:
                    try:
                        main_activity_details = ActivityDetails.objects.get(
                            activity_id=main_activity
                        )
                        supplementary_activity_details = ActivityDetails.objects.get(
                            activity_id=activity_id
                        )
                    except ActivityDetails.DoesNotExist:
                        print(
                            f"ActivityDetails with id: {activity_id}"
                            f" or {main_activity} does not exist"
                        )
                        continue
                section = Section.objects.get(paragraph=paragraph)

                Account.objects.update_or_create(
                    main_activity=main_activity_details,
                    supplementary_activity=supplementary_activity_details,
                    section=section,
                    defaults={"number": account_number},
                )
