from decimal import Decimal
from datetime import date

from django.contrib.auth import get_user_model

from core.models import (
    Case,
    Municipality,
    SchoolDistrict,
    Team,
    Activity,
    PaymentSchedule,
    ActivityDetails,
    Appropriation,
    Payment,
)


class CaseMixin:
    @staticmethod
    def create_case():
        case_worker = get_user_model().objects.create(
            username="Orla Frøsnapper"
        )
        team = Team.objects.create(name="FCK", leader=case_worker)
        municipality = Municipality.objects.create(name="København")
        district = SchoolDistrict.objects.create(name="Baltorpskolen")
        case = Case.objects.create(
            sbsys_id="13212",
            cpr_number="0205891234",
            name="Jens Jensen",
            case_worker=case_worker,
            team=team,
            scaling_step=1,
            effort_step="STEP_ONE",
            acting_municipality=municipality,
            district=district,
            paying_municipality=municipality,
            residence_municipality=municipality,
        )
        return case

    @staticmethod
    def create_case_as_json():
        case_worker = get_user_model().objects.create(username="Andersine And")
        team = Team.objects.create(name="Brøndby", leader=case_worker)
        municipality_id = Municipality.objects.create(name="Andeby").id
        district = SchoolDistrict.objects.create(
            name="Kornelius Blisand-skolen"
        )
        json = {
            "sbsys_id": "xxx-yyyx",
            "cpr_number": "111213-0014",
            "name": "Mak Mouse",
            "target_group": "FAMILY_DEPT",
            "refugee_integration": True,
            "cross_department_measure": True,
            "case_worker": case_worker.id,
            "team": team.id,
            "scaling_step": 1,
            "effort_step": "STEP_ONE",
            "district": district.id,
            "paying_municipality": municipality_id,
            "acting_municipality": municipality_id,
            "residence_municipality": municipality_id,
        }

        return json


class PaymentScheduleMixin:
    @staticmethod
    def create_payment_schedule(
        payment_frequency=PaymentSchedule.DAILY,
        payment_type=PaymentSchedule.RUNNING_PAYMENT,
        payment_amount=Decimal("500.0"),
        payment_units=0,
    ):
        payment_schedule = PaymentSchedule.objects.create(
            payment_amount=payment_amount,
            payment_frequency=payment_frequency,
            payment_type=payment_type,
            payment_units=payment_units,
        )
        return payment_schedule


class ActivityMixin:
    @staticmethod
    def create_activity(
        start_date=date(year=2019, month=1, day=1),
        end_date=date(year=2019, month=1, day=10),
        status=Activity.STATUS_DRAFT,
        **kwargs
    ):
        activity_details = ActivityDetails.objects.create(
            max_tolerance_in_percent=10, max_tolerance_in_dkk=1000
        )

        activity = Activity.objects.create(
            start_date=start_date,
            end_date=end_date,
            details=activity_details,
            status=status,
            **kwargs
        )
        return activity


class AppropriationMixin:
    @staticmethod
    def create_appropriation(sbsys_id="test"):
        # create the related case
        case_worker = get_user_model().objects.create(
            username="Orla Frøsnapper"
        )
        team = Team.objects.create(name="FCK", leader=case_worker)
        municipality = Municipality.objects.create(name="København")
        district = SchoolDistrict.objects.create(name="Baltorpskolen")
        case = Case.objects.create(
            sbsys_id="13212",
            cpr_number="0205891234",
            name="Jens Jensen",
            case_worker=case_worker,
            team=team,
            scaling_step=1,
            effort_step="STEP_ONE",
            acting_municipality=municipality,
            district=district,
            paying_municipality=municipality,
            residence_municipality=municipality,
        )

        appropriation = Appropriation.objects.create(
            sbsys_id=sbsys_id, case=case
        )
        return appropriation


class PaymentMixin:
    @staticmethod
    def create_payment(date=date.today(), amount=Decimal("500")):
        payment_schedule = PaymentSchedule.objects.create(
            payment_amount=amount,
            payment_frequency=PaymentSchedule.DAILY,
            payment_type=PaymentSchedule.ONE_TIME_PAYMENT,
            payment_units=0,
        )
        payment = Payment.objects.create(
            recipient_id="Test",
            recipient_name="Test",
            date=date,
            amount=amount,
            payment_schedule=payment_schedule,
        )
        return payment
