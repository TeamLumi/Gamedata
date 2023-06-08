import json

class JsonCache:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(JsonCache, cls).__new__(cls)
            cls._instance.cache = {}
        return cls._instance

    def get_json(self, filepath):
        if filepath in self.cache:
            return self.cache[filepath]

        # Load the JSON file
        with open(filepath, "r", encoding="utf-8") as f:
            json_data = json.load(f)

        # Cache the loaded JSON
        self.cache[filepath] = json_data
        return json_data

# Create an instance of JsonCache
json_cache = JsonCache()
