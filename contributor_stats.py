import os
import requests
import argparse
from datetime import datetime

API_URL = "https://api.github.com/graphql"


# === QUERY BUILDER ===
def build_query(org, repo, cursor=None):
    """Build the GraphQL query for fetching merged PRs."""
    after_clause = f', after: "{cursor}"' if cursor else ""
    return f"""
    query {{
      repository(owner: "{org}", name: "{repo}") {{
        pullRequests(
          first: 50
          states: MERGED
          orderBy: {{ field: CREATED_AT, direction: DESC }}
          {after_clause}
        ) {{
          nodes {{
            author {{
              login
            }}
            createdAt
          }}
          pageInfo {{
            hasNextPage
            endCursor
          }}
        }}
      }}
    }}
    """


# === API CALL ===
def execute_query(query, headers):
    """Send the GraphQL query to GitHub API and return JSON response."""
    response = requests.post(API_URL, json={"query": query}, headers=headers)
    data = response.json()
    if "errors" in data:
        raise Exception(f"GraphQL Error: {data['errors']}")
    return data


# === DATE FILTER ===
def is_within_date_range(created_at, start_date, end_date):
    """Check if PR createdAt is within the given date range."""
    created = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
    start = datetime.fromisoformat(start_date.replace("Z", "+00:00"))
    end = datetime.fromisoformat(end_date.replace("Z", "+00:00"))
    return start <= created <= end


# === DATA EXTRACTION ===
def extract_pr_authors(pr_nodes, start_date, end_date):
    """Extract PR authors for PRs in date range and count merges."""
    pr_counts = {}
    for pr in pr_nodes:
        if not is_within_date_range(pr["createdAt"], start_date, end_date):
            continue
        author = pr["author"]["login"] if pr["author"] else None
        if author:
            pr_counts[author] = pr_counts.get(author, 0) + 1
    return pr_counts


# === PAGINATION HANDLER ===
def fetch_all_prs(org, repo, start_date, end_date, headers):
    """Fetch all merged PRs for the given date range and aggregate counts."""
    cursor = None
    aggregated_counts = {}

    while True:
        query = build_query(org, repo, cursor)
        data = execute_query(query, headers)
        pr_data = data["data"]["repository"]["pullRequests"]

        # Aggregate PR counts for PRs in date range
        batch_counts = extract_pr_authors(pr_data["nodes"], start_date, end_date)
        for author, count in batch_counts.items():
            aggregated_counts[author] = aggregated_counts.get(author, 0) + count

        # Check pagination
        if pr_data["pageInfo"]["hasNextPage"]:
            cursor = pr_data["pageInfo"]["endCursor"]
        else:
            break

    return aggregated_counts


# === OUTPUT ===
def print_leaderboard(pr_counts):
    """Print the leaderboard sorted by number of merged PRs."""
    sorted_counts = sorted(pr_counts.items(), key=lambda x: x[1], reverse=True)
    print("\n=== Contributor Leaderboard ===")
    for author, count in sorted_counts:
        print(f"{author}: {count} merged PRs")


# === MAIN ===
if __name__ == "__main__":
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Generate GitHub PR leaderboard.")
    parser.add_argument("--org", required=True, help="GitHub organisation or user name (owner)")
    parser.add_argument("--repo", required=True, help="GitHub repository name")
    parser.add_argument("--start", required=True, help="Start date (ISO format: YYYY-MM-DDTHH:MM:SSZ)")
    parser.add_argument("--end", required=True, help="End date (ISO format: YYYY-MM-DDTHH:MM:SSZ)")
    args = parser.parse_args()

    # Read token from environment
    github_token = os.getenv("GITHUB_TOKEN")
    if not github_token:
        raise EnvironmentError("GITHUB_TOKEN environment variable is not set.")

    headers = {"Authorization": f"Bearer {github_token}"}

    try:
        pr_counts = fetch_all_prs(args.org, args.repo, args.start, args.end, headers)
        print_leaderboard(pr_counts)
    except Exception as e:
        print(f"Error: {e}")
