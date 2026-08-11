# NsfwGateBypass

Vencord plugin that bypasses Discord's **"Sorry, you're not old enough to view this age-restricted channel"** gate.

## Install

```bash
# Clone into Vencord userplugins
git clone https://github.com/everyoneexe/NsfwGateBypass.git ~/.config/Vencord/src/userplugins/NsfwGateBypass
```

Then rebuild Vencord and restart Discord.

## How it works

Discord sends `nsfw_allowed: false` in the WebSocket `READY` event for accounts with an under-18 date of birth. The `date_of_birth` field is **immutable** — once set, it cannot be changed. Discord's age verification endpoint requires hCaptcha.

However, the NSFW gate is **purely a client-side UI blocker**. The API already serves NSFW channel messages regardless of `nsfw_allowed`. This plugin patches the `READY` event to set `nsfw_allowed: true` before the client processes it.

## Will I get banned?

No. This is a client-side only modification — no requests are sent, no account data is changed server-side. Discord cannot distinguish this from a normal session.

## Quick alternative (no build needed)

If you don't want to rebuild Vencord, paste this in Discord's console (F12) while Vencord is loaded:

```js
(() => {
  const UserStore = Vencord.Webpack.findByProps("getCurrentUser", "getUser");
  const user = UserStore.getCurrentUser();
  user.nsfwAllowed = true;
  const Dispatcher = Vencord.Webpack.findByProps("dispatch", "subscribe");
  Dispatcher.dispatch({
    type: "CURRENT_USER_UPDATE",
    user: { ...user, nsfw_allowed: true, nsfwAllowed: true }
  });
})();
```

This works instantly without page reload, but needs to be re-pasted after every refresh.

## License

MIT
