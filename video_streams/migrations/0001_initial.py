# Generated by Django 5.0 on 2023-12-23 08:33

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('events', '0001_initial'),
        ('video_channels', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='VideoStream',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=2147483647)),
                ('url', models.CharField(max_length=2147483647)),
                ('password', models.CharField(blank=True, max_length=2147483647, null=True)),
                ('additional_information', models.CharField(blank=True, max_length=2147483647, null=True)),
                ('extra', models.JSONField(blank=True, null=True)),
                ('bg_img_url', models.CharField(blank=True, max_length=2147483647, null=True)),
                ('is_chat_enabled', models.BooleanField(blank=True, null=True)),
                ('is_global_event_room', models.BooleanField(blank=True, null=True)),
                ('chat_room_id', models.CharField(blank=True, max_length=2147483647, null=True)),
                ('channel', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='video_channels.videochannel')),
                ('event', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='events.event')),
            ],
        ),
    ]
