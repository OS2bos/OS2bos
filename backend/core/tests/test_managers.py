# Copyright (C) 2019 Magenta ApS, http://magenta.dk.
# Contact: info@magenta.dk.
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.


from datetime import date, timedelta
from decimal import Decimal

from freezegun import freeze_time

from django.test import TestCase
from django.utils import timezone

from core.tests.testing_utils import (
    create_payment,
    BasicTestMixin,
    create_case,
    create_appropriation,
    create_payment_schedule,
    create_activity,
    create_municipality,
    create_section,
    create_approval_level,
)
from core.models import (
    Payment,
    PaymentSchedule,
    Case,
    SectionInfo,
    MAIN_ACTIVITY,
    SUPPL_ACTIVITY,
    STATUS_GRANTED,
    STATUS_EXPECTED,
    STATUS_DRAFT,
    CASH,
    Activity,
    Appropriation,
)


class PaymentQuerySetTestCase(TestCase, BasicTestMixin):
    @classmethod
    def setUpTestData(cls):
        cls.basic_setup()

    def test_in_year_true(self):
        payment_schedule = create_payment_schedule()
        payment = create_payment(payment_schedule)
        self.assertIn(payment, Payment.objects.in_year())

    def test_in_this_year_false(self):
        now = timezone.now()
        payment_schedule = create_payment_schedule()
        payment = create_payment(
            payment_schedule, date=date(year=now.year - 1, month=1, day=1)
        )

        self.assertNotIn(payment, Payment.objects.in_year())

    def test_in_this_year_true_paid_date(self):
        case = create_case(self.case_worker, self.municipality, self.district)
        appropriation = create_appropriation(case=case)
        activity = create_activity(
            case=case,
            appropriation=appropriation,
            activity_type=MAIN_ACTIVITY,
            status=STATUS_GRANTED,
        )
        payment_schedule = create_payment_schedule(activity=activity)

        now = timezone.now()
        payment = create_payment(
            payment_schedule,
            date=date(year=now.year - 1, month=12, day=31),
            paid_date=date(year=now.year, month=1, day=1),
            paid_amount=Decimal("500.0"),
            paid=True,
        )

        self.assertIn(payment, Payment.objects.in_year())

    def test_paid_date_or_date_gte(self):
        case = create_case(self.case_worker, self.municipality, self.district)
        appropriation = create_appropriation(case=case)
        activity = create_activity(
            case=case,
            appropriation=appropriation,
            activity_type=MAIN_ACTIVITY,
            status=STATUS_GRANTED,
        )
        payment_schedule = create_payment_schedule(activity=activity)

        now = timezone.now()

        # should be included
        paid_date_gte_payment = create_payment(
            payment_schedule,
            date=date(year=now.year - 1, month=12, day=29),
            paid_date=date(year=now.year, month=1, day=1),
            paid_amount=Decimal("500.0"),
            paid=True,
        )

        # should be included
        date_gte_payment = create_payment(
            payment_schedule, date=date(year=now.year, month=1, day=1)
        )

        # should not be included
        paid_date_lt_payment = create_payment(
            payment_schedule,
            date=date(year=now.year - 1, month=12, day=30),
            paid_date=date(year=now.year - 1, month=12, day=31),
            paid_amount=Decimal("500.0"),
            paid=True,
        )

        # should not be included
        date_lt_payment = create_payment(
            payment_schedule, date=date(year=now.year - 1, month=12, day=31)
        )

        self.assertIn(
            paid_date_gte_payment,
            Payment.objects.paid_date_or_date_gte(
                date(year=now.year, month=1, day=1)
            ),
        )

        self.assertIn(
            date_gte_payment,
            Payment.objects.paid_date_or_date_gte(
                date(year=now.year, month=1, day=1)
            ),
        )
        self.assertNotIn(
            paid_date_lt_payment,
            Payment.objects.paid_date_or_date_gte(
                date(year=now.year, month=1, day=1)
            ),
        )

        self.assertNotIn(
            date_lt_payment,
            Payment.objects.paid_date_or_date_gte(
                date(year=now.year, month=1, day=1)
            ),
        )

    def test_paid_date_or_date_lte(self):
        case = create_case(self.case_worker, self.municipality, self.district)
        appropriation = create_appropriation(case=case)
        activity = create_activity(
            case=case,
            appropriation=appropriation,
            activity_type=MAIN_ACTIVITY,
            status=STATUS_GRANTED,
        )
        payment_schedule = create_payment_schedule(activity=activity)

        now = timezone.now()

        # should be included
        paid_date_lte_payment = create_payment(
            payment_schedule,
            date=date(year=now.year - 1, month=12, day=29),
            paid_date=date(year=now.year, month=1, day=1),
            paid_amount=Decimal("500.0"),
            paid=True,
        )

        # should be included
        date_lte_payment = create_payment(
            payment_schedule, date=date(year=now.year, month=1, day=1)
        )

        # should not be included
        paid_date_gt_payment = create_payment(
            payment_schedule,
            date=date(year=now.year - 1, month=12, day=30),
            paid_date=date(year=now.year, month=1, day=2),
            paid_amount=Decimal("500.0"),
            paid=True,
        )

        # should not be included
        date_gt_payment = create_payment(
            payment_schedule, date=date(year=now.year, month=1, day=2)
        )

        self.assertIn(
            paid_date_lte_payment,
            Payment.objects.paid_date_or_date_lte(
                date(year=now.year, month=1, day=1)
            ),
        )

        self.assertIn(
            date_lte_payment,
            Payment.objects.paid_date_or_date_lte(
                date(year=now.year, month=1, day=1)
            ),
        )
        self.assertNotIn(
            paid_date_gt_payment,
            Payment.objects.paid_date_or_date_lte(
                date(year=now.year, month=1, day=1)
            ),
        )

        self.assertNotIn(
            date_gt_payment,
            Payment.objects.paid_date_or_date_lte(
                date(year=now.year, month=1, day=1)
            ),
        )

    def test_in_this_year_false_paid_date(self):
        case = create_case(self.case_worker, self.municipality, self.district)
        appropriation = create_appropriation(case=case)
        activity = create_activity(
            case=case,
            appropriation=appropriation,
            activity_type=MAIN_ACTIVITY,
            status=STATUS_GRANTED,
        )
        payment_schedule = create_payment_schedule(activity=activity)

        now = timezone.now()
        payment = create_payment(
            payment_schedule,
            date=date(year=now.year, month=1, day=1),
            paid_date=date(year=now.year - 1, month=1, day=1),
            paid_amount=Decimal("500.0"),
            paid=True,
        )

        self.assertNotIn(payment, Payment.objects.in_year())

    def test_amount_sum(self):
        now = timezone.now()

        payment_schedule = create_payment_schedule()
        create_payment(
            payment_schedule,
            amount=Decimal("1000"),
            date=date(year=now.year, month=1, day=1),
        )
        create_payment(
            payment_schedule,
            amount=Decimal("100"),
            date=date(year=now.year, month=1, day=2),
        )
        create_payment(
            payment_schedule,
            amount=Decimal("50"),
            date=date(year=now.year, month=1, day=3),
        )

        self.assertEqual(Payment.objects.amount_sum(), Decimal("1150"))

    def test_amount_sum_paid_amount_overrides(self):
        case = create_case(self.case_worker, self.municipality, self.district)
        appropriation = create_appropriation(case=case)
        # Default 10 days of 500DKK.
        activity = create_activity(
            case=case,
            appropriation=appropriation,
            activity_type=MAIN_ACTIVITY,
            status=STATUS_GRANTED,
        )
        create_payment_schedule(activity=activity)

        # mark last payment paid with 1000.
        last_payment = Payment.objects.last()
        last_payment.paid = True
        last_payment.paid_date = date(year=2019, month=1, day=10)
        last_payment.paid_amount = Decimal(1000)
        last_payment.save()

        self.assertEqual(Payment.objects.amount_sum(), Decimal("5500"))

    def test_strict_amount_sum_paid_amount_does_not_override(self):
        case = create_case(self.case_worker, self.municipality, self.district)
        appropriation = create_appropriation(case=case)
        # Default 10 days of 500DKK.
        activity = create_activity(
            case=case,
            appropriation=appropriation,
            activity_type=MAIN_ACTIVITY,
            status=STATUS_GRANTED,
        )
        create_payment_schedule(activity=activity)

        # mark last payment paid with 700.
        last_payment = Payment.objects.last()
        last_payment.paid = True
        last_payment.paid_date = date(year=2019, month=1, day=10)
        last_payment.paid_amount = Decimal(700)
        last_payment.save()

        self.assertEqual(Payment.objects.strict_amount_sum(), Decimal("5000"))

    def test_group_by_monthly_amounts(self):
        payment_schedule = create_payment_schedule()
        create_payment(
            payment_schedule,
            amount=Decimal("1000"),
            date=date(year=2019, month=1, day=1),
        )
        create_payment(
            payment_schedule,
            amount=Decimal("100"),
            date=date(year=2019, month=2, day=1),
        )
        create_payment(
            payment_schedule,
            amount=Decimal("50"),
            date=date(year=2019, month=3, day=1),
        )

        expected = [
            {"date_month": "2019-01", "amount": Decimal("1000")},
            {"date_month": "2019-02", "amount": Decimal("100")},
            {"date_month": "2019-03", "amount": Decimal("50")},
        ]
        self.assertEqual(
            [entry for entry in Payment.objects.group_by_monthly_amounts()],
            expected,
        )

    def test_group_by_monthly_amounts_paid(self):
        case = create_case(self.case_worker, self.municipality, self.district)
        appropriation = create_appropriation(case=case)
        # 4 payments of 500DKK.
        activity = create_activity(
            case=case,
            appropriation=appropriation,
            activity_type=MAIN_ACTIVITY,
            status=STATUS_GRANTED,
            start_date=date(year=2019, month=2, day=27),
            end_date=date(year=2019, month=3, day=2),
        )
        create_payment_schedule(activity=activity)
        # Mark one March payment paid with 700.
        last_payment = activity.payment_plan.payments.get(
            date=date(year=2019, month=3, day=2)
        )
        last_payment.paid = True
        last_payment.paid_date = date(year=2019, month=3, day=1)
        last_payment.paid_amount = Decimal(700)
        last_payment.save()

        # Expected are two payments in February of 500
        # and two payments in March of 500 and 700.
        expected = [
            {"date_month": "2019-02", "amount": Decimal("1000")},
            {"date_month": "2019-03", "amount": Decimal("1200")},
        ]
        self.assertCountEqual(
            [entry for entry in Payment.objects.group_by_monthly_amounts()],
            expected,
        )


class CaseQuerySetTestCase(TestCase, BasicTestMixin):
    @classmethod
    def setUpTestData(cls):
        cls.basic_setup()

    def test_expired_one_expired_one_ongoing(self):
        now_date = timezone.now().date()
        case = create_case(self.case_worker, self.municipality, self.district)
        appropriation = create_appropriation(case=case)

        # create an expired main activity
        activity = create_activity(
            case=case,
            appropriation=appropriation,
            start_date=now_date - timedelta(days=3),
            end_date=now_date - timedelta(days=2),
            activity_type=MAIN_ACTIVITY,
            status=STATUS_GRANTED,
        )
        create_payment_schedule(
            payment_frequency=PaymentSchedule.DAILY,
            payment_type=PaymentSchedule.RUNNING_PAYMENT,
            activity=activity,
        )

        # create an ongoing main activity
        ongoing_activity = create_activity(
            case=case,
            appropriation=appropriation,
            start_date=now_date - timedelta(days=1),
            end_date=now_date + timedelta(days=1),
            activity_type=MAIN_ACTIVITY,
            status=STATUS_GRANTED,
            modifies=activity,
        )
        create_payment_schedule(
            payment_frequency=PaymentSchedule.DAILY,
            payment_type=PaymentSchedule.RUNNING_PAYMENT,
            activity=ongoing_activity,
        )
        # create a second appropriation
        appropriation = create_appropriation(case=case, sbsys_id="6521")

        # create an expired main activity
        activity = create_activity(
            case=case,
            appropriation=appropriation,
            start_date=now_date - timedelta(days=3),
            end_date=now_date - timedelta(days=2),
            activity_type=MAIN_ACTIVITY,
            status=STATUS_GRANTED,
        )
        create_payment_schedule(
            payment_frequency=PaymentSchedule.DAILY,
            payment_type=PaymentSchedule.RUNNING_PAYMENT,
            activity=activity,
        )

        # create an ongoing main activity
        ongoing_activity = create_activity(
            case=case,
            appropriation=appropriation,
            start_date=now_date - timedelta(days=1),
            end_date=now_date + timedelta(days=1),
            activity_type=MAIN_ACTIVITY,
            status=STATUS_GRANTED,
            modifies=activity,
        )
        create_payment_schedule(
            payment_frequency=PaymentSchedule.DAILY,
            payment_type=PaymentSchedule.RUNNING_PAYMENT,
            activity=ongoing_activity,
        )
        expired_cases = Case.objects.all().expired()
        ongoing_cases = Case.objects.all().ongoing()
        self.assertEqual(expired_cases.count(), 0)
        self.assertEqual(ongoing_cases.count(), 1)

    def test_expired_all_expired(self):
        now_date = timezone.now().date()
        case = create_case(self.case_worker, self.municipality, self.district)
        appropriation = create_appropriation(case=case)

        # create an expired main activity
        activity = create_activity(
            case=case,
            appropriation=appropriation,
            start_date=now_date - timedelta(days=4),
            end_date=now_date - timedelta(days=3),
            activity_type=MAIN_ACTIVITY,
            status=STATUS_GRANTED,
        )
        create_payment_schedule(
            payment_frequency=PaymentSchedule.DAILY,
            payment_type=PaymentSchedule.RUNNING_PAYMENT,
            activity=activity,
        )

        # create an expired main activity
        expired_activity = create_activity(
            case=case,
            appropriation=appropriation,
            start_date=now_date - timedelta(days=2),
            end_date=now_date - timedelta(days=1),
            activity_type=MAIN_ACTIVITY,
            status=STATUS_GRANTED,
            modifies=activity,
        )
        create_payment_schedule(
            payment_frequency=PaymentSchedule.DAILY,
            payment_type=PaymentSchedule.RUNNING_PAYMENT,
            activity=expired_activity,
        )
        # create a second appropriation
        appropriation = create_appropriation(case=case, sbsys_id="6521")

        # create an expired main activity
        activity = create_activity(
            case=case,
            appropriation=appropriation,
            start_date=now_date - timedelta(days=10),
            end_date=now_date - timedelta(days=9),
            activity_type=MAIN_ACTIVITY,
            status=STATUS_GRANTED,
        )
        create_payment_schedule(
            payment_frequency=PaymentSchedule.DAILY,
            payment_type=PaymentSchedule.RUNNING_PAYMENT,
            activity=activity,
        )

        # create an expired main activity
        expired_activity = create_activity(
            case=case,
            appropriation=appropriation,
            start_date=now_date - timedelta(days=8),
            end_date=now_date - timedelta(days=7),
            activity_type=MAIN_ACTIVITY,
            status=STATUS_GRANTED,
            modifies=activity,
        )
        create_payment_schedule(
            payment_frequency=PaymentSchedule.DAILY,
            payment_type=PaymentSchedule.RUNNING_PAYMENT,
            activity=expired_activity,
        )

        expired_cases = Case.objects.all().expired()
        ongoing_cases = Case.objects.all().ongoing()
        self.assertEqual(expired_cases.count(), 1)
        self.assertEqual(ongoing_cases.count(), 0)

    @freeze_time("2022-01-01")
    def test_filter_changed_cases_for_dst_payload_from_date(self):
        case = create_case(self.case_worker, self.municipality, self.district)
        alternate_municipality = create_municipality("Hillerød")

        with freeze_time("2022-02-01"):
            case.acting_municipality = alternate_municipality
            case.save()

        # only from_date is given so change should be included.
        cases = Case.objects.filter_changed_cases_for_dst_payload(
            from_date=date(2022, 1, 1)
        )

        self.assertTrue(case in cases)

    @freeze_time("2022-01-01")
    def test_filter_changed_cases_for_dst_payload_from_date_to_date(self):
        case = create_case(self.case_worker, self.municipality, self.district)
        alternate_municipality = create_municipality("Hillerød")

        with freeze_time("2022-02-01"):
            case.acting_municipality = alternate_municipality
            case.save()

        # to_date is before change so case should not be included.
        cases = Case.objects.filter_changed_cases_for_dst_payload(
            from_date=date(2022, 1, 1), to_date=date(2022, 1, 31)
        )

        self.assertFalse(case in cases)

    @freeze_time("2022-02-01")
    def test_filter_changed_cases_for_dst_payload_no_to_date(self):
        case = create_case(self.case_worker, self.municipality, self.district)

        # from_date and to_date is before case creation
        # so case should not be included.
        cases = Case.objects.filter_changed_cases_for_dst_payload(
            from_date=date(2022, 1, 1), to_date=date(2022, 1, 31)
        )

        self.assertFalse(case in cases)


class ActivityQuerySetTestCase(TestCase, BasicTestMixin):
    @classmethod
    def setUpTestData(cls):
        cls.basic_setup()

    def test_expired(self):
        today = timezone.now().date()
        case = create_case(self.case_worker, self.municipality, self.district)
        appropriation = create_appropriation(case=case)

        expired_activity = create_activity(
            case=case,
            appropriation=appropriation,
            start_date=today - timedelta(days=4),
            end_date=today - timedelta(days=3),
            activity_type=SUPPL_ACTIVITY,
            status=STATUS_GRANTED,
        )

        ongoing_activity = create_activity(
            case=case,
            appropriation=appropriation,
            start_date=today - timedelta(days=4),
            end_date=today,
            activity_type=MAIN_ACTIVITY,
            status=STATUS_GRANTED,
        )

        self.assertIn(expired_activity, Activity.objects.all().expired())
        self.assertNotIn(ongoing_activity, Activity.objects.all().expired())

    def test_ongoing(self):
        today = timezone.now().date()
        case = create_case(self.case_worker, self.municipality, self.district)
        appropriation = create_appropriation(case=case)

        # create an expired main activity
        expired_activity = create_activity(
            case=case,
            appropriation=appropriation,
            start_date=today - timedelta(days=4),
            end_date=today - timedelta(days=3),
            activity_type=SUPPL_ACTIVITY,
            status=STATUS_GRANTED,
        )

        ongoing_activity = create_activity(
            case=case,
            appropriation=appropriation,
            start_date=today - timedelta(days=4),
            end_date=today,
            activity_type=MAIN_ACTIVITY,
            status=STATUS_GRANTED,
        )

        self.assertNotIn(expired_activity, Activity.objects.all().ongoing())
        self.assertIn(ongoing_activity, Activity.objects.all().ongoing())

    def test_ongoing_no_end_date(self):
        today = timezone.now().date()
        case = create_case(self.case_worker, self.municipality, self.district)
        appropriation = create_appropriation(case=case)

        ongoing_activity = create_activity(
            case=case,
            appropriation=appropriation,
            start_date=today - timedelta(days=4),
            end_date=None,
            activity_type=MAIN_ACTIVITY,
            status=STATUS_GRANTED,
        )

        self.assertIn(ongoing_activity, Activity.objects.all().ongoing())


class AppropriationQuerySetTestCase(TestCase, BasicTestMixin):
    @classmethod
    def setUpTestData(cls):
        cls.basic_setup()

    def test_ongoing(self):
        today = timezone.now().date()
        case = create_case(self.case_worker, self.municipality, self.district)
        appropriation = create_appropriation(case=case)

        self.assertIn(appropriation, Appropriation.objects.ongoing())

        # create an expired supplementary activity
        # but an ongoing main activity.
        create_activity(
            case=case,
            appropriation=appropriation,
            start_date=today - timedelta(days=4),
            end_date=today - timedelta(days=3),
            activity_type=SUPPL_ACTIVITY,
            status=STATUS_GRANTED,
        )

        create_activity(
            case=case,
            appropriation=appropriation,
            start_date=today - timedelta(days=4),
            end_date=today,
            activity_type=MAIN_ACTIVITY,
            status=STATUS_GRANTED,
        )

        self.assertIn(appropriation, Appropriation.objects.ongoing())

    def test_expired(self):
        today = timezone.now().date()
        case = create_case(self.case_worker, self.municipality, self.district)
        appropriation = create_appropriation(case=case)

        self.assertNotIn(appropriation, Appropriation.objects.expired())

        # create an expired supplementary activity
        # and an expired main activity.
        create_activity(
            case=case,
            appropriation=appropriation,
            start_date=today - timedelta(days=4),
            end_date=today - timedelta(days=3),
            activity_type=SUPPL_ACTIVITY,
            status=STATUS_GRANTED,
        )

        create_activity(
            case=case,
            appropriation=appropriation,
            start_date=today - timedelta(days=4),
            end_date=today - timedelta(days=1),
            activity_type=MAIN_ACTIVITY,
            status=STATUS_GRANTED,
        )

        self.assertIn(appropriation, Appropriation.objects.expired())

    def test_appropriations_for_dst_payload_initial(self):
        now = timezone.now().date()
        start_date = now
        case = create_case(self.case_worker, self.municipality, self.district)
        section = create_section(dst_code="123")
        appropriation = create_appropriation(
            sbsys_id="XXX-YYY", case=case, section=section
        )
        granted_activity = create_activity(
            case,
            appropriation,
            start_date=start_date,
            appropriation_date=start_date,
            end_date=None,
            activity_type=MAIN_ACTIVITY,
            status=STATUS_GRANTED,
        )
        create_payment_schedule(
            payment_frequency=PaymentSchedule.DAILY,
            payment_type=PaymentSchedule.RUNNING_PAYMENT,
            recipient_type=PaymentSchedule.PERSON,
            payment_method=CASH,
            payment_amount=Decimal(666),
            activity=granted_activity,
        )
        section.main_activities.add(granted_activity.details)

        SectionInfo.objects.get(
            activity_details=granted_activity.details, section=section
        )
        # start_date is within date span.
        dst_appropriations = (
            Appropriation.objects.appropriations_for_dst_payload(
                from_date=None, to_date=start_date
            )
        )

        self.assertTrue(appropriation in dst_appropriations)

    def test_appropriations_for_dst_payload_initial_exclude_dates(self):
        now = timezone.now().date()
        start_date = now
        case = create_case(self.case_worker, self.municipality, self.district)
        section = create_section(dst_code="123")
        appropriation = create_appropriation(
            sbsys_id="XXX-YYY", case=case, section=section
        )
        granted_activity = create_activity(
            case,
            appropriation,
            start_date=start_date,
            appropriation_date=start_date,
            end_date=None,
            activity_type=MAIN_ACTIVITY,
            status=STATUS_GRANTED,
        )
        create_payment_schedule(
            payment_frequency=PaymentSchedule.DAILY,
            payment_type=PaymentSchedule.RUNNING_PAYMENT,
            recipient_type=PaymentSchedule.PERSON,
            payment_method=CASH,
            payment_amount=Decimal(666),
            activity=granted_activity,
        )
        section.main_activities.add(granted_activity.details)

        SectionInfo.objects.get(
            activity_details=granted_activity.details, section=section
        )
        # appropriation_date and start_date is not within date span.
        dst_appropriations = (
            Appropriation.objects.appropriations_for_dst_payload(
                from_date=None, to_date=start_date - timedelta(days=1)
            )
        )

        self.assertFalse(appropriation in dst_appropriations)

    def test_appropriations_for_dst_payload_initial_exclude_start_date(self):
        now = timezone.now().date()
        start_date = now
        case = create_case(self.case_worker, self.municipality, self.district)
        section = create_section(dst_code="123")
        appropriation = create_appropriation(
            sbsys_id="XXX-YYY", case=case, section=section
        )
        granted_activity = create_activity(
            case,
            appropriation,
            start_date=start_date,
            appropriation_date=start_date - timedelta(days=1),
            end_date=None,
            activity_type=MAIN_ACTIVITY,
            status=STATUS_GRANTED,
        )
        create_payment_schedule(
            payment_frequency=PaymentSchedule.DAILY,
            payment_type=PaymentSchedule.RUNNING_PAYMENT,
            recipient_type=PaymentSchedule.PERSON,
            payment_method=CASH,
            payment_amount=Decimal(666),
            activity=granted_activity,
        )
        section.main_activities.add(granted_activity.details)

        SectionInfo.objects.get(
            activity_details=granted_activity.details, section=section
        )
        # start_date is in the future of from_date->to_date.
        dst_appropriations = (
            Appropriation.objects.appropriations_for_dst_payload(
                from_date=None, to_date=start_date - timedelta(days=1)
            )
        )

        self.assertFalse(appropriation in dst_appropriations)

    def test_appropriations_for_dst_payload_initial_exclude_payment_date(self):
        now = timezone.now().date()
        start_date = now
        case = create_case(self.case_worker, self.municipality, self.district)
        section = create_section(dst_code="123")
        appropriation = create_appropriation(
            sbsys_id="XXX-YYY", case=case, section=section
        )
        granted_activity = create_activity(
            case,
            appropriation,
            start_date=None,
            appropriation_date=start_date - timedelta(days=1),
            end_date=None,
            activity_type=MAIN_ACTIVITY,
            status=STATUS_GRANTED,
        )
        create_payment_schedule(
            payment_frequency=None,
            payment_type=PaymentSchedule.ONE_TIME_PAYMENT,
            recipient_type=PaymentSchedule.PERSON,
            payment_method=CASH,
            payment_amount=Decimal(666),
            payment_date=start_date,
            activity=granted_activity,
        )
        section.main_activities.add(granted_activity.details)

        SectionInfo.objects.get(
            activity_details=granted_activity.details, section=section
        )

        granted_suppl_activity = create_activity(
            case,
            appropriation,
            start_date=start_date - timedelta(days=1),
            appropriation_date=start_date - timedelta(days=1),
            end_date=None,
            activity_type=SUPPL_ACTIVITY,
            status=STATUS_GRANTED,
        )
        create_payment_schedule(
            payment_frequency=PaymentSchedule.DAILY,
            payment_type=PaymentSchedule.RUNNING_PAYMENT,
            recipient_type=PaymentSchedule.PERSON,
            payment_method=CASH,
            payment_amount=Decimal(666),
            activity=granted_suppl_activity,
        )

        # payment_date is in the future of from_date->to_date.
        dst_appropriations = (
            Appropriation.objects.appropriations_for_dst_payload(
                from_date=None, to_date=start_date - timedelta(days=1)
            )
        )

        self.assertFalse(appropriation in dst_appropriations)

    def test_appropriations_for_dst_payload_initial_exclude_appr_date(self):
        now = timezone.now().date()
        start_date = now
        case = create_case(self.case_worker, self.municipality, self.district)
        section = create_section(dst_code="123")
        appropriation = create_appropriation(
            sbsys_id="XXX-YYY", case=case, section=section
        )
        granted_activity = create_activity(
            case,
            appropriation,
            start_date=start_date + timedelta(days=1),
            appropriation_date=start_date - timedelta(days=1),
            end_date=None,
            activity_type=MAIN_ACTIVITY,
            status=STATUS_GRANTED,
        )
        create_payment_schedule(
            payment_frequency=PaymentSchedule.DAILY,
            payment_type=PaymentSchedule.RUNNING_PAYMENT,
            recipient_type=PaymentSchedule.PERSON,
            payment_method=CASH,
            payment_amount=Decimal(666),
            activity=granted_activity,
        )
        section.main_activities.add(granted_activity.details)

        SectionInfo.objects.get(
            activity_details=granted_activity.details, section=section
        )
        # appropriation_date is outside from_date->to_date.
        dst_appropriations = (
            Appropriation.objects.appropriations_for_dst_payload(
                from_date=None, to_date=start_date
            )
        )

        self.assertFalse(appropriation in dst_appropriations)

    @freeze_time("2022-01-01")
    def test_appropriations_for_dst_payload_delta_include_future_start(self):
        now = timezone.now().date()
        case = create_case(self.case_worker, self.municipality, self.district)
        section = create_section(dst_code="123")
        appropriation = create_appropriation(
            sbsys_id="XXX-YYY", case=case, section=section
        )
        # Create an activity appropriated now but with a future start_date.
        granted_activity = create_activity(
            case,
            appropriation,
            start_date=date(2022, 2, 1),
            end_date=None,
            appropriation_date=now,
            activity_type=MAIN_ACTIVITY,
            status=STATUS_GRANTED,
        )
        create_payment_schedule(
            payment_frequency=PaymentSchedule.DAILY,
            payment_type=PaymentSchedule.RUNNING_PAYMENT,
            recipient_type=PaymentSchedule.PERSON,
            payment_method=CASH,
            payment_amount=Decimal(666),
            activity=granted_activity,
        )
        section.main_activities.add(granted_activity.details)

        SectionInfo.objects.get(
            activity_details=granted_activity.details, section=section
        )
        # appropriation with earlier appropriated activities but
        # with a start_date in the period should be included and marked new.
        dst_appropriations = (
            Appropriation.objects.appropriations_for_dst_payload(
                from_date=date(2022, 2, 1), to_date=date(2022, 3, 1)
            )
        )

        self.assertEqual(dst_appropriations.count(), 1)
        self.assertTrue(appropriation in dst_appropriations)
        self.assertEqual(dst_appropriations.first().dst_report_type, "Ny")

    @freeze_time("2022-01-01")
    def test_appropriations_for_dst_payload_delta_include_future_onetime(self):
        now = timezone.now().date()
        case = create_case(self.case_worker, self.municipality, self.district)
        section = create_section(dst_code="123")
        appropriation = create_appropriation(
            sbsys_id="XXX-YYY", case=case, section=section
        )
        # Create an activity appropriated now but with a future start_date.
        granted_activity = create_activity(
            case,
            appropriation,
            start_date=None,
            end_date=None,
            appropriation_date=now,
            activity_type=MAIN_ACTIVITY,
            status=STATUS_GRANTED,
        )
        create_payment_schedule(
            payment_frequency=None,
            payment_type=PaymentSchedule.ONE_TIME_PAYMENT,
            recipient_type=PaymentSchedule.PERSON,
            payment_method=CASH,
            payment_date=date(2022, 2, 1),
            payment_amount=Decimal(666),
            activity=granted_activity,
        )
        section.main_activities.add(granted_activity.details)

        SectionInfo.objects.get(
            activity_details=granted_activity.details, section=section
        )
        # appropriation with earlier appropriated activities but
        # with a payment_date in the period should be included and marked new.
        dst_appropriations = (
            Appropriation.objects.appropriations_for_dst_payload(
                from_date=date(2022, 2, 1), to_date=date(2022, 3, 1)
            )
        )

        self.assertEqual(dst_appropriations.count(), 1)
        self.assertTrue(appropriation in dst_appropriations)
        self.assertEqual(dst_appropriations.first().dst_report_type, "Ny")

    @freeze_time("2022-01-01")
    def test_appropriations_for_dst_payload_delta_include_future_changed(self):
        now = timezone.now().date()
        case = create_case(self.case_worker, self.municipality, self.district)
        section = create_section(dst_code="123")
        appropriation = create_appropriation(
            sbsys_id="XXX-YYY", case=case, section=section
        )
        # Create an activity appropriated now but with a future start_date.
        activity = create_activity(
            case,
            appropriation,
            start_date=date(2022, 2, 1),
            end_date=date(2022, 2, 5),
            appropriation_date=now,
            activity_type=MAIN_ACTIVITY,
            status=STATUS_DRAFT,
        )
        create_payment_schedule(
            payment_frequency=PaymentSchedule.DAILY,
            payment_type=PaymentSchedule.RUNNING_PAYMENT,
            recipient_type=PaymentSchedule.PERSON,
            payment_method=CASH,
            payment_amount=Decimal(666),
            activity=activity,
        )
        section.main_activities.add(activity.details)

        SectionInfo.objects.get(
            activity_details=activity.details, section=section
        )
        approval_level = create_approval_level()

        activities = Activity.objects.filter(pk=activity.pk)
        appropriation.grant(
            activities, approval_level.id, "note", self.case_worker
        )

        # appropriation with earlier appropriated activities but
        # with a start_date in the period should be included and marked new.
        dst_appropriations = (
            Appropriation.objects.appropriations_for_dst_payload(
                from_date=date(2022, 2, 1), to_date=date(2022, 3, 1)
            )
        )
        self.assertEqual(dst_appropriations.count(), 1)
        self.assertTrue(appropriation in dst_appropriations)
        self.assertEqual(dst_appropriations.first().dst_report_type, "Ny")

        # Revive the activity by creating a modified.
        # Next we create a modification to the main activity
        # at 2022-01-03 and grant it.
        with freeze_time("2022-03-01"):
            modifies_activity = create_activity(
                case,
                appropriation,
                start_date=date(2022, 4, 1),
                end_date=date(2022, 4, 5),
                activity_type=MAIN_ACTIVITY,
                status=STATUS_EXPECTED,
                modifies=activity,
            )
            create_payment_schedule(
                payment_frequency=PaymentSchedule.DAILY,
                payment_type=PaymentSchedule.RUNNING_PAYMENT,
                recipient_type=PaymentSchedule.PERSON,
                payment_method=CASH,
                payment_amount=Decimal(777),
                activity=modifies_activity,
            )
            activities = Activity.objects.filter(pk=modifies_activity.pk)
            appropriation.grant(
                activities, approval_level.id, "note", self.case_worker
            )
        # appropriation with earlier appropriated activities
        # and which modifies an activity, but with a start_date
        # in the period should be included and marked changed.
        dst_appropriations = (
            Appropriation.objects.appropriations_for_dst_payload(
                from_date=date(2022, 4, 1), to_date=date(2022, 5, 1)
            )
        )
        self.assertEqual(dst_appropriations.count(), 1)
        self.assertTrue(appropriation in dst_appropriations)
        self.assertEqual(dst_appropriations.first().dst_report_type, "Ændring")
