import json
from fuzzywuzzy import fuzz
from fuzzywuzzy import process

# Load the existing database
def load_database(filename="aisurvey-data.json"):
    try:
        with open(filename, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

# Save the updated database
def save_database(data, filename="aisurvey-data.json"):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# Match a new idea to existing entries
def match_idea(new_idea, existing_ideas, high_thresh=90, med_thresh=80):
    matches = []
    for idea in existing_ideas:
        score = fuzz.ratio(new_idea, idea)
        if score >= high_thresh:
            matches.append((idea, score))

    if matches:
        # Return the best high match
        return sorted(matches, key=lambda x: -x[1])[0][0]

    # If no high matches, check for medium matches
    med_matches = [
        (idea, fuzz.ratio(new_idea, idea))
        for idea in existing_ideas
        if med_thresh <= fuzz.ratio(new_idea, idea) < high_thresh
    ]

    if med_matches:
        return {
            "prompt": new_idea,
            "options": sorted(med_matches, key=lambda x: -x[1])
        }

    # Otherwise, it's a new idea
    return None

# Update the database with new ideas
def update_database_with_idea(new_idea):
    db = load_database()
    existing_ideas = list(db.keys())

    result = match_idea(new_idea, existing_ideas)

    if isinstance(result, str):  # exact match found
        db[result] += 1
        save_database(db)
        return f"Updated existing idea: {result}"

    elif isinstance(result, dict):  # medium matches found
        return result  # let the frontend handle user confirmation

    else:  # completely new idea
        db[new_idea] = 1
        save_database(db)
        return f"Inserted new idea: {new_idea}"

# For testing/demo
if __name__ == "__main__":
    test_idea = "बिजली नहीं आती"
    result = update_database_with_idea(test_idea)
    print(result)