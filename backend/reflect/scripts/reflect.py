#!/usr/bin/env python3
"""
Main reflection orchestration engine.
Coordinates signal extraction, skill updates, and user review.
"""

import json
import sys
import os
from pathlib import Path
from datetime import datetime
import subprocess

# Add scripts directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from extract_signals import extract_signals
from update_skill import update_skill
from present_review import present_review

def main():
    """Main reflection workflow"""
    # 1. Get transcript path from env or argument
    transcript_path = os.getenv('TRANSCRIPT_PATH') or (sys.argv[1] if len(sys.argv) > 1 else None)

    print("🧠 Reflection Analysis Starting...")

    # 2. Extract signals from transcript
    try:
        signals_by_skill = extract_signals(transcript_path)
    except Exception as e:
        print(f"✗ Error extracting signals: {e}")
        return 1

    if not signals_by_skill:
        print("✓ No improvement suggestions found")
        return 0

    print(f"Found signals in {len(signals_by_skill)} skill(s)")

    # 3. Present for review
    try:
        approved_changes = present_review(signals_by_skill)
    except KeyboardInterrupt:
        print("\n\nReview interrupted by user")
        return 1
    except Exception as e:
        print(f"✗ Error during review: {e}")
        return 1

    if not approved_changes:
        print("\nNo changes approved")
        return 0

    # 4. Apply changes with backups
    success_count = 0
    for change in approved_changes:
        try:
            if update_skill(change):
                success_count += 1
        except Exception as e:
            print(f"✗ Error updating {change['skill_name']}: {e}")

    if success_count == 0:
        print("\n✗ No skills were updated successfully")
        return 1

    # 5. Git commit
    try:
        commit_changes(approved_changes)
    except Exception as e:
        print(f"Warning: Git commit failed: {e}")
        print("Changes were applied but not committed. Commit manually if needed.")

    print(f"\n✓ {success_count} skill(s) updated successfully")

    # 6. Update reflection timestamp
    update_last_reflection_timestamp()

    return 0

def commit_changes(changes):
    """Commit skill updates to git"""
    skills_dir = Path.home() / '.claude' / 'skills'

    # Check if git repo exists
    if not (skills_dir / '.git').exists():
        print("\nNote: Skills directory is not a git repository")
        print("Initialize with: cd ~/.claude/skills && git init")
        return

    skill_names = [c['skill_name'] for c in changes]

    # Build commit message
    message_lines = ["refactor(skills): apply reflection learnings\n"]
    message_lines.append("Signals detected:")

    for change in changes:
        proposed = change.get('proposed_updates', {})
        high_count = len(proposed.get('high_confidence', []))
        medium_count = len(proposed.get('medium_confidence', []))
        low_count = len(proposed.get('low_confidence', []))

        if high_count:
            message_lines.append(f"- HIGH ({high_count}): {change['skill_name']}")
        if medium_count:
            message_lines.append(f"- MEDIUM ({medium_count}): {change['skill_name']}")
        if low_count:
            message_lines.append(f"- LOW ({low_count}): {change['skill_name']}")

    message_lines.append(f"\nSkills updated: {', '.join(skill_names)}\n")

    # Add session info if available
    session_id = os.getenv('SESSION_ID', 'unknown')
    auto_reflected = os.getenv('AUTO_REFLECTED', 'false')
    message_lines.append(f"Session: {session_id}")
    message_lines.append(f"Auto-reflected: {auto_reflected}\n")

    message_lines.append("🤖 Generated with [Claude Code](https://claude.com/claude-code)")
    message_lines.append("Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>")

    commit_message = "\n".join(message_lines)

    try:
        # Stage all changes in skills directory
        subprocess.run(['git', 'add', '.'], cwd=skills_dir, check=True, capture_output=True)

        # Commit
        subprocess.run(['git', 'commit', '-m', commit_message], cwd=skills_dir, check=True, capture_output=True)

        print("\n✓ Changes committed to git")

        # Note: We don't auto-push for safety
        # User can push manually if they want
        print("  (Run 'cd ~/.claude/skills && git push' to push to remote)")

    except subprocess.CalledProcessError as e:
        # Check if it's just "nothing to commit"
        if b'nothing to commit' in e.stdout or b'nothing to commit' in e.stderr:
            print("\nNote: Git reported nothing to commit (files may be unchanged)")
        else:
            raise

def update_last_reflection_timestamp():
    """Update the last reflection timestamp to prevent duplicates"""
    timestamp_file = Path.home() / '.claude' / 'skills' / 'reflect' / '.state' / 'last-reflection.timestamp'
    try:
        with open(timestamp_file, 'w') as f:
            f.write(datetime.now().isoformat())
    except Exception as e:
        print(f"Warning: Could not update timestamp: {e}")

if __name__ == '__main__':
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\nReflection cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
