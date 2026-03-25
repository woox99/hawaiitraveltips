from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from core.models import *

# Guides will be naturally crawled, no need to create sitemap

class StaticViewSitemap(Sitemap):
    priority = 0.5
    changefreq = 'monthly'

    def items(self):
        # Use the URL **names** defined in urlpatterns
        return ['about', 'contact', 'legal', 'home', 'index']

    def location(self, item):
        return reverse(f'core:{item}')


class IslandSitemap(Sitemap):
    priority = 1.0
    changefreq = 'monthly'

    def items(self):
        return Island.objects.all()

    def lastmod(self, obj):
        return obj.modified

    def location(self, obj):
        return reverse('core:island', args=[obj.slug])
    

class IslandToursSitemap(Sitemap):
    priority = 0.8
    changefreq = 'monthly'

    def items(self):
        # Return all islands
        return Island.objects.all()

    def lastmod(self, obj):
        return obj.modified

    def location(self, obj):
        # URL pattern: <island_slug>/tours-activities/
        return reverse('core:bookings', args=[obj.slug])


class IslandGuidesSitemap(Sitemap):
    priority = 0.5
    changefreq = 'monthly'

    def items(self):
        # Return all islands
        return Island.objects.all()

    def lastmod(self, obj):
        return obj.modified

    def location(self, obj):
        # URL pattern: <island_slug>/tours-activities/
        return reverse('core:guides', args=[obj.slug])