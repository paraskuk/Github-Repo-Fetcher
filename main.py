import os
import requests
import logging
from collections import defaultdict
import sys
import hvac  # Ensure hvac is installed: pip install hvac

# Configure logging
logging.basicConfig(level=logging.WARNING, format='%(asctime)s - %(levelname)s - %(message)s')
def get_vault_client():
    """
    Initializes and returns a Vault client.
    """
    vault_addr = os.getenv('VAULT_ADDR', 'http://127.0.0.1:8200')  # Use http
    vault_token = os.getenv('VAULT_TOKEN')

    if not vault_token:
        logging.error("VAULT_TOKEN environment variable not set.")
        sys.exit(1)

    client = hvac.Client(
        url=vault_addr,
        token=vault_token,
        verify=False  # Disable SSL verification for HTTP
    )

    if not client.is_authenticated():
        logging.error("Unable to authenticate to Vault.")
        sys.exit(1)

    return client

def get_github_token(client):
    """
    Retrieves the GitHub token from Vault.

    :param client: Authenticated Vault client
    :return: GitHub token as a string
    """
    try:
        secret = client.secrets.kv.v2.read_secret_version(path='github', raise_on_deleted_version=True)
        token = secret['data']['data']['token']
        return token
    except Exception as e:
        logging.error(f"Error retrieving GitHub token from Vault: {e}")
        sys.exit(1)

def get_github_user_profile(username, token=None):
    """
    Fetches the GitHub user profile information.

    :param username: GitHub username
    :param token: Personal access token (optional)
    :return: JSON response of user profile
    """
    url = f"https://api.github.com/users/{username}"
    headers = {}
    if token:
        headers['Authorization'] = f'token {token}'

    response = requests.get(url, headers=headers)  # SSL verification not needed here
    if response.status_code == 200:
        return response.json()
    else:
        logging.error(f"Failed to fetch user profile: {response.status_code} - {response.text}")
        sys.exit(1)

def get_github_user_repos(username, token=None):
    """
    Fetches all public repositories of the user.

    :param username: GitHub username
    :param token: Personal access token (optional)
    :return: List of repository JSON objects
    """
    repos = []
    page = 1
    per_page = 100  # GitHub allows up to 100 per page

    headers = {}
    if token:
        headers['Authorization'] = f'token {token}'

    while True:
        url = f"https://api.github.com/users/{username}/repos?page={page}&per_page={per_page}"
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            page_repos = response.json()
            if not page_repos:
                break
            repos.extend(page_repos)
            page += 1
        else:
            logging.error(f"Failed to fetch repositories: {response.status_code} - {response.text}")
            sys.exit(1)
    return repos

def validate_repository_access(repo_api_url, token=None):
    """
    Validates if the repository is accessible.

    :param repo_api_url: API URL of the repository
    :param token: Personal access token (optional)
    :return: Boolean indicating access
    """
    headers = {}
    if token:
        headers['Authorization'] = f'token {token}'

    response = requests.get(repo_api_url)
    if response.status_code == 200:
        return True
    else:
        logging.error(f"Repository not accessible: {repo_api_url} - {response.status_code} - {response.text}")
        return False

def get_repo_languages(repo_languages_url, token=None):
    """
    Fetches the programming languages used in a repository.

    :param repo_languages_url: API URL of the repository's languages
    :param token: Personal access token (optional)
    :return: Dictionary with languages and bytes of code
    """
    headers = {}
    if token:
        headers['Authorization'] = f'token {token}'

    response = requests.get(repo_languages_url)
    if response.status_code == 200:
        return response.json()
    else:
        logging.error(f"Failed to fetch languages for repo {repo_languages_url}: {response.status_code} - {response.text}")
        return {}

def aggregate_languages(repos, token=None):
    """
    Aggregates languages used across all repositories.

    :param repos: List of repository JSON objects
    :param token: Personal access token (optional)
    :return: Dictionary with languages and total bytes of code
    """
    language_totals = defaultdict(int)
    for repo in repos:
        repo_api_url = repo.get('url')
        repo_name = repo.get('name')

        if not repo_api_url or not repo_name:
            logging.warning(f"Skipping repository with missing data: {repo}")
            continue

        if not validate_repository_access(repo_api_url, token):
            logging.warning(f"Skipping inaccessible repository: {repo_name}")
            continue

        languages = get_repo_languages(repo['languages_url'], token)
        if languages:
            for language, bytes_of_code in languages.items():
                language_totals[language] += bytes_of_code
        else:
            logging.warning(f"No languages found for repository: {repo_name}")
    return dict(language_totals)

def main():
    import argparse

    parser = argparse.ArgumentParser(description="Fetch GitHub user profile and languages used.")
    parser.add_argument("username", help="GitHub username")
    args = parser.parse_args()
    username = args.username

    # Initialize Vault client
    client = get_vault_client()

    # Retrieve GitHub token from Vault
    token = get_github_token(client)

    print(f"Fetching profile for user: {username}")
    profile = get_github_user_profile(username, token)

    # Display some profile information
    print("\n=== User Profile ===")
    print(f"Name: {profile.get('name')}")
    print(f"Bio: {profile.get('bio')}")
    print(f"Location: {profile.get('location')}")
    print(f"Public Repos: {profile.get('public_repos')}")
    print(f"Followers: {profile.get('followers')}")
    print(f"Following: {profile.get('following')}")
    print(f"Profile URL: {profile.get('html_url')}")

    print("\nFetching repositories...")
    repos = get_github_user_repos(username, token)
    print(f"Total Public Repositories: {len(repos)}")

    print("\nAggregating languages used across repositories...")
    languages = aggregate_languages(repos, token)

    print("\n=== Languages Used ===")
    if languages:
        # Sort languages by bytes of code in descending order
        sorted_languages = sorted(languages.items(), key=lambda item: item[1], reverse=True)
        for language, bytes_of_code in sorted_languages:
            print(f"{language}: {bytes_of_code} bytes")
    else:
        print("No languages found.")

if __name__ == "__main__":
    main()
