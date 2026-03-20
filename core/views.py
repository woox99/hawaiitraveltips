from urllib import response
from django.shortcuts import get_object_or_404, redirect, render

from core.models import *
from .util import *

from django.shortcuts import HttpResponse
from core.models import Booking, Island, Category
from openpyxl import load_workbook
from django.utils.text import slugify

from django.db.models import Q




def home(request):
    # Check if 'current_island' is in the session and render the island instead of the home page
    if 'current_island' in request.session:
        return redirect('core:island', island_slug=request.session['current_island_slug'])
    

    # Get 4 popular bookings for the island
    bookings = Booking.objects.filter(is_pinned=True, is_public=True)[:4]
    
    context = {
        'islands' : Island.objects.all().order_by('modified'),
        'bookings': bookings,
    }
    return render(request, 'core/home.html', context)


def island_view(request, island_slug):

    # Set the current island in the session if coming from the home page
    request.session['current_island_slug'] = island_slug
    island = get_object_or_404(Island, slug=island_slug)



    # Get 4 popular bookings for the island
    bookings = Booking.objects.filter(island=island, is_public=True, is_pinned=True)[:4]

    # WordPress.com REST API endpoint - Limit = 3
    WP_API_URL = f"https://public-api.wordpress.com/wp/v2/sites/team92d3a5e49bc-kctlm.wordpress.com/posts?categories={island.wp_category_id}&per_page=3&_embed"
    wp_posts = get_wp_posts(WP_API_URL)

    # back_url = f'www.hawaiitraveltips.com/{quote(island.slug)}/?page={page_obj.number}'



    context = {
        'island': island,
        'islands' : Island.objects.all().order_by('modified'),
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

    # Filter by category if category slug is provided in query params
    category_slug = request.GET.get('category', '')
    current_category = None
    if category_slug:
        for cat in Category.objects.all():
            if slugify(cat.name) == category_slug:
                current_category = cat
                break

    if current_category:
        bookings = Booking.objects.filter(island=island, is_public=True, tags=current_category).order_by("-is_pinned")
    elif request.GET.get('q'):
        query = request.GET.get('q')
        bookings = Booking.objects.filter(
            Q(title__icontains=query) |
            Q(city__icontains=query) |
            Q(details__icontains=query),
            island=island,
            is_public=True
        ).order_by("-is_pinned")
    else:
        bookings = Booking.objects.filter(island=island, is_public=True).order_by("-is_pinned")

    # Apply sorting based on query param
    sort_slug = request.GET.get('sort', '')
    if sort_slug == 'best-seller':
        bookings = bookings.order_by("is_popular")
    elif sort_slug == 'promo-code':
        bookings = bookings.order_by("-is_promo", "-promo_amount")
    elif sort_slug == 'price':
        bookings = bookings.order_by("price")
    elif sort_slug == 'title':
        bookings = bookings.order_by("title")



    # Pagination
    page_obj, page_range = paginate_bookings(bookings, request)

    # Get all categories that have visible bookings for this island
    categories = Category.objects.filter(bookings__island=island, bookings__is_public=True).distinct().order_by('name')
    
    # Get count of visible bookings for each category
    for cat in categories:
        # cat.visible_bookings_count = cat.bookings.filter(island=island).count
        cat.visible_bookings_count = cat.bookings.filter(island=island, is_public=True).count
        
    context = {
        'island': island,
        'islands' : Island.objects.all().order_by('modified'),
        'categories': categories,
        'current_category': current_category,
        'page_obj' : page_obj,
        'page_range': page_range,
        'bookings_count': bookings.count(),
        'total_bookings_count': Booking.objects.filter(island=island, is_public=True).count(),
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
        'islands' : Island.objects.all().order_by('modified'),
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
        'islands' : Island.objects.all().order_by('modified'),
        "wp_post": wp_post,
        "wp_posts": wp_posts,
    }

    # Build the template path dynamically
    return render(request, 'core/views/guide_detail.html', context)

def about_view(request):
    if 'current_island_slug' in request.session:
        island = get_object_or_404(Island, slug=request.session['current_island_slug'])

    context = {
        'island': island,
        'islands' : Island.objects.all().order_by('modified'),
    }
    return render(request, 'core/views/about.html', context)

def contact_view(request):
    if 'current_island_slug' in request.session:
        island = get_object_or_404(Island, slug=request.session['current_island_slug'])

    context = {
        'island': island,
        'islands' : Island.objects.all().order_by('modified'),
    }
    return render(request, 'core/views/contact.html', context)


def legal_view(request):
    if 'current_island_slug' in request.session:
        island = get_object_or_404(Island, slug=request.session['current_island_slug'])

    context = {
        'island': island,
        'islands' : Island.objects.all().order_by('modified'),
    }
    return render(request, 'core/views/legal.html', context)




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

