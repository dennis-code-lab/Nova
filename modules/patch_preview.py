# modules/patch_preview.py
import difflib

class PatchPreview:
    @staticmethod
    def render_diff(file_path: str, original_code: str, transformed_code: str) -> str:
        """Generates a clean terminal unified diff output."""
        orig_lines = original_code.splitlines(keepends=True)
        trans_lines = transformed_code.splitlines(keepends=True)

        diff = list(difflib.unified_diff(
            orig_lines,
            trans_lines,
            fromfile=f"a/{file_path}",
            tofile=f"b/{file_path}",
            n=2
        ))

        if not diff:
            return f"No changes detected for {file_path}."

        header = [
            f"Previewing Patch for: {file_path}",
            "=" * 50
        ]
        
        formatted_diff = []
        for line in diff:
            stripped = line.rstrip()
            if stripped.startswith("---") or stripped.startswith("+++"):
                formatted_diff.append(stripped)
            elif stripped.startswith("-"):
                formatted_diff.append(f"  [Old] {stripped[1:]}")
            elif stripped.startswith("+"):
                formatted_diff.append(f"  [New] {stripped[1:]}")
            elif stripped.startswith("@@"):
                formatted_diff.append(f"\n{stripped}")

        return "\n".join(header + formatted_diff)