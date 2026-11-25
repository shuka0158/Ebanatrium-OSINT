"""Auto Data Fetcher - Automatically extract data from verified accounts"""
import requests
from bs4 import BeautifulSoup
import re
import json
from ..core import Module

class AutoDataFetcher(Module):
    name = "auto_data_fetcher"
    title = "Auto Data Fetcher"
    category = "Intelligence"
    description = "Automatically fetch & extract data from discovered profiles"
    accepts = ["account"]
    enricher = True  # Runs on every new account entity

    def run(self, ent, ctx):
        """Auto-fetch data from account URL"""

        url = ent.value
        platform = ent.data.get("platform", "unknown") if ent.data else "unknown"
        username = ent.data.get("username", "") if ent.data else ""

        ctx.log(f"Auto-fetching data from {platform}: {username}", "info")

        try:
            # Fetch page
            resp = requests.get(url, timeout=8, allow_redirects=True)
            if resp.status_code != 200:
                ctx.log(f"Cannot fetch: HTTP {resp.status_code}", "warn")
                return

            soup = BeautifulSoup(resp.text, 'html.parser')

            # Platform-specific extraction
            if "docker" in platform.lower():
                self._extract_docker(soup, url, username, ent, ctx)
            elif "gitlab" in platform.lower():
                self._extract_gitlab(soup, url, username, ent, ctx)
            elif "github" in platform.lower():
                self._extract_github(soup, url, username, ent, ctx)
            elif "tiktok" in platform.lower():
                self._extract_tiktok(soup, url, username, ent, ctx)
            elif "pinterest" in platform.lower():
                self._extract_pinterest(soup, url, username, ent, ctx)
            else:
                self._extract_generic(soup, url, username, ent, ctx)

        except requests.exceptions.Timeout:
            ctx.log("Timeout fetching profile", "warn")
        except Exception as e:
            ctx.log(f"Error: {str(e)[:100]}", "error")

    def _extract_docker(self, soup, url, username, ent, ctx):
        """Extract from Docker Hub profile"""
        ctx.log("Extracting Docker Hub profile data...", "info")

        # Docker Hub shows user info
        try:
            # Look for user info in page
            user_info = soup.find('div', class_='user-info')
            if user_info:
                profile_name = user_info.get_text()
                ctx.emit("text", f"Docker Profile: {profile_name[:100]}", profile_name[:200],
                    {"type": "docker_profile", "source": url}, rel="profile_data")

            # Count repositories
            repo_count = len(soup.find_all('a', class_='repo-link'))
            ctx.emit("text", f"Docker Repositories: {repo_count}", str(repo_count),
                {"type": "docker_repo_count", "source": url}, rel="profile_stats")

        except Exception as e:
            ctx.log(f"Docker extraction error: {str(e)[:50]}", "warn")

    def _extract_gitlab(self, soup, url, username, ent, ctx):
        """Extract from GitLab profile"""
        ctx.log("Extracting GitLab profile data...", "info")

        try:
            # Get full name
            name_elem = soup.find('h1')
            if name_elem:
                full_name = name_elem.get_text().strip()
                ctx.emit("text", f"GitLab Name: {full_name}", full_name,
                    {"type": "gitlab_name", "source": url}, rel="profile_data")

            # Get bio
            bio_elem = soup.find('p', class_='bio')
            if bio_elem:
                bio = bio_elem.get_text().strip()
                ctx.emit("text", f"GitLab Bio: {bio[:100]}", bio,
                    {"type": "gitlab_bio", "source": url}, rel="profile_bio")

            # Count projects
            projects = soup.find_all('a', class_='project-link')
            ctx.emit("text", f"GitLab Projects: {len(projects)}", str(len(projects)),
                {"type": "gitlab_project_count", "source": url}, rel="profile_stats")

        except Exception as e:
            ctx.log(f"GitLab extraction error: {str(e)[:50]}", "warn")

    def _extract_github(self, soup, url, username, ent, ctx):
        """Extract from GitHub profile"""
        ctx.log("Extracting GitHub profile data...", "info")

        try:
            # Get full name
            name = soup.find('span', class_='p-name')
            if name:
                full_name = name.get_text().strip()
                ctx.emit("text", f"GitHub Name: {full_name}", full_name,
                    {"type": "github_name", "source": url}, rel="profile_data")

            # Get bio
            bio = soup.find('div', class_='p-note')
            if bio:
                bio_text = bio.get_text().strip()
                ctx.emit("text", f"GitHub Bio: {bio_text}", bio_text,
                    {"type": "github_bio", "source": url}, rel="profile_bio")

            # Get location, company, links
            location = soup.find('span', class_='p-label')
            if location:
                ctx.emit("text", f"Location: {location.get_text().strip()}", location.get_text().strip(),
                    {"type": "github_location", "source": url}, rel="profile_location")

        except Exception as e:
            ctx.log(f"GitHub extraction error: {str(e)[:50]}", "warn")

    def _extract_tiktok(self, soup, url, username, ent, ctx):
        """Extract from TikTok profile"""
        ctx.log("Extracting TikTok profile data...", "info")

        try:
            # Get account name
            page_text = soup.get_text()
            if "followers" in page_text.lower():
                followers_match = re.search(r'(\d+[.K]?)\s*followers', page_text, re.IGNORECASE)
                if followers_match:
                    ctx.emit("text", f"TikTok Followers: {followers_match.group(1)}", followers_match.group(1),
                        {"type": "tiktok_followers", "source": url}, rel="profile_stats")

            # Try to get bio from meta tags
            og_desc = soup.find('meta', attrs={'property': 'og:description'})
            if og_desc:
                desc = og_desc.get('content', '')
                ctx.emit("text", f"TikTok Bio: {desc[:100]}", desc,
                    {"type": "tiktok_bio", "source": url}, rel="profile_bio")

        except Exception as e:
            ctx.log(f"TikTok extraction error: {str(e)[:50]}", "warn")

    def _extract_pinterest(self, soup, url, username, ent, ctx):
        """Extract from Pinterest profile"""
        ctx.log("Extracting Pinterest profile data...", "info")

        try:
            # Get profile name
            name = soup.find('h1')
            if name:
                profile_name = name.get_text().strip()
                ctx.emit("text", f"Pinterest Name: {profile_name}", profile_name,
                    {"type": "pinterest_name", "source": url}, rel="profile_data")

            # Count boards
            boards = soup.find_all('div', class_='board')
            ctx.emit("text", f"Pinterest Boards: {len(boards)}", str(len(boards)),
                {"type": "pinterest_board_count", "source": url}, rel="profile_stats")

            # Get bio
            bio = soup.find('p', class_='bio')
            if bio:
                bio_text = bio.get_text().strip()
                ctx.emit("text", f"Pinterest Bio: {bio_text[:100]}", bio_text,
                    {"type": "pinterest_bio", "source": url}, rel="profile_bio")

        except Exception as e:
            ctx.log(f"Pinterest extraction error: {str(e)[:50]}", "warn")

    def _extract_generic(self, soup, url, username, ent, ctx):
        """Generic data extraction for unknown platforms"""
        ctx.log("Extracting generic profile data...", "info")

        try:
            # Get page title
            title = soup.find('title')
            if title:
                ctx.emit("text", f"Profile: {title.string[:100]}", title.string,
                    {"type": "page_title", "source": url}, rel="profile_data")

            # Get meta description
            desc = soup.find('meta', attrs={'name': 'description'})
            if desc:
                desc_text = desc.get('content', '')
                ctx.emit("text", f"Description: {desc_text[:100]}", desc_text,
                    {"type": "meta_description", "source": url}, rel="profile_bio")

            # Count images
            images = soup.find_all('img')
            ctx.log(f"Found {len(images)} images", "info")

            # Get first profile image
            if images:
                img_src = images[0].get('src', '')
                if img_src:
                    ctx.emit("image", f"Profile Image", img_src,
                        {"source": url, "type": "profile_pic"}, rel="profile_image")

        except Exception as e:
            ctx.log(f"Generic extraction error: {str(e)[:50]}", "warn")
