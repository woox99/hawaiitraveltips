from django.contrib import admin
from core.models import *

class BookingAdmin(admin.ModelAdmin):
    search_fields = ['title', 'fh_id']
    list_display = ['title', 'is_public', 'company_name',  'fh_id', 'island', 'is_promo', 'promo_amount']
    ordering = ['title']


admin.site.register(Booking, BookingAdmin)

registered_models = [Island, Category]
admin.site.register(registered_models)