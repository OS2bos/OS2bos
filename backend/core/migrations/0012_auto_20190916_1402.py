# Generated by Django 2.2.1 on 2019-09-16 12:02

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [("core", "0011_add_default_team_to_case")]

    operations = [
        migrations.AlterField(
            model_name="case",
            name="team",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name="cases",
                to="core.Team",
                verbose_name="team",
            ),
        )
    ]
