# Directory Index — {{PROJECT_NAME}}

Record time: {{DATE}}
Authority: `AGENTS.md` directory rules + `governance.py index`
Changes: {{CHANGES}}

## Root layout
```
{{PROJECT_ROOT}}
├── 🔴 Core spec zone
│   ├── [AGENTS.md](AGENTS.md) — project protocol
│   ├── [ARCHITECTURE.md](ARCHITECTURE.md) — system architecture
│   ├── [PROJECT.md](PROJECT.md) — project card
│   └── [index.md](index.md) — this file (authoritative map)
├── 🟡 Core code zone
│   └── ...
├── 🟢 Agent workspace
│   ├── [LESSONS.md](LESSONS.md) — AI error & correction log
│   └── [session_handoff.md](session_handoff.md) — end-of-session handoff
├── 📂 Reference / assets (read-only)
└── 🗑️ Archived (read-only)
```

## Change log
| Time | Change | Notes |
|---|---|---|
| {{DATE}} | Initial record | ... |

> 目录树区块（`## Root layout` 的代码块）由 `governance.py index` 独占维护：
> 每次运行会整体重写该区块，并把头部 `Record time` 更新为 UTC 日期。
> 两个区块标题之间只保留机器生成的代码块——如需人工补充内容，请写在
> `## Change log` 之后，或放入 `index_notes.json` / 自定义 section。
> 若检测到两个标题之间存在人工内容，`index` 默认停止并提示，确认覆盖需加 `--force`。
> 本文件的 Change log 只是 `CHANGELOG.md` 的镜像，决策与状态变化以 `CHANGELOG.md` 为唯一事实源。
