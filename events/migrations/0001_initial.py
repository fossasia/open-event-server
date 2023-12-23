# Generated by Django 5.0 on 2023-12-23 08:33

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('discount_codes', '0001_initial'),
        ('event_sub_topics', '0001_initial'),
        ('event_topics', '0001_initial'),
        ('event_types', '0001_initial'),
        ('groups', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('identifier', models.CharField(max_length=2147483647, null=True, unique=True)),
                ('name', models.CharField(max_length=2147483647, null=True)),
                ('external_event_url', models.CharField(max_length=2147483647, null=True)),
                ('logo_url', models.CharField(max_length=2147483647, null=True)),
                ('starts_at', models.DateTimeField(null=True)),
                ('ends_at', models.DateTimeField(null=True)),
                ('timezone', models.CharField(max_length=2147483647, null=True)),
                ('latitude', models.FloatField(null=True)),
                ('longitude', models.FloatField(null=True)),
                ('location_name', models.CharField(max_length=2147483647, null=True)),
                ('searchable_location_name', models.CharField(max_length=2147483647, null=True)),
                ('description', models.TextField(null=True)),
                ('original_image_url', models.CharField(max_length=2147483647, null=True)),
                ('thumbnail_image_url', models.CharField(max_length=2147483647, null=True)),
                ('large_image_url', models.CharField(max_length=2147483647, null=True)),
                ('icon_image_url', models.CharField(max_length=2147483647, null=True)),
                ('owner_name', models.CharField(max_length=2147483647, null=True)),
                ('is_map_shown', models.BooleanField(default=True)),
                ('owner_description', models.CharField(max_length=2147483647, null=True)),
                ('is_sessions_speakers_enabled', models.BooleanField(default=True)),
                ('privacy', models.CharField(max_length=2147483647, null=True)),
                ('state', models.CharField(max_length=2147483647, null=True)),
                ('ticket_url', models.CharField(max_length=2147483647, null=True)),
                ('code_of_conduct', models.CharField(max_length=2147483647, null=True)),
                ('schedule_published_on', models.DateTimeField(null=True)),
                ('is_ticketing_enabled', models.BooleanField(default=True)),
                ('deleted_at', models.DateTimeField(null=True)),
                ('payment_country', models.CharField(max_length=2147483647, null=True)),
                ('payment_currency', models.CharField(max_length=2147483647, null=True)),
                ('paypal_email', models.CharField(max_length=2147483647, null=True)),
                ('is_tax_enabled', models.BooleanField(default=True)),
                ('can_pay_by_paypal', models.BooleanField(default=False)),
                ('can_pay_by_stripe', models.BooleanField(default=False)),
                ('can_pay_by_cheque', models.BooleanField(default=False)),
                ('can_pay_by_bank', models.BooleanField(default=False)),
                ('can_pay_onsite', models.BooleanField(default=False)),
                ('cheque_details', models.CharField(max_length=2147483647, null=True)),
                ('bank_details', models.CharField(max_length=2147483647, null=True)),
                ('onsite_details', models.CharField(max_length=2147483647, null=True)),
                ('created_at', models.DateTimeField(null=True)),
                ('is_sponsors_enabled', models.BooleanField(default=False)),
                ('ical_url', models.CharField(max_length=2147483647, null=True)),
                ('pentabarf_url', models.CharField(max_length=2147483647, null=True)),
                ('xcal_url', models.CharField(max_length=2147483647, null=True)),
                ('has_owner_info', models.BooleanField(default=True)),
                ('refund_policy', models.CharField(max_length=2147483647, null=True)),
                ('is_stripe_linked', models.BooleanField(default=True)),
                ('online', models.BooleanField(default=False)),
                ('is_donation_enabled', models.BooleanField(default=True)),
                ('is_featured', models.BooleanField(default=False)),
                ('can_pay_by_omise', models.BooleanField(default=False)),
                ('is_ticket_form_enabled', models.BooleanField(default=True)),
                ('can_pay_by_alipay', models.BooleanField(default=False)),
                ('show_remaining_tickets', models.BooleanField(default=False)),
                ('is_billing_info_mandatory', models.BooleanField(default=False)),
                ('can_pay_by_paytm', models.BooleanField(default=False)),
                ('is_promoted', models.BooleanField(default=False)),
                ('is_demoted', models.BooleanField(default=False)),
                ('after_order_message', models.TextField(null=True)),
                ('is_chat_enabled', models.BooleanField(default=False)),
                ('chat_room_id', models.CharField(max_length=2147483647, null=True)),
                ('document_links', models.JSONField(null=True)),
                ('is_document_enabled', models.BooleanField(default=False)),
                ('is_videoroom_enabled', models.BooleanField(default=False)),
                ('is_oneclick_signup_enabled', models.BooleanField(default=True)),
                ('is_cfs_enabled', models.BooleanField(default=False)),
                ('is_announced', models.BooleanField(default=False)),
                ('completed_order_sales', models.IntegerField(null=True)),
                ('placed_order_sales', models.IntegerField(null=True)),
                ('pending_order_sales', models.IntegerField(null=True)),
                ('completed_order_tickets', models.IntegerField(null=True)),
                ('placed_order_tickets', models.IntegerField(null=True)),
                ('pending_order_tickets', models.IntegerField(null=True)),
                ('can_pay_by_invoice', models.BooleanField(default=False)),
                ('invoice_details', models.CharField(max_length=2147483647, null=True)),
                ('public_stream_link', models.CharField(max_length=2147483647, null=True)),
                ('stream_loop', models.BooleanField(default=True)),
                ('stream_autoplay', models.BooleanField(default=True)),
                ('is_badges_enabled', models.BooleanField(default=True)),
                ('discount_code', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='events', to='discount_codes.discountcode')),
                ('event_sub_topic', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='event_sub_topics.eventsubtopic')),
                ('event_topic', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='event_topics.eventtopic')),
                ('event_type', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='event_types.eventtype')),
                ('group', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='groups.group')),
            ],
        ),
    ]
