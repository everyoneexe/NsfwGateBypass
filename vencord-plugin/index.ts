import definePlugin from "@utils/types";
import { FluxDispatcher } from "@webpack/common";

let interceptor: ((event: any) => void) | null = null;

export default definePlugin({
    name: "NsfwBypass",
    description: "NSFW age gate bypass - nsfw_allowed'i true yapar",
    authors: [{ name: "fukushima", id: 0n }],
    enabledByDefault: true,

    start() {
        // READY ve CURRENT_USER_UPDATE event'lerini intercept et
        interceptor = (event: any) => {
            // READY event: ilk baglantiginda user bilgisi geliyor
            if (event.type === "READY" || event.type === "READY_SUPPLEMENTAL") {
                if (event.user) {
                    event.user.nsfw_allowed = true;
                    event.user.nsfwAllowed = true;
                }
                // d.user (raw data)
                if (event.d?.user) {
                    event.d.user.nsfw_allowed = true;
                    event.d.user.nsfwAllowed = true;
                }
                console.log("[NsfwBypass] READY event patched");
            }

            // CURRENT_USER_UPDATE
            if (event.type === "CURRENT_USER_UPDATE") {
                if (event.user) {
                    event.user.nsfw_allowed = true;
                    event.user.nsfwAllowed = true;
                }
                console.log("[NsfwBypass] CURRENT_USER_UPDATE patched");
            }
        };

        // FluxDispatcher intercept - dispatch'ten ONCE calisir
        FluxDispatcher.subscribe("READY", interceptor);
        FluxDispatcher.subscribe("READY_SUPPLEMENTAL", interceptor);
        FluxDispatcher.subscribe("CURRENT_USER_UPDATE", interceptor);

        // Mevcut user'i da patch'le (zaten giris yapmissa)
        try {
            const UserStore = Vencord.Webpack.findByProps("getCurrentUser", "getUser");
            if (UserStore) {
                const user = UserStore.getCurrentUser();
                if (user) {
                    user.nsfwAllowed = true;
                    user.nsfw_allowed = true;
                    console.log("[NsfwBypass] Mevcut user patched:", user.username);

                    // Dispatch ile UI'i guncelle
                    FluxDispatcher.dispatch({
                        type: "CURRENT_USER_UPDATE",
                        user: { ...user, nsfw_allowed: true, nsfwAllowed: true }
                    });
                }
            }
        } catch (e) {
            console.log("[NsfwBypass] Mevcut user patch atlaması (normal):", e);
        }

        console.log("[NsfwBypass] Plugin baslatildi");
    },

    stop() {
        if (interceptor) {
            FluxDispatcher.unsubscribe("READY", interceptor);
            FluxDispatcher.unsubscribe("READY_SUPPLEMENTAL", interceptor);
            FluxDispatcher.unsubscribe("CURRENT_USER_UPDATE", interceptor);
            interceptor = null;
        }
        console.log("[NsfwBypass] Plugin durduruldu");
    },
});
