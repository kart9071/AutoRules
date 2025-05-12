import os
import json
import shutil

def load_rules(filename="rules.json"):
    with open(filename, "r") as f:
        return json.load(f)

def match_conditions(file_path, conditions):
    if conditions.get("type") and not file_path.endswith(f".{conditions['type']}"):
        return False
    if conditions.get("size_greater_than_mb"):
        size_in_bytes = os.path.getsize(file_path)
        if size_in_bytes <= conditions["size_greater_than_mb"] * 1024 * 1024:
            return False
    return True

def perform_action(file_path, action):
    dest_dir = action.get("move_to")
    if dest_dir:
        os.makedirs(dest_dir, exist_ok=True)
        shutil.move(file_path, os.path.join(dest_dir, os.path.basename(file_path)))
        print(f"Moved {file_path} to {dest_dir}")

def apply_rule_to_file(file_path, rule_name):
    rules = load_rules()
    rule = next((r for r in rules if r["rule_name"] == rule_name), None)
    if not rule:
        print(f"No rule found with name: {rule_name}")
        return

    if os.path.isfile(file_path) and match_conditions(file_path, rule["conditions"]):
        print(f"Rule matched: {rule_name} -> {file_path}")
        perform_action(file_path, rule["action"])
    else:
        print(f"Rule did not match or file not found.")

if __name__ == "__main__":
    user_input = input("Enter the file path and rule name (comma-separated): ")
    try:
        file_path, rule_name = [x.strip() for x in user_input.split(",", 1)]
        apply_rule_to_file(file_path, rule_name)
    except ValueError:
        print("Invalid input format. Please enter: <file_path>, <rule_name>")
