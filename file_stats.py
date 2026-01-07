import os
import requests
import argparse
from datetime import datetime
from collections import defaultdict

API_URL = "https://api.github.com/graphql"

# === QUERY BUILDER ===
def build_prs_query(org, repo, cursor=None):
    """Build GraphQL query fetching PRs and up to 100 files per PR."""
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
            files(first: 100) {{
              nodes {{
                path
                additions
                deletions
              }}
              pageInfo {{
                hasNextPage
                endCursor
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
    created = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
    start = datetime.fromisoformat(start_date.replace("Z", "+00:00"))
    end = datetime.fromisoformat(end_date.replace("Z", "+00:00"))
    return start <= created <= end

# === DATA EXTRACTION ===
def process_pr_files(pr_node, file_pr_counts, file_change_counts, dir_pr_counts, dir_change_counts):
    """Given a single PR node, update file and directory stats.

    This function counts:
      - file_pr_counts[path]: number of PRs touching this file (counts each PR once per file)
      - file_change_counts[path]: sum of additions+deletions across PRs
      - dir_* for the immediate containing directory (os.path.dirname). Root files use '.'
    """
    seen_files_in_pr = set()

    files_conn = pr_node.get("files") or {}
    nodes = files_conn.get("nodes") or []

    for f in nodes:
        path = f.get("path")
        if not path:
            continue
        # Ensure per-PR per-file is counted once
        if path not in seen_files_in_pr:
            file_pr_counts[path] += 1
            seen_files_in_pr.add(path)

            # directory (immediate)
            dirname = os.path.dirname(path) or "."
            dir_pr_counts[dirname] += 1

        # additions/deletions may be None - default to 0
        adds = f.get("additions") or 0
        dels = f.get("deletions") or 0
        changes = adds + dels

        file_change_counts[path] += changes
        dirname = os.path.dirname(path) or "."
        dir_change_counts[dirname] += changes

# === PAGINATION HANDLER ===
def fetch_all_file_stats(org, repo, start_date, end_date, headers):
    """Fetch merged PRs in date range and aggregate file/directory stats.

    PRs that have more than 100 files (files.pageInfo.hasNextPage == True) are ignored and recorded.
    """
    cursor = None

    file_pr_counts = defaultdict(int)
    file_change_counts = defaultdict(int)
    dir_pr_counts = defaultdict(int)
    dir_change_counts = defaultdict(int)
    ignored_prs = []

    while True:
        query = build_prs_query(org, repo, cursor)
        data = execute_query(query, headers)
        pr_data = data["data"]["repository"]["pullRequests"]

        for pr in pr_data["nodes"]:
            if not is_within_date_range(pr["createdAt"], start_date, end_date):
                continue

            files_conn = pr.get("files") or {}
            files_page = files_conn.get("pageInfo") or {}
            if files_page.get("hasNextPage"):
                # Skip this PR entirely and record it
                ignored_prs.append({"number": pr.get("number"), "createdAt": pr.get("createdAt")})
                continue

            # process files for this PR
            process_pr_files(pr, file_pr_counts, file_change_counts, dir_pr_counts, dir_change_counts)

        if pr_data["pageInfo"]["hasNextPage"]:
            cursor = pr_data["pageInfo"]["endCursor"]
        else:
            break

    return {
        "file_pr_counts": file_pr_counts,
        "file_change_counts": file_change_counts,
        "dir_pr_counts": dir_pr_counts,
        "dir_change_counts": dir_change_counts,
        "ignored_prs": ignored_prs,
    }

# === OUTPUT ===
def print_top(mapping, top=20, label="Items"):
    print(f"\n=== Top {top} {label} ===")
    items = list(mapping.items())
    items.sort(key=lambda x: x[1], reverse=True)
    for i, (key, val) in enumerate(items[:top], start=1):
        print(f"{i}. {key}: {val}")

def print_leaderboards(stats, top=20, by="pr"):
    if by not in ("pr", "changes"):
        raise ValueError("by must be either 'pr' or 'changes'")

    if by == "pr":
        print_top(stats["file_pr_counts"], top=top, label="Files by PRs touched")
        print_top(stats["dir_pr_counts"], top=top, label="Directories by PRs touched")
    else:
        print_top(stats["file_change_counts"], top=top, label="Files by total changes")
        print_top(stats["dir_change_counts"], top=top, label="Directories by total changes")

# === MAIN ===
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate stats for files and directories changed in merged PRs.")
    parser.add_argument("--org", required=True, help="GitHub organisation or user name (owner)")
    parser.add_argument("--repo", required=True, help="GitHub repository name")
    parser.add_argument("--start", required=True, help="Start date (ISO format: YYYY-MM-DDTHH:MM:SSZ)")
    parser.add_argument("--end", required=True, help="End date (ISO format: YYYY-MM-DDTHH:MM:SSZ)")
    parser.add_argument("--top", type=int, default=20, help="Show top N results (default 20)")
    parser.add_argument("--by", choices=["pr", "changes"], default="pr", help="Rank by PRs touched ('pr') or by total line changes ('changes')")
    args = parser.parse_args()

    github_token = os.getenv("GITHUB_TOKEN")
    if not github_token:
        raise EnvironmentError("GITHUB_TOKEN environment variable is not set.")

    headers = {"Authorization": f"Bearer {github_token}"}

    try:
        stats = fetch_all_file_stats(args.org, args.repo, args.start, args.end, headers)
        print_leaderboards(stats, top=args.top, by=args.by)

        if stats.get("ignored_prs"):
            print("\n=== Ignored PRs (more than 100 files) ===")
            for p in stats["ignored_prs"]:
                print(f"PR #{p['number']} createdAt: {p['createdAt']}")
            print(f"Total ignored PRs: {len(stats['ignored_prs'])}")

    except Exception as e:
        print(f"Error: {e}")
