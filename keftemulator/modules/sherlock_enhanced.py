"""Sherlock Enhanced - Find username across 100+ sites (REAL SHERLOCK TOOL)"""
import subprocess
import json
import re
import os
from ..core import Module

class SherlockEnhanced(Module):
    name = "sherlock_enhanced"
    title = "Username Finder (100+ Sites)"
    category = "People Search"
    description = "Search username across 100+ platforms using real Sherlock tool"
    accepts = ("username", "name", "person")
    external = True
    requires_tool = "sherlock"

    def run(self, ent, ctx):
        username = ent.value.strip()
        ctx.log(f"Running real Sherlock on: {username}", "info")

        try:
            # Run actual Sherlock tool
            result = subprocess.run(
                ["sherlock", username, "--timeout", "5", "--no-color"],
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode == 0:
                output = result.stdout
                # Parse real results from Sherlock output
                # Pattern: [+] Site: https://...
                matches = re.findall(r'\[\+\]\s+([^:]+):\s+(https?://[^\s]+)', output)

                found_count = 0
                for site, url in matches:
                    site = site.strip()
                    url = url.strip()

                    ctx.emit("account",
                        f"{site}: {username}",
                        url,
                        {"platform": site, "username": username, "verified": True, "source": "sherlock"},
                        rel="verified_account")

                    ctx.log(f"✅ VERIFIED: {site} - {url}", "info")
                    found_count += 1

                ctx.log(f"Sherlock found on {found_count} verified sites", "info")
            else:
                ctx.log(f"Sherlock error: {result.stderr[:200]}", "warn")

        except FileNotFoundError:
            ctx.log("Sherlock tool not installed", "error")
        except subprocess.TimeoutExpired:
            ctx.log("Sherlock search timed out", "warn")
        except Exception as e:
            ctx.log(f"Sherlock error: {str(e)[:100]}", "error")

