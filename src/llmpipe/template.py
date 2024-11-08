from dataclasses import dataclass


@dataclass
class Template:
    """A string template with keys marked by double curly braces."""

    template: str  #: A string template

    def format(self, **kwargs) -> str:
        """Replace template keys with `kwarg` values."""
        template = self.template
        for k, v in kwargs.items():
            kk = "{{" + k + "}}"
            if kk in template:
                template = template.replace(kk, str(v) or "")
        return template
