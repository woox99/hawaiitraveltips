import requests
import re
import math
from datetime import datetime
from .models import *
from django.core.paginator import Paginator


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