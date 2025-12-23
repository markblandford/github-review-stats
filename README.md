
# GitHub Review Stats

A Python script to generate a **leaderboard of pull request reviews** for a specific GitHub repository within a given time period.  
It counts:

- ✅ **Approvals**
- 💬 **Comments**

## Features

- Fetches all merged pull requests for a given date range.
- Aggregates review counts per user.
- Breaks down reviews into:
  - **Approvals**
  - **Comments**
- Outputs a sorted leaderboard.

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
| --- | --- | --- |
| `GITHUB_TOKEN` | GitHub Personal Access Token (Classic) | Environment variable, `GITHUB_TOKEN` | `export GITHUB_TOKEN="your-token-here"` |
| `ORG_NAME` | The organisation or owner of the repo | Input argument, `--org` | `--org your-org` |
| `REPO_NAME` | The name of the repo | Input argument, `--repo` | `--repo your-repo` |
| `START_DATE` | The organisation or owner of the repo | Input argument, `--start` | `--start 2025-01-01T00:00:00Z` |
| `END_DATE` | The organisation or owner of the repo | Input argument, `--end` | `--end 2025-12-31T23:59:59Z` |

## Usage

1. Set your token: `export GITHUB_TOKEN="your-token-here"`
2. Run the script with arguments:

```bash
python review_stats.py --org your-org --repo your-repo --start 2025-01-01T00:00:00Z --end 2025-12-31T23:59:59Z
```

### Output

```plaintext
=== Review Leaderboard for 2025 ===
alice: 42 reviews (Approvals: 30, Comments: 12)
bob: 35 reviews (Approvals: 20, Comments: 15)
```
