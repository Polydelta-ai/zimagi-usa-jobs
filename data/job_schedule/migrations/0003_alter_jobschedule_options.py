# Generated by Django 3.2.5 on 2021-11-30 05:14

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('job_schedule', '0002_alter_jobschedule_options'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='jobschedule',
            options={'ordering': ['code'], 'verbose_name': 'job schedule', 'verbose_name_plural': 'job schedules'},
        ),
    ]
