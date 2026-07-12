# Trusted Alarms — Build Prompt for Claude Code

You are building **Trusted Alarms**, an iOS 26+ app where trusted contacts can set real alarms on each other's iPhones with explicit permission. Backend is Node.js + TypeScript on Railway. iOS is SwiftUI + AlarmKit. Built as a monorepo so a single contract change updates both sides at once.

The two specs in `/docs/backend-spec.md` and `/docs/ios-spec.md` are the **source of truth** for what to build. This prompt covers everything *around* those specs: repo layout, deployment, design system, and working rules.

---

## 0. Before you start

Inspect first, write second:

1. Read `/docs/backend-spec.md` end to end.
2. Read `/docs/ios-spec.md` end to end.
3. Read this entire prompt.
4. Check if sibling repos `../remote-alarm/` and `../remote-alarm-ios/` exist. They contain earlier work toward this product. **Treat them as prior art, not source of truth.** If anything there is useful (helper functions, a working APIClient, schema sketches), port it in. Otherwise build fresh — do not copy code that contradicts the two specs.
5. Confirm Xcode command-line tools and CocoaPods are installed. Do **not** install them yourself with `sudo`. If something is missing, stop and tell me the `brew install` / `gem install` command.
6. Confirm Node 20+ and Postgres available locally (Docker is fine).

Do not open Xcode's GUI at any point. The whole iOS workflow must run from the terminal.

---

## 1. Repo layout

Create a monorepo at the current working directory:

```
trusted-alarms/
├── apps/
│   ├── backend/                 # Node/TS API, deploys to Railway
│   │   ├── src/
│   │   ├── prisma/
│   │   ├── test/
│   │   ├── package.json
│   │   ├── tsconfig.json
│   │   ├── railway.json
│   │   └── Dockerfile           # optional, nixpacks works too
│   └── ios/                     # SwiftUI iOS 26+ app
│       ├── project.yml          # xcodegen config — NO .xcodeproj checked in
│       ├── Sources/
│       │   ├── App/
│       │   ├── Core/
│       │   ├── Alarm/
│       │   ├── Trust/
│       │   ├── DesignSystem/    # Liquid Glass tokens & wrappers
│       │   └── UI/
│       ├── Tests/
│       ├── Resources/
│       └── Makefile
├── packages/
│   └── shared-types/            # TS types + generated Swift models
│       ├── src/
│       │   ├── alarm.ts
│       │   ├── trust.ts
│       │   ├── device.ts
│       │   ├── user.ts
│       │   └── index.ts
│       ├── generated/
│       │   └── SharedModels.swift
│       └── package.json
├── tools/
│   └── generate-swift.ts        # TS → Swift codegen
├── docs/
│   ├── backend-spec.md          # already in repo
│   ├── ios-spec.md              # already in repo
│   └── ARCHITECTURE.md          # you write this after Phase 1
├── .github/
│   └── workflows/
│       ├── backend.yml
│       └── ios.yml
├── .editorconfig
├── .gitignore
├── package.json                 # root, npm workspaces
├── tsconfig.base.json
└── README.md
```

Root `package.json` uses npm workspaces:

```json
{
  "private": true,
  "workspaces": ["apps/backend", "packages/*"],
  "scripts": {
    "dev:backend": "npm run dev -w apps/backend",
    "test:backend": "npm test -w apps/backend",
    "types:build": "npm run build -w @trusted-alarms/shared-types",
    "types:swift": "tsx tools/generate-swift.ts",
    "ios:run": "make -C apps/ios run"
  }
}
```

`apps/ios` is **not** in npm workspaces — it's not Node.

---

## 2. Execution phases

Work in phases. Stop and commit at the end of each. Do not start the next phase until the previous one builds and tests green.

### Phase 1 — Bootstrap (no app code yet)

- Create the directory tree above (empty packages where needed).
- Initialize git. First commit: `chore: bootstrap monorepo`.
- Set up `.gitignore` for Node, Swift, Xcode, macOS, .env, Prisma generated client.
- Create root `package.json` with workspaces.
- Create `tsconfig.base.json` with strict mode on.
- Write a short root `README.md` with `npm run dev:backend` and `npm run ios:run` instructions.
- Write `docs/ARCHITECTURE.md` describing the data flow: setter → backend → APNs → owner device → AlarmKit → confirmation back to backend → setter. One diagram in ASCII or Mermaid is plenty.

Commit. Run `npm install` at root. Verify it succeeds.

### Phase 2 — Shared types package

Define the wire contract once. This is the package that prevents the mismatches in the earlier alignment work (`/devices/heartbeat` vs `/devices/register`, etc).

- Create `packages/shared-types` as a TS package.
- Define enums and DTOs for: trust statuses, alarm statuses, alarm permission statuses, allowed-hours format, device payloads, alarm request/response payloads, audit log entries.
- Match the spec exactly: trust = `pending | trusted | blocked | revoked`, alarm permission = `authorized | denied | unknown`, allowed hours = `"HH:mm"` strings.
- Write `tools/generate-swift.ts` that reads the TS definitions and emits `packages/shared-types/generated/SharedModels.swift` with matching Swift `enum` and `Codable struct` types. Snake_case JSON keys in TS map to Swift `CodingKeys`.
- Add a test that round-trips one example of each DTO through JSON.

Commit.

### Phase 3 — Backend

Follow `/docs/backend-spec.md` exactly. Highlights you must not miss:

- **NestJS** + Prisma + Postgres + JWT.
- Endpoint surface from the spec — no `/devices/heartbeat` style legacy paths.
- Allowed-hours logic must handle overnight windows (22:00–06:00). Include the boundary tests from the spec.
- `PushService` abstraction with `MockPushService` for dev/tests. APNs adapter behind a feature flag.
- Alarm cannot be marked scheduled until the device calls `POST /alarms/:id/device-confirmed`.
- Seed `Madiyar` and `Aida` with mutual trust per the spec.
- Import types from `@trusted-alarms/shared-types` for request/response bodies. Do not redefine them.
- All tests from the spec must pass.

**Local dev:**
- `apps/backend/.env.example` with `DATABASE_URL`, `JWT_SECRET`, `PORT=3000`, `APNS_MODE=mock`.
- `docker-compose.yml` at root for Postgres only.
- `npm run dev:backend` starts the API on port 3000.

**Railway readiness:**
- `apps/backend/railway.json` with `nixpacks` builder and `npm run start:prod` as start command.
- Document in `apps/backend/README.md`: set **Root Directory** to `apps/backend` and **Watch Paths** to `apps/backend/**` and `packages/shared-types/**` so unrelated iOS commits don't trigger redeploys.
- Use Railway's Postgres add-on for `DATABASE_URL`.
- `JWT_SECRET` and APNs key set as Railway variables (do not commit). APNs key as a file variable.
- Health check at `GET /health`.

Commit per logical chunk (auth, devices, trust, alarms, audit, push). Push and verify CI passes.

### Phase 4 — iOS app

Follow `/docs/ios-spec.md` exactly, then layer Phase 5's design system on top.

**Project setup, terminal-only:**
- Use `xcodegen` driven by `apps/ios/project.yml`. Target iOS 26.0+ minimum. No earlier deployment target.
- `apps/ios/Makefile` with targets:
  - `make generate` — runs `xcodegen generate`
  - `make build` — `xcodebuild -scheme TrustedAlarms -destination 'generic/platform=iOS Simulator' build`
  - `make run` — boots iPhone 17 Pro simulator, installs app, launches it (use `xcrun simctl`)
  - `make test` — runs unit tests on simulator
  - `make clean`
- Add `.xcodeproj` to `.gitignore`. Project is regenerated, never edited by hand.
- Tell me what to `brew install` if `xcodegen` is missing — don't install it yourself.

**Code architecture from spec:**
- Folder layout per the iOS spec.
- `AlarmService` protocol with `AlarmKitAlarmService` (real) and `MockAlarmService` (preview/sim fallback). Keep all AlarmKit imports inside `AlarmKitAlarmService`.
- `APIClient` defaults to `http://localhost:3000` on simulator builds, configurable via `Info.plist` `API_BASE_URL` for device builds.
- JWT stored in Keychain, not UserDefaults.
- `DeviceStatusReporter` sends heartbeat with battery, charging, timezone, app version, alarm permission — using `PATCH /devices/:id/heartbeat`.
- All API calls use `async/await` and `Codable` types from the generated `SharedModels.swift`.
- All view models use `@Observable` (iOS 17+ macro, fine on iOS 26).

**Status transitions wired to backend endpoints:**
- AlarmKit schedule success → `POST /alarms/:id/device-confirmed`
- AlarmKit schedule failure → `POST /alarms/:id/failed` with `failureReason`
- Ring / snooze / stop / cancel → matching backend endpoints. **No `/alarms/:id/status` calls anywhere.**

**Tests from the iOS spec must pass.** Run them via `make test`.

Commit per logical chunk.

### Phase 5 — iOS 26 Liquid Glass design system

This is where the app stops looking generic. Build a tiny design system in `apps/ios/Sources/DesignSystem/` and apply it across every screen. The user wants Liquid Glass everywhere — native components first, custom only where Apple doesn't provide one.

**Use native iOS 26 APIs, not custom blur:**

- Buttons: `.buttonStyle(.glass)` and `.buttonStyle(.glassProminent)` — these are the new bubble buttons. Use `.glassProminent` for primary actions (Schedule alarm, Approve, Stop alarm), `.glass` for secondary.
- Tab bar: standard `TabView` — in iOS 26 it auto-renders with liquid glass. Do not customize unless needed.
- Nav bar: standard `NavigationStack` with `.toolbar { }` — toolbars get glass automatically.
- Surfaces: `.glassEffect()` modifier for cards, status pills, sheets that need to read over content.
- Grouped glass: wrap related glass elements in `GlassEffectContainer { }` so they morph and merge correctly when animating (this matters on the alarm status feed where pills appear/disappear).
- Sheets and popovers: native — already glass in iOS 26.
- Status pills: `Capsule().glassEffect(.regular.tint(color))` with tint color carrying state (amber for waiting, green for scheduled, red for failed, gray for stopped).

**Design tokens** (`DesignSystem/Tokens.swift`):

```swift
enum AlarmStatusColor {
    static let waiting   = Color.orange
    static let scheduled = Color.green
    static let ringing   = Color.red
    static let snoozed   = Color.yellow
    static let stopped   = Color.gray
    static let failed    = Color.red
    static let cancelled = Color.gray
}
```

Typography: SF Pro via `.font(.system(...))` only. No custom fonts.

Spacing: 8pt grid. `Spacing.xs = 4`, `sm = 8`, `md = 16`, `lg = 24`, `xl = 32`.

Corner radius: `Radius.card = 20`, `Radius.pill = 999`, `Radius.button = 16`.

**Screen-by-screen guidance:**

- **Onboarding**: full-bleed background, glass cards stacked, primary button uses `.buttonStyle(.glassProminent)`. Permission explanation card uses `.glassEffect()` over a soft gradient.
- **Home feed / audit log**: list of glass cards inside a `GlassEffectContainer` so morphing animations look right when items reorder.
- **Trusted contacts list**: native `List` — looks good with glass by default. Each row's status pill uses tinted glass.
- **Contact detail / allowed hours**: native form, allowed-hours pickers as time wheels.
- **Set alarm**: time picker prominent, then a glass card showing dual-timezone preview ("8:00 AM for Aida in Almaty / 7:00 AM for you in Dubai"). Primary button glassProminent.
- **Alarm status detail**: hero status pill at top (large, tinted glass), timeline below in a glass container.
- **First alarm approval**: full-screen modal sheet. Two big glass buttons — Approve (glassProminent, green tint) and Decline (glass).
- **Ringing screen**: full-bleed dramatic background, two glass buttons (Stop glassProminent, Snooze glass). Live Activity also required — see Phase 5b.
- **Settings / device status**: native form. Battery, charging, permission status as glass info rows.

**Phase 5b — Live Activity + widget:**

Add a Live Activity that shows when an alarm is waiting/scheduled/ringing. Lock screen and Dynamic Island both. This is a major UX win for "Scheduled on Madiyar's iPhone" — the setter sees it on their own lock screen as a Live Activity. ActivityKit + WidgetKit, native styling, glass surfaces.

Skip a home screen widget for v1 unless trivial.

**Avoid:**
- Custom `.ultraThinMaterial` backgrounds. Use `.glassEffect()`.
- Hardcoded colors. Use `AlarmStatusColor.*`.
- Custom navigation chrome. Use `NavigationStack` + `.toolbar`.
- Emoji in UI copy (the spec says "no childish/gimmicky tone").

### Phase 6 — CI + deployment

- `.github/workflows/backend.yml`: on push to main affecting `apps/backend/**` or `packages/**`, run lint + tests. Railway auto-deploys from main, so CI only needs to gate.
- `.github/workflows/ios.yml`: macOS runner, `xcodegen`, `xcodebuild test`. Triggered on push affecting `apps/ios/**` or `packages/**`.
- Document in `README.md`: how to set up Railway service (root directory `apps/backend`, watch paths, env vars, Postgres add-on).
- Document APNs setup: certificate vs. key, where to put it in Railway, mock mode for local.

---

## 3. Working rules

- **Commit frequently.** Conventional commits (`feat:`, `fix:`, `chore:`, `test:`).
- **Stop and ask** before: installing system packages, modifying anything in sibling repos `../remote-alarm/` or `../remote-alarm-ios/`, changing the spec docs, adding a paid dependency, or restructuring folders.
- **Never commit secrets.** `.env` is gitignored. `.env.example` only.
- **Don't open Xcode UI.** If you think you need to, stop and tell me why.
- **Don't use SwiftLint custom rules** beyond default — keep tooling minimal.
- **Print the exact terminal commands** you ran in your responses, so I can replay them.
- **If a spec contradicts itself or is ambiguous**, stop and summarize the ambiguity. Don't guess.
- **If you discover a real backend bug or missing endpoint** while building iOS, propose the backend change in chat first — don't silently add it.

---

## 4. Definition of done (Phase 6 → ship-ready)

- `npm run dev:backend` boots the API locally with seeded Madiyar + Aida.
- `make -C apps/ios run` boots the simulator and launches the app, talking to local backend.
- Aida (in the app) can invite Madiyar by handle, accept trust, set an alarm 6 minutes out for Madiyar.
- Madiyar receives the request, approves it (first alarm), AlarmKit schedules it, backend gets `device-confirmed`, Aida sees "Scheduled on Madiyar's iPhone".
- Alarm fires in simulator, Madiyar stops it, Aida sees "Stopped".
- Revoking trust cancels future alarms.
- Backend deploys to Railway from a push to main.
- iOS test suite green. Backend test suite green.
- Every UI screen uses Liquid Glass via native APIs — no custom blur, no `.ultraThinMaterial`.

---

## 5. First actions to take right now

1. Confirm you've read both spec docs.
2. Confirm tools available: `node -v`, `npm -v`, `xcodebuild -version`, `xcrun simctl list devices | head`, `which xcodegen`, `which pod`, `psql --version` (or Docker).
3. Report back what's missing before installing anything.
4. Once green, start Phase 1.

Go.
