from django.db import models
from django.utils import timezone

class Island(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.CharField(max_length=50)
    wp_category_id = models.IntegerField(null=True, blank=True)
    island_page_title = models.CharField(max_length=80, default='Page Title')
    modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Booking(models.Model):
    title = models.CharField(max_length=100)
    company_name = models.CharField(max_length=100, blank=True)
    company_rating = models.DecimalField(max_digits=2, decimal_places=1, blank=True, null=True, default=0.0)
    company_reviews = models.IntegerField(blank=True, null=True, default=0)
    city = models.CharField(max_length=100)
    tags = models.ManyToManyField('Category', related_name='bookings')
    island = models.ForeignKey(Island, on_delete=models.CASCADE)
    details = models.TextField(blank=True, null=True)
    duration = models.CharField(max_length=10, blank=True, null=True)
    price = models.IntegerField(default=0)
    is_promo = models.BooleanField(default=False)
    promo_amount = models.IntegerField(default=0)
    promo_code = models.CharField(max_length=100, blank=True, null=True)
    is_public = models.BooleanField(default=False)
    is_popular = models.BooleanField(default=False)
    is_pinned = models.BooleanField(default=False)
    fh_id = models.IntegerField(blank=True, null=True)
    referral_link = models.URLField(blank=True)
    image_URL = models.URLField(blank=True)
    modified = models.DateTimeField(auto_now=True)

    @property
    def adjusted_price(self):
        discounted = self.price - (self.price * self.promo_amount / 100)
        return max(round(discounted), 0)

    def __str__(self):
        return self.title



class Category(models.Model):
    name = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return self.name