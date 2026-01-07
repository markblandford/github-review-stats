# GitHub Review & PR Merge Stats

This repository contains Python scripts to generate leaderboards for GitHub repositories. Ideal for tracking team contributions and review activity over a given time period.

## Features

- Fetches all merged pull requests for a given date range.
- Aggregates:
  - **Review Stats**: Approvals, Comments, Changes Requested.
  - **Contributor Stats**: Number of merged PRs per contributor.
  - **File Stats**: The most touched files by PRs, indicating the most used / volatile files.
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

### PR Contributor Stats (contributor_stats.py)

#### Usage

1. Set your token: `export GITHUB_TOKEN="your-token-here"`
2. Run the script with arguments:

```bash
python contributor_stats.py --org your-org --repo your-repo --start 2025-01-01T00:00:00Z --end 2025-12-31T23:59:59Z
```

##### Output

```plaintext
=== Contributor Leaderboard ===
alice: 25 merged PRs
bob: 18 merged PRs
```

### Files & Directories Stats (file_stats.py)

#### Usage

1. Set your token: `export GITHUB_TOKEN="your-token-here"`
2. Run the script with arguments:

```bash
python file_stats.py --org your-org --repo your-repo --start 2025-01-01T00:00:00Z --end 2025-12-31T23:59:59Z --top 20 --by pr
```

##### Options

- `--top N` - show top N results (default 20)
- `--by` `["pr", "changes"]` - choose pr to rank by number of PRs touching the file/directory, or changes to rank by total additions+deletions

##### Output

###### By pr

```plaintext
=== Top 20 Files by PRs touched ===
1. src/app/content/article-list.ts: 3
2. routes.txt: 1
...

=== Top 20 Directories by PRs touched ===
1. src/app/content: 3
2. .: 3
...

=== Ignored PRs (more than 100 files) ===
PR #123 createdAt: 2025-06-01T12:34:56Z
Total ignored PRs: 1
```

###### By changes

```plaintext
=== Top 20 Files by total changes ===
1. package-lock.json: 13630
2. src/assets/articles/threat-modelling/article.md: 208
...

=== Top 20 Directories by total changes ===
1. .: 13636
2. src/assets/articles/threat-modelling: 208
...

=== Ignored PRs (more than 100 files) ===
PR #123 createdAt: 2025-06-01T12:34:56Z
Total ignored PRs: 1
```

#### Notes

The script fetches up to 100 files per PR. PRs that touch more than 100 files are ignored and listed in a summary so you can review which PRs were excluded.
