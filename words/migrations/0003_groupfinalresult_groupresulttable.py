# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.conf import settings
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('words', '0002_userprofile'),
    ]

    operations = [
        migrations.CreateModel(
            name='GroupFinalResult',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('groupname', models.CharField(max_length=100)),
                ('marks', models.IntegerField(default=0)),
                ('starttime', models.DateTimeField(default=datetime.datetime(2015, 9, 11, 14, 10, 22, 14724, tzinfo=utc))),
                ('endtime', models.DateTimeField(default=datetime.datetime(2015, 9, 11, 14, 10, 22, 14755, tzinfo=utc))),
                ('re_user', models.ForeignKey(default=0, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='GroupResultTable',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('correct_ans', models.CharField(max_length=25)),
                ('ans', models.CharField(max_length=25)),
                ('marks', models.IntegerField(default=0)),
                ('usertest', models.ForeignKey(default=0, to='words.GroupFinalResult')),
            ],
        ),
    ]
