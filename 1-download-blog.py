#!/usr/bin/env python3
"""
Script to download all blog posts from jouninlappujuoksut.blogspot.com in chronological order
and save them as markdown files in the blog/ folder.

NOTE: this is AI generated code
"""

import os
import re
import requests
from bs4 import BeautifulSoup
import html2text
from datetime import datetime
import time
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Constants
BLOG_URL = "https://jouninlappujuoksut.blogspot.com/"
BLOG_DIR = "blog"
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"

# Initialize HTML to Markdown converter
h2t = html2text.HTML2Text()
h2t.ignore_links = False
h2t.ignore_images = True
h2t.ignore_tables = False
h2t.body_width = 0  # No wrapping

def get_soup(url):
    """Fetch a URL and return a BeautifulSoup object."""
    headers = {"User-Agent": USER_AGENT}
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return BeautifulSoup(response.text, "html.parser")
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching {url}: {e}")
        return None

def get_all_post_urls(base_url):
    """Get URLs of all blog posts in chronological order."""
    all_post_urls = []
    next_page_url = base_url

    while next_page_url:
        logger.info(f"Fetching post list from: {next_page_url}")
        soup = get_soup(next_page_url)
        if not soup:
            break

        # Find all blog post links on the current page
        post_links = soup.select(".post-title a")
        for link in post_links:
            post_url = link.get("href")
            if post_url:
                all_post_urls.append(post_url)

        # Find the "Older Posts" link for pagination
        older_posts = soup.select("a.blog-pager-older-link")
        next_page_url = older_posts[0].get("href") if older_posts else None

        # Be nice to the server
        time.sleep(1)

    # Reverse the list to get chronological order (oldest first)
    all_post_urls.reverse()
    return all_post_urls

def extract_post_date(soup, url):
    """Extract the post date from the blog post."""
    date_element = soup.select_one("time.published")
    if not date_element:
        return None

    date_str = date_element.text.strip()

    # Try different date formats (Blogspot might use different formats)
    date_formats = [
        "%A, %B %d, %Y",  # Monday, January 01, 2023
        "%A, %d %B %Y",   # Monday, 01 January 2023
        "%B %d, %Y",      # March 31, 2025
        "%d.%m.%Y",       # 01.01.2023 (Finnish format)
        "%d.%m.%Y %H:%M"  # 01.01.2023 12:00 (Finnish format with time)
    ]

    for date_format in date_formats:
        try:
            return datetime.strptime(date_str, date_format)
        except ValueError:
            continue

    raise Exception(f"Failed to parse date for {url}")

def extract_post_content(soup):
    """Extract the post title and content."""
    title_element = soup.select_one(".post-title")
    title = title_element.text.strip() if title_element else "Untitled Post"

    # Extract the main content
    content_element = soup.select_one(".post-body")
    if not content_element:
        return title, ""

    # Convert HTML to Markdown
    content_html = str(content_element)
    content_markdown = h2t.handle(content_html)

    return title, content_markdown

def save_post_as_markdown(post_url, date, title, content):
    """Save the post as a markdown file with a date-based filename."""
    if not os.path.exists(BLOG_DIR):
        os.makedirs(BLOG_DIR)

    # Create a filename based on the date (YYYY-MM-DD-title.md)
    if date:
        date_str = date.strftime("%Y-%m-%d")
        # Create a slug from the title
        slug = re.sub(r'[^\w\s-]', '', title.lower())
        slug = re.sub(r'[\s-]+', '-', slug)
        filename = f"{date_str}-{slug}.md"
    else:
        raise Exception(f"Invalid date {date}")

    filepath = os.path.join(BLOG_DIR, filename)

    # Create markdown content with frontmatter
    frontmatter = f"""---
title: "{title}"
date: {date.strftime('%Y-%m-%d') if date else 'Unknown'}
original_url: {post_url}
---

"""
    markdown_content = frontmatter + content

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(markdown_content)

    return filepath

def main():
    """Main function to download all blog posts."""
    logger.info(f"Starting to download blog posts from {BLOG_URL}")

    # Get all post URLs
    post_urls = get_all_post_urls(BLOG_URL)
    logger.info(f"Found {len(post_urls)} blog posts")

    # Process each post
    for i, post_url in enumerate(post_urls, 1):
        logger.info(f"Processing post {i}/{len(post_urls)}: {post_url}")

        soup = get_soup(post_url)
        if not soup:
            continue

        date = extract_post_date(soup, post_url)
        title, content = extract_post_content(soup)

        filepath = save_post_as_markdown(post_url, date, title, content)
        logger.info(f"Saved post to {filepath}")

        # Be nice to the server
        time.sleep(1)

    logger.info("Finished downloading all blog posts")

if __name__ == "__main__":
    main()
