import factory
from django.contrib.auth import get_user_model

User = get_user_model()

class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User
    
    email = factory.Faker('email') # Generate random email
    password = factory.PostGenerationMethodCall('set_password', 'defaultpassword') # Set hashed password
    is_active = False