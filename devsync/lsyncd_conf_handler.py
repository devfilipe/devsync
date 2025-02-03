import os
import json
import re

def load_config(config_path):
    """
    Loads sync entries from a Lua configuration file that contains a settings block
    and one or more sync blocks.

    Each sync block may be preceded by a comment line with the alias in the format:
      -- alias: <alias>

    Returns a list of dictionaries with at least the following keys:
      - alias (optional)
      - source
      - target
      - port (extracted from the rsh line, defaulting to 22)
      - binary (if present; otherwise None)
      - on_event (this example does not parse the onEvent block; assume empty list)
    """
    if not os.path.exists(config_path):
        return []

    with open(config_path, "r") as f:
        content = f.read()

    pattern = re.compile(
        r'(?:--\s*alias:\s*(?P<alias>.+?)\s*\n)?\s*sync\s*{(?P<block>.*?)}',
        re.DOTALL
    )

    entries = []
    for m in pattern.finditer(content):
        entry = {}
        alias = m.group("alias")
        if alias:
            entry["alias"] = alias.strip()
        block = m.group("block")

        # Extract source
        m_source = re.search(r'source\s*=\s*"([^"]+)"', block)
        entry["source"] = m_source.group(1).strip() if m_source else ""

        # Extract target
        m_target = re.search(r'target\s*=\s*"([^"]+)"', block)
        entry["target"] = m_target.group(1).strip() if m_target else ""

        # Extract port from rsh line, e.g.: rsh      = "ssh -p 22",
        m_port = re.search(r'rsh\s*=\s*"ssh\s+-p\s+(\d+)"', block)
        entry["port"] = int(m_port.group(1)) if m_port else 22

        # Extract binary if present
        m_binary = re.search(r'binary\s*=\s*"([^"]+)"', block)
        entry["binary"] = m_binary.group(1).strip() if m_binary else None

        entry["on_event"] = []  # Simplification; not parsing onEvent block

        entries.append(entry)

    return entries

def save_config(config_path, syncs):
    """
    Generates a Lua configuration file for Lsyncd.
    The file will contain a 'settings' block and, for each sync entry,
    a 'sync { ... }' block.

    For each sync entry:
      - If an alias is provided, a preceding comment line "-- alias: <alias>" is output.
      - The rsync block is built including the binary handler if defined.
    """
    config_lines = []
    # Settings block
    config_lines.append("settings {")
    config_lines.append('    logfile    = "/tmp/lsyncd.log",         -- Log file path')
    config_lines.append('    statusFile = "/tmp/lsyncd-status.log",  -- Status file path')
    config_lines.append("    nodaemon   = false,                     -- Run in background or foreground")
    config_lines.append("}\n")

    # For each sync entry, generate a sync block
    for sync in syncs:
        alias = sync.get("alias", "").strip()
        source = sync.get("source", "")
        target = sync.get("target", "")
        port = sync.get("port", 22)
        binary = sync.get("binary")

        # If alias exists, add a comment line with alias.
        if alias:
            config_lines.append(f"-- alias: {alias}")
        config_lines.append("sync {")
        config_lines.append("    default.rsync,")
        config_lines.append(f'    source = "{source}",')
        config_lines.append(f'    target = "{target}",')
        # (Optional) onEvent block can be added here if desired.
        config_lines.append("    rsync  = {")
        config_lines.append(f'        rsh      = "ssh -p {port}",')
        config_lines.append("        archive  = true,")
        config_lines.append("        compress = true,")
        config_lines.append("        verbose  = true,")
        config_lines.append('        _extra   = {"--delete"},')
        # Add the binary option if defined (and non-empty)
        if binary and binary.strip():
            config_lines.append(f'        binary   = "{binary.strip()}",')
        config_lines.append("    }")
        config_lines.append("}\n")

    with open(config_path, "w") as f:
        f.write("\n".join(config_lines))
