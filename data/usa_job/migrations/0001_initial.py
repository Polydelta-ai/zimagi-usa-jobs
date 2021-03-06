# Generated by Django 4.0.1 on 2022-02-09 02:55

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('job_remuneration', '0001_initial'),
        ('job', '0001_initial'),
        ('job_offering_type', '0001_initial'),
        ('job_grade', '0001_initial'),
        ('job_schedule', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='USAJob',
            fields=[
                ('job_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='job.job')),
                ('who_may_apply', models.CharField(max_length=256, null=True)),
                ('low_grade', models.CharField(max_length=10, null=True)),
                ('high_grade', models.CharField(max_length=10, null=True)),
                ('promotion_potential', models.CharField(max_length=10, null=True)),
                ('organization_codes', models.CharField(max_length=10, null=True)),
                ('vendor', models.CharField(max_length=256, null=True)),
                ('service_type', models.CharField(max_length=256, null=True)),
                ('security_clearance_required', models.BooleanField(null=True)),
                ('security_clearance', models.CharField(max_length=256, null=True)),
                ('job_grades', models.ManyToManyField(related_name='%(class)s_relations', to='job_grade.JobGrade')),
                ('job_offering_types', models.ManyToManyField(related_name='%(class)s_relations', to='job_offering_type.JobOfferingType')),
                ('job_remunerations', models.ManyToManyField(related_name='%(class)s_relations', to='job_remuneration.JobRemuneration')),
                ('job_schedules', models.ManyToManyField(related_name='%(class)s_relations', to='job_schedule.JobSchedule')),
            ],
            options={
                'verbose_name': 'usa job',
                'verbose_name_plural': 'usa jobs',
                'db_table': 'usa_jobs_usa_job',
                'ordering': ['job_source__name', 'name'],
                'abstract': False,
            },
            bases=('job.job', models.Model),
        ),
    ]
