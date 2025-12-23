import os
import requests
import argparse
from datetime import datetime

API_URL = "https://api.github.com/graphql"


# === QUERY BUILDER ===
def build_query(org, repo, cursor=None):
    """Build the GraphQL query for fetching PR reviews."""
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
            number
            createdAt
            reviews(first: 100) {{
              nodes {{
                author {{
                  login
                }}
                state
              }}
            }}
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
def extract_reviews(pr_nodes, start_date, end_date):
    """Extract review data and aggregate counts per reviewer for PRs in date range."""
    review_stats = {}
    for pr in pr_nodes:
        if not is_within_date_range(pr["createdAt"], start_date, end_date):
            continue
        for review in pr["reviews"]["nodes"]:
            reviewer = review["author"]["login"]
            state = review["state"]  # APPROVED, COMMENTED, CHANGES_REQUESTED
            if reviewer:
                if reviewer not in review_stats:
                    review_stats[reviewer] = {"approvals": 0, "comments": 0, "changes_requested": 0}
                if state == "APPROVED":
                    review_stats[reviewer]["approvals"] += 1
                elif state == "CHANGES_REQUESTED":
                    review_stats[reviewer]["changes_requested"] += 1
                else:
                    review_stats[reviewer]["comments"] += 1
    return review_stats


# === PAGINATION HANDLER ===
def fetch_all_reviews(org, repo, start_date, end_date, headers):
    """Fetch all PR reviews for the given date range and aggregate stats."""
    cursor = None
    aggregated_stats = {}

    while True:
        query = build_query(org, repo, cursor)
        data = execute_query(query, headers)
        pr_data = data["data"]["repository"]["pullRequests"]

        # Aggregate reviews for PRs in date range
        batch_stats = extract_reviews(pr_data["nodes"], start_date, end_date)
        for reviewer, counts in batch_stats.items():
            if reviewer not in aggregated_stats:
                aggregated_stats[reviewer] = {"approvals": 0, "comments": 0, "changes_requested": 0}
            aggregated_stats[reviewer]["approvals"] += counts["approvals"]
            aggregated_stats[reviewer]["comments"] += counts["comments"]
            aggregated_stats[reviewer]["changes_requested"] += counts["changes_requested"]

        # Check pagination
        if pr_data["pageInfo"]["hasNextPage"]:
            cursor = pr_data["pageInfo"]["endCursor"]
        else:
            break

    return aggregated_stats


# === OUTPUT ===
def print_leaderboard(stats):
    """Print the leaderboard sorted by total reviews."""
    sorted_stats = sorted(stats.items(), key=lambda x: (x[1]["approvals"] + x[1]["comments"] + x[1]["changes_requested"]), reverse=True)
    print("\n=== Review Leaderboard ===")
    for reviewer, counts in sorted_stats:
        total = counts["approvals"] + counts["comments"] + counts["changes_requested"]
        print(f"{reviewer}: {total} reviews (Approvals: {counts['approvals']}, Comments: {counts['comments']}, Changes Requested: {counts['changes_requested']})")


# === MAIN ===
if __name__ == "__main__":
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Generate GitHub PR review stats.")
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
        stats = fetch_all_reviews(args.org, args.repo, args.start, args.end, headers)
        print_leaderboard(stats)
    except Exception as e:
        print(f"Error: {e}")
