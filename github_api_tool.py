import requests
import json

print("\n=== GitHub API Investigation Tool ===")

# ===============================
# Authentication (API token)
# ===============================
TOKEN = "YOUR_TOKEN_HERE"

headers = {
    "Authorization": f"token {TOKEN}"
}

# ===============================
# Check API rate limit
# ===============================
print("\n--- API Rate Limit ---")

rate_url = "https://api.github.com/rate_limit"
rate_response = requests.get(rate_url, headers=headers)

if rate_response.status_code == 200:
    rate_data = rate_response.json()

    limit = rate_data.get("rate", {}).get("limit")
    remaining = rate_data.get("rate", {}).get("remaining")

    print("Limit:", limit)
    print("Remaining:", remaining)
else:
    print("Failed to check rate limit")
    print("Response:", rate_response.text)

# ===============================
# Repositories to check
# ===============================
repos = [
    {"name": "python/cpython", "category": "Python"},
    {"name": "pallets/flask", "category": "Python"},
    {"name": "aws/aws-cli", "category": "AWS"},
    {"name": "hashicorp/terraform", "category": "Infrastructure"},
    {"name": "Azure/azure-sdk-for-python", "category": "Azure"},
    {"name": "wireshark/wireshark", "category": "Networking"},
    {"name": "postgres/postgres", "category": "SQL"},
    {"name": "microsoft/vscode", "category": "Development Tools"},
    {"name": "docker/compose", "category": "Containers"},
    {"name": "nonexistent/repo123", "category": "Test Failure"}
]

# Counters for summary
success_count = 0
fail_count = 0

# Store all results
results = []

# Track results per category
category_summary = {}

# ===============================
# Main loop - check each repository
# ===============================
for repo_info in repos:

    repo = repo_info["name"]
    category = repo_info["category"]

    print("\n" + "=" * 40)
    print("Checking:", repo)
    print("Category:", category)

    url = f"https://api.github.com/repos/{repo}"
    response = requests.get(url, headers=headers)

    print("Status Code:", response.status_code)

    # Initialise category tracking
    if category not in category_summary:
        category_summary[category] = {"success": 0, "failed": 0}

    # ===============================
    # Successful response
    # ===============================
    if response.status_code == 200:

        success_count += 1
        category_summary[category]["success"] += 1

        data = response.json()

        # Extract basic repository information
        name = data.get("name")
        owner = data.get("owner", {}).get("login")
        stars = data.get("stargazers_count")

        print("Name:", name)
        print("Owner:", owner)
        print("Stars:", stars)

        # ===============================
        # Get issues
        # ===============================
        issues_url = f"https://api.github.com/repos/{repo}/issues"
        issues_response = requests.get(issues_url, headers=headers)

        if issues_response.status_code == 200:
            issues_data = issues_response.json()
            issue_count = len(issues_data)
            print("Issues Retrieved:", issue_count)
        else:
            issue_count = "Error"
            print("Issues fetch failed")

        # ===============================
        # Get latest commit
        # ===============================
        commits_url = f"https://api.github.com/repos/{repo}/commits"
        commits_response = requests.get(commits_url, headers=headers)

        if commits_response.status_code == 200:
            commits_data = commits_response.json()

            if commits_data:
                latest_commit = commits_data[0].get("commit", {}).get("message")
            else:
                latest_commit = "None"
        else:
            latest_commit = "Error"

        # Store successful result
        results.append({
            "repo": repo,
            "category": category,
            "status": "success",
            "stars": stars,
            "issues": issue_count,
            "latest_commit": latest_commit
        })

    # ===============================
    # Failed response
    # ===============================
    else:
        fail_count += 1
        category_summary[category]["failed"] += 1

        print("Error occurred")
        print("Response:", response.text)

        # Error handling
        if response.status_code == 400:
            reason = "Bad request"

        elif response.status_code == 401:
            reason = "Unauthorized (token issue)"

        elif response.status_code == 403:
            reason = "Forbidden or rate limited"

        elif response.status_code == 404:
            reason = "Repository not found"

        elif response.status_code == 429:
            reason = "Rate limited"

        elif response.status_code >= 500:
            reason = "Server error"

        else:
            reason = "Unexpected error"

        print("Reason:", reason)

        # Store failure result
        results.append({
            "repo": repo,
            "category": category,
            "status": "failed",
            "reason": reason
        })

# ===============================
# Overall summary
# ===============================
print("\n" + "=" * 40)
print("--- Summary ---")
print("Successful:", success_count)
print("Failed:", fail_count)

# ===============================
# Category summary
# ===============================
print("\n--- Category Summary ---")

for category, stats in category_summary.items():
    print("\n" + category)
    print("  Successful:", stats["success"])
    print("  Failed:", stats["failed"])

# ===============================
# Save results to file
# ===============================
with open("github_results.json", "w") as file:
    json.dump(results, file, indent=2)

print("\nResults saved to github_results.json")

# ===============================
# Failure report
# ===============================
print("\n--- Failure Report ---")

failures = []

for r in results:
    if r["status"] == "failed":
        failures.append(r)

        print("Repo:", r["repo"])
        print("Category:", r["category"])
        print("Reason:", r["reason"])
        print()

# Only save failure file if exists
if failures:
    with open("github_failures.json", "w") as file:
        json.dump(failures, file, indent=2)

    print("Failures saved to github_failures.json")
else:
    print("No failures detected")