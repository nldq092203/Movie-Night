from rest_framework import serializers
from .models import UserProfile


class UserProfileSerializer(serializers.ModelSerializer):
    user = serializers.EmailField()
    class Meta:
        model = UserProfile
        fields = ['user', 'name', 'bio', 'gender', 'custom_gender', 'avatar_url']
        read_only = ['user', 'avatar_url']

    def validate(self, data):
        """
        Validate that if gender is 'Custom', custom_gender is provided.
        """
        gender = data.get('gender')
        custom_gender = data.get('custom_gender')

        # If gender is 'Custom', custom_gender must not be empty
        if gender == 'Custom' and not custom_gender:
            raise serializers.ValidationError({
                'custom_gender': 'Please provide a custom gender when selecting "Custom".'
            })

        # If gender is not 'Custom', custom_gender should be empty
        if gender != 'Custom' and custom_gender:
            raise serializers.ValidationError({
                'custom_gender': 'Custom gender should be empty unless you select "Custom" as gender.'
            })

        return data
