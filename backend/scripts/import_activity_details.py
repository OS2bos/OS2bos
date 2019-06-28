"""
This script imports ActivityDetails from the CBUR "Klassifikationer"
spreadsheet.

Currently this requires the sheet "Aktiviteter v2" be saved
as "aktiviteter.csv" in the current directory.

NOTE: This requires the Section models to have been populated first.
"""
from core.models import ActivityDetails, Sections
import csv

with open("aktiviteter.csv") as csvfile:
    reader = csv.reader(csvfile)
    models_list = []
    rows = [row for row in reader]
    for row in rows[1:]:
        activity_id = row[0]
        if not activity_id:
            continue
        name = row[1]
        tolerance_percent = row[2][:-1]
        tolerance_dkk = row[3]
        main_activity_on = row[4]
        suppl_activity_on = row[5]
        object, created = ActivityDetails.objects.update_or_create(
            name=name,
            activity_id=activity_id,
            max_tolerance_in_percent=tolerance_percent,
            max_tolerance_in_dkk=tolerance_dkk,
        )
        main_activity_for = Sections.objects.filter(paragraph=main_activity_on)
        if main_activity_for.exists():
            main_activity_for = main_activity_for.first()
            object.main_activity_for.add(main_activity_for)

        supplementary_activity_for = Sections.objects.filter(
            paragraph=suppl_activity_on
        )
        if supplementary_activity_for.exists():
            supplementary_activity_for = supplementary_activity_for.first()
            object.supplementary_activity_for.add(supplementary_activity_for)
