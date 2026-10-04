class SummaryRenderer:
    def render(
        self,
        template: str,
        values: dict[str, object],
    ) -> str:
        normalized = {
            key: "" if value is None else str(value)
            for key, value in values.items()
        }

        return template.format_map(normalized)