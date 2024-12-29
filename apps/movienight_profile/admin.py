from django.contrib import admin
from apps.movienight_profile.models import UserProfile


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'name', 'gender', 'custom_gender']
    search_fields = ['user__email', 'name', 'gender', 'custom_gender']
    list_filter = ['gender']
    ordering = ['user__email']

    # For handling gender and custom gender fields based on the custom gender logic
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if obj and obj.gender != 'Custom':
            form.base_fields['custom_gender'].disabled = True
        return form