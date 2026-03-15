from pathlib import Path
from typing import Any

import typer
from jinja2 import Environment, FileSystemLoader
from rich.prompt import Prompt


class Template:
    """
    zh: 模板基类，用于管理和渲染模板目录。
    en: Base template class for managing and rendering template directories.

    Attributes:
        name (str):
            zh: 模板名称。
            en: Template name.
        description (str):
            zh: 模板描述。
            en: Template description.
        env (Environment):
            zh: Jinja2 环境对象。
            en: Jinja2 Environment object.
    """

    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description

        # 设置 Jinja2 环境
        template_dir = Path(__file__).parent.parent / "templates" / name
        self.env = Environment(loader=FileSystemLoader(str(template_dir)))

    def render_directory(self, context: dict[str, Any], output_dir: Path) -> None:
        """
        zh: 递归地将模板目录渲染到 output_dir。
        en: Recursively render template directory to output_dir.

        模板文件路径可以包含 jinja2 变量（例如 {{name}}）。
        Template file paths can contain jinja2 variables (e.g. {{name}}).

        Args:
            context (dict[str, Any]):
                zh: 渲染上下文变量。
                en: Context variables for rendering.
            output_dir (Path):
                zh: 输出目录路径。
                en: Output directory path.
        """
        template_base = Path(__file__).parent.parent / "templates" / self.name

        # 遍历模板目录中的所有文件
        for template_file in template_base.rglob("*"):
            if not template_file.is_file():
                continue

            # 获取相对于模板基准的路径
            rel_path = template_file.relative_to(template_base)

            # 渲染路径本身（以支持动态文件名/目录）
            # 我们将路径转换为字符串，渲染它，然后转换回 Path
            # 注意：路径中的 Jinja2 变量语法 {{name}}
            # 我们使用临时 env 来渲染字符串路径
            path_template = self.env.from_string(str(rel_path))
            rendered_rel_path = Path(path_template.render(**context))

            # 如果存在 .jinja 后缀，则在最终文件名中移除
            if rendered_rel_path.suffix == ".jinja":
                rendered_rel_path = rendered_rel_path.with_suffix("")

            target_path = output_dir / rendered_rel_path

            # 创建父目录
            target_path.parent.mkdir(parents=True, exist_ok=True)

            # 渲染文件内容
            # Jinja2 loader 期望正斜杠
            template_name = str(rel_path).replace("\\", "/")
            self.render_template(template_name, context, target_path)

    def render_template(self, template_name: str, context: dict[str, Any], output_path: Path) -> None:
        """
        zh: 渲染单个模板文件并保存。
        en: Render a single template file and save it.

        Args:
            template_name (str):
                zh: 模板文件名（相对于 loader 根目录）。
                en: Template file name (relative to loader root).
            context (dict[str, Any]):
                zh: 渲染上下文变量。
                en: Context variables for rendering.
            output_path (Path):
                zh: 输出文件路径。
                en: Output file path.
        """
        template = self.env.get_template(template_name)
        content = template.render(**context)
        with open(output_path, "w") as f:
            f.write(content)

    def create(self, name: str, output_dir: Path, **kwargs: Any) -> None:
        """
        zh: 执行创建操作（抽象方法）。
        en: Execute creation operation (abstract method).

        Args:
            name (str):
                zh: 工件名称。
                en: Artifact name.
            output_dir (Path):
                zh: 输出目录。
                en: Output directory.
            **kwargs:
                zh: 其他参数。
                en: Additional arguments.
        """
        raise NotImplementedError


class ToolTemplate(Template):
    """
    zh: 用于创建新分析工具包的模板。
    en: Template for creating a new analysis tool package.
    """

    def __init__(self):
        super().__init__("tool", "Create a new analysis tool package")

    def create(self, name: str, output_dir: Path, **kwargs: Any) -> None:
        package_name = f"bio_analyze_{name}"
        package_dir = output_dir / "packages" / name

        if package_dir.exists():
            typer.echo(f"Error: Directory {package_dir} already exists.")
            raise typer.Exit(code=1)

        context = {"name": name}

        # 使用递归目录渲染
        self.render_directory(context, package_dir)

        # 确保 __init__.py 存在（如果模板中没有）
        # 注意：在我们的模板结构中，如果需要，我们应该有 __init__.py.jinja 或类似文件。
        # 但如果模板是完整的，我们不需要手动触摸。
        # 让我们检查渲染后 src/bio_analyze_{name}/__init__.py 是否存在
        src_init = package_dir / "src" / package_name / "__init__.py"
        if not src_init.exists():
            src_init.parent.mkdir(parents=True, exist_ok=True)
            src_init.touch()

        # 如果不存在则创建测试目录（理想情况下应该在模板中）
        (package_dir / "tests").mkdir(exist_ok=True)

        typer.echo(f"Successfully created tool '{name}' at {package_dir}")
        typer.echo("Don't forget to run `uv sync` to install the new package!")


class ThemeTemplate(Template):
    """
    zh: 用于创建新绘图主题包的模板。
    en: Template for creating a new plot theme package.
    """

    def __init__(self):
        super().__init__("theme", "Create a new plot theme package")

    def create(self, name: str, output_dir: Path, **kwargs: Any) -> None:
        package_name = name
        target_dir = output_dir / package_name

        if target_dir.exists():
            typer.echo(f"Error: Directory {target_dir} already exists.")
            raise typer.Exit(code=1)

        # 上下文需要下划线名称作为模块路径
        context = {"name": name, "name_underscore": name.replace("-", "_")}

        # 使用递归目录渲染
        self.render_directory(context, target_dir)

        typer.echo(f"Successfully created theme package '{package_name}' at {target_dir}")
        typer.echo(
            f"To use it: `pip install -e {package_name}` then `bioanalyze plot ... --theme {context['name_underscore']}`"
        )


# Registry for templates
TEMPLATES: dict[str, Template] = {
    "tool": ToolTemplate(),
    "theme": ThemeTemplate(),
}


def create_command(
    template_type: str = typer.Argument(None, help="Type of artifact to create (tool, theme).", metavar="TYPE"),
    name: str = typer.Option(None, "--name", "-n", help="Name of the artifact."),
    output: Path = typer.Option(Path.cwd(), "--output", "-o", help="Output directory (default: current directory)."),
) -> None:
    """
    zh: 根据模板创建新工具或主题。
    en: Create a new tool or theme based on a template.

    Args:
        template_type (str, optional):
            zh: 要创建的工件类型 (tool, theme)。
            en: Type of artifact to create (tool, theme).
        name (str, optional):
            zh: 工件名称。
            en: Name of the artifact.
        output (Path, optional):
            zh: 输出目录 (默认为当前目录)。
            en: Output directory (default: current directory).
    """
    # 如果未提供，则进行交互式选择
    if not template_type:
        template_type = Prompt.ask("What do you want to create?", choices=list(TEMPLATES.keys()), default="tool")

    if template_type not in TEMPLATES:
        typer.echo(f"Unknown template type: {template_type}")
        raise typer.Exit(code=1)

    if not name:
        name = Prompt.ask("Enter the name (e.g. 'genomics' or 'dark-mode')")

    template = TEMPLATES[template_type]
    template.create(name, output)
