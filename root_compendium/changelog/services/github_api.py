"""
Service for interacting with the GitHub REST API to fetch commits.
"""
import os
import requests
from typing import List, Dict, Any, Optional

GITHUB_API_URL = "https://api.github.com"

class GitHubAPIService:
    """
    Service for fetching commits from a GitHub repository using the REST API.
    """
    def __init__(self, token: Optional[str] = None):
        self.token = token or os.environ.get("GITHUB_API_TOKEN")
        if not self.token:
            raise ValueError("GitHub API token must be provided via argument or GITHUB_API_TOKEN env var.")
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"token {self.token}",
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "Django-Changelog-App"
        })

    def fetch_commits(self, owner: str, repo: str, per_page: int = 30, page: int = 1) -> List[Dict[str, Any]]:
        """
        Fetch recent commits from a GitHub repository.

        Args:
            owner (str): GitHub username or organization.
            repo (str): Repository name.
            per_page (int): Number of commits per page (max 100).
            page (int): Page number.

        Returns:
            List[Dict[str, Any]]: List of commit data dicts.
        """
        url = f"{GITHUB_API_URL}/repos/{owner}/{repo}/commits"
        params = {"per_page": per_page, "page": page}
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return response.json()
