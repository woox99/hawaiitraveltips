from urllib import response
from django.shortcuts import get_object_or_404, redirect, render

from core.models import *
from .util import *

from django.shortcuts import HttpResponse
from core.models import Booking, Island, Category
from openpyxl import load_workbook




def home(request):
    # Check if 'current_island' is in the session and render the island instead of the home page
    if 'current_island' in request.session:
        return redirect('core:island', island_slug=request.session['current_island'])
    
    context = {
        'islands' : Island.objects.all()
    }
    return render(request, 'core/home.html', context)


def island_view(request, island_slug):

    # Set the current island in the session if coming from the home page
    request.session['current_island_slug'] = island_slug
    island = get_object_or_404(Island, slug=island_slug)
    

    # Get 4 popular bookings for the island
    bookings = Booking.objects.filter(island=island, is_public=True)[:4]

    # WordPress.com REST API endpoint - Limit = 3
    WP_API_URL = f"https://public-api.wordpress.com/wp/v2/sites/team92d3a5e49bc-kctlm.wordpress.com/posts?categories={island.wp_category_id}&per_page=3&_embed"
    wp_posts = get_wp_posts(WP_API_URL)


    context = {
        'island': island,
        'islands' : Island.objects.all(),
        'bookings': bookings,
        "wp_posts": wp_posts,
    }
    
    # Build the template path dynamically
    template_path = f'core/views/islands/{island.slug}.html'

    return render(request, template_path, context)


def bookings_view(request, island_slug):

    # Set the current island in the session if coming from the home page
    request.session['current_island_slug'] = island_slug
    island = get_object_or_404(Island, slug=island_slug)

    bookings = Booking.objects.filter(island=island, is_public=True)[:12]
    
    
    context = {
        'island': island,
        'islands' : Island.objects.all(),
        'bookings': bookings,
        'bookings_count': Booking.objects.filter(island=island, is_public=True).count()
    }

    # Build the template path dynamically
    template_path = f'core/views/bookings/{island.slug}.html'
    return render(request, template_path, context)


def guide_list_view(request, island_slug):

    # set the current island in the session if coming from the home page
    request.session['current_island_slug'] = island_slug
    island = get_object_or_404(Island, slug=island_slug)

    # WordPress.com REST API endpoint
    WP_API_URL = f"https://public-api.wordpress.com/wp/v2/sites/team92d3a5e49bc-kctlm.wordpress.com/posts?categories={island.wp_category_id}&_embed"
    wp_posts = get_wp_posts(WP_API_URL)
    
    context = {
        'island': island,
        'islands' : Island.objects.all(),
        "wp_posts": wp_posts,
    }

    # Build the template path dynamically
    return render(request, 'core/views/guide_list.html', context)


def guide_detail_view(request, island_slug, guide_slug):

    # set the current island in the session if coming from the home page
    request.session['current_island_slug'] = island_slug
    island = get_object_or_404(Island, slug=island_slug)

    # WordPress.com REST API endpoint - filter by slug to get the specific post
    WP_API_URL = f"https://public-api.wordpress.com/wp/v2/sites/team92d3a5e49bc-kctlm.wordpress.com/posts?slug={guide_slug}&_embed"
    wp_posts = get_wp_posts(WP_API_URL)
    wp_post = wp_posts[0]

    # Get all posts for the sidebar
    WP_API_URL = f"https://public-api.wordpress.com/wp/v2/sites/team92d3a5e49bc-kctlm.wordpress.com/posts?categories={island.wp_category_id}&_embed"
    wp_posts = get_wp_posts(WP_API_URL)
    
    context = {
        'island': island,
        'islands' : Island.objects.all(),
        "wp_post": wp_post,
        "wp_posts": wp_posts,
    }

    # Build the template path dynamically
    return render(request, 'core/views/guide_detail.html', context)





# Importing from .xlsx file - debug
# Importing from .xlsx file - debug
# Importing from .xlsx file - debug
def to_bool(value):
    return str(value).strip().lower() in ["true", "1", "yes"]


def import_view(request):
    path = 'core/bookings.xlsx'

    wb = load_workbook(path)
    sheet = wb.active

    # Get headers
    headers = [cell.value for cell in sheet[1]]

    for row in sheet.iter_rows(min_row=2, values_only=True):
        data = dict(zip(headers, row))

        try:
            # ISLAND
            island_name = (data.get("island") or "").strip()
            island, _ = Island.objects.get_or_create(name=island_name)

            # BOOKING (prevent duplicates using fh_id)
            booking, _ = Booking.objects.get_or_create(
                fh_id=data.get("fh_id"),
                defaults={
                    "title": data.get("title", ""),
                    "company_name": data.get("company_name", ""),
                    "company_rating": data.get("company_rating") or 0,
                    "company_reviews": data.get("company_reviews") or 0,
                    "city": data.get("city", ""),
                    "island": island,
                    "details": data.get("details", ""),
                    "duration": data.get("duration", ""),
                    "price": data.get("price") or 0,
                    "is_promo": to_bool(data.get("is_promo")),
                    "promo_amount": data.get("promo_amount") or 0,
                    "promo_code": data.get("promo_code", ""),
                    "is_public": to_bool(data.get("is_public")),
                    "is_popular": to_bool(data.get("is_popular")),
                    "is_pinned": to_bool(data.get("is_pinned")),
                    "referral_link": data.get("referral_link", ""),
                    "image_URL": data.get("image_URL", ""),
                }
            )

            # TAGS (handles: "Boat, Whale Watch")
            tags_string = data.get("tags", "")
            if tags_string:
                tag_names = [tag.strip() for tag in str(tags_string).split(",")]

                tag_objects = []
                for tag_name in tag_names:
                    if tag_name:
                        category, _ = Category.objects.get_or_create(name=tag_name)
                        tag_objects.append(category)

                booking.tags.set(tag_objects)

        except Exception as e:
            print(f"Skipping row due to error: {e}")

    return HttpResponse("Import complete ✅")

