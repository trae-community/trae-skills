#!/usr/bin/env node

const fs = require("fs");

const DEFAULT_IGNORED_USERS = new Set(["github-actions[bot]"]);

function getArg(flag) {
  const index = process.argv.indexOf(flag);
  if (index === -1 || index + 1 >= process.argv.length) {
    return undefined;
  }
  return process.argv[index + 1];
}

function readJson(path) {
  const raw = fs.readFileSync(path, "utf8").replace(/^\uFEFF/, "");
  return JSON.parse(raw);
}

function getDispatchInput(payload, key) {
  if (!payload || !payload.inputs || typeof payload.inputs !== "object") {
    return "";
  }
  const value = payload.inputs[key];
  if (value === undefined || value === null) {
    return "";
  }
  return String(value).trim();
}

function parsePositiveInteger(rawValue, fallbackValue) {
  if (rawValue === undefined || rawValue === null || String(rawValue).trim() === "") {
    return fallbackValue;
  }
  const parsed = Number.parseInt(String(rawValue), 10);
  if (!Number.isFinite(parsed) || parsed <= 0) {
    return fallbackValue;
  }
  return parsed;
}

function normalizeEventKeySegment(value, fallback) {
  const normalized = String(value || "")
    .toLowerCase()
    .replace(/[^a-z0-9._:-]+/g, "-")
    .replace(/^-+|-+$/g, "");
  return normalized || fallback;
}

function toIsoDate(dateStr) {
  if (!dateStr) {
    return "";
  }
  const value = new Date(dateStr);
  if (Number.isNaN(value.getTime())) {
    return "";
  }
  return value.toISOString();
}

function parseRepository(repo) {
  if (!repo || typeof repo !== "string" || !repo.includes("/")) {
    return null;
  }
  const [owner, name] = repo.split("/", 2);
  if (!owner || !name) {
    return null;
  }
  return { owner, repo: name };
}

function buildIgnoredUsers(raw) {
  const users = new Set(Array.from(DEFAULT_IGNORED_USERS, (item) => item.toLowerCase()));
  if (!raw) {
    return users;
  }
  for (const item of raw.split(",")) {
    const login = item.trim().toLowerCase();
    if (login) {
      users.add(login);
    }
  }
  return users;
}

function isIgnoredUser(login, ignoredUsers) {
  if (!login) {
    return true;
  }
  const normalized = login.toLowerCase();
  return ignoredUsers.has(normalized) || normalized.endsWith("[bot]");
}

function extractIssueNumbersFromPr(pr, owner, repo) {
  const text = `${pr.title || ""}\n${pr.body || ""}`;
  if (!text.trim()) {
    return [];
  }

  const issueNumbers = new Set();

  const localRefPattern =
    /\b(?:close[sd]?|fix(?:e[sd])?|resolve[sd]?)\s+#(\d+)\b/gi;
  let match = localRefPattern.exec(text);
  while (match) {
    issueNumbers.add(Number(match[1]));
    match = localRefPattern.exec(text);
  }

  const repoRefPattern =
    /\b(?:close[sd]?|fix(?:e[sd])?|resolve[sd]?)\s+([a-z0-9_.-]+)\/([a-z0-9_.-]+)#(\d+)\b/gi;
  match = repoRefPattern.exec(text);
  while (match) {
    if (
      match[1].toLowerCase() === owner.toLowerCase() &&
      match[2].toLowerCase() === repo.toLowerCase()
    ) {
      issueNumbers.add(Number(match[3]));
    }
    match = repoRefPattern.exec(text);
  }

  const urlPattern =
    /\b(?:close[sd]?|fix(?:e[sd])?|resolve[sd]?)\s+https?:\/\/github\.com\/([a-z0-9_.-]+)\/([a-z0-9_.-]+)\/issues\/(\d+)\b/gi;
  match = urlPattern.exec(text);
  while (match) {
    if (
      match[1].toLowerCase() === owner.toLowerCase() &&
      match[2].toLowerCase() === repo.toLowerCase()
    ) {
      issueNumbers.add(Number(match[3]));
    }
    match = urlPattern.exec(text);
  }

  return Array.from(issueNumbers).sort((a, b) => a - b);
}

function loadPoints(path) {
  if (!fs.existsSync(path)) {
    return { scores: {}, ledger: {} };
  }

  const data = readJson(path);
  if (!data || typeof data !== "object") {
    return { scores: {}, ledger: {} };
  }

  if (!data.scores || typeof data.scores !== "object") {
    data.scores = {};
  }

  if (!data.ledger || typeof data.ledger !== "object") {
    data.ledger = {};
  }

  return data;
}

function formatLeaderboard(pointsData) {
  const entries = Object.entries(pointsData.scores || {})
    .filter((entry) => Number(entry[1]) > 0)
    .sort((left, right) => {
      if (Number(right[1]) !== Number(left[1])) {
        return Number(right[1]) - Number(left[1]);
      }
      return left[0].localeCompare(right[0]);
    });

  const lines = [
    "# Community Leaderboard",
    "",
    "| Rank | User | Points |",
    "| --- | --- | ---: |",
  ];

  if (entries.length === 0) {
    lines.push("| - | _No contributors yet_ | 0 |");
  } else {
    for (let index = 0; index < entries.length; index += 1) {
      const [login, score] = entries[index];
      lines.push(`| ${index + 1} | @${login} | ${Number(score)} |`);
    }
  }

  lines.push("");
  lines.push(`Updated at: ${new Date().toISOString()}`);

  return `${lines.join("\n")}\n`;
}

async function githubGraphql(token, query, variables) {
  const response = await fetch("https://api.github.com/graphql", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
      "User-Agent": "community-points-workflow",
    },
    body: JSON.stringify({ query, variables }),
  });

  if (!response.ok) {
    throw new Error(`GraphQL request failed: ${response.status}`);
  }

  const payload = await response.json();
  if (payload.errors && payload.errors.length > 0) {
    throw new Error(`GraphQL response error: ${payload.errors[0].message}`);
  }

  return payload.data;
}

function pickResolverFromTimeline(nodes) {
  const candidates = [];
  for (const node of nodes || []) {
    if (
      node &&
      node.__typename === "ClosedEvent" &&
      node.closer &&
      node.closer.__typename === "PullRequest" &&
      node.closer.merged &&
      node.closer.author &&
      node.closer.author.login
    ) {
      candidates.push({
        prNumber: node.closer.number,
        login: node.closer.author.login,
        mergedAt: toIsoDate(node.closer.mergedAt),
      });
    }

    if (
      node &&
      node.__typename === "CrossReferencedEvent" &&
      node.source &&
      node.source.__typename === "PullRequest" &&
      node.source.merged &&
      node.source.author &&
      node.source.author.login
    ) {
      candidates.push({
        prNumber: node.source.number,
        login: node.source.author.login,
        mergedAt: toIsoDate(node.source.mergedAt),
      });
    }
  }

  if (candidates.length === 0) {
    return null;
  }

  candidates.sort((left, right) => {
    if (left.mergedAt && right.mergedAt && left.mergedAt !== right.mergedAt) {
      return right.mergedAt.localeCompare(left.mergedAt);
    }
    return right.prNumber - left.prNumber;
  });

  return candidates[0];
}

async function findIssueResolverByMergedPr(input) {
  const { owner, repo, issueNumber, token } = input;
  if (!token) {
    return null;
  }

  const query = `
    query IssueResolver($owner: String!, $repo: String!, $issueNumber: Int!) {
      repository(owner: $owner, name: $repo) {
        issue(number: $issueNumber) {
          timelineItems(first: 100, itemTypes: [CLOSED_EVENT, CROSS_REFERENCED_EVENT]) {
            nodes {
              __typename
              ... on ClosedEvent {
                closer {
                  __typename
                  ... on PullRequest {
                    number
                    merged
                    mergedAt
                    author {
                      login
                    }
                  }
                }
              }
              ... on CrossReferencedEvent {
                source {
                  __typename
                  ... on PullRequest {
                    number
                    merged
                    mergedAt
                    author {
                      login
                    }
                  }
                }
              }
            }
          }
        }
      }
    }
  `;

  const data = await githubGraphql(token, query, { owner, repo, issueNumber });
  const issue = data && data.repository && data.repository.issue;
  if (!issue || !issue.timelineItems) {
    return null;
  }

  return pickResolverFromTimeline(issue.timelineItems.nodes);
}

async function resolveEvent(payload, context) {
  const { eventName, actor, token, owner, repo, manualRunId } = context;
  if (eventName === "workflow_dispatch") {
    const manualUser = getDispatchInput(payload, "manual_user");
    const manualReason =
      getDispatchInput(payload, "manual_reason") || "Manual points adjustment";
    const manualPoints = parsePositiveInteger(
      getDispatchInput(payload, "manual_points"),
      1
    );
    const customEventKey = getDispatchInput(payload, "manual_event_key");
    const eventSuffix = customEventKey
      ? normalizeEventKeySegment(customEventKey, "manual")
      : `run-${normalizeEventKeySegment(manualRunId, String(Date.now()))}`;

    if (!manualUser) {
      return [];
    }

    return [
      {
        eventKey: `manual:${eventSuffix}:${manualUser.toLowerCase()}`,
        login: manualUser,
        points: manualPoints,
        reason: manualReason,
      },
    ];
  }

  if (
    eventName === "pull_request" &&
    payload.action === "closed" &&
    payload.pull_request &&
    payload.pull_request.merged === true
  ) {
    const prNumber = payload.pull_request.number;
    const login = payload.pull_request.user && payload.pull_request.user.login;
    const events = [
      {
        eventKey: `pr:${prNumber}:merged`,
        login,
        points: 1,
        reason: `PR #${prNumber} merged`,
      },
    ];

    const issueNumbers = extractIssueNumbersFromPr(payload.pull_request, owner, repo);
    for (const issueNumber of issueNumbers) {
      events.push({
        eventKey: `issue:${issueNumber}:resolved-by-pr:${prNumber}`,
        login,
        points: 1,
        reason: `Issue #${issueNumber} resolved by merged PR #${prNumber}`,
      });
    }

    return events;
  }

  if (eventName === "issues" && payload.action === "closed" && payload.issue) {
    const issueNumber = payload.issue.number;
    const closedBy =
      (payload.issue.closed_by && payload.issue.closed_by.login) || actor;
    let resolvedBy = null;

    if (owner && repo && token) {
      try {
        resolvedBy = await findIssueResolverByMergedPr({
          owner,
          repo,
          issueNumber,
          token,
        });
      } catch (error) {
        console.log(`Failed to resolve issue via GraphQL: ${error.message}`);
      }
    }

    if (resolvedBy && resolvedBy.login && resolvedBy.prNumber) {
      return [
        {
          eventKey: `issue:${issueNumber}:resolved-by-pr:${resolvedBy.prNumber}`,
          login: resolvedBy.login,
          points: 1,
          reason: `Issue #${issueNumber} resolved by merged PR #${resolvedBy.prNumber}`,
        },
      ];
    }

    return [
      {
        eventKey: `issue:${issueNumber}:closed`,
        login: closedBy,
        points: 1,
        reason: `Issue #${issueNumber} closed`,
      },
    ];
  }

  return [];
}

async function main() {
  const eventPath =
    getArg("--event-path") || process.env.GITHUB_EVENT_PATH || "";
  const eventName =
    getArg("--event-name") || process.env.GITHUB_EVENT_NAME || "";
  const actor = getArg("--actor") || process.env.GITHUB_ACTOR || "";
  const outputPath = getArg("--output-path") || "community-points.json";
  const leaderboardPath =
    getArg("--leaderboard-path") || "community-leaderboard.md";
  const repository =
    getArg("--repository") || process.env.GITHUB_REPOSITORY || "";
  const manualRunId =
    getArg("--manual-run-id") || process.env.GITHUB_RUN_ID || "";
  const token =
    getArg("--github-token") ||
    process.env.GITHUB_TOKEN ||
    process.env.GH_TOKEN ||
    "";
  const ignoredUsers = buildIgnoredUsers(
    getArg("--ignore-users") || process.env.POINTS_IGNORE_USERS || ""
  );
  const repoParts = parseRepository(repository);
  const owner = repoParts ? repoParts.owner : "";
  const repo = repoParts ? repoParts.repo : "";

  if (!eventPath || !eventName) {
    console.log("Missing event context, skipping.");
    process.exit(0);
  }

  const payload = readJson(eventPath);
  const resolvedEvents = await resolveEvent(payload, {
    eventName,
    actor,
    token,
    owner,
    repo,
    manualRunId,
  });

  if (!resolvedEvents || resolvedEvents.length === 0) {
    console.log(`No scoring rule for event ${eventName}:${payload.action}`);
    process.exit(0);
  }

  const points = loadPoints(outputPath);
  let changes = 0;

  for (const event of resolvedEvents) {
    if (!event.login) {
      console.log(`Skipped ${event.eventKey}: missing login.`);
      continue;
    }

    if (isIgnoredUser(event.login, ignoredUsers)) {
      console.log(`Skipped ${event.eventKey}: ignored user ${event.login}.`);
      continue;
    }

    if (points.ledger[event.eventKey]) {
      console.log(`Already recorded ${event.eventKey}, skipping.`);
      continue;
    }

    const awardedPoints = parsePositiveInteger(event.points, 1);
    const current = Number(points.scores[event.login] || 0);
    points.scores[event.login] = current + awardedPoints;
    points.ledger[event.eventKey] = {
      user: event.login,
      points: awardedPoints,
      reason: event.reason,
      at: new Date().toISOString(),
    };
    changes += 1;
    console.log(`Added +${awardedPoints} for ${event.login} via ${event.eventKey}.`);
  }

  if (changes === 0) {
    console.log("No points changes.");
    process.exit(0);
  }

  fs.writeFileSync(outputPath, `${JSON.stringify(points, null, 2)}\n`, "utf8");
  fs.writeFileSync(leaderboardPath, formatLeaderboard(points), "utf8");
}

main().catch((error) => {
  console.error(error);
  process.exit(1);
});
