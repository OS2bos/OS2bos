from decimal import Decimal
from datetime import date
from unittest import mock

from django.utils import timezone
from django.test import TestCase
from django.contrib.auth import get_user_model
from parameterized import parameterized

from core.tests.testing_mixins import (
    PaymentScheduleMixin,
    ActivityMixin,
    AppropriationMixin,
)
from core.models import (
    Appropriation,
    Municipality,
    SchoolDistrict,
    Section,
    ActivityDetails,
    Account,
    ApprovalLevel,
    Team,
    Payment,
    PaymentSchedule,
    Activity,
    ServiceProvider,
    Activity,
)


class AppropriationTestCase(TestCase, PaymentScheduleMixin, ActivityMixin):
    def test_appropriation_str(self):
        section = Section(paragraph="ABZ-52-54", kle_number="11.22.33")
        appropriation = Appropriation(sbsys_id="XXX-YYY-ZZZ", section=section)

        self.assertEqual(
            str(appropriation), "XXX-YYY-ZZZ - ABZ-52-54 - 11.22.33"
        )

    def test_total_granted_this_year(self):
        # generate a start and end span of 10 days
        now = timezone.now()
        start_date = date(year=now.year, month=1, day=1)
        end_date = date(year=now.year, month=1, day=10)
        # create main activity with GRANTED.
        payment_schedule = self.create_payment_schedule(
            payment_frequency=PaymentSchedule.DAILY,
            payment_type=PaymentSchedule.RUNNING_PAYMENT,
        )
        activity = self.create_activity(
            start_date=start_date,
            end_date=end_date,
            activity_type=Activity.MAIN_ACTIVITY,
            status=Activity.STATUS_GRANTED,
            payment_plan=payment_schedule,
        )

        payment_schedule = self.create_payment_schedule(
            payment_frequency=PaymentSchedule.DAILY,
            payment_type=PaymentSchedule.RUNNING_PAYMENT,
        )

        self.create_activity(
            start_date=start_date,
            end_date=end_date,
            status=Activity.STATUS_GRANTED,
            activity_type=Activity.SUPPL_ACTIVITY,
            payment_plan=payment_schedule,
        )
        self.assertEqual(
            activity.appropriation.total_granted_this_year, Decimal("10000")
        )

    def test_total_expected_this_year(self):
        # generate a start and end span of 10 days
        now = timezone.now()
        start_date = date(year=now.year, month=1, day=1)
        end_date = date(year=now.year, month=1, day=10)
        # create main activity with GRANTED.
        payment_schedule = self.create_payment_schedule(
            payment_frequency=PaymentSchedule.DAILY,
            payment_type=PaymentSchedule.RUNNING_PAYMENT,
        )
        activity = self.create_activity(
            start_date=start_date,
            end_date=end_date,
            activity_type=Activity.MAIN_ACTIVITY,
            status=Activity.STATUS_GRANTED,
            payment_plan=payment_schedule,
        )

        payment_schedule = self.create_payment_schedule(
            payment_frequency=PaymentSchedule.DAILY,
            payment_type=PaymentSchedule.RUNNING_PAYMENT,
        )
        # create a GRANTED supplementary activity.
        supplementary_activity = self.create_activity(
            start_date=start_date,
            end_date=end_date,
            status=Activity.STATUS_GRANTED,
            activity_type=Activity.SUPPL_ACTIVITY,
            payment_plan=payment_schedule,
        )

        payment_schedule = self.create_payment_schedule(
            payment_frequency=PaymentSchedule.DAILY,
            payment_type=PaymentSchedule.RUNNING_PAYMENT,
            payment_amount=Decimal("700"),
        )
        # create an EXPECTED supplementary activity overruling the GRANTED.
        self.create_activity(
            start_date=start_date,
            end_date=end_date,
            status=Activity.STATUS_EXPECTED,
            activity_type=Activity.SUPPL_ACTIVITY,
            payment_plan=payment_schedule,
            modifies=supplementary_activity,
        )

        self.assertEqual(
            activity.appropriation.total_expected_this_year, Decimal("12000")
        )

    def test_main_activity(self):
        activity = self.create_activity()
        appropriation = activity.appropriation
        activity.activity_type = Activity.MAIN_ACTIVITY
        activity.save()
        self.assertEqual(activity, appropriation.main_activity)

    def test_supplementary_activities(self):
        activity = self.create_activity()
        appropriation = activity.appropriation
        activity.activity_type = Activity.SUPPL_ACTIVITY
        activity.save()
        self.assertEqual(
            activity, next(appropriation.supplementary_activities)
        )


class MunicipalityTestCase(TestCase):
    def test_municipality_str(self):
        municipality = Municipality.objects.create(name="København")

        self.assertEqual(str(municipality), "København")


class SchoolDistrictTestCase(TestCase):
    def test_school_district_str(self):
        school_district = SchoolDistrict.objects.create(name="Skovlunde Skole")

        self.assertEqual(str(school_district), "Skovlunde Skole")


class TeamTestCase(TestCase):
    def test_team_str(self):
        user = get_user_model().objects.create(username="Anders And")
        team = Team.objects.create(name="C-BUR", leader=user)

        self.assertEqual(str(team), "C-BUR")


class SectionTestCase(TestCase):
    def test_section_str(self):
        sections = Section.objects.create(
            paragraph="ABL-105-2",
            kle_number="27.45.04",
            text="Lov om almene boliger",
            allowed_for_steps=[],
            law_text_name="Lov om almene boliger",
        )

        self.assertEqual(str(sections), "ABL-105-2 - 27.45.04")


class ActivityDetailsTestCase(TestCase):
    def test_activitydetails_str(self):
        details = ActivityDetails.objects.create(
            name="Betaling til andre kommuner/region for specialtandpleje",
            activity_id="010001",
            max_tolerance_in_dkk=5000,
            max_tolerance_in_percent=10,
        )

        self.assertEqual(
            str(details),
            "010001 - Betaling til andre kommuner/region for specialtandpleje",
        )


class ActivityTestCase(TestCase, ActivityMixin, PaymentScheduleMixin):
    def test_activity_synchronize_payments_on_save(self):
        payment_schedule = self.create_payment_schedule()
        activity = self.create_activity(payment_plan=payment_schedule)

        self.assertEqual(activity.payment_plan.payments.count(), 10)

        activity.end_date = date(year=2019, month=1, day=13)
        activity.save()
        self.assertEqual(activity.payment_plan.payments.count(), 13)

    def test_activity_total_cost_with_service_provider(self):
        service_provider = ServiceProvider.objects.create(
            name="Test leverandør", vat_factor=Decimal("90")
        )
        payment_schedule = self.create_payment_schedule()
        activity = self.create_activity(
            payment_plan=payment_schedule, service_provider=service_provider
        )

        self.assertEqual(activity.total_cost, Decimal("4500.0"))

    def test_activity_no_payment_plan_on_save(self):
        activity = self.create_activity()
        self.assertIsNone(activity.payment_plan)

    def test_activity_total_cost(self):
        payment_schedule = self.create_payment_schedule()
        # 10 days, daily payments of 500.
        activity = self.create_activity(payment_plan=payment_schedule)

        self.assertEqual(activity.total_cost, Decimal("5000"))

    def test_activity_total_cost_spanning_years(self):
        payment_schedule = self.create_payment_schedule()
        start_date = date(year=2019, month=12, day=1)
        end_date = date(year=2020, month=1, day=1)
        # 32 days, daily payments of 500.
        activity = self.create_activity(
            start_date=start_date,
            end_date=end_date,
            payment_plan=payment_schedule,
        )

        self.assertEqual(activity.total_cost, Decimal("16000"))

    def test_activity_total_cost_this_year(self):
        now = timezone.now()
        payment_schedule = self.create_payment_schedule()
        start_date = date(year=now.year, month=12, day=1)
        end_date = date(year=now.year, month=12, day=15)
        # 15 days, daily payments of 500.
        activity = self.create_activity(
            start_date=start_date,
            end_date=end_date,
            payment_plan=payment_schedule,
        )
        self.assertEqual(activity.total_cost_this_year, Decimal("7500"))

    def test_activity_total_cost_this_year_spanning_years(self):
        now = timezone.now()
        payment_schedule = self.create_payment_schedule()
        start_date = date(year=now.year, month=12, day=1)
        end_date = date(year=now.year + 1, month=1, day=1)
        # 31 days, daily payments of 500.
        activity = self.create_activity(
            start_date=start_date,
            end_date=end_date,
            payment_plan=payment_schedule,
        )
        self.assertEqual(activity.total_cost_this_year, Decimal("15500"))

    def test_activity_monthly_payment_plan(self):
        start_date = date(year=2019, month=12, day=1)
        end_date = date(year=2020, month=1, day=1)
        payment_schedule = self.create_payment_schedule()
        # 32 days, daily payments of 500.
        activity = self.create_activity(
            start_date=start_date,
            end_date=end_date,
            payment_plan=payment_schedule,
        )
        expected = [
            {"date_month": "2019-12", "amount": Decimal("15500")},
            {"date_month": "2020-01", "amount": Decimal("500")},
        ]
        self.assertEqual(
            [entry for entry in activity.monthly_payment_plan], expected
        )


class AccountTestCase(TestCase):
    def test_account_str(self):
        sections = Section.objects.create(
            paragraph="ABL-105-2",
            kle_number="27.45.04",
            text="Lov om almene boliger",
            allowed_for_steps=[],
            law_text_name="Lov om almene boliger",
        )
        activity_details = ActivityDetails.objects.create(
            name="Betaling til andre kommuner/region for specialtandpleje",
            activity_id="010001",
            max_tolerance_in_dkk=5000,
            max_tolerance_in_percent=10,
        )
        account = Account.objects.create(
            number="123456", section=sections, activity=activity_details
        )

        self.assertEqual(
            str(account), f"123456 - {activity_details} - {sections}"
        )


class ApprovalLevelTestCase(TestCase):
    def test_approvallevel_str(self):
        approval_level = ApprovalLevel.objects.create(name="egenkompetence")

        self.assertEqual(str(approval_level), f"{approval_level.name}")


class PaymentTestCase(TestCase, PaymentScheduleMixin):
    def test_payment_str(self):
        payment_schedule = self.create_payment_schedule()
        payment = Payment.objects.create(
            payment_schedule=payment_schedule,
            date=date(year=2019, month=1, day=1),
            amount=Decimal("500.0"),
        )
        self.assertEqual(str(payment), "2019-01-01 - 500.0")


class PaymentScheduleTestCase(TestCase, PaymentScheduleMixin, ActivityMixin):
    @parameterized.expand(
        [
            (
                PaymentSchedule.DAILY,
                date(year=2019, month=1, day=1),
                date(year=2019, month=1, day=10),
                10,
            ),
            (
                PaymentSchedule.DAILY,
                date(year=2019, month=1, day=1),
                date(year=2019, month=1, day=1),
                1,
            ),
            (
                PaymentSchedule.MONTHLY,
                date(year=2019, month=1, day=1),
                date(year=2019, month=10, day=1),
                10,
            ),
            (
                PaymentSchedule.MONTHLY,
                date(year=2019, month=1, day=1),
                date(year=2019, month=1, day=1),
                1,
            ),
            (
                PaymentSchedule.WEEKLY,
                date(year=2019, month=1, day=1),
                date(year=2019, month=2, day=1),
                5,
            ),
            (
                PaymentSchedule.WEEKLY,
                date(year=2019, month=1, day=1),
                date(year=2019, month=1, day=1),
                1,
            ),
        ]
    )
    def test_create_rrule_frequency(self, frequency, start, end, expected):
        payment_schedule = self.create_payment_schedule(
            payment_frequency=frequency
        )
        rrule = payment_schedule.create_rrule(start=start, end=end)

        self.assertEqual(len(list(rrule)), expected)

    def test_create_rrule_one_time_1_day(self):
        payment_schedule = self.create_payment_schedule(
            payment_type=PaymentSchedule.ONE_TIME_PAYMENT,
            payment_frequency=PaymentSchedule.DAILY,
        )

        rrule = payment_schedule.create_rrule(
            start=date(year=2019, month=1, day=1),
            end=date(year=2019, month=2, day=1),
        )

        self.assertEqual(len(list(rrule)), 1)
        self.assertEqual(
            list(rrule)[0].date(), date(year=2019, month=1, day=1)
        )

    def test_create_rrule_incorrect_frequency(self):
        payment_schedule = self.create_payment_schedule(
            payment_type=PaymentSchedule.RUNNING_PAYMENT,
            payment_frequency="incorrect frequency",
        )

        with self.assertRaises(ValueError):
            payment_schedule.create_rrule(
                start=date(year=2019, month=1, day=1),
                end=date(year=2019, month=2, day=1),
            )

    @parameterized.expand(
        [
            (
                PaymentSchedule.ONE_TIME_PAYMENT,
                PaymentSchedule.DAILY,
                Decimal("100"),
                0,
                Decimal("100"),
                Decimal("100"),
            ),
            (
                PaymentSchedule.RUNNING_PAYMENT,
                PaymentSchedule.DAILY,
                Decimal("100"),
                0,
                Decimal("100"),
                Decimal("100"),
            ),
            (
                PaymentSchedule.PER_HOUR_PAYMENT,
                PaymentSchedule.DAILY,
                Decimal("100"),
                5,
                Decimal("100"),
                Decimal("500"),
            ),
            (
                PaymentSchedule.PER_KM_PAYMENT,
                PaymentSchedule.DAILY,
                Decimal("100"),
                10,
                Decimal("100"),
                Decimal("1000"),
            ),
        ]
    )
    def test_calculate_per_payment_amount(
        self,
        payment_type,
        payment_frequency,
        payment_amount,
        payment_units,
        vat_factor,
        expected,
    ):
        payment_schedule = self.create_payment_schedule(
            payment_type=payment_type,
            payment_frequency=payment_frequency,
            payment_amount=payment_amount,
            payment_units=payment_units,
        )

        amount = payment_schedule.calculate_per_payment_amount(
            vat_factor=vat_factor
        )

        self.assertEqual(amount, expected)

    def test_calculate_per_payment_amount_invalid_payment_type(self):
        payment_schedule = self.create_payment_schedule(
            payment_type="ugyldig betalingstype",
            payment_frequency=PaymentSchedule.DAILY,
        )

        with self.assertRaises(ValueError):
            payment_schedule.calculate_per_payment_amount(
                vat_factor=Decimal("100")
            )

    def test_generate_payments(self):
        payment_schedule = self.create_payment_schedule(
            payment_type=PaymentSchedule.RUNNING_PAYMENT,
            payment_frequency=PaymentSchedule.DAILY,
            payment_amount=Decimal("100"),
        )
        start_date = date(year=2019, month=1, day=1)
        end_date = date(year=2019, month=1, day=10)

        payment_schedule.generate_payments(start_date, end_date)

        self.assertEqual(payment_schedule.payments.count(), 10)

    def test_generate_payments_no_end_date(self):
        payment_schedule = self.create_payment_schedule(
            payment_type=PaymentSchedule.RUNNING_PAYMENT,
            payment_frequency=PaymentSchedule.MONTHLY,
            payment_amount=Decimal("100"),
        )
        start_date = date(year=2019, month=1, day=1)
        # Start in January and no end should generate 24 monthly payments
        # (till end of next year)
        payment_schedule.generate_payments(start_date, None)

        self.assertIsNotNone(payment_schedule.payments)
        self.assertEqual(payment_schedule.payments.count(), 24)

    def test_synchronize_payments_no_end_needs_further_payments(self):
        # Test the case where end is unbounded and payments are generated till
        # end of next year then middle of next year is reached
        # and new payments should be generated once again
        payment_schedule = self.create_payment_schedule(
            payment_type=PaymentSchedule.RUNNING_PAYMENT,
            payment_frequency=PaymentSchedule.MONTHLY,
            payment_amount=Decimal("100"),
        )
        start_date = date(year=2019, month=1, day=1)
        end_date = None
        # Initial call to generate payments will generate 24 payments.
        payment_schedule.generate_payments(start_date, end_date)
        self.assertEqual(len(payment_schedule.payments.all()), 24)

        # Now we are in the future and we need to generate new payments
        # because end is still unbounded
        with mock.patch("core.models.date") as date_mock:
            date_mock.today.return_value = date(year=2020, month=7, day=1)
            date_mock.max.month = 12
            date_mock.max.day = 31
            payment_schedule.synchronize_payments(start_date, end_date)
        self.assertEqual(payment_schedule.payments.count(), 36)

    def test_synchronize_payments_new_end_date_in_past(self):
        # Test the case where we generate payments for an unbounded end
        # and next the end is set so we need to delete some generated payments.
        payment_schedule = self.create_payment_schedule(
            payment_type=PaymentSchedule.RUNNING_PAYMENT,
            payment_frequency=PaymentSchedule.MONTHLY,
            payment_amount=Decimal("100"),
        )
        start_date = date(year=2019, month=1, day=1)
        end_date = None

        payment_schedule.generate_payments(start_date, end_date)

        self.assertEqual(len(payment_schedule.payments.all()), 24)

        new_end_date = date(year=2019, month=6, day=1)
        payment_schedule.synchronize_payments(start_date, new_end_date)

        self.assertEqual(payment_schedule.payments.count(), 6)

    def test_synchronize_payments_new_end_date_in_future(self):
        payment_schedule = self.create_payment_schedule(
            payment_type=PaymentSchedule.RUNNING_PAYMENT,
            payment_frequency=PaymentSchedule.MONTHLY,
            payment_amount=Decimal("100"),
        )
        start_date = date(year=2019, month=1, day=1)
        end_date = None

        # Generate payments till 2020-12-1
        payment_schedule.generate_payments(start_date, end_date)

        self.assertEqual(len(payment_schedule.payments.all()), 24)

        new_end_date = date(year=2021, month=2, day=1)
        payment_schedule.synchronize_payments(start_date, new_end_date)

        self.assertEqual(payment_schedule.payments.count(), 26)

    def test_synchronize_payments_same_end_date_no_changes(self):
        payment_schedule = self.create_payment_schedule(
            payment_type=PaymentSchedule.RUNNING_PAYMENT,
            payment_frequency=PaymentSchedule.MONTHLY,
            payment_amount=Decimal("100"),
        )
        start_date = date(year=2019, month=1, day=1)
        end_date = date(year=2019, month=9, day=1)

        payment_schedule.generate_payments(start_date, end_date)

        self.assertEqual(len(payment_schedule.payments.all()), 9)

        payment_schedule.synchronize_payments(start_date, end_date)

        self.assertEqual(payment_schedule.payments.count(), 9)

    def test_synchronize_payments_no_payments(self):
        payment_schedule = self.create_payment_schedule(
            payment_type=PaymentSchedule.RUNNING_PAYMENT,
            payment_frequency=PaymentSchedule.MONTHLY,
            payment_amount=Decimal("100"),
        )
        start_date = date(year=2019, month=1, day=1)
        end_date = None
        payment_schedule.synchronize_payments(start_date, end_date)

        self.assertEqual(payment_schedule.payments.count(), 0)

    def test_synchronize_payments_end_date_in_future_for_weeks(self):
        payment_schedule = self.create_payment_schedule(
            payment_type=PaymentSchedule.RUNNING_PAYMENT,
            payment_frequency=PaymentSchedule.WEEKLY,
            payment_amount=Decimal("100"),
        )
        start_date = date(year=2019, month=1, day=1)
        end_date = date(year=2019, month=3, day=1)
        payment_schedule.generate_payments(start_date, end_date)

        self.assertEqual(payment_schedule.payments.count(), 9)

        end_date = date(year=2019, month=4, day=1)
        payment_schedule.synchronize_payments(start_date, end_date)

        self.assertEqual(payment_schedule.payments.count(), 13)

    def test_synchronize_payments_invalid_frequency(self):
        payment_schedule = self.create_payment_schedule(
            payment_type=PaymentSchedule.RUNNING_PAYMENT,
            payment_frequency=PaymentSchedule.WEEKLY,
            payment_amount=Decimal("100"),
        )
        start_date = date(year=2019, month=1, day=1)
        end_date = date(year=2019, month=3, day=1)
        payment_schedule.generate_payments(start_date, end_date)

        self.assertEqual(payment_schedule.payments.count(), 9)

        end_date = date(year=2019, month=4, day=1)
        payment_schedule.payment_frequency = "invalid_frequency"
        payment_schedule.save()
        with self.assertRaises(ValueError):
            payment_schedule.synchronize_payments(start_date, end_date)
