# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.utils.timezone import utc
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('words', '0003_groupfinalresult_groupresulttable'),
    ]

    operations = [
        migrations.CreateModel(
            name='FinalResult',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('session_id', models.IntegerField(default=0)),
                ('marks', models.IntegerField(default=0)),
                ('starttime', models.DateTimeField(default=datetime.datetime(2015, 9, 11, 15, 49, 43, 193389, tzinfo=utc))),
                ('endtime', models.DateTimeField(default=datetime.datetime(2015, 9, 11, 15, 49, 43, 193413, tzinfo=utc))),
                ('re_user', models.ForeignKey(default=0, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='ResultTable',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('session_id', models.IntegerField(default=0)),
                ('correct_ans', models.CharField(max_length=25)),
                ('ans', models.CharField(max_length=25)),
                ('marks', models.IntegerField(default=0)),
                ('re_user', models.ForeignKey(default=0, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AlterField(
            model_name='groupfinalresult',
            name='endtime',
            field=models.DateTimeField(default=datetime.datetime(2015, 9, 11, 15, 49, 43, 192239, tzinfo=utc)),
        ),
        migrations.AlterField(
            model_name='groupfinalresult',
            name='starttime',
            field=models.DateTimeField(default=datetime.datetime(2015, 9, 11, 15, 49, 43, 192206, tzinfo=utc)),
        ),
    ]
