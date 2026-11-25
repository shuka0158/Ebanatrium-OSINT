"""Data Extractor - Fetch ALL profile information from discovered accounts"""
import requests
from bs4 import BeautifulSoup
import json
import re
import hashlib
from ..core import Module

class DataExtractor(Module):
    name = "data_extractor"
    title = "Profile Data Extractor"
    category = "Intelligence"
    description = "Extract images, names, bios, contact info, hashes from profiles"
    accepts = ["account", "url"]

    def run(self, ent, ctx):
        """Extract all data from account URLs"""

        if ent.type == "url":
            url = ent.value
        else:
            url = ent.value

        ctx.log(f"Extracting data from: {url}", "info")

        try:
            resp = requests.get(url, timeout=10, allow_redirects=True)
            if resp.status_code != 200:
                ctx.log(f"Cannot fetch: HTTP {resp.status_code}", "warn")
                return

            soup = BeautifulSoup(resp.text, 'html.parser')

            # Extract different data types
            self._extract_images(soup, url, ent, ctx)
            self._extract_text_data(soup, url, ent, ctx)
            self._extract_contact_info(soup, url, ent, ctx)
            self._extract_metadata(soup, url, resp, ent, ctx)
            self._extract_links(soup, url, ent, ctx)

        except requests.exceptions.Timeout:
            ctx.log("Request timeout", "warn")
        except Exception as e:
            ctx.log(f"Extraction error: {str(e)[:100]}", "error")

    def _extract_images(self, soup, url, ent, ctx):
        """Extract profile images, avatars, photos"""
        ctx.log("Extracting images...", "info")

        # Find all images
        img_tags = soup.find_all('img')
        image_count = 0

        for img in img_tags[:20]:  # Limit to first 20 images
            src = img.get('src', '')
            alt = img.get('alt', '')

            if src:
                # Make URL absolute
                if src.startswith('/'):
                    from urllib.parse import urljoin
                    src = urljoin(url, src)

                image_count += 1
                ctx.emit("image",
                    f"Image: {alt or 'Unknown'[:50]}",
                    src,
                    {"source": url, "alt": alt, "title": img.get('title', '')},
                    rel="profile_image")

        ctx.log(f"Found {image_count} images", "info")

    def _extract_text_data(self, soup, url, ent, ctx):
        """Extract names, bios, descriptions, text content"""
        ctx.log("Extracting text data...", "info")

        # Get page title
        title = soup.find('title')
        if title:
            ctx.emit("text",
                f"Page Title: {title.string[:100]}",
                title.string,
                {"type": "page_title", "source": url},
                rel="profile_text")

        # Extract meta descriptions
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if meta_desc:
            desc = meta_desc.get('content', '')
            ctx.emit("text",
                f"Bio/Description: {desc[:100]}",
                desc,
                {"type": "meta_description", "source": url},
                rel="profile_bio")

        # Extract h1-h3 headings (usually contain name/main info)
        for heading in soup.find_all(['h1', 'h2', 'h3'])[:10]:
            text = heading.get_text().strip()
            if text and len(text) < 200:
                ctx.emit("text",
                    f"Heading: {text}",
                    text,
                    {"type": "heading", "source": url},
                    rel="profile_heading")

        # Extract profile/bio text
        bio_patterns = ['about', 'bio', 'profile', 'description', 'summary']
        for section in soup.find_all(['div', 'section', 'p']):
            class_attr = section.get('class', [])
            class_str = ' '.join(class_attr).lower()

            if any(pattern in class_str for pattern in bio_patterns):
                text = section.get_text().strip()
                if text and 50 < len(text) < 1000:
                    ctx.emit("text",
                        f"Bio: {text[:80]}...",
                        text,
                        {"type": "profile_bio", "source": url},
                        rel="profile_biography")
                    break

    def _extract_contact_info(self, soup, url, ent, ctx):
        """Extract emails, phones, social links, contact info"""
        ctx.log("Extracting contact info...", "info")

        page_text = soup.get_text()

        # Find emails
        emails = re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', page_text)
        for email in set(emails)[:10]:
            ctx.emit("email",
                f"Email: {email}",
                email,
                {"source": url, "confidence": "medium"},
                rel="contact_email")
            ctx.log(f"Found email: {email}", "info")

        # Find phone numbers
        phones = re.findall(r'[\+]?[(]?[0-9]{3}[)]?[-\s\.]?[0-9]{3}[-\s\.]?[0-9]{4,6}', page_text)
        for phone in set(phones)[:5]:
            ctx.emit("phone",
                f"Phone: {phone}",
                phone,
                {"source": url, "confidence": "medium"},
                rel="contact_phone")
            ctx.log(f"Found phone: {phone}", "info")

        # Find social links
        social_patterns = {
            'twitter': r'twitter\.com/[\w]+',
            'github': r'github\.com/[\w-]+',
            'linkedin': r'linkedin\.com/in/[\w-]+',
            'instagram': r'instagram\.com/[\w.]+',
            'facebook': r'facebook\.com/[\w.]+',
        }

        for social, pattern in social_patterns.items():
            matches = re.findall(pattern, page_text, re.IGNORECASE)
            for match in set(matches)[:3]:
                ctx.emit("account",
                    f"{social.capitalize()}: {match}",
                    f"https://{match}",
                    {"platform": social, "source": url},
                    rel="linked_account")

    def _extract_metadata(self, soup, url, resp, ent, ctx):
        """Extract metadata, hashes, codes"""
        ctx.log("Extracting metadata...", "info")

        # Get page hash (fingerprint)
        page_hash_md5 = hashlib.md5(resp.text.encode()).hexdigest()
        page_hash_sha256 = hashlib.sha256(resp.text.encode()).hexdigest()

        ctx.emit("hash",
            f"Page MD5: {page_hash_md5[:16]}...",
            page_hash_md5,
            {"type": "md5", "source": url, "purpose": "content_fingerprint"},
            rel="page_hash")

        ctx.emit("hash",
            f"Page SHA256: {page_hash_sha256[:16]}...",
            page_hash_sha256,
            {"type": "sha256", "source": url, "purpose": "content_fingerprint"},
            rel="page_hash")

        # Extract meta keywords
        meta_keywords = soup.find('meta', attrs={'name': 'keywords'})
        if meta_keywords:
            keywords = meta_keywords.get('content', '')
            ctx.emit("text",
                f"Keywords: {keywords[:100]}",
                keywords,
                {"type": "meta_keywords", "source": url},
                rel="profile_keywords")

        # Extract all links on page
        links = soup.find_all('a', href=True)
        ctx.log(f"Found {len(links)} links on page", "info")

        # Get page information
        ctx.emit("text",
            f"Page Info: {len(resp.text)} bytes, {len(links)} links",
            json.dumps({"size": len(resp.text), "links": len(links), "url": url}),
            {"type": "page_metrics", "source": url},
            rel="page_info")

    def _extract_links(self, soup, url, ent, ctx):
        """Extract and categorize all links"""
        ctx.log("Extracting links...", "info")

        links = soup.find_all('a', href=True)
        external_links = 0

        for link in links[:30]:  # Limit to first 30 links
            href = link.get('href', '')
            text = link.get_text().strip()[:100]

            if href.startswith('http'):
                if url not in href:  # External link
                    external_links += 1
                    ctx.emit("url",
                        f"Link: {text or href[:50]}",
                        href,
                        {"source": url, "text": text},
                        rel="external_link")

        ctx.log(f"Found {external_links} external links", "info")
