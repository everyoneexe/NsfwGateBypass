# NsfwGateBypass

A Vencord research plugin for studying Discord's client-side content gating mechanisms.

> **Disclaimer:** This project is for **educational and research purposes only**. It demonstrates how client-side UI restrictions differ from server-side access controls. Use responsibly and in accordance with Discord's Terms of Service. The authors are not responsible for any misuse.

## Background

Discord's age-restricted channel gate is implemented as a **client-side UI overlay**. The underlying API does not enforce this restriction — channel messages are served regardless of the `nsfw_allowed` flag in the user object. This plugin documents and demonstrates this architectural inconsistency.

The `nsfw_allowed` field is derived from `date_of_birth`, which is immutable once set. Users who accidentally entered an incorrect date of birth have no official way to correct this, as Discord's age verification endpoint requires hCaptcha and does not always resolve the issue.

## Technical Details

Discord's WebSocket gateway sends a `READY` event on connection containing the full user object. The `nsfw_allowed` boolean in this payload controls whether the client renders the age gate overlay on NSFW-flagged channels. This plugin subscribes to the `READY` Flux dispatch and modifies the flag before the UI processes it.

No network requests are made. No server-side data is modified.

## Install

```bash
git clone https://github.com/everyoneexe/NsfwGateBypass.git ~/.config/Vencord/src/userplugins/NsfwGateBypass
```

Rebuild Vencord and restart Discord.

## Console Alternative

With Vencord loaded, paste in DevTools (F12):

```js
(() => {
  const US = Vencord.Webpack.findByProps("getCurrentUser", "getUser");
  const u = US.getCurrentUser();
  u.nsfwAllowed = true;
  Vencord.Webpack.findByProps("dispatch", "subscribe").dispatch({
    type: "CURRENT_USER_UPDATE",
    user: { ...u, nsfw_allowed: true, nsfwAllowed: true }
  });
})();
```

Non-persistent — needs to be re-applied after page reload.

## License

MIT
