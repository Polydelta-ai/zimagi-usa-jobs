# Generated by Django 4.0.1 on 2022-02-09 02:55

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='JobRemuneration',
            fields=[
                ('created', models.DateTimeField(editable=False, null=True)),
                ('updated', models.DateTimeField(editable=False, null=True)),
                ('id', models.CharField(editable=False, max_length=64, primary_key=True, serialize=False)),
                ('interval', models.CharField(max_length=256)),
                ('min_range', models.CharField(max_length=30)),
                ('max_range', models.CharField(max_length=30)),
            ],
            options={
                'verbose_name': 'job remuneration',
                'verbose_name_plural': 'job remunerations',
                'db_table': 'usa_jobs_job_remuneration',
                'ordering': ['interval', '-max_range'],
                'abstract': False,
            },
        ),
    ]
