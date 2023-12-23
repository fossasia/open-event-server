# Generated by Django 5.0 on 2023-12-23 08:33

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('microlocation', '0001_initial'),
        ('video_streams', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='microlocation',
            name='video_stream',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='video_streams.videostream'),
        ),
    ]
