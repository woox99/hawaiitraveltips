from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.home, name='home'),
    path('welcome/', views.index, name='index'),
    path('import/', views.import_view, name='import'), #debug
    path('about/', views.about_view, name='about'),
    path('legal/', views.legal_view, name='legal'),
    path('contact/', views.contact_view, name='contact'),
    path('logout/', views.logout_admin, name='logout'),
    path('guide/<str:guide_slug>/', views.guide_detail_view, name='guide-detail'),
    path('update-booking/<int:booking_id>/', views.update_booking_view, name='update-booking'),
    path('save-booking/<int:booking_id>/', views.save_booking, name='save-booking'),
    path('<str:island_slug>/', views.island_view, name='island'),
    path('<str:island_slug>/tours-activities/', views.bookings_view, name='bookings'),
    path('<str:island_slug>/guides/', views.guide_list_view, name='guides'),
    path('<str:island_slug>/clear-bookings/', views.clear_bookings_filter, name='clear-bookings'),

]