# Generated by Django 2.2.13 on 2020-07-21 07:16

from django.db import migrations, models


def migrate_targetgroups(apps, schema_editor):
    TargetGroup = apps.get_model("core", "TargetGroup")

    for target_group in TargetGroup.objects.all():
        csv_required = ",".join(target_group.required_fields_for_case)
        target_group.required_fields_for_case_csv = csv_required
        target_group.save()


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0079_migrate_payment_schedules'),
    ]

    operations = [
        migrations.AddField(
            model_name='targetgroup',
            name='required_fields_for_case_csv',
            field=models.CharField(blank=True, max_length=128, verbose_name='påkrævede felter på sag'),
        ),
        migrations.RunPython(migrate_targetgroups),
        migrations.RemoveField(model_name="targetgroup", name="required_fields_for_case"),
        migrations.RenameField(model_name="targetgroup", old_name="required_fields_for_case_csv", new_name="required_fields_for_case")
    ]
