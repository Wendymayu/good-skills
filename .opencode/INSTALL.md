# Installing Good Skills for OpenCode

## Prerequisites

- [OpenCode.ai](https://opencode.ai) installed

## Installation

Add good-skills to the `plugin` array in your `opencode.json` (global or project-level):

```json
{
  "plugin": ["good-skills@git+https://github.com/Wendymayu/good-skills.git"]
}
```

Restart OpenCode. The plugin installs through OpenCode's plugin manager and
registers all skills.

Verify by asking: "Research the latest in LLM observability"

## Usage

Use OpenCode's native `skill` tool:

```
use skill tool to list skills
use skill tool to load good-skills/research-observe
```

## Updating

OpenCode installs good-skills through a git-backed package spec. If updates do
not appear, clear OpenCode's package cache or reinstall the plugin.

To pin a specific version:

```json
{
  "plugin": ["good-skills@git+https://github.com/Wendymayu/good-skills.git#v0.2.0"]
}
```

## Troubleshooting

### Plugin not loading

1. Check logs: `opencode run --print-logs "hello" 2>&1 | grep -i good-skills`
2. Verify the plugin line in your `opencode.json`

### Skills not found

1. Use `skill` tool to list what's discovered
2. Check that the plugin is loading (see above)

### Tool mapping

When skills reference Claude Code tools:
- `TodoWrite` → `todowrite`
- `Task` with subagents → `@mention` syntax
- `Skill` tool → OpenCode's native `skill` tool
- File operations → your native tools
- `WebSearch`, `WebFetch` → OpenCode's native web tools (if available)

### Windows install issues

Try installing with system npm and pointing OpenCode at the local package:

```powershell
npm install good-skills@git+https://github.com/Wendymayu/good-skills.git --prefix "$HOME\.config\opencode"
```

Then use the installed package path in `opencode.json`:

```json
{
  "plugin": ["~/.config/opencode/node_modules/good-skills"]
}
```
