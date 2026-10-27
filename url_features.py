
import re
from urllib.parse import urlparse


def extract_url_features(url):
    # Add a scheme so urlparse can identify the domain
    if not url.lower().startswith(("http://", "https://")):
        url = "http://" + url

    parsed = urlparse(url)
    hostname = parsed.hostname or ""

    # Check whether the hostname is an IPv4 address
    is_ip_address = bool(
        re.fullmatch(r"(?:\d{1,3}\.){3}\d{1,3}", hostname)
    )

    # Count subdomains, excluding the main domain and suffix
    domain_parts = hostname.split(".")
    subdomain_count = max(0, len(domain_parts) - 2)

    return {
        "url_length": len(url),
        "uses_https": int(parsed.scheme == "https"),
        "dot_count": url.count("."),
        "digit_count": sum(char.isdigit() for char in url),
        "special_char_count": sum(
            url.count(char) for char in "@-?=&_%"
        ),
        "has_ip_address": int(is_ip_address),
        "subdomain_count": subdomain_count
    }