# from .models import TRACK, User
from rest_framework import serializers
import re
from rest_framework.serializers import ValidationError
from accounts.models import TRACK, TRACK_CHOICES


from django.contrib.auth import get_user_model
User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        # fields = '__all__'
        exclude = ['password']

    def create(self, validated_data):
        user = User.objects.create_user(
            email = validated_data['email'],
            # password = validated_data['password'],
            oauth_id = validated_data['ouath_id']
        )
        return user
    

class UserSignupSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['name', 'phone', 'univ', 'track', 'student_id']
    
    def get_queryset(self):
        return super().get_queryset().filter(is_register=False)
    
    # def create(self, data):
    #     user = User.registers.create_user(
    #         oauth_id = data['oauth_id']
    #     )
    #     return user

    def validate(self, data):
        number_validation = re.compile(r'^010-\d{4}-\d{4}$')
        student_id_validation = re.compile(r'^[a-zA-Z]\d{6}$')
        if not number_validation.match(data.get('phone')):
            raise ValidationError('010-0000-0000 형식으로 적어주세요')
        if data.get('track') not in TRACK:
            raise ValidationError('Backend, Frontend, Design에서 선택해주세요')
        if not student_id_validation.match(data.get('student_id')):
            raise ValidationError('C000000 형식으로 적어주세요')
        return data
