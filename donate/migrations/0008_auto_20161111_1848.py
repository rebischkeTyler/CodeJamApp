# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2016-11-11 18:48
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('donate', '0007_auto_20161025_1937'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='donate',
            name='author',
        ),
        migrations.RemoveField(
            model_name='donate',
            name='category',
        ),
        migrations.RemoveField(
            model_name='donate',
            name='condition',
        ),
        migrations.RemoveField(
            model_name='donate',
            name='contact_method',
        ),
        migrations.RemoveField(
            model_name='donate',
            name='created_date',
        ),
        migrations.RemoveField(
            model_name='donate',
            name='location',
        ),
        migrations.RemoveField(
            model_name='donate',
            name='published_date',
        ),
        migrations.RemoveField(
            model_name='donate',
            name='subcategory',
        ),
    ]
