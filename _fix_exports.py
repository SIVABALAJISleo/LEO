"""
Auto-fixer for Vite 8 / rolldown `export type` compliance.

For each barrel *index.ts in ui_core/src, this script:
  1. Reads every `export { A, B, C } from "path"` line.
  2. For each name, checks whether the source file declares it as
     `interface`, `type`, or `enum` (type-only) vs `class`, `function`,
     `const`, `let`, `var` (value).
  3. Rewrites the barrel line as:
       export { ValueA, ValueB } from "path"          <- values
       export type { TypeA, TypeB } from "path"       <- types
"""
import re, pathlib

ROOT = pathlib.Path(__file__).parent
UI_SRC = ROOT / "ui_core" / "src"

# Regex to match a barrel export line
EXPORT_RE = re.compile(r'^export \{([^}]+)\} from ["\'](["\']+)["\']', re.MULTILINE)

def find_source_file(barrel_dir: pathlib.Path, rel_import: str) -> pathlib.Path | None:
    """Resolve a relative import path to a .ts file."""
    for ext in (".ts", ".tsx"):
        candidate = (barrel_dir / rel_import).with_suffix(ext)
        if candidate.exists():
            return candidate
        # Try index file
        candidate = barrel_dir / rel_import / ("index" + ext)
        if candidate.exists():
            return candidate
    return None

def classify_names(source_path: pathlib.Path, names: list[str]) -> tuple[list[str], list[str]]:
    """Return (value_names, type_names) for the given name list."""
    try:
        src = source_path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return names, []

    types, values = [], []
    for name in names:
        name = name.strip()
        # Check if declared as type-only construct
        type_patterns = [
            rf'\bexport\s+interface\s+{re.escape(name)}\b',
            rf'\bexport\s+type\s+{re.escape(name)}\b',
            rf'\bexport\s+enum\s+{re.escape(name)}\b',
        ]
        value_patterns = [
            rf'\bexport\s+class\s+{re.escape(name)}\b',
            rf'\bexport\s+(?:async\s+)?function\s+{re.escape(name)}\b',
            rf'\bexport\s+(?:const|let|var)\s+{re.escape(name)}\b',
        ]
        is_type = any(re.search(p, src) for p in type_patterns)
        is_value = any(re.search(p, src) for p in value_patterns)

        if is_type and not is_value:
            types.append(name)
        else:
            values.append(name)
    return values, types

def fix_barrel(barrel_path: pathlib.Path) -> int:
    """Rewrite barrel file with proper export/export type splits. Returns number of lines changed."""
    src = barrel_path.read_text(encoding="utf-8", errors="ignore")
    barrel_dir = barrel_path.parent
    changed = 0
    output_lines = []

    for line in src.splitlines(keepends=True):
        m = re.match(r'^export \{([^}]+)\} from ["\']([^"\']+)["\']', line.strip())
        if not m:
            output_lines.append(line)
            continue

        raw_names = [n.strip() for n in m.group(1).split(",") if n.strip()]
        import_path = m.group(2)

        # Resolve source file (relative to barrel dir)
        if import_path.startswith("../") or import_path.startswith("./"):
            resolved = find_source_file(barrel_dir, import_path)
        else:
            resolved = None

        if not resolved:
            # Can't resolve -> keep original line (safe fallback)
            output_lines.append(line)
            continue

        values, types = classify_names(resolved, raw_names)
        quote = '"' if '"' in line else "'"
        indent = line[: len(line) - len(line.lstrip())]
        new_lines = []
        if values:
            new_lines.append(f"{indent}export {{ {', '.join(values)} }} from {quote}{import_path}{quote};\n")
        if types:
            new_lines.append(f"{indent}export type {{ {', '.join(types)} }} from {quote}{import_path}{quote};\n")
        if not new_lines:
            new_lines = [line]

        if new_lines != [line]:
            changed += 1
        output_lines.extend(new_lines)

    barrel_path.write_text("".join(output_lines), encoding="utf-8")
    return changed

def main():
    barrel_files = list(UI_SRC.rglob("*index.ts"))
    total_changed = 0
    for bf in sorted(barrel_files):
        # Skip test files
        if ".test." in bf.name:
            continue
        n = fix_barrel(bf)
        if n:
            print(f"  Fixed {n} line(s): {bf.relative_to(ROOT)}")
            total_changed += n
        else:
            print(f"  OK (no changes): {bf.relative_to(ROOT)}")

    print(f"\nTotal barrel lines fixed: {total_changed}")

if __name__ == "__main__":
    main()
