# Discord NSFW Gate Bypass

Bypasses Discord's "Sorry, you're not old enough to view this age-restricted channel" gate — **client-side only**, no server modification, no account risk.

## Why?

Discord sets `nsfw_allowed: false` on accounts that were created with an under-18 date of birth. The `date_of_birth` field is **immutable** — you can't change it. Discord's age verification requires hCaptcha. But the NSFW gate is **purely a client-side UI blocker** — the API already allows you to read NSFW channel messages even with `nsfw_allowed: false`.

This tool patches the Discord client to report `nsfw_allowed: true`, removing the gate.

## Methods (pick one)

### 1. Console Code (quickest, not persistent)

Requires [Vencord](https://vencord.dev) installed. Open Discord, go to any non-gated page, press F12, paste:

```js
(() => {
  const UserStore = Vencord.Webpack.findByProps("getCurrentUser", "getUser");
  const user = UserStore.getCurrentUser();
  user.nsfwAllowed = true;
  user.nsfw_allowed = true;
  const Dispatcher = Vencord.Webpack.findByProps("dispatch", "subscribe");
  Dispatcher.dispatch({
    type: "CURRENT_USER_UPDATE",
    user: { ...user, nsfw_allowed: true, nsfwAllowed: true }
  });
  console.log("[NSFW Bypass] Done! Navigate to the NSFW channel now.");
})();
```

Works instantly, no page reload needed. But you have to paste it again after every page refresh.

### 2. Vencord Plugin (persistent, recommended)

Copy `vencord-plugin/index.ts` to your Vencord userplugins:

```bash
cp -r vencord-plugin ~/.config/Vencord/src/userplugins/NsfwBypass
```

Then rebuild Vencord:

```bash
cd /path/to/Vencord
pnpm build
```

The plugin auto-patches `nsfw_allowed` on every Discord load.

### 3. Tampermonkey Userscript (persistent, no build needed)

Install [Tampermonkey](https://www.tampermonkey.net/), then install `nsfw-bypass.user.js`. Requires Vencord to be installed (uses `Vencord.Webpack` API).

### 4. mitmproxy (works without Vencord)

For setups without Vencord. Intercepts the WebSocket READY event and patches `nsfw_allowed` in transit:

```bash
./start.sh
```

Uses a PAC file so **only Discord traffic goes through the proxy** — all other sites connect directly.

## How it works

1. When Discord loads, the gateway sends a `READY` event via WebSocket containing user data with `nsfw_allowed: false`
2. The Discord client reads this and shows the age gate on NSFW channels
3. This tool intercepts/patches that value to `true` before the client processes it
4. The gate disappears — you can view NSFW channels normally

**Important:** The API already allows reading NSFW messages regardless of `nsfw_allowed`. The gate is purely a client-side UI element. No server rules are bypassed.

## Will I get banned?

No. This is a **client-side only** modification:
- No fake requests are sent to Discord servers
- No account data is modified (date_of_birth, nsfw_allowed stay unchanged server-side)
- Discord cannot detect this — it's equivalent to editing an HTML element in DevTools
- The API already serves NSFW channel content to your account

## What doesn't work

Things we tried that Discord blocks:

| Method | Why it fails |
|--------|-------------|
| `PATCH /users/@me` with `date_of_birth` | `DATE_OF_BIRTH_IMMUTABLE` |
| `PATCH /users/@me` with `nsfw_allowed: true` | Requires hCaptcha |
| Firefox extension `webRequest.filterResponseData` | 0 requests intercepted |
| Content script `<script>` injection | CSP blocks inline scripts |
| Content script `exportFunction` override | Cross-compartment permission error |
| Tampermonkey `@run-at document-start` | Cannot override fetch in page context |
| `"world": "MAIN"` in content script | Firefox doesn't support it |

## Files

```
├── vencord-plugin/index.ts    # Vencord plugin (recommended)
├── nsfw-bypass.user.js        # Tampermonkey userscript
├── mitm_bypass.py             # mitmproxy addon (WebSocket patching)
├── proxy.pac                  # PAC file (Discord-only proxy)
├── start.sh                   # One-command mitmproxy launcher
├── stop.sh                    # Stop mitmproxy
├── proxy.py                   # HTTP viewer proxy (standalone)
└── index.html                 # Web-based channel viewer
```

## Requirements

- **Console/Plugin method:** [Vencord](https://vencord.dev) (browser extension or userscript)
- **mitmproxy method:** `mitmproxy` installed, Firefox

## License

MIT
