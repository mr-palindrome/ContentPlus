from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.generics import UpdateAPIView


class PublicApi(APIView):
    authentication_classes = ()
    permission_classes = ()

class PublicUpdateApi(UpdateAPIView):
    authentication_classes = ()
    permission_classes = ()
