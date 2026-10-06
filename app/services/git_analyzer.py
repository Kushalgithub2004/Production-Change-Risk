def parse_diff(diff_text: str):
    """
    Parses a unified diff string and returns basic metrics like:
    - lines_added
    - lines_deleted
    - files_changed
    """
    lines_added = 0
    lines_deleted = 0
    files = set()
    
    for line in diff_text.split('\n'):
        if line.startswith('+++ b/'):
            files.add(line[6:])
        elif line.startswith('+') and not line.startswith('+++'):
            lines_added += 1
        elif line.startswith('-') and not line.startswith('---'):
            lines_deleted += 1
            
    return {
        "files_changed": len(files),
        "lines_added": lines_added,
        "lines_deleted": lines_deleted,
        "files_list": list(files)
    }
