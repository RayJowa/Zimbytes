# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2018-07-23 06:32
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('sessions', '0001_initial'),
        ('zim', '0007_remove_order_session'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='session',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='sessions.Session'),
        ),
    ]