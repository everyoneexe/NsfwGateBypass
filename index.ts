import definePlugin from "@utils/types";
import { FluxDispatcher } from "@webpack/common";
import { findByProps } from "@webpack";

let interceptor: ((event: any) => void) | null = null;

export default definePlugin({
    name: "NsfwBypass",
    description: "Research plugin — studies client-side content gate behavior",
    authors: [{ name: "fukushima", id: 0n }],
    enabledByDefault: true,

    start() {
        const patch = (obj: any) => {
            if (obj?.user) {
                obj.user.nsfw_allowed = true;
                obj.user.nsfwAllowed = true;
            }
            if (obj?.d?.user) {
                obj.d.user.nsfw_allowed = true;
                obj.d.user.nsfwAllowed = true;
            }
        };

        interceptor = (event: any) => {
            patch(event);
        };

        FluxDispatcher.subscribe("READY", interceptor);
        FluxDispatcher.subscribe("READY_SUPPLEMENTAL", interceptor);
        FluxDispatcher.subscribe("CURRENT_USER_UPDATE", interceptor);

        // Patch current user if already logged in
        try {
            const UserStore = findByProps("getCurrentUser", "getUser");
            const user = UserStore?.getCurrentUser();
            if (user) {
                user.nsfwAllowed = true;
                user.nsfw_allowed = true;
                FluxDispatcher.dispatch({
                    type: "CURRENT_USER_UPDATE",
                    user: { ...user, nsfw_allowed: true, nsfwAllowed: true }
                });
            }
        } catch { }
    },

    stop() {
        if (interceptor) {
            FluxDispatcher.unsubscribe("READY", interceptor);
            FluxDispatcher.unsubscribe("READY_SUPPLEMENTAL", interceptor);
            FluxDispatcher.unsubscribe("CURRENT_USER_UPDATE", interceptor);
            interceptor = null;
        }
    },
});
