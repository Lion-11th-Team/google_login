from typing import Any
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin

# 헬퍼 클래스
class UserManager(BaseUserManager):
    def create_user(self, email, password, oauth_id, **kwargs): # email -> oauth_id로 바꿔야 하나?
        # 주어진 이메일, 비밀번호 등 개인정보로 User 인스턴스 생성
        if not email:
            raise ValueError('The Email must be set')
        if not oauth_id:
            raise ValueError('The ID must be set')
        email = self.normalize_email(email)
        user = self.model(
            email=email,
            oauth_id=oauth_id,
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email=None, password=None, oauth_id=0, **extra_fields):
        # 주어진 이메일, 비밀번호 등 개인정보로 User 인스턴스 생성
        # 단, 최상위 사용자이므로 권한을 부여
        superuser = self.create_user(
            email=email,
            password=password,
            oauth_id=oauth_id,
        )
        superuser.is_staff = True
        superuser.is_superuser = True
        superuser.is_active = True
        superuser.save(using=self._db)
        return superuser
    

class UserSignupManager(BaseUserManager):
    def create_user(self, oauth_id, **kwargs):
        if not oauth_id:
            raise ValueError('The ID must be set')
        user = self.model(
            oauth_id=oauth_id,
        )
        user.save(using=self._db)
        return user


TRACK = (
    'Backend',
    'Frontend',
    'Design'
)
TRACK_CHOICES = [(t, t) for t in TRACK]

# AbstractBaseUser를 상속해서 유저 커스텀
class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(max_length=30, unique=True, null=False, blank=False)
    oauth_id = models.CharField(max_length=50, unique=True, default=False, blank=False)
    is_superuser = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_register = models.BooleanField(default=False)
    name = models.CharField(max_length=50, null=False, default=False, blank=False)
    phone = models.CharField(max_length=20, null=False, default=False, blank=False)
    univ = models.CharField(max_length=50, null=False, default=False, blank=False)
    track = models.CharField(max_length=10, null=False, default=False, blank=False)
    student_id = models.CharField(max_length=50, choices=TRACK_CHOICES, null=False, default=False, blank=False)

	# 헬퍼 클래스 사용
    objects = UserManager() # default manager
    registers = UserSignupManager()

	# 사용자의 username field는 oauth_id로 설정 (고유값)
    USERNAME_FIELD = 'oauth_id'
