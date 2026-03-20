import subprocess


def generate_changelog(package_name, version):
    print(f"Generating changelog for {package_name}...")
    # Get commits for this specific package
    cmd = ["git", "log", "--format=%H", "--", f"packages/{package_name}"]
    result = subprocess.run(cmd, capture_capture=True, text=True)
    if result.returncode != 0:
        print(f"Error getting git log: {result.stderr}")
        return

    commits = result.stdout.strip().split("\n")
    if not commits or not commits[0]:
        print(f"No commits found for {package_name}")
        return

    # How to pass these commits to commitizen?
    # Unfortunately, commitizen doesn't support filtering commits by path directly in its CLI.
    # It seems we need a custom script or another tool.
