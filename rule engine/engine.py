import os
import json
import shutil
import logging

# Configure logger
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

class Engine:
    def __init__(self, rules_file="rules.json"):
        self.rules = self.load_rules(rules_file)

    def load_rules(self, filename):
        with open(filename, "r") as f:
            return json.load(f)

    def match_conditions(self, file_path, conditions):
        file_type = conditions.get("type")
        min_size_mb = float(conditions.get("size_greater_than_mb", 0))

        if file_type and not file_path.lower().endswith(f".{file_type.lower()}"):
            return False

        size_in_bytes = os.path.getsize(file_path)
        if size_in_bytes <= min_size_mb * 1024 * 1024:
            return False

        return True

    def perform_action(self, file_path, action):
        dest_dir = action.get("move_to") or action.get("copy_to")

        if not dest_dir:
            logger.warning(f"No destination specified for action on: {file_path}")
            return

        os.makedirs(dest_dir, exist_ok=True)
        destination = os.path.join(dest_dir, os.path.basename(file_path))

        if action.get("move_to"):
            shutil.move(file_path, destination)
            logger.info(f"Moved: {file_path} -> {destination}")
        elif action.get("copy_to"):
            shutil.copy(file_path, destination)
            logger.info(f"Copied: {file_path} -> {destination}")

    def apply_rule_to_file(self, file_path, rule_name):
        rule = next((r for r in self.rules if r["rule_name"] == rule_name), None)
        if not rule:
            logger.warning(f"No rule found with name: {rule_name}")
            return

        if not os.path.isfile(file_path):
            logger.warning(f"Not a valid file: {file_path}")
            return

        if self.match_conditions(file_path, rule["conditions"]):
            logger.info(f"Rule matched: {rule_name} for file {file_path}")
            self.perform_action(file_path, rule["action"])
        else:
            logger.info(f"Rule did not match: {rule_name} for file {file_path}")

    def apply_rule_to_folder(self, folder_path, rule_name):
        if not os.path.isdir(folder_path):
            logger.warning(f"Invalid folder path: {folder_path}")
            return

        for entry in os.listdir(folder_path):
            full_path = os.path.join(folder_path, entry)
            if os.path.isfile(full_path):
                self.apply_rule_to_file(full_path, rule_name)


if __name__ == "__main__":
    user_input = input("Enter the folder/file path and rule name (comma-separated): ")
    try:
        path, rule_name = [x.strip() for x in user_input.split(",", 1)]
        engine = Engine()

        if os.path.isdir(path):
            engine.apply_rule_to_folder(path, rule_name)
        elif os.path.isfile(path):
            engine.apply_rule_to_file(path, rule_name)
        else:
            logger.warning("Provided path is neither a valid file nor a folder.")
    except ValueError:
        logger.error("Invalid input format. Please enter: <path>, <rule_name>")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
