"""
Task Breakdown Module
Automatically splits a task into smaller subtasks based on risk level.
"""

from typing import List
import re
import random

# Keywords that indicate complexity
COMPLEXITY_KEYWORDS = [
    "essay", "report", "project", "analysis",
    "presentation", "coding", "design", "study"
]

def simple_tokenizer(text: str) -> List[str]:
    """Split text into words, simple tokenizer."""
    return re.findall(r'\w+', text.lower())

def count_complexity_words(text: str) -> int:
    """Count number of 'complexity' keywords in text."""
    tokens = simple_tokenizer(text)
    return sum(1 for word in COMPLEXITY_KEYWORDS if word in tokens)

def estimate_num_subtasks(task_description: str, risk_category: str) -> int:
    """
    Estimate number of subtasks based on task length and risk.
    High-risk tasks get more granular breakdown.
    """
    word_count = len(simple_tokenizer(task_description))
    
    # Base subtasks from length
    base = max(1, word_count // 50)  # ~1 subtask per 50 words
    
    # Adjust by risk
    if risk_category == "high":
        return base + 2
    elif risk_category == "medium":
        return base + 1
    else:
        return base

def generate_subtask_titles(task_description: str, n_subtasks: int) -> List[str]:
    """
    Generate simple subtask titles from main task.
    Splits the task description into smaller chunks.
    """
    sentences = re.split(r'[.!?]', task_description)
    sentences = [s.strip() for s in sentences if s.strip()]
    
    # If not enough sentences, generate placeholders
    if len(sentences) < n_subtasks:
        sentences += [f"Step {i+1}" for i in range(n_subtasks - len(sentences))]
    
    # Select or repeat sentences to match number of subtasks
    subtasks = []
    for i in range(n_subtasks):
        s = sentences[i % len(sentences)]
        subtasks.append(s)
    
    return subtasks

def breakdown_task(task_description: str, risk_category: str) -> List[dict]:
    """
    Main function: return a list of subtasks as dictionaries.
    
    Each subtask dict:
    {
        "title": str,
        "order": int,
        "is_completed": bool
    }
    """
    n_subtasks = estimate_num_subtasks(task_description, risk_category)
    titles = generate_subtask_titles(task_description, n_subtasks)
    
    subtasks = []
    for idx, title in enumerate(titles):
        subtasks.append({
            "title": title,
            "order": idx + 1,
            "is_completed": False
        })
    return subtasks

# -----------------------------
# Example usage
# -----------------------------
if __name__ == "__main__":
    example_task = "Write a 2000-word essay on climate change analysis. Include graphs and research references. Submit by Friday."
    risk = "high"
    
    subtasks = breakdown_task(example_task, risk)
    
    print("📌 Generated Subtasks:")
    for st in subtasks:
        print(f"  {st['order']}. {st['title']}")
