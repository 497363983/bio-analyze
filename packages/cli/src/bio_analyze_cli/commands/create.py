from pathlib import Path
from typing import Any

from jinja2 import Environment, FileSystemLoader
from rich.prompt import Prompt

from bio_analyze_core.cli.app import Argument, Exit, Option, echo
from bio_analyze_core.i18n import _


class Template:
    """
    Base template class for managing and rendering template directories.

    Attributes:
        name (str):
            Template name.
        description (str):
            Template description.
        env (Environment):
            Jinja2 Environment object.
    """

    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description

        # Configure the Jinja2 environment.
        template_dir = Path(__file__).parent.parent / "templates" / name
        self.env = Environment(loader=FileSystemLoader(str(template_dir)))

    def render_directory(self, context: dict[str, Any], output_dir: Path) -> None:
        """
        Recursively render template directory to output_dir.

        Template file paths can contain jinja2 variables (e.g. {{name}}).

        Args:
            context (dict[str, Any]):
                Context variables for rendering.
            output_dir (Path):
                Output directory path.
        """
        template_base = Path(__file__).parent.parent / "templates" / self.name

        # Walk all files in the template directory.
        for template_file in template_base.rglob("*"):
            if not template_file.is_file():
                continue

            # Resolve the path relative to the template root.
            rel_path = template_file.relative_to(template_base)

            # Render the path itself so file and directory names can be dynamic.
            path_template = self.env.from_string(str(rel_path))
            rendered_rel_path = Path(path_template.render(**context))

            # Drop the .jinja suffix from the rendered output path.
            if rendered_rel_path.suffix == ".jinja":
                rendered_rel_path = rendered_rel_path.with_suffix("")

            target_path = output_dir / rendered_rel_path

            # Create parent directories.
            target_path.parent.mkdir(parents=True, exist_ok=True)

            # Render file content. Jinja2 loader expects forward slashes.
            template_name = str(rel_path).replace("\\", "/")
            self.render_template(template_name, context, target_path)

    def render_template(self, template_name: str, context: dict[str, Any], output_path: Path) -> None:
        """
        Render a single template file and save it.

        Args:
            template_name (str):
                Template file name (relative to loader root).
            context (dict[str, Any]):
                Context variables for rendering.
            output_path (Path):
                Output file path.
        """
        template = self.env.get_template(template_name)
        content = template.render(**context)
        with open(output_path, "w") as f:
            f.write(content)

    def create(self, name: str, output_dir: Path, **kwargs: Any) -> None:
        """
        Execute creation operation (abstract method).

        Args:
            name (str):
                Artifact name.
            output_dir (Path):
                Output directory.
            **kwargs:
                Additional arguments.
        """
        raise NotImplementedError

class ToolTemplate(Template):
    """
    Template for creating a new analysis tool package.
    """

    def __init__(self):
        super().__init__("tool", _("Create a new analysis tool package"))

    def create(self, name: str, output_dir: Path, **kwargs: Any) -> None:
        package_name = f"bio_analyze_{name}"
        package_dir = output_dir / "packages" / name

        if package_dir.exists():
            echo(_("Error: Directory {path} already exists.").format(path=package_dir))
            raise Exit(code=1)

        context = {"name": name}

        # Render the whole template directory.
        self.render_directory(context, package_dir)

        # Ensure __init__.py exists even if the template omits it.
        src_init = package_dir / "src" / package_name / "__init__.py"
        if not src_init.exists():
            src_init.parent.mkdir(parents=True, exist_ok=True)
            src_init.touch()

        # Create a tests directory if the template does not include one.
        (package_dir / "tests").mkdir(exist_ok=True)

        echo(_("Successfully created tool '{name}' at {path}").format(name=name, path=package_dir))
        echo(_("Don't forget to run `uv sync` to install the new package!"))

class ThemeTemplate(Template):
    """
    Template for creating a new plot theme package.
    """

    def __init__(self):
        super().__init__("theme", _("Create a new plot theme package"))

    def create(self, name: str, output_dir: Path, **kwargs: Any) -> None:
        package_name = name
        target_dir = output_dir / package_name

        if target_dir.exists():
            echo(_("Error: Directory {path} already exists.").format(path=target_dir))
            raise Exit(code=1)

        # The template needs an underscore variant for module paths.
        context = {"name": name, "name_underscore": name.replace("-", "_")}

        # Render the whole template directory.
        self.render_directory(context, target_dir)

        echo(_("Successfully created theme package '{name}' at {path}").format(name=package_name, path=target_dir))
        echo(
            _(
                "To use it: `pip install -e {package_name}` then `bioanalyze plot ... --theme {theme_name}`"
            ).format(package_name=package_name, theme_name=context["name_underscore"])
        )

# Registry for templates.
TEMPLATES: dict[str, Template] = {
    "tool": ToolTemplate(),
    "theme": ThemeTemplate(),
}

def create_command(
    template_type: str = Argument(None, help=_("Type of artifact to create (tool, theme)."), metavar="TYPE"),
    name: str = Option(None, "--name", "-n", help=_("Name of the artifact.")),
    output: Path = Option(Path.cwd(), "--output", "-o", help=_("Output directory (default: current directory).")),
) -> None:
    """
    Create a new tool or theme based on a template.

    Args:
        template_type (str, optional):
            Type of artifact to create (tool, theme).
        name (str, optional):
            Name of the artifact.
        output (Path, optional):
            Output directory (default: current directory).
    """
    # 如果未提供，则进行交互式选择
    if not template_type:
        template_type = Prompt.ask("What do you want to create?", choices=list(TEMPLATES.keys()), default="tool")

    if template_type not in TEMPLATES:
        echo(f"Unknown template type: {template_type}")
        raise Exit(code=1)

    if not name:
        name = Prompt.ask("Enter the name (e.g. 'genomics' or 'dark-mode')")

    template = TEMPLATES[template_type]
    template.create(name, output)
