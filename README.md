# GitHub Review & PR Merge Stats

This repository contains Python scripts to generate leaderboards for GitHub repositories. Ideal for tracking team contributions and review activity over a given time period.

## Features

- Fetches all merged pull requests for a given date range.
- Aggregates:
  - **Review Stats**: Approvals, Comments, Changes Requested.
  - **Contributor Stats**: Number of merged PRs per contributor.
- Handles pagination automatically.
- Outputs sorted leaderboards.

## Requirements
- Python 3.7+
- [GitHub Personal Access Token](https://github.com/settings/tokens) with:
  - `repo` scope (for private repos)
  - `read:org` (if needed)

---

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/github-review-stats.git
cd github-review-stats
```

### 2. Create a Virtual Environment (Recommended)

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

## Configuration

| Item | About | Source | Example |
| --- | --- | --- | --- |
| `GITHUB_TOKEN` | GitHub Personal Access Token (Classic) | Environment variable, `GITHUB_TOKEN` | `export GITHUB_TOKEN="your-token-here"` |
| `ORG_NAME` | The organisation or owner of the repo | Input argument, `--org` | `--org your-org` |
| `REPO_NAME` | The name of the repo | Input argument, `--repo` | `--repo your-repo` |
| `START_DATE` | The organisation or owner of the repo | Input argument, `--start` | `--start 2025-01-01T00:00:00Z` |
| `END_DATE` | The organisation or owner of the repo | Input argument, `--end` | `--end 2025-12-31T23:59:59Z` |

## The Scripts

### PR Review Stats (review_stats.py)

#### Usage

1. Set your token: `export GITHUB_TOKEN="your-token-here"`
2. Run the script with arguments:

```bash
python review_stats.py --org your-org --repo your-repo --start 2025-01-01T00:00:00Z --end 2025-12-31T23:59:59Z
```

##### Output

```plaintext
=== Review Leaderboard ===
alice: 42 reviews (Approvals: 30, Comments: 10, Changes Requested: 2)
bob: 35 reviews (Approvals: 20, Comments: 15, Changes Requested: 0)
```

### PR Contributor Stats (contributor-stats.py)

#### Usage

1. Set your token: `export GITHUB_TOKEN="your-token-here"`
2. Run the script with arguments:

```bash
python contributor-stats.py --org your-org --repo your-repo --start 2025-01-01T00:00:00Z --end 2025-12-31T23:59:59Z
```

##### Output

```plaintext
=== Contributor Leaderboard ===
alice: 25 merged PRs
bob: 18 merged PRs
```
