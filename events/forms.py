from django import forms
from events.models import Exhibitors


class ExhibitorForm(forms.ModelForm):
    class Meta:
        model = Exhibitors
        fields = [
            "name",
            "description",
            "url",
            "position",
            "event_id" "logo_url",
            "banner_url",
            "video_url",
            "slides_url",
            "contact_email",
            "contact_link",
            "enable_video_room",
            "thumbnail_image_url",
        ]
