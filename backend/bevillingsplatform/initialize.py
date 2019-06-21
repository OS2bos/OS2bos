# -*- coding: utf-8 -*-
from django.core.management import call_command

from core.data.municipalities import municipalities
from core.data.school_districts import school_districts
from core.data.teams import teams
from core.models import Municipality, SchoolDistrict, Team, User


def initialize():
    """Main script for initializing all the basic data we want at start.

    Should be able to be run multiple times over without generating duplicates.
    """
    initialize_municipalities()
    initialize_school_districts()
    initialize_sections()
    initialize_activity_catalogs()
    initialize_service_providers()
    initialize_users()
    initialize_teams()
    initialize_approval_levels()


def initialize_municipalities():
    """Initialize all the danish municipalities."""
    for name in municipalities:
        Municipality.objects.get_or_create(name=name)


def initialize_approval_levels():
    """Initialize all the initial approval levels.

    Data should be the output of manage.py dumpdata core.approvallevels
    """
    call_command("loaddata", "approvallevels.json", app_label="core")


def initialize_sections():
    """Initialize all the relevant law sections.

    Data should be the output of manage.py dumpdata core.sections
    """
    call_command("loaddata", "sections.json", app_label="core")


def initialize_activity_catalogs():
    """Initialize all the relevant activity catalogs

    Data should be the output of manage.py dumpdata core.activitycatalog

    """
    call_command("loaddata", "activitycatalog.json", app_label="core")


def initialize_service_providers():
    """Initialize all the relevant service providers

    Data should be the output of manage.py dumpdata core.serviceprovider
    """
    call_command("loaddata", "serviceproviders.json", app_label="core")


def initialize_users():
    """Prime the system with some users to get started.

    Data should be the output of manage.py dumpdata core.User.

    """
    call_command("loaddata", "users.json", app_label="core")


def initialize_school_districts():
    """Initialize all the school districts for Ballerup."""
    for name in school_districts:
        SchoolDistrict.objects.get_or_create(name=name)


def initialize_teams():
    """Initialize all the school districts for Ballerup."""
    for (name, team_leader, members) in teams:
        leader = User.objects.get(username=team_leader)
        team, _ = Team.objects.get_or_create(name=name, leader=leader)
        for name in members:
            user = User.objects.get(username=name)
            user.team = team
            user.save()
