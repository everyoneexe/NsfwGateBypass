// ==UserScript==
// @name         Discord NSFW Bypass (Vencord)
// @namespace    nsfwbypass
// @version      1.0
// @description  Vencord uzerinden NSFW age gate bypass
// @match        https://discord.com/*
// @run-at       document-idle
// @grant        none
// ==/UserScript==

(function() {
    'use strict';

    function tryBypass() {
        if (typeof Vencord === 'undefined') return false;

        const UserStore = Vencord.Webpack.findByProps("getCurrentUser", "getUser");
        if (!UserStore) return false;

        const user = UserStore.getCurrentUser();
        if (!user) return false;

        if (user.nsfwAllowed === true) return true; // zaten bypass'li

        user.nsfwAllowed = true;
        user.nsfw_allowed = true;

        const Dispatcher = Vencord.Webpack.findByProps("dispatch", "subscribe");
        if (Dispatcher) {
            Dispatcher.dispatch({
                type: "CURRENT_USER_UPDATE",
                user: { ...user, nsfw_allowed: true, nsfwAllowed: true }
            });
        }

        console.log('[NSFW Bypass] Aktif');
        return true;
    }

    // Vencord yuklenene kadar bekle
    let attempts = 0;
    const interval = setInterval(() => {
        attempts++;
        if (tryBypass() || attempts > 30) {
            clearInterval(interval);
        }
    }, 1000);
})();
