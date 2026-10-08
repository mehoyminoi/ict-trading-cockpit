from string import Formatter


class SummaryRenderer:
    def fields(self, template: str) -> set[str]:
        try:
            return {
                field_name
                for _literal, field_name, _format_spec, _conversion
                in Formatter().parse(template)
                if field_name
            }
        except ValueError as exc:
            raise ValueError(f"Invalid summary template syntax: {exc}") from exc

    def validate(
        self,
        template: str,
        allowed_fields: set[str] | frozenset[str],
    ) -> None:
        unknown = sorted(self.fields(template) - set(allowed_fields))
        if unknown:
            raise ValueError(
                "Unknown summary template field(s): " + ", ".join(unknown)
            )

    def render(
        self,
        template: str,
        values: dict[str, object],
    ) -> str:
        normalized = {
            key: "" if value is None else str(value)
            for key, value in values.items()
        }
        try:
            return template.format_map(normalized)
        except KeyError as exc:
            raise ValueError(
                f"Summary template field has no value: {exc.args[0]}"
            ) from exc
        except ValueError as exc:
            raise ValueError(f"Invalid summary template syntax: {exc}") from exc


    def render_versioned(
        self,
        definition,
        values: dict[str, object],
    ) -> str:
        rendered = self.render(definition.body, values).rstrip()
        return (
            f"{rendered}\n\n"
            f"Template: {definition.name} · r{definition.revision}\n"
        )
