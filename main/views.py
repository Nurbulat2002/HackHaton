import django_filters
import telebot
from django.db.models import Avg
from django.http import JsonResponse
from django.views import View
from rest_framework.filters import OrderingFilter
import django_filters.rest_framework
from django.shortcuts import render, get_object_or_404
# from dtb.settings import DEBUG
import json

# from tgbot.handlers.dispatcher import process_telegram_event, TELEGRAM_BOT_USERNAME

from rest_framework import status, viewsets, mixins, filters
from rest_framework.decorators import api_view, action
from rest_framework.generics import ListAPIView, RetrieveAPIView, CreateAPIView, UpdateAPIView, DestroyAPIView
from rest_framework.permissions import IsAdminUser, IsAuthenticated

from rest_framework.response import Response
from rest_framework.views import APIView

from hackhaton_api.settings import DEBUG
from .filters import ProductFilter
from .models import Post, Review, WishList, FavouriteList
from .permissions import IsAuthorOrAdminPermissions, DenyAll
from .serializers import PostListSerializer, PostDetailsSerializer, ReviewSerializer, FavouriteSerializer


class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostDetailsSerializer
    filter_backends = (django_filters.rest_framework.DjangoFilterBackend, OrderingFilter)
    filterset_class = ProductFilter
    ordering_fields = ['title', 'description']
    bad_request_message = 'An error has occurred'

    def get_serializer_class(self):
        if self.action == 'list':
            return PostListSerializer
        return self.serializer_class      #super().get_serializer_class()

    def get_permissions(self):
        if self.action in ['create', 'create_review', 'like']:
            return [IsAuthenticated()]
        elif self.action in ['destroy', 'update', 'partial_update']:
            return [IsAuthorOrAdminPermissions()]
        return []

    # api/v1/products/id/create_review
    @action(detail=True, methods=['POST'])
    def create_review(self, request, pk):
        data = request.data.copy()
        data['post'] = pk
        serializer = ReviewSerializer(data=data, context={'request': request})
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=201)

    # /api/v1/products/id/like
    @action(detail=True, methods=['POST'])
    def like(self, request, pk):
        post = self.get_object()
        user = request.user
        like_obj, created = WishList.objects.get_or_create(post=post,
                                                           user=user)
        if like_obj.is_liked:
            like_obj.is_liked = False
            like_obj.save()
            return Response('disliked')
        else:
            like_obj.is_liked = True
            like_obj.save()
            return Response('liked')

    @action(detail=True, methods=['POST'])
    def favourite(self, request, pk):
        title = self.get_object()
        user = request.user
        favourite_obj, created = FavouriteList.objects.get_or_create(title=title, user=user)
        if favourite_obj.is_favourite:
            favourite_obj.is_favourite = False
            favourite_obj.delete()
            return Response('remove from favourites')
        else:
            favourite_obj.is_favourite = True
            favourite_obj.save()
            return Response('add to favourites')


class ReviewViewSet(mixins.CreateModelMixin,
                    mixins.UpdateModelMixin,
                    mixins.DestroyModelMixin,
                    viewsets.GenericViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer

    def get_permissions(self):
        if self.action == 'create':
            return [IsAuthenticated()]
        return [IsAuthorOrAdminPermissions()]


class FavouriteViewSet(viewsets.ModelViewSet):
    queryset = FavouriteList.objects.all()
    serializer_class = FavouriteSerializer
    permission_classes = [IsAuthenticated, ]

