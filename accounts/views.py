from django.shortcuts import render
import requests
import json
from django.http import JsonResponse
from json.decoder import JSONDecodeError
from accounts.models import User
from django.conf import settings
from dj_rest_auth.registration.views import APIView, AllowAny
from rest_framework import status
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from accounts.serializers import UserSerializer
from django.contrib.auth import get_user_model


state = getattr(settings, 'STATE')
BASE_URL = 'http://localhost:3000/'
REDIRECT_URI = 'http://localhost:3000/googleCallback'

class GoogleCallbackAPIView(APIView):

    permission_classes = (AllowAny,)

    def post(self, request, *args, **kwargs):
        try:
            # Google Login Parameters
            # grant_type = 'authorization_code' # 발급일 경우
            # 인가코드 받아오기
            code = request.data.get('code')

            # parameters = f"grant_type={grant_type}&client_id={client_id}&client_secret={client_secret}&code={code}&state={state}"
            # access token 요청할 url
            # token_request = requests.get(
            #     f"https://oauth2.googleapis.com/token?client_id={GOOGLE_CLIENT_ID}&client_secret={GOOGLE_SECRET}&code={code}&grant_type=authorization_code&redirect_uri={REDIRECT_URI}&state={state}"
                
            # )
            # 구글에 토큰 요청
            token_request = requests.post(
                'https://oauth2.googleapis.com/token',
                headers={
                    'Content-Type': 'application/x-www-form-urlencoded'
                },
                data={
                    'grant_type': 'authorization_code',
                    'client_id': '374838732950-m9o6ik80g35uf9j7u7mh5jrhatl8869n.apps.googleusercontent.com',
                    'client_secret': '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',
                    'redirect_uri': 'http://localhost:3000/googleCallback',
                    'code': code,
                }
            )
            # print(token_request.json())

            # JSON 형태로 받은 응답을 Python에서 확인할 수 있게 변환
            token_response_json = token_request.json()
            error = token_response_json.get("error", None)
            # 에러 있으면
            if error is not None:
                raise JSONDecodeError(error)
            # 에러 없으면
            access_token = token_response_json.get("access_token")

            # 구글에서 유저 정보 가져오기
            user_info_request = requests.get(
                'https://www.googleapis.com/oauth2/v1/userinfo',
                headers={
                    'Authorization': f'Bearer {access_token}'
                }
            )
            # print(user_info_request.json())

            # User 정보를 가지고 오는 요청이 잘못된 경우
            if user_info_request.status_code != 200:
                return JsonResponse({"error": "failed to get email."}, status=status.HTTP_400_BAD_REQUEST)
            
            # 잘못되지 않았으면
            user_info = user_info_request.json()
            oauth_id = user_info["id"]
            email = user_info["email"]
            # email_req_json = email_req.json()
            # email = email_req_json.get('email')

            # User 의 id 를 받아오지 못한 경우
            if oauth_id is None:
                return JsonResponse({
                    "error": "Can't Get ID Information from Google"
                }, status=status.HTTP_400_BAD_REQUEST)
            
            try:
                user = User.objects.get(oauth_id=oauth_id) # oauth_id가 oauth_id인 객체 하나를 반환 
                # 동일한 id를 사용하는 사용자가 db에 있는 경우에
                refresh = RefreshToken.for_user(user)
                return JsonResponse({
                        'access': str(refresh.access_token),
                        'refresh': str(refresh),
                        'register_state': user.is_register,
                    },
                    status=status.HTTP_200_OK,
                )
            # 기존에 가입된 유저가 없으면 임시로 저장하고 새로 가입
            except User.DoesNotExist:
                user = User.objects.create_user(email=email, password=None, oauth_id=oauth_id)
                refresh = RefreshToken.for_user(user)
                return JsonResponse({
                        'access': str(refresh.access_token),
                        'refresh': str(refresh),
                        'register_state': user.is_register,
                    },
                    status=status.HTTP_200_OK,
                )
        except:
            return JsonResponse({
                "error": "error",
            }, status=status.HTTP_404_NOT_FOUND)
        

# 사용자 정보 조회
class UserInfoView(APIView):
    #로그인
    def get(self, request):
        user_email = request.user
        user = User.objects.get(email=user_email)
        return Response(UserSerializer(user).data)
    #회원가입