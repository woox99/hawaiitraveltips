from django.contrib import admin
from django.urls import path, include # import include

from django.contrib.sitemaps.views import sitemap
from core.sitemaps import *


sitemaps = {
    'static': StaticViewSitemap,
    'islands': IslandSitemap,
    'island_tours': IslandToursSitemap,
    'island_guides': IslandGuidesSitemap,
}

urlpatterns = [
    path("admin/", admin.site.urls),
    path('', include('core.urls')), # add pattern here
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
]