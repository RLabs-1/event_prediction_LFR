import yaml


class ConfigLoader:
    def __init__(self, config_path):
        self.config_path = config_path

    def load(self):
        try:
            with open(self.config_path, 'r', encoding='utf-8') as file:
                return yaml.safe_load(file)
        except Exception as e:
            print(f"Error loading config file: {e}")
            raise
