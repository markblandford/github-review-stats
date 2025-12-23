import requests

# === CONFIGURATION ===
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
if not GITHUB_TOKEN:
    raise EnvironmentError("GITHUB_TOKEN environment variable is not set.")

ORG_NAME = "your-org"
REPO_NAME = "your-repo"
START_DATE = "2025-01-01T00:00:00Z"
END_DATE = "2025-12-31T23:59:59Z"

API_URL = "https://api.github.com/graphql"
HEADERS = {"Authorization": f"Bearer {GITHUB_TOKEN}"}


# === QUERY BUILDER ===
def build_query(cursor=None):
    """Build the GraphQL query for fetching PR reviews."""
    after_clause = f', after: "{cursor}"' if cursor else ""
    return f"""
    query {{
      repository(owner: "{ORG_NAME}", name: "{REPO_NAME}") {{
        pullRequests(
          first: 50
          states: MERGED
          orderBy: {{ field: CREATED_AT, direction: DESC }}
          filterBy: {{
            createdAfter: "{START_DATE}"
            createdBefore: "{END_DATE}"
          }}
          {after_clause}
        ) {{
          nodes {{
            number
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
def execute_query(query):
    """Send the GraphQL query to GitHub API and return JSON response."""
    response = requests.post(API_URL, json={"query": query}, headers=HEADERS)
    data = response.json()
    if "errors" in data:
        raise Exception(f"GraphQL Error: {data['errors']}")
    return data


# === DATA EXTRACTION ===
def extract_reviews(pr_nodes):
    """Extract review data and aggregate counts per reviewer."""
    review_stats = {}
    for pr in pr_nodes:
        for review in pr["reviews"]["nodes"]:
            reviewer = review["author"]["login"]
            state = review["state"]  # APPROVED, COMMENTED, CHANGES_REQUESTED
            if reviewer:
                if reviewer not in review_stats:
                    review_stats[reviewer] = {"approvals": 0, "comments": 0}
                if state == "APPROVED":
                    review_stats[reviewer]["approvals"] += 1
                else:
                    review_stats[reviewer]["comments"] += 1
    return review_stats


# === PAGINATION HANDLER ===
def fetch_all_reviews():
    """Fetch all PR reviews for the given date range and aggregate stats."""
    cursor = None
    aggregated_stats = {}

    while True:
        query = build_query(cursor)
        data = execute_query(query)
        pr_data = data["data"]["repository"]["pullRequests"]

        # Aggregate reviews
        batch_stats = extract_reviews(pr_data["nodes"])
        for reviewer, counts in batch_stats.items():
            if reviewer not in aggregated_stats:
                aggregated_stats[reviewer] = {"approvals": 0, "comments": 0}
            aggregated_stats[reviewer]["approvals"] += counts["approvals"]
            aggregated_stats[reviewer]["comments"] += counts["comments"]

        # Check pagination
        if pr_data["pageInfo"]["hasNextPage"]:
            cursor = pr_data["pageInfo"]["endCursor"]
        else:
            break

    return aggregated_stats


# === OUTPUT ===
def print_leaderboard(stats):
    """Print the leaderboard sorted by total reviews."""
    sorted_stats = sorted(stats.items(), key=lambda x: (x[1]["approvals"] + x[1]["comments"]), reverse=True)
    print("\n=== Review Leaderboard for 2025 ===")
