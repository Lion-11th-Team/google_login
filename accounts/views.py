from django.shortcuts import render
import requests
import json
from django.http import JsonResponse
from json.decoder import JSONDecodeError
from accounts.models import User
from allauth.socialaccount.models import SocialAccount
from django.conf import settings
from dj_rest_auth.registration.views import SocialLoginView, APIView, AllowAny
from allauth.socialaccount.providers.google import views as google_view
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from rest_framework import status
from rest_framework.response import Response
from config.settings import GOOGLE_CLIENT_ID, GOOGLE_SECRET


state = getattr(settings, 'STATE')
BASE_URL = 'http://localhost:3000/'
REDIRECT_URI = 'http://localhost:3000/googleCallback'

class GoogleCallbackAPIView(APIView):

    permission_classes = (AllowAny,)

    def get(self, request, *args, **kwargs):
        try:
            # Google Login Parameters
            # grant_type = 'authorization_code' # 발급일 경우
            client_id = GOOGLE_CLIENT_ID
            client_secret = GOOGLE_SECRET
            code = request.GET.get('code') # callback으로 전달받은 access code와
            state = request.GET.get('state') # state 값

            # parameters = f"grant_type={grant_type}&client_id={client_id}&client_secret={client_secret}&code={code}&state={state}"

            # access token 요청할 url
            token_request = requests.get(
                f"https://oauth2.googleapis.com/token?client_id={client_id}&client_secret={client_secret}&code={code}&grant_type=authorization_code&redirect_uri={REDIRECT_URI}&state={state}"
            )

            # JSON 형태로 받은 응답을 Python에서 확인할 수 있게 변환
            token_response_json = token_request.json()
            error = token_response_json.get("error", None)

            # 에러 있으면
            if error is not None:
                raise JSONDecodeError(error)
            # 에러 없으면
            access_token = token_response_json.get("access_token")

            
            # User info get request
            user_info_request = requests.get(
                f"https://www.googleapis.com/oauth2/v1/tokeninfo?access_token={access_token}"
            )

            # User 정보를 가지고 오는 요청이 잘못된 경우
            if user_info_request.status_code != 200:
                return JsonResponse({"error": "failed to get email."}, status=status.HTTP_400_BAD_REQUEST)

            user_info = user_info_request.json().get("response")
            email = user_info["email"]
            # email_req_json = email_req.json()
            # email = email_req_json.get('email')

            # User 의 email 을 받아오지 못한 경우
            if email is None:
                return JsonResponse({
                    "error": "Can't Get Email Information from Google"
                }, status=status.HTTP_400_BAD_REQUEST)
            try:
            # 동일한 email을 사용하는 사용자가 있는 경우에, access_token과 code를 google에 보낸다.
                user = User.objects.get(email=email)
                data = {'access_token': access_token, 'code': code}
                # accept에는 token 값이 json 형태로 들어온다({"key"}:"token value")
                # 여기서 오는 key 값은 authtoken_token에 저장된다.
                accept = requests.post(
                    f"{BASE_URL}accounts/google/login/finish/", data=data
                )
                # 만약 token 요청이 제대로 이루어지지 않으면 오류처리
                if accept.status_code != 200:
                    return JsonResponse({"error": "Failed to Signin."}, status=accept.status_code)
                return Response(accept.json(), status=status.HTTP_200_OK)

            # 기존에 가입된 유저가 없으면 새로 가입
            except User.DoesNotExist:
                data = {'access_token': access_token, 'code': code}
                accept = requests.post(
                    f"{BASE_URL}accounts/google/login/finish/", data=data
                )
                # token 발급
                return Response(accept.json(), status=status.HTTP_200_OK)
        except:
            return JsonResponse({
                "error": "error",
            }, status=status.HTTP_404_NOT_FOUND)
        

#로그인 정보 저장
class GoogleToDjangoLoginView(SocialLoginView):
    adapter_class = google_view.GoogleOAuth2Adapter
    callback_url = REDIRECT_URI
    client_class = OAuth2Client