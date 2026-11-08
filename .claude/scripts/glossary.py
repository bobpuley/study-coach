#!/usr/bin/env python3
"""
Glossary Manager for Markdown glossary tables.

Manages a glossary stored as a Markdown table with columns "Term" and "Definition".
The table must follow the format:

| Term | Definition |
|------|------------|
| **Term1** | definition |
| **Term2** | definition |

All operations read from and write to the file specified by --file.
If only --file is given (no other actions), the help is shown.
"""

import argparse
import sys
import re
from pathlib import Path
from typing import List, Dict, Optional

class Glossary:
    """Represents the glossary with operations on its table."""

    def __init__(self, filepath: str):
        self.filepath = Path(filepath)
        self.header = "| Term | Definition |"
        self.separator = "|------|------------|"
        self.terms: List[Dict[str, str]] = []
        self.before_lines: List[str] = []
        self.after_lines: List[str] = []
        self.dirty = False

    def load(self) -> None:
        """Load the glossary from the file. If file doesn't exist, create empty state."""
        if not self.filepath.exists():
            self.terms = []
            self.before_lines = []
            self.after_lines = []
            return

        with open(self.filepath, 'r', encoding='utf-8') as f:
            lines = [line.rstrip('\n') for line in f]

        header_idx = None
        sep_idx = None
        for i, line in enumerate(lines):
            if line.strip() == self.header:
                header_idx = i
            elif line.strip() == self.separator:
                sep_idx = i

        if header_idx is None or sep_idx is None or sep_idx != header_idx + 1:
            # Malformed table – treat entire file as content before the table
            self.before_lines = lines
            self.after_lines = []
            self.terms = []
            return

        self.before_lines = lines[:header_idx]
        data_start = sep_idx + 1
        data_lines = []
        for i in range(data_start, len(lines)):
            if lines[i].strip().startswith('|'):
                data_lines.append(lines[i])
            else:
                self.after_lines = lines[i:]
                break
        else:
            self.after_lines = []

        self.terms = []
        for row in data_lines:
            parsed = self._parse_row(row)
            if parsed:
                self.terms.append(parsed)

    def _parse_row(self, row: str) -> Optional[Dict[str, str]]:
        parts = [p.strip() for p in row.split('|')]
        if len(parts) < 4:
            return None
        term = parts[1]
        definition = parts[2]
        term = re.sub(r'\*\*', '', term).strip()
        if not term:
            return None
        return {'term': term, 'definition': definition}

    def save(self) -> None:
        """Write the current glossary back to the file."""
        lines = []
        lines.extend(self.before_lines)
        lines.append(self.header)
        lines.append(self.separator)
        for entry in self.terms:
            term = f"**{entry['term']}**"
            definition = entry['definition']
            lines.append(f"| {term} | {definition} |")
        lines.extend(self.after_lines)
        with open(self.filepath, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))
            if lines:
                f.write('\n')
        self.dirty = False

    def create_scaffold(self, learning_path: str) -> None:
        """Create a brand new glossary skeleton with the given title."""
        lines = [
            f"# Glossary — {learning_path}",
            "",
            self.header,
            self.separator,
        ]
        with open(self.filepath, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines) + '\n')
        self.terms = []
        self.before_lines = lines[:2]   # title and blank line
        self.after_lines = []
        self.dirty = False

    def sort(self) -> None:
        self.terms.sort(key=lambda x: x['term'].lower())
        self.dirty = True

    def list_terms(self) -> List[str]:
        return [entry['term'] for entry in self.terms]

    def get_definition(self, term: str) -> Optional[str]:
        for entry in self.terms:
            if entry['term'].lower() == term.lower():
                return entry['definition']
        return None

    def insert(self, term: str, definition: str) -> bool:
        for entry in self.terms:
            if entry['term'].lower() == term.lower():
                return False
        self.terms.append({'term': term, 'definition': definition})
        self.dirty = True
        return True

    def update(self, term: str, definition: str) -> bool:
        for entry in self.terms:
            if entry['term'].lower() == term.lower():
                entry['definition'] = definition
                self.dirty = True
                return True
        return False

    def remove(self, term: str) -> bool:
        for i, entry in enumerate(self.terms):
            if entry['term'].lower() == term.lower():
                del self.terms[i]
                self.dirty = True
                return True
        return False

    def search(self, query: str) -> List[Dict[str, str]]:
        q = query.lower()
        return [e for e in self.terms if q in e['term'].lower() or q in e['definition'].lower()]


def main():
    parser = argparse.ArgumentParser(
        description="Manage a Markdown glossary (table with Term and Definition).",
        epilog="If only --file is given (no other actions), this help is shown.",
        add_help=True
    )
    parser.add_argument(
        '--file', required=True,
        help="Path to the glossary markdown file (mandatory)."
    )
    parser.add_argument(
        '--scaffold', metavar='NAME',
        help="Create a new glossary skeleton with the given learning path name and exit. "
             "Overwrites the file if it exists. Cannot be combined with other operations."
    )
    parser.add_argument(
        '-s', '--sort', action='store_true',
        help="Sort the glossary by Term (case‑insensitive) and save."
    )
    parser.add_argument(
        '-l', '--list', action='store_true',
        help="List all term names (one per line)."
    )
    parser.add_argument(
        '--get', metavar='TERM',
        help="Print the definition of the specified term."
    )
    parser.add_argument(
        '-i', '--insert', nargs=2, metavar=('TERM', 'DEFINITION'),
        help="Insert a new term with its definition. Fails if term already exists."
    )
    parser.add_argument(
        '-u', '--update', nargs=2, metavar=('TERM', 'DEFINITION'),
        help="Update the definition of an existing term. Fails if term not found."
    )
    parser.add_argument(
        '-r', '--remove', metavar='TERM',
        help="Remove the specified term. Fails if term not found."
    )
    parser.add_argument(
        '--search', metavar='STRING',
        help="Search case‑insensitively for STRING in Term or Definition (partial match). "
             "Prints matching rows as 'Term: definition'."
    )

    args = parser.parse_args()

    # If no action is requested (except --file), print help and exit.
    actions = [args.scaffold, args.sort, args.list, args.get,
               args.insert, args.update, args.remove, args.search]
    if not any(actions):
        parser.print_help()
        sys.exit(0)

    # Scaffold is exclusive
    if args.scaffold is not None:
        other_actions = [args.sort, args.list, args.get,
                         args.insert, args.update, args.remove, args.search]
        if any(other_actions):
            print("Error: --scaffold cannot be combined with other operations.", file=sys.stderr)
            sys.exit(1)
        glossary = Glossary(args.file)
        glossary.create_scaffold(args.scaffold)
        print(f"Scaffold created at {args.file} with title 'Glossary — {args.scaffold}'.")
        sys.exit(0)

    # Normal operations
    glossary = Glossary(args.file)
    glossary.load()

    modifications = False

    if args.insert:
        term, definition = args.insert
        if not glossary.insert(term, definition):
            print(f"Error: Term '{term}' already exists.", file=sys.stderr)
            sys.exit(1)
        modifications = True

    if args.update:
        term, definition = args.update
        if not glossary.update(term, definition):
            print(f"Error: Term '{term}' not found.", file=sys.stderr)
            sys.exit(1)
        modifications = True

    if args.remove:
        term = args.remove
        if not glossary.remove(term):
            print(f"Error: Term '{term}' not found.", file=sys.stderr)
            sys.exit(1)
        modifications = True

    if args.sort:
        glossary.sort()
        modifications = True

    if modifications:
        glossary.save()

    # Read-only outputs
    if args.list:
        terms = glossary.list_terms()
        if terms:
            sys.stdout.write('\n'.join(terms) + '\n')

    if args.get:
        definition = glossary.get_definition(args.get)
        if definition is None:
            print(f"Error: Term '{args.get}' not found.", file=sys.stderr)
            sys.exit(1)
        print(definition)

    if args.search:
        results = glossary.search(args.search)
        for entry in results:
            print(f"{entry['term']}: {entry['definition']}")


if __name__ == "__main__":
    main()