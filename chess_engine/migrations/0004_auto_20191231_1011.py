# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2019-12-31 02:11
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('chess_engine', '0003_userranking'),
    ]

    operations = [
        migrations.CreateModel(
            name='News',
            fields=[
                ('persistentobject_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='chess_engine.PersistentObject')),
            ],
            bases=('chess_engine.persistentobject',),
        ),
        migrations.AlterField(
            model_name='persistentobject',
            name='data',
            field=models.TextField(default='{}'),
        ),
    ]
