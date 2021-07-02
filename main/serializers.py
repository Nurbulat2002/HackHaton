from django.contrib.auth import get_user_model

from rest_framework import serializers

from .models import Post, Review, FavouriteList

User = get_user_model()


class PostListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ('id', 'title', 'image')


class ReviewAuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('first_name', 'last_name')

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        if not instance.first_name and not instance.last_name:
            representation['full_name'] = 'Anonimus polzovatel'
        return representation


class FavouriteInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ['title']


class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        exclude = ('id', 'author')

    def validate_product(self, post):
        request = self.context.get('request')
        if post.reviews.filter(author=request.user).exists():
            raise serializers.ValidationError('Вы не можете добавить второй товар')
        return post

    def validate_rating(self, rating):
        if not rating in range(1, 6):
            raise serializers.ValidationError('Рейтинг должен быть от 1 до 5')
        return rating

    def validate(self, attrs):
        request = self.context.get('request')
        attrs['author'] = request.user
        return attrs

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep['author'] = ReviewAuthorSerializer(instance.author).data
        return rep


class FavouriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = FavouriteList
        exclude = ('is_favourite', 'user', 'id', 'title')

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['My Favourites'] = FavouriteInfoSerializer(instance.title).data
        return representation


class PostDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = '__all__'

    def get_rating(self, instance):
        total_rating = sum(instance.reviews.values_list('rating', flat=True))
        reviews_count = instance.reviews.count()
        rating = total_rating / reviews_count if reviews_count > 0 else 0
        return round(rating, 1)

    def total_likes(self, instance):
        total_likes = sum(instance.likes.values_list('is_liked', flat=True))
        likes = total_likes if total_likes > 0 else 0
        return likes

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['reviews'] = ReviewSerializer(instance.reviews.all(), many=True).data
        representation['rating'] = self.get_rating(instance)
        representation['likes'] = self.total_likes(instance)
        return representation