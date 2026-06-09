#!/usr/bin/env python3
"""
fetch_codeforces.py
Fetches Codeforces statistics and accepted submissions history.
Saves the result to data/codeforces_data.json.
"""

import os
import sys
import json
import argparse
import datetime
import requests

def fetch_codeforces_data(handle):
    info_url = f"https://codeforces.com/api/user.info?handles={handle}"
    status_url = f"https://codeforces.com/api/user.status?handle={handle}&from=1&count=10000"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
    }

    print(f"Fetching Codeforces user info for handle: {handle}...")
    try:
        response = requests.get(info_url, headers=headers, timeout=15)
        response.raise_for_status()
        info_data = response.json()
        
        if info_data.get("status") != "OK":
            print(f"Codeforces API error in user.info: {info_data.get('comment')}", file=sys.stderr)
            sys.exit(1)
            
        user_info = info_data["result"][0]
    except Exception as e:
        print(f"Failed to fetch user info from Codeforces: {e}", file=sys.stderr)
        sys.exit(1)

    print(f"Fetching Codeforces submissions for handle: {handle}...")
    try:
        response = requests.get(status_url, headers=headers, timeout=15)
        response.raise_for_status()
        status_data = response.json()
        
        if status_data.get("status") != "OK":
            print(f"Codeforces API error in user.status: {status_data.get('comment')}", file=sys.stderr)
            sys.exit(1)
            
        submissions = status_data["result"]
    except Exception as e:
        print(f"Failed to fetch submission history from Codeforces: {e}", file=sys.stderr)
        sys.exit(1)

    # Process submissions
    # 1. Total solved counts (unique problems solved)
    # 2. Activity calendar for heatmap (count of accepted submissions per day)
    solved_problems = set()
    accepted_by_date = {}

    for sub in submissions:
        if sub.get("verdict") == "OK":
            # Identify unique problem
            problem = sub.get("problem", {})
            contest_id = problem.get("contestId")
            index = problem.get("index")
            if contest_id is not None and index is not None:
                problem_id = f"{contest_id}{index}"
                solved_problems.add(problem_id)

            # Map creation timestamp to YYYY-MM-DD
            creation_time = sub.get("creationTimeSeconds")
            if creation_time:
                date_str = datetime.datetime.fromtimestamp(creation_time, datetime.timezone.utc).strftime("%Y-%m-%d")
                accepted_by_date[date_str] = accepted_by_date.get(date_str, 0) + 1

    processed_data = {
        "handle": handle,
        "rating": user_info.get("rating", 0),
        "rank": user_info.get("rank", "unrated"),
        "max_rating": user_info.get("maxRating", 0),
        "max_rank": user_info.get("maxRank", "unrated"),
        "solved_count": len(solved_problems),
        "submission_calendar": accepted_by_date
    }

    # Write to target data file
    output_dir = "data"
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "codeforces_data.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(processed_data, f, indent=4)

    print(f"Successfully fetched and saved Codeforces data to {output_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fetch and store Codeforces profile stats.")
    parser.add_argument("--handle", required=True, help="Codeforces handle to fetch")
    args = parser.parse_args()
    fetch_codeforces_data(args.handle)
