from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models


User = get_user_model()


class Category(models.Model):
    title = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, primary_key=True)

    def __str__(self):
        return self.title


class Post(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products',)
    image = models.ImageField(upload_to='products', blank=True, null=True,)

    def __str__(self):
        return self.title


class Review(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='reviews')
    text = models.TextField()
    rating = models.SmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


# class Meta:
#     unique_together = ['author', 'product']


class WishList(models.Model):
    user = models.ForeignKey(User,
                             on_delete=models.CASCADE,
                             related_name='likes')
    post = models.ForeignKey(Post,
                             on_delete=models.CASCADE,
                             related_name='likes')
    is_liked = models.BooleanField(default=False)


class FavouriteList(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favourites')
    title = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='favourites')
    is_favourite = models.BooleanField(default=False)
