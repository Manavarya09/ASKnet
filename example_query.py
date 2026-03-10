#!/usr/bin/env python3
"""
Example query script for ASK-Net multi-agent system.
Run this after starting the API with: docker-compose up
"""

import requests
import json
import time

# API base URL
BASE_URL = "http://localhost:8000"


def submit_query(query_text, user_id="demo_user"):
    """Submit a query to the ASK-Net system."""
    response = requests.post(
        f"{BASE_URL}/query", json={"user_id": user_id, "query_text": query_text}
    )

    if response.status_code == 200:
        result = response.json()
        print(f"Query submitted successfully!")
        print(f"Task ID: {result['task_id']}")
        print(f"Status: {result['status']}")
        return result["task_id"]
    else:
        print(f"Error submitting query: {response.status_code}")
        print(response.text)
        return None


def get_task_status(task_id, poll_interval=2, max_polls=30):
    """Poll for task status until completion."""
    for i in range(max_polls):
        response = requests.get(f"{BASE_URL}/tasks/{task_id}")

        if response.status_code != 200:
            print(f"Error getting task status: {response.status_code}")
            return None

        task = response.json()
        status = task["status"]

        print(f"\nPoll {i + 1}: Status = {status}")

        if status in ["completed", "error"]:
            return task

        time.sleep(poll_interval)

    print("Timeout waiting for task completion")
    return None


def submit_feedback(task_id, rating=5, comments=""):
    """Submit feedback for a task."""
    response = requests.post(
        f"{BASE_URL}/feedback",
        json={"task_id": task_id, "rating": rating, "comments": comments},
    )

    if response.status_code == 200:
        print(f"\nFeedback submitted successfully!")
        print(f"Rating: {rating}")
        return True
    else:
        print(f"Error submitting feedback: {response.status_code}")
        return False


def main():
    """Main example function."""
    print("=" * 60)
    print("ASK-Net Multi-Agent Climate Science Demo")
    print("=" * 60)

    # Sample climate science queries
    queries = [
        "Assess wildfire risk under drought-prone conditions and propose mitigation strategies",
        "Analyze climate trends in the Southwest United States and predict future risks",
        "What are the key factors contributing to increased wildfire frequency in California?",
    ]

    # Submit a query
    print("\n1. Submitting query...")
    query = queries[0]
    print(f"Query: {query}")

    task_id = submit_query(query)

    if task_id:
        print(f"\n2. Polling for task completion...")
        task = get_task_status(task_id)

        if task:
            print("\n3. Task completed!")
            print("-" * 40)
            print(f"Domain: {task.get('domain', 'N/A')}")
            print(f"Status: {task['status']}")

            if task.get("final_answer"):
                print("\nFinal Answer:")
                print("-" * 40)
                print(task["final_answer"])
                print("-" * 40)

            if task.get("debate_history"):
                print(f"\nDebate rounds: {len(task['debate_history'])}")

            # Submit feedback
            print("\n4. Submitting feedback...")
            submit_feedback(task_id, rating=5, comments="Great climate analysis!")

    print("\n" + "=" * 60)
    print("Demo completed!")
    print("=" * 60)


if __name__ == "__main__":
    main()
