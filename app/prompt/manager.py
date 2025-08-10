import os
from typing import Dict, Optional


class PromptManager:
    """
    Simple prompt registry that loads prompt templates from filesystem and renders them
    using Python str.format with strict variable requirements.

    Design goals:
    - No fallback logic. Missing templates or variables raise explicit errors.
    - Keep prompts outside codebase (config/prompts) for easier maintenance and i18n.
    - Zero new runtime dependencies (no jinja2).
    """

    DEFAULT_DIR_ENV: str = "PROMPT_DIR"
    DEFAULT_DIR: str = os.path.join("config", "prompts")
    NAME_TO_FILE: Dict[str, str] = {
        "gen_sql": "gen_sql.j2",
        "intention": "intention.j2",
        "ddl_sql": "ddl.sql",
    }

    def __init__(self, base_dir: Optional[str] = None):
        self.base_dir = base_dir or os.getenv(self.DEFAULT_DIR_ENV, self.DEFAULT_DIR)
        self._cache: Dict[str, str] = {}

    def _path_for(self, name: str) -> str:
        if name not in self.NAME_TO_FILE:
            raise KeyError(f"Unknown prompt name: {name}")
        return os.path.join(self.base_dir, self.NAME_TO_FILE[name])

    def load(self, name: str) -> str:
        if name in self._cache:
            return self._cache[name]
        path = self._path_for(name)
        if not os.path.exists(path):
            raise FileNotFoundError(f"Prompt file not found: {path}")
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        # cache immutable content
        self._cache[name] = content
        return content

    def render(self, name: str, **kwargs) -> str:
        template = self.load(name)
        try:
            return template.format(**kwargs)
        except KeyError as e:
            missing_key = str(e).strip("'")
            raise ValueError(f"Missing required template variable: {missing_key} for prompt '{name}'")


# default singleton
prompt_manager = PromptManager()


