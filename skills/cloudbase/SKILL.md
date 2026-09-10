---
name: cloudbase
description: Use when building, deploying, or debugging Tencent CloudBase (腾讯云开发 / TCB) apps in Trae — Web, WeChat Mini Program, cloud functions, CloudRun, auth, NoSQL/PostgreSQL, storage, and built-in AI. Prefer CloudBase MCP tools first, then load published CloudBase skills for scenario details.
---

# CloudBase (Tencent Cloud Development)

## Description

Guide Trae to develop on **Tencent CloudBase** with the correct order of operations: environment binding → MCP management tools → scenario skill → implementation → review/deploy.

CloudBase covers Web / H5, WeChat Mini Program, cloud functions, CloudRun, document DB / PostgreSQL / MySQL, cloud storage, auth, and built-in AI models.

## Usage Scenario

Use this skill when the user:

- Mentions CloudBase, 云开发, TCB, 腾讯云开发, or WeChat Mini Program cloud development
- Asks to scaffold, deploy, or debug a CloudBase Web / Mini Program / CloudRun app
- Needs auth, database, storage, cloud functions, or CloudBase AI model integration
- Wants Trae wired to `@cloudbase/cloudbase-mcp`

Do **not** use for non-CloudBase backends or pure frontend work with no CloudBase dependency.

## Preconditions

- Trae can run terminal commands and edit project files
- Prefer enabling CloudBase MCP (see below) before management API work
- User should have a Tencent Cloud / CloudBase account (browser login is prompted by MCP)

## Instructions

1. **Confirm scenario** — Web, WeChat Mini Program, CloudRun, database-only, auth-only, or AI model. State which scenario you will follow.
2. **Ensure CloudBase MCP is available in Trae**
   - Settings → MCP → Add → Manual:

```json
{
  "mcpServers": {
    "cloudbase-mcp": {
      "command": "npx",
      "args": ["-y", "@cloudbase/cloudbase-mcp@latest"],
      "env": {}
    }
  }
}
```

   - On first use, complete browser login / environment selection.
3. **Bind environment explicitly**
   - Call `envQuery` (or equivalent) to resolve the canonical `EnvId`.
   - Never pass aliases/nicknames directly into SDK init or deploy configs — resolve to full `EnvId` first.
4. **Prefer MCP tools for management work**
   - Auth providers, DB schema, functions, hosting, CloudRun, storage, security rules: use MCP first.
   - Inspect tool schemas before calling; do not invent parameters.
5. **Load the matching published CloudBase skill before coding**
   - Main entry: https://github.com/TencentCloudBase/skills (or `npx skills add tencentcloudbase/cloudbase-skills`)
   - Common ids: `web-development`, `miniprogram-development`, `auth-tool-cloudbase`, `auth-web-cloudbase`, `cloud-functions`, `cloudrun-development`, `postgresql-development-cloudbase`, `ui-design`, `cloudbase-platform`
   - Read the skill fully before writing application code.
6. **Implementation order**
   - Resource prep via MCP (providers, collections/tables, permissions) → then frontend/backend code → local verify → deploy.
7. **Close-out**
   - Run a CloudBase-aware review when available (`cloudbase-code-review` skill).
   - Report EnvId, resources touched, and preview/deploy URLs.

## Examples

### Example 1 — Web app with username/password auth

**User:** “用云开发做一个带登录的 Web 管理后台”

**Agent should:**

1. Enable CloudBase MCP and bind `EnvId`
2. Use auth MCP tools to enable username/password (and publishable key) before writing login UI
3. Follow `auth-tool-cloudbase` then `auth-web-cloudbase` / `web-development`
4. Deploy static hosting only after auth providers are confirmed

### Example 2 — WeChat Mini Program CRUD

**User:** “小程序云开发读写文档数据库”

**Agent should:**

1. Confirm Mini Program + CloudBase scenario
2. Use NoSQL MCP tools / `cloudbase-document-database-in-wechat-miniprogram` guidance
3. Avoid Web SDK auth patterns in Mini Program code

## References

- Docs: https://docs.cloudbase.net/ai/cloudbase-ai-toolkit/ai-agent-plugins
- Toolkit source: https://github.com/TencentCloudBase/CloudBase-AI-Toolkit
- Open Plugin / skills package: https://github.com/TencentCloudBase/cloudbase-plugin
- Published skills: https://github.com/TencentCloudBase/skills

## Constraints

- Do not invent CloudBase API paths or MCP tool arguments
- Do not expose API keys / `service_role` credentials in frontend code
- After 2–3 failed attempts on the same path, stop and reroute (env, auth domain, permission model, or skill)
