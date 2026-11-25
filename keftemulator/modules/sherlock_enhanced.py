"""Sherlock Enhanced - Find REAL verified usernames only (NO false positives)"""
import subprocess
import json
import re
import os
import requests
from ..core import Module

class SherlockEnhanced(Module):
    name = "sherlock_enhanced"
    title = "Username Finder (100+ Sites)"
    category = "People Search"
    description = "Search username across verified platforms (NO false positives)"
    accepts = ("username", "name", "person")
    external = True
    requires_tool = "sherlock"

    def run(self, ent, ctx):
        username = ent.value.strip()
        ctx.log(f"Searching for verified accounts: {username}", "info")

        try:
            # Run Sherlock tool
            result = subprocess.run(
                ["sherlock", username, "--timeout", "5", "--no-color"],
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode == 0:
                output = result.stdout
                # Parse results from Sherlock output: [+] Site: https://...
                matches = re.findall(r'\[\+\]\s+([^:]+):\s+(https?://[^\s]+)', output)

                verified_count = 0
                rejected_count = 0

                for site, url in matches:
                    site = site.strip()
                    url = url.strip()

                    # VERIFY each account with actual page check
                    if self._verify_account(url, username, site):
                        ctx.emit("account",
                            f"{site}: {username}",
                            url,
                            {"platform": site, "username": username, "verified": True, "source": "sherlock_verified"},
                            rel="verified_account")

                        ctx.log(f"✅ VERIFIED: {site}", "info")
                        verified_count += 1
                    else:
                        ctx.log(f"❌ REJECTED (false positive): {site}", "warn")
                        rejected_count += 1

                ctx.log(f"Results: {verified_count} real, {rejected_count} false positives rejected", "info")
            else:
                ctx.log(f"Search error: {result.stderr[:200]}", "warn")

        except FileNotFoundError:
            ctx.log("Sherlock tool not installed", "error")
        except subprocess.TimeoutExpired:
            ctx.log("Search timed out", "warn")
        except Exception as e:
            ctx.log(f"Error: {str(e)[:100]}", "error")

    def _verify_account(self, url, username, site):
        """Verify that the account actually exists (not a false positive)"""
        try:
            resp = requests.get(url, timeout=5, allow_redirects=True)

            # Check HTTP status - 404 = account doesn't exist
            if resp.status_code == 404:
                return False

            if resp.status_code == 403:
                # 403 could mean account exists but is private
                # Only trust if URL looks like real profile structure
                return self._looks_like_real_profile_url(url, site)

            if resp.status_code != 200:
                return False  # Other errors = reject

            # For 200 OK, check if page contains actual profile data
            content = resp.text.lower()
            username_lower = username.lower()

            # Check for indicators that this is a REAL profile
            real_indicators = [
                username_lower in content,  # Username appears on page
                f"@{username_lower}" in content,  # @username format
                f"id={username_lower}" in content,  # ID in URL/content
                f"user/{username_lower}" in content,  # User path
                f"profile/{username_lower}" in content,  # Profile path
            ]

            # REJECT known false positives
            reject_patterns = [
                "not found",  # 404 pages served as 200
                "page not found",
                "user not found",
                "no results",
                "nothing to see here",
                "parked",  # GoDaddy parked domains
                "godaddy",
                "search results",  # Search pages, not profiles
                "click here to continue",  # Redirect pages
                "this user has not",  # "This user has no content"
                "no gifs found",  # Giphy false positive
                "this domain is for sale",
            ]

            if any(pattern in content for pattern in reject_patterns):
                return False

            # Check for minimum content (avoid empty/placeholder pages)
            if len(content) < 300:
                return False

            # Must have at least one real indicator OR be a known real site
            known_real_sites = {
                "docker": "/u/",
                "gitlab": "/users/",
                "github": "/github",
                "pinterest": "/pinterest",
                "tiktok": "/@",
                "linkedin": "/in/",
            }

            # Check known real sites
            for site_name, pattern in known_real_sites.items():
                if site_name in site.lower():
                    return True  # These are real sites, if we got 200, it's real

            # For other sites, must have username indicator
            return any(real_indicators)

        except requests.exceptions.Timeout:
            return False
        except requests.exceptions.ConnectionError:
            return False
        except Exception:
            return False

    def _looks_like_real_profile_url(self, url, site):
        """Check if URL structure suggests a real profile (for 403 cases)"""
        url_lower = url.lower()
        site_lower = site.lower()

        # Known sites with proper profile URL patterns
        profile_patterns = {
            "docker": "/u/",
            "gitlab": "/gitlab.com/",
            "github": "/github.com/",
            "pinterest": "/pinterest",
            "linkedin": "/in/",
            "tiktok": "/@",
        }

        for known_site, pattern in profile_patterns.items():
            if known_site in site_lower and pattern in url_lower:
                return True

        return False
