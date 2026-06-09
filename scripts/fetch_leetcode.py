#!/usr/bin/env python3
"""
fetch_leetcode.py
Fetches LeetCode statistics and submission calendar using LeetCode's public GraphQL API.
Saves the result to data/leetcode_data.json.
"""

import os
import sys
import json
import argparse
import requests

def fetch_leetcode_data(username):
    url = "https://leetcode.com/graphql"
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
    }

    # GraphQL query for user solved questions break down
    stats_query = """
    query userProblemsSolved($username: String!) {
      allQuestionsCount {
        difficulty
        count
      }
      matchedUser(username: $username) {
        submitStats {
          acSubmissionNum {
            difficulty
            count
          }
        }
      }
    }
    """

    # GraphQL query for user submission calendar
    calendar_query = """
    query userProfileCalendar($username: String!) {
      matchedUser(username: $username) {
        userCalendar {
          submissionCalendar
        }
      }
    }
    """

    print(f"Fetching LeetCode statistics for user: {username}...")
    
    # Fetch questions statistics
    try:
        response = requests.post(
            url,
            json={"query": stats_query, "variables": {"username": username}},
            headers=headers,
            timeout=15
        )
        response.raise_for_status()
        stats_data = response.json()
        
        if "errors" in stats_data:
            print(f"GraphQL Errors in stats query: {stats_data['errors']}", file=sys.stderr)
            sys.exit(1)
            
        if not stats_data.get("data") or not stats_data["data"].get("matchedUser"):
            print(f"Error: User '{username}' not found on LeetCode.", file=sys.stderr)
            sys.exit(1)
            
    except Exception as e:
        print(f"Failed to fetch statistics from LeetCode GraphQL endpoint: {e}", file=sys.stderr)
        sys.exit(1)

    # Fetch contribution calendar
    try:
        response = requests.post(
            url,
            json={"query": calendar_query, "variables": {"username": username}},
            headers=headers,
            timeout=15
        )
        response.raise_for_status()
        calendar_data = response.json()
        
        if "errors" in calendar_data:
            print(f"GraphQL Errors in calendar query: {calendar_data['errors']}", file=sys.stderr)
            sys.exit(1)
            
    except Exception as e:
        print(f"Failed to fetch calendar from LeetCode GraphQL endpoint: {e}", file=sys.stderr)
        sys.exit(1)

    # Parse questions count
    matched_user = stats_data["data"]["matchedUser"]
    ac_submissions = matched_user["submitStats"]["acSubmissionNum"]
    all_questions = stats_data["data"]["allQuestionsCount"]
    
    ac_dict = {item["difficulty"]: item["count"] for item in ac_submissions}
    all_dict = {item["difficulty"]: item["count"] for item in all_questions}
    
    # Parse calendar
    user_calendar = calendar_data.get("data", {}).get("matchedUser", {}).get("userCalendar", {})
    sub_cal_str = user_calendar.get("submissionCalendar", "{}") if user_calendar else "{}"
    
    try:
        submission_calendar = json.loads(sub_cal_str)
    except Exception:
        submission_calendar = {}

    processed_data = {
        "username": username,
        "total_questions": all_dict.get("All", 0),
        "total_easy": all_dict.get("Easy", 0),
        "total_medium": all_dict.get("Medium", 0),
        "total_hard": all_dict.get("Hard", 0),
        "solved_all": ac_dict.get("All", 0),
        "solved_easy": ac_dict.get("Easy", 0),
        "solved_medium": ac_dict.get("Medium", 0),
        "solved_hard": ac_dict.get("Hard", 0),
        "submission_calendar": submission_calendar
    }

    # Write to target data file
    output_dir = "data"
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "leetcode_data.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(processed_data, f, indent=4)
        
    print(f"Successfully fetched and saved LeetCode data to {output_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fetch and store LeetCode profile stats.")
    parser.add_argument("--username", required=True, help="LeetCode username to fetch")
    args = parser.parse_args()
    fetch_leetcode_data(args.username)
