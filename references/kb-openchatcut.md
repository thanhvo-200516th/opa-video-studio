# kb-openchatcut — toàn văn tài liệu của nguồn `openchatcut`

> Trong `opa-video-studio`: mọi chỗ nhắc tới skill/mô-đun khác ("nạp X", "dùng skill X", `modules/X/MODULE.md`) = đọc `references/kb-X.md` trong chính skill này. Code / dữ liệu của nguồn này (nếu có) nằm ở `scripts/apps/openchatcut/` (riêng nguồn lõi `master-video-edit`: `scripts/`, `assets/`, `tests/`). Nội dung dưới đây giữ NGUYÊN VĂN bản gốc; luật hiện hành và cách giải mâu thuẫn nằm ở `references/rules-full.md` + `rules.json`.

<!-- ===== file: openchatcut/SKILL.md ===== -->

---
name: openchatcut
description: Connect an MCP-capable coding agent to OpenChatCut and edit local video projects. Use when the user asks to install, connect, or set up OpenChatCut; inspect or edit an OpenChatCut project; work with its timeline, transcript, captions, media, generation, motion graphics, audio, color, or export tools; or recover from an OpenChatCut MCP error.
---

# OpenChatCut

OpenChatCut is a local-first, agent-native video editor. This skill is the
single external entry point; specialized editing guidance remains inside the
running editor and is loaded on demand with `load_skill`.

## Route the task

- Install, connect, or diagnose the MCP server: read
  `references/getting-started.md`.
- Inspect or modify a project: read `references/editing-workflow.md`.
- Recover from a failed tool call, stale session, or missing editor:
  read `references/known-errors.md`.

## Essentials

1. Start OpenChatCut before connecting. The default MCP endpoint is
   `http://localhost:5199/api/external-mcp/mcp`.
2. Call `openchatcut_status`, then `list_projects`. Select a project only when
   the user names it or the current context identifies it.
3. Call `load_skill` before specialized work. It is read-only and requires
   neither `begin_edit_session` nor `editSessionId`; available names and support
   files come from the live MCP tool description.
   With progressive exposure enabled, this call reveals the skill's referenced
   tools and emits `tools/list_changed`; refresh the list before continuing.
4. Before project reads or edits, call `begin_edit_session`. Keep its
   `editSessionId` and pass it to every draft-safe editor tool.
5. Set `reuseExisting: true` on `begin_edit_session` to reuse your active draft
   or adopt an unchanged orphan. Existing operations and approval mode are kept.
   If reuse is rejected, call `list_edit_sessions`. Use `recover_edit_session`
   only with a listed `recoveryActions` value; another online owner must finish
   or discard its own session.
6. Use `approvalMode: "manual"` unless the user explicitly asks for unattended
   application. In manual mode, the user approves the complete proposal in
   OpenChatCut. In auto mode, `review_edit_session` applies the complete draft.
7. Finish with `review_edit_session`. Report success only after
   `get_edit_session` returns `applied`.

## Skill version

`2026-09-04.1`

The OpenChatCut MCP server announces its required skill baseline. If the server
baseline is newer, run:

```bash
npx skills update openchatcut
```

Fallback command:

```bash
npx skills add 0xsline/OpenChatCut --skill openchatcut
```

<!-- ===== /file: openchatcut/SKILL.md ===== -->

<!-- ===== file: openchatcut/references/editing-workflow.md ===== -->

# Edit an OpenChatCut project

## Start with current state

1. Call `openchatcut_status`.
2. Call `list_projects` when the project is not already identified.
3. Call `target_project` with the selected project ID.
4. When specialized guidance applies, call `load_skill`; it requires no edit
   session or `editSessionId`.
5. Call `begin_edit_session` and keep the returned `editSessionId`.
6. Call `read_project` with that session ID before the first mutation.

Use `approvalMode: "manual"` by default. Use `"auto"` only when the user asks
for an unattended, atomic application.

## Load specialized guidance

Call `load_skill` after targeting the project and before specialized work. Common skill names include:

- `talking-head-guide`
- `transcription`
- `create-motion-graphics`
- `image-gen`
- `video-gen`
- `voice`
- `music`
- `shader-gen`
- `export`
- `verification`

Treat the live `load_skill` tool description as the current catalog. If a
loaded skill lists support files, request the relevant one with its `file`
argument.

## Apply edits

- Use IDs returned by `read_project`, discovery tools, or prior receipts.
- Keep every editor call in the same edit session.
- Re-read the project after a failed mutation or when the timeline may be
  stale.
- Use `view_timeline_frames`, `inspect_color`, or the verification skill after
  visual edits.
- Keep generation and other immediate side effects outside a proposal unless
  the exposed tool explicitly supports the draft session.

## Review and finish

1. Call `review_edit_session` after all draft edits are ready.
2. For manual mode, tell the user the proposal is ready inside OpenChatCut.
3. Poll `get_edit_session` when the client needs the final state.
4. Report completion only when the status is `applied`.
5. If the status is `rejected` or `discarded`, report that exact result.

Applied operations form one atomic undo step.

<!-- ===== /file: openchatcut/references/editing-workflow.md ===== -->

<!-- ===== file: openchatcut/references/getting-started.md ===== -->

# Connect OpenChatCut

Use this flow when the user says “set up OpenChatCut”, when the `openchatcut`
MCP server is missing, or when its endpoint cannot be reached.

## 1. Find the endpoint

The default endpoint is:

```text
http://localhost:5199/api/external-mcp/mcp
```

Start OpenChatCut first. Open **Settings → MCP** in the trusted editor window,
copy the displayed bearer-token configuration, and use the endpoint shown there.
If desktop port 5199 was occupied, that page reflects the active fallback port.

## 2. Register the MCP server

### Codex

Check the existing entry:

```bash
codex mcp get openchatcut
```

If it is missing, export the token copied from **Settings → MCP** and register it:

```bash
export OPENCHATCUT_MCP_TOKEN='<token>'
codex mcp add openchatcut \
  --url http://localhost:5199/api/external-mcp/mcp \
  --bearer-token-env-var OPENCHATCUT_MCP_TOKEN
```

If an existing URL or token setting is stale, replace only that entry:

```bash
export OPENCHATCUT_MCP_TOKEN='<token>'
codex mcp remove openchatcut
codex mcp add openchatcut \
  --url http://localhost:5199/api/external-mcp/mcp \
  --bearer-token-env-var OPENCHATCUT_MCP_TOKEN
```

### Claude Code

```bash
claude mcp add --transport http \
  -H "Authorization: Bearer <token>" \
  openchatcut http://localhost:5199/api/external-mcp/mcp
```

For another client, register the endpoint as a Streamable HTTP MCP server and
set its `Authorization` header to `Bearer <token>`.
Clients that honor MCP `tools/list_changed` can reduce their initial prompt by
negotiating progressive exposure:

```text
http://localhost:5199/api/external-mcp/mcp?toolExposure=progressive
```

The equivalent request header is
`X-OpenChatCut-Tool-Exposure: progressive`. The initial list keeps connection,
session, project-read, `ToolSearch`, and `load_skill` tools. `ToolSearch` and
`load_skill` expand only that transport session's list. Clients that cache one
fixed tool list for the whole connection must use the default URL, which retains
the full compatibility surface.


## 3. Verify

When the MCP tools are available, call:

1. `openchatcut_status`
2. `list_projects`

Interpret the result:

- Editors listed: the live editor bridge is ready.
- Projects listed but no editor connected: project discovery works; open the
  intended project using its `editorUrl`.
- No projects: the connection works; ask whether to create a project.
- Connection error: follow `known-errors.md`.

Do not create or select a project just because one looks plausible.

## 4. Start the first task

Once the user has identified a project:

1. Call `target_project`.
2. Surface the URL returned by `get_editor_url`.
3. Follow `editing-workflow.md`.

## Token lifecycle

The endpoint always requires a bearer token, including on localhost. By default,
OpenChatCut generates it in private server memory and shows it only through the
trusted editor's **Settings → MCP** page. A server restart changes that generated
token, so reconnect clients using the newly displayed configuration.

`OPENCHATCUT_MCP_TOKEN` overrides the generated token when a stable deployment
secret is required. Keep it in the MCP client's secret/environment configuration;
never write it into a repository, project document, chat, or browser storage.

<!-- ===== /file: openchatcut/references/getting-started.md ===== -->

<!-- ===== file: openchatcut/references/known-errors.md ===== -->

# OpenChatCut MCP recovery

## Connection refused

OpenChatCut is closed, the configured URL is stale, or desktop port 5199 fell
back to another port.

1. Start OpenChatCut.
2. Read the endpoint from **Settings → MCP** or the startup log.
3. Update the single `openchatcut` MCP entry.
4. Call `openchatcut_status` again.

## Projects exist but no editor is connected

Call `get_editor_url` for the intended project and have the user open it.
Project listing and creation can work without a live editor, while timeline
tools require the target project to be open.

## Tool missing

The editor registers project tools after its bridge connects. Open the target
project, call `openchatcut_status`, and refresh the MCP tool list.

## Active edit session

`begin_edit_session` rejects an existing draft unless `reuseExisting: true` is
set. Reuse keeps the session ID, staged operations and approval mode. It can
reuse a draft owned by the same MCP transport or adopt an unchanged orphan.
It cannot take a draft from another online transport or a recovery in progress,
and it does not bypass stale-project checks.

## Stale edit session

Call `list_edit_sessions` before starting another session. For an entry marked
`orphaned: true`, call `recover_edit_session` with one of its `recoveryActions`:

- `resume` continues a draft only when its checkpoint still matches the project.
- `discard` removes the abandoned draft without changing the live project.

An online owner must finish or discard its own session. Terminal `stale`,
`cancelled`, and `failed` sessions cannot be resumed; begin a fresh session.
An auto session stays auto and does not fall back to manual review.

## Proposal awaiting review

The draft is ready, but manual approval is still pending in OpenChatCut. Keep
polling `get_edit_session` only when the client needs the final state. Report
`applied`, `rejected`, or `discarded` exactly as returned.

## Skill baseline is newer

Update the installed skill, then re-read its files:

```bash
npx skills update openchatcut
```

If the source alias is unavailable:

```bash
npx skills add 0xsline/OpenChatCut --skill openchatcut
```

<!-- ===== /file: openchatcut/references/known-errors.md ===== -->
