import requests
import re
import math
from datetime import datetime
from .models import *
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404
from decimal import Decimal




def update_booking_util(request, booking_id):
    booking = get_object_or_404(Booking, pk=booking_id)

    booking.title = request.POST.get('title', '') 
    booking.is_public = True if request.POST['is_public'] == 'true' else False
    booking.is_popular = True if request.POST['is_popular'] == 'true' else False
    booking.is_pinned = True if request.POST['is_pinned'] == 'true' else False
    booking.details = request.POST['details']
    booking.duration = request.POST['duration']

    price = request.POST.get('price')
    company_rating = request.POST.get('company_rating')
    company_reviews = request.POST.get('company_reviews')
    promo_amount = request.POST.get('promo_amount')
    
    booking.price = int(price) if price else 0
    booking.company_rating = float(company_rating) if company_rating else 0.0
    booking.company_reviews = int(company_reviews) if company_reviews else 0
    booking.promo_amount = int(promo_amount) if promo_amount else 0

    booking.is_promo = True if request.POST['is_promo'] == 'true' else False
    booking.promo_code = request.POST['promo_code']
    booking.city = request.POST['city']
    booking.island = get_object_or_404(Island, pk=request.POST['island_id'])

    category_ids = request.POST.getlist('category_ids')
    if category_ids:
        tags = Category.objects.filter(pk__in=category_ids)
        booking.tags.set(tags)

    booking.save()
    return booking



def paginate_bookings(bookings, request, per_page=12):
    paginator = Paginator(bookings, per_page)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    page_range = paginator.get_elided_page_range(page_number, on_each_side=0, on_ends=1)
    return page_obj, page_range


def get_wp_posts(WP_API_URL):
    try:
        response = requests.get(WP_API_URL, timeout=5)
        response.raise_for_status()
        wp_posts = response.json()
    except requests.exceptions.RequestException as e:
        print("Error fetching WordPress posts:", e)
        wp_posts = []
    
    for post in wp_posts:
        # Extract tag names from the embedded data
        tags = []
        if "_embedded" in post and "wp:term" in post["_embedded"]:
            for term_group in post["_embedded"]["wp:term"]:
                for term in term_group:
                    if term.get("taxonomy") == "post_tag":
                        tags.append(term["name"])
        post["tag_names"] = tags
    
        # Format modified date
        modified_str = post.get("modified")
        if modified_str:
            try:
                # Convert WordPress ISO date string -> datetime object
                post["modified"] = datetime.fromisoformat(modified_str.replace("Z", "+00:00"))
            except Exception:
                # Fallback: if parsing fails, keep original
                post["modified"] = modified_str

        # # Read Time
        # content_html = post.get("content", {}).get("rendered", "")
        # content_text = re.sub(r"<[^>]+>", "", content_html)
        # word_count = len(content_text.split())
        # post["read_time"] = math.ceil(word_count / 250)
    return wp_posts