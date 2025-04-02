"""Generate the API reference pages and navigation."""

from pathlib import Path
import mkdocs_gen_files

nav = mkdocs_gen_files.Nav()

# Root path to the source code
src_root = Path("nubby")
# Destination path in the docs
dest_root = Path("reference")

# Iterate through all Python files
for path in sorted(src_root.rglob("*.py")):
    module_path = path.relative_to(src_root).with_suffix("")
    doc_path = dest_root / path.relative_to(src_root).with_suffix(".md")
    full_doc_path = Path("docs", doc_path)

    parts = tuple(module_path.parts)

    # Skip __init__.py files for navigation but still generate docs
    if parts[-1] == "__init__":
        parts = parts[:-1]
        doc_path = doc_path.with_name("index.md")
        full_doc_path = full_doc_path.with_name("index.md")
    elif parts[-1] == "__main__":
        continue

    # Create the navigation structure
    if parts:
        nav[parts] = doc_path.as_posix()

    # Create the Markdown file with the appropriate mkdocstrings directive
    with mkdocs_gen_files.open(full_doc_path, "w") as fd:
        identifier = "nubby"
        if parts:
            identifier = "nubby." + ".".join(parts)
        
        fd.write(f"# {identifier}\n\n")
        fd.write(f":::{identifier}\n")

# Write the navigation file
with mkdocs_gen_files.open("reference/SUMMARY.md", "w") as nav_file:
    nav_file.writelines(nav.build_literate_nav())
