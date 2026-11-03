(globalThis["TURBOPACK"] || (globalThis["TURBOPACK"] = [])).push([typeof document === "object" ? document.currentScript : undefined,
"[project]/components/IntegrationsModal.tsx [app-client] (ecmascript)", ((__turbopack_context__) => {
"use strict";

__turbopack_context__.s([
    "default",
    ()=>IntegrationsModal
]);
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/next/dist/compiled/react/jsx-dev-runtime.js [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/next/dist/compiled/react/index.js [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$check$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__Check$3e$__ = __turbopack_context__.i("[project]/node_modules/lucide-react/dist/esm/icons/check.js [app-client] (ecmascript) <export default as Check>");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$external$2d$link$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__ExternalLink$3e$__ = __turbopack_context__.i("[project]/node_modules/lucide-react/dist/esm/icons/external-link.js [app-client] (ecmascript) <export default as ExternalLink>");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$eye$2d$off$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__EyeOff$3e$__ = __turbopack_context__.i("[project]/node_modules/lucide-react/dist/esm/icons/eye-off.js [app-client] (ecmascript) <export default as EyeOff>");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$link$2d$2$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__Link2$3e$__ = __turbopack_context__.i("[project]/node_modules/lucide-react/dist/esm/icons/link-2.js [app-client] (ecmascript) <export default as Link2>");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$mail$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__Mail$3e$__ = __turbopack_context__.i("[project]/node_modules/lucide-react/dist/esm/icons/mail.js [app-client] (ecmascript) <export default as Mail>");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$sparkles$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__Sparkles$3e$__ = __turbopack_context__.i("[project]/node_modules/lucide-react/dist/esm/icons/sparkles.js [app-client] (ecmascript) <export default as Sparkles>");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$trash$2d$2$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__Trash2$3e$__ = __turbopack_context__.i("[project]/node_modules/lucide-react/dist/esm/icons/trash-2.js [app-client] (ecmascript) <export default as Trash2>");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$x$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__X$3e$__ = __turbopack_context__.i("[project]/node_modules/lucide-react/dist/esm/icons/x.js [app-client] (ecmascript) <export default as X>");
var __TURBOPACK__imported__module__$5b$project$5d2f$components$2f$JarvisBridge$2e$tsx__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/components/JarvisBridge.tsx [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$components$2f$theme$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/components/theme.ts [app-client] (ecmascript)");
;
var _s = __turbopack_context__.k.signature();
"use client";
;
;
;
;
const GREEN = "#34d399";
const RED = "#ff5b79";
function IntegrationsModal() {
    _s();
    const { assistantName, activePersona, theme, personaChosen, integrationsReady, integrations, integrationsModalOpen, setIntegrationsModalOpen, setPreviewPersona, choosePersona, saveIntegrations, skipIntegrations, disconnectIntegration, startGoogleOAuth, connectSocialWeb, importSocialCookies, openSocialHud } = (0, __TURBOPACK__imported__module__$5b$project$5d2f$components$2f$JarvisBridge$2e$tsx__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useJarvis"])();
    const PRIMARY = theme.primary;
    const SECONDARY = theme.secondary;
    const isFirstRunStep = !integrationsReady || !personaChosen;
    // Per-service ignore flags + form values
    const [ignoredMap, setIgnoredMap] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])({});
    const [socialHandles, setSocialHandles] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])({});
    const [socialPerms, setSocialPerms] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])({});
    const [socialMsg, setSocialMsg] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])({});
    const [emailAddr, setEmailAddr] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])("");
    const [emailAppPw, setEmailAppPw] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])("");
    const [imapHost, setImapHost] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])("");
    const [smtpHost, setSmtpHost] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])("");
    const [googleClientId, setGoogleClientId] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])("");
    const [googleClientSecret, setGoogleClientSecret] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])("");
    const [googleToken, setGoogleToken] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])("");
    const [googleRefreshToken, setGoogleRefreshToken] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])("");
    const [oauthMsg, setOauthMsg] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])("");
    const [githubToken, setGithubToken] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])("");
    const [notionToken, setNotionToken] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])("");
    const [notionPageId, setNotionPageId] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])("");
    const [slackToken, setSlackToken] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])("");
    const [slackWebhook, setSlackWebhook] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])("");
    const [slackChannel, setSlackChannel] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])("");
    const [discordWebhook, setDiscordWebhook] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])("");
    const [discordToken, setDiscordToken] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])("");
    const [discordChannelId, setDiscordChannelId] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])("");
    const [telegramToken, setTelegramToken] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])("");
    const [spotifyId, setSpotifyId] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])("");
    const [spotifySecret, setSpotifySecret] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])("");
    const [trelloKey, setTrelloKey] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])("");
    const [trelloToken, setTrelloToken] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])("");
    const [linearToken, setLinearToken] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])("");
    const [linearTeamId, setLinearTeamId] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])("");
    const [outlookToken, setOutlookToken] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])("");
    const [dropboxToken, setDropboxToken] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])("");
    const [hubspotToken, setHubspotToken] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])("");
    const [calendlyToken, setCalendlyToken] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])("");
    const [saving, setSaving] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])(false);
    (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useEffect"])({
        "IntegrationsModal.useEffect": ()=>{
            if (!integrationsModalOpen) return;
            const svcs = integrations.services || {};
            setIgnoredMap({
                email: Boolean(svcs.email?.ignored),
                google: Boolean(svcs.google_drive?.ignored && svcs.gmail?.ignored && svcs.google_calendar?.ignored),
                github: Boolean(svcs.github?.ignored),
                notion: Boolean(svcs.notion?.ignored),
                slack: Boolean(svcs.slack?.ignored),
                discord: Boolean(svcs.discord?.ignored),
                telegram: Boolean(svcs.telegram?.ignored),
                spotify: Boolean(svcs.spotify?.ignored),
                trello: Boolean(svcs.trello?.ignored),
                linear: Boolean(svcs.linear?.ignored),
                outlook: Boolean(svcs.outlook?.ignored),
                dropbox: Boolean(svcs.dropbox?.ignored),
                hubspot: Boolean(svcs.hubspot?.ignored),
                calendly: Boolean(svcs.calendly?.ignored),
                instagram: Boolean(svcs.instagram?.ignored),
                snapchat: Boolean(svcs.snapchat?.ignored),
                tiktok: Boolean(svcs.tiktok?.ignored),
                x: Boolean(svcs.x?.ignored),
                whatsapp: Boolean(svcs.whatsapp?.ignored),
                reddit: Boolean(svcs.reddit?.ignored)
            });
            setSocialHandles({
                "IntegrationsModal.useEffect": (prev)=>{
                    const next = {
                        ...prev
                    };
                    for (const sk of [
                        "instagram",
                        "snapchat",
                        "tiktok",
                        "x",
                        "whatsapp",
                        "reddit"
                    ]){
                        if (svcs[sk]?.handle && !next[sk]) {
                            next[sk] = svcs[sk].handle || "";
                        }
                    }
                    return next;
                }
            }["IntegrationsModal.useEffect"]);
            setSocialPerms({
                "IntegrationsModal.useEffect": (prev)=>{
                    const next = {
                        ...prev
                    };
                    for (const sk of [
                        "instagram",
                        "snapchat",
                        "tiktok",
                        "x",
                        "whatsapp",
                        "reddit"
                    ]){
                        next[sk] = svcs[sk]?.permission || prev[sk] || "ask";
                    }
                    return next;
                }
            }["IntegrationsModal.useEffect"]);
            if (svcs.email?.email && !emailAddr) {
                setEmailAddr(svcs.email.email);
            }
            if (svcs.discord?.channel_id && !discordChannelId) {
                setDiscordChannelId(svcs.discord.channel_id);
            }
        }
    }["IntegrationsModal.useEffect"], [
        integrationsModalOpen,
        integrations,
        emailAddr,
        discordChannelId
    ]);
    if (!integrationsModalOpen) return null;
    const svcs = integrations.services || {};
    const isGoogleConnected = Boolean(svcs.google_drive?.connected || svcs.gmail?.connected || svcs.google_calendar?.connected);
    const toggleIgnore = (key)=>{
        setIgnoredMap((prev)=>({
                ...prev,
                [key]: !prev[key]
            }));
    };
    const onSave = async (e)=>{
        e.preventDefault();
        setSaving(true);
        await saveIntegrations({
            email: {
                ignore: Boolean(ignoredMap.email),
                email: emailAddr,
                app_password: emailAppPw,
                imap_host: imapHost,
                smtp_host: smtpHost
            },
            google: {
                ignore: Boolean(ignoredMap.google),
                client_id: googleClientId,
                client_secret: googleClientSecret,
                token: googleToken,
                refresh_token: googleRefreshToken,
                email: emailAddr
            },
            github: {
                ignore: Boolean(ignoredMap.github),
                token: githubToken
            },
            notion: {
                ignore: Boolean(ignoredMap.notion),
                token: notionToken,
                parent_page_id: notionPageId
            },
            slack: {
                ignore: Boolean(ignoredMap.slack),
                token: slackToken,
                webhook_url: slackWebhook,
                default_channel: slackChannel
            },
            discord: {
                ignore: Boolean(ignoredMap.discord),
                webhook_url: discordWebhook,
                token: discordToken,
                channel_id: discordChannelId
            },
            telegram: {
                ignore: Boolean(ignoredMap.telegram),
                token: telegramToken
            },
            spotify: {
                ignore: Boolean(ignoredMap.spotify),
                client_id: spotifyId,
                client_secret: spotifySecret
            },
            trello: {
                ignore: Boolean(ignoredMap.trello),
                api_key: trelloKey,
                token: trelloToken
            },
            linear: {
                ignore: Boolean(ignoredMap.linear),
                token: linearToken,
                team_id: linearTeamId
            },
            outlook: {
                ignore: Boolean(ignoredMap.outlook),
                token: outlookToken
            },
            dropbox: {
                ignore: Boolean(ignoredMap.dropbox),
                token: dropboxToken
            },
            hubspot: {
                ignore: Boolean(ignoredMap.hubspot),
                token: hubspotToken
            },
            calendly: {
                ignore: Boolean(ignoredMap.calendly),
                token: calendlyToken
            },
            instagram: {
                ignore: Boolean(ignoredMap.instagram),
                handle: socialHandles.instagram || "",
                permission: socialPerms.instagram || "ask"
            },
            snapchat: {
                ignore: Boolean(ignoredMap.snapchat),
                handle: socialHandles.snapchat || "",
                permission: socialPerms.snapchat || "ask"
            },
            tiktok: {
                ignore: Boolean(ignoredMap.tiktok),
                handle: socialHandles.tiktok || "",
                permission: socialPerms.tiktok || "ask"
            },
            x: {
                ignore: Boolean(ignoredMap.x),
                handle: socialHandles.x || "",
                permission: socialPerms.x || "ask"
            },
            whatsapp: {
                ignore: Boolean(ignoredMap.whatsapp),
                handle: socialHandles.whatsapp || "",
                permission: socialPerms.whatsapp || "ask"
            },
            reddit: {
                ignore: Boolean(ignoredMap.reddit),
                handle: socialHandles.reddit || "",
                permission: socialPerms.reddit || "ask"
            }
        });
        setSaving(false);
    };
    const onOAuthClick = async ()=>{
        setOauthMsg("");
        const res = await startGoogleOAuth(googleClientId, googleClientSecret);
        if (!res.ok) {
            setOauthMsg(res.error || "Enter Client ID & Client Secret first.");
        } else {
            setOauthMsg("Opened Google sign-in in your browser — complete consent and this status updates automatically.");
        }
    };
    const inputStyle = {
        width: "100%",
        background: theme.inputBg,
        color: "#f0ede8",
        border: `1px solid ${theme.primaryBorder}`,
        borderRadius: 8,
        padding: "8px 10px",
        fontSize: 12,
        outline: "none",
        fontFamily: "var(--font-mono)"
    };
    const cardWrap = (ignored, connected)=>({
            borderRadius: 14,
            padding: "13px 15px",
            background: ignored ? "rgba(255,255,255,0.015)" : connected ? `${GREEN}0d` : "rgba(255,255,255,0.03)",
            border: `1px solid ${ignored ? "rgba(255,255,255,0.07)" : connected ? `${GREEN}55` : `${PRIMARY}2a`}`,
            opacity: ignored ? 0.62 : 1,
            display: "flex",
            flexDirection: "column",
            gap: 9,
            transition: "all 0.2s ease"
        });
    const renderCardHeader = (key, title, subtitle, connected, disconnectKey)=>{
        const ignored = Boolean(ignoredMap[key]);
        return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
            style: {
                display: "flex",
                alignItems: "center",
                justifyContent: "space-between",
                gap: 10,
                flexWrap: "wrap"
            },
            children: [
                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                    children: [
                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                            style: {
                                display: "flex",
                                alignItems: "center",
                                gap: 8,
                                fontFamily: "var(--font-mono)",
                                fontSize: 11,
                                letterSpacing: "0.14em",
                                color: connected ? GREEN : ignored ? "rgba(240,237,232,0.5)" : PRIMARY,
                                fontWeight: 600
                            },
                            children: [
                                title,
                                connected && /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("span", {
                                    style: {
                                        display: "inline-flex",
                                        alignItems: "center",
                                        gap: 4,
                                        fontSize: 9,
                                        padding: "2px 7px",
                                        borderRadius: 999,
                                        background: `${GREEN}22`,
                                        border: `1px solid ${GREEN}66`,
                                        color: GREEN
                                    },
                                    children: [
                                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$check$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__Check$3e$__["Check"], {
                                            size: 10
                                        }, void 0, false, {
                                            fileName: "[project]/components/IntegrationsModal.tsx",
                                            lineNumber: 351,
                                            columnNumber: 17
                                        }, this),
                                        " CONNECTED"
                                    ]
                                }, void 0, true, {
                                    fileName: "[project]/components/IntegrationsModal.tsx",
                                    lineNumber: 338,
                                    columnNumber: 15
                                }, this),
                                ignored && !connected && /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("span", {
                                    style: {
                                        fontSize: 9,
                                        padding: "2px 7px",
                                        borderRadius: 999,
                                        background: "rgba(255,255,255,0.06)",
                                        color: "rgba(240,237,232,0.5)"
                                    },
                                    children: "IGNORED"
                                }, void 0, false, {
                                    fileName: "[project]/components/IntegrationsModal.tsx",
                                    lineNumber: 355,
                                    columnNumber: 15
                                }, this)
                            ]
                        }, void 0, true, {
                            fileName: "[project]/components/IntegrationsModal.tsx",
                            lineNumber: 324,
                            columnNumber: 11
                        }, this),
                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                            style: {
                                fontSize: 11,
                                color: "rgba(240,237,232,0.58)",
                                marginTop: 2
                            },
                            children: subtitle
                        }, void 0, false, {
                            fileName: "[project]/components/IntegrationsModal.tsx",
                            lineNumber: 368,
                            columnNumber: 11
                        }, this)
                    ]
                }, void 0, true, {
                    fileName: "[project]/components/IntegrationsModal.tsx",
                    lineNumber: 323,
                    columnNumber: 9
                }, this),
                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                    style: {
                        display: "flex",
                        alignItems: "center",
                        gap: 6
                    },
                    children: [
                        connected && /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("button", {
                            type: "button",
                            onClick: ()=>disconnectIntegration(disconnectKey || key),
                            style: {
                                display: "inline-flex",
                                alignItems: "center",
                                gap: 4,
                                fontFamily: "var(--font-mono)",
                                fontSize: 9.5,
                                letterSpacing: "0.12em",
                                padding: "4px 9px",
                                borderRadius: 999,
                                border: `1px solid ${RED}55`,
                                background: "transparent",
                                color: RED,
                                cursor: "pointer"
                            },
                            children: [
                                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$trash$2d$2$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__Trash2$3e$__["Trash2"], {
                                    size: 10
                                }, void 0, false, {
                                    fileName: "[project]/components/IntegrationsModal.tsx",
                                    lineNumber: 399,
                                    columnNumber: 15
                                }, this),
                                " DISCONNECT"
                            ]
                        }, void 0, true, {
                            fileName: "[project]/components/IntegrationsModal.tsx",
                            lineNumber: 381,
                            columnNumber: 13
                        }, this),
                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("button", {
                            type: "button",
                            onClick: ()=>toggleIgnore(key),
                            style: {
                                display: "inline-flex",
                                alignItems: "center",
                                gap: 5,
                                fontFamily: "var(--font-mono)",
                                fontSize: 9.5,
                                letterSpacing: "0.12em",
                                padding: "4px 10px",
                                borderRadius: 999,
                                border: `1px solid ${ignored ? `${SECONDARY}66` : "rgba(255,255,255,0.18)"}`,
                                background: ignored ? `${SECONDARY}1e` : "transparent",
                                color: ignored ? SECONDARY : "rgba(240,237,232,0.72)",
                                cursor: "pointer"
                            },
                            children: [
                                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$eye$2d$off$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__EyeOff$3e$__["EyeOff"], {
                                    size: 10
                                }, void 0, false, {
                                    fileName: "[project]/components/IntegrationsModal.tsx",
                                    lineNumber: 422,
                                    columnNumber: 13
                                }, this),
                                ignored ? "UN-IGNORE" : "IGNORE"
                            ]
                        }, void 0, true, {
                            fileName: "[project]/components/IntegrationsModal.tsx",
                            lineNumber: 402,
                            columnNumber: 11
                        }, this)
                    ]
                }, void 0, true, {
                    fileName: "[project]/components/IntegrationsModal.tsx",
                    lineNumber: 379,
                    columnNumber: 9
                }, this)
            ]
        }, void 0, true, {
            fileName: "[project]/components/IntegrationsModal.tsx",
            lineNumber: 314,
            columnNumber: 7
        }, this);
    };
    return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
        role: "dialog",
        "aria-modal": "true",
        "aria-label": "Configure Optional Integrations",
        onClick: ()=>{
            if (!isFirstRunStep) setIntegrationsModalOpen(false);
        },
        style: {
            position: "fixed",
            inset: 0,
            zIndex: 89,
            background: "rgba(2, 6, 14, 0.76)",
            backdropFilter: "blur(12px)",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            padding: 14
        },
        children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("form", {
            onSubmit: onSave,
            onClick: (e)=>e.stopPropagation(),
            style: {
                width: "min(760px, 96vw)",
                maxHeight: "88vh",
                background: theme.panelBg,
                border: `1px solid ${PRIMARY}55`,
                borderRadius: 22,
                padding: "20px 22px 18px",
                boxShadow: `0 0 60px ${PRIMARY}26, 0 22px 64px rgba(0,0,0,0.88)`,
                display: "flex",
                flexDirection: "column",
                gap: 14
            },
            children: [
                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                    style: {
                        display: "flex",
                        alignItems: "center",
                        justifyContent: "space-between",
                        gap: 10,
                        flexWrap: "wrap"
                    },
                    children: [
                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                            style: {
                                display: "flex",
                                alignItems: "center",
                                gap: 9
                            },
                            children: [
                                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$link$2d$2$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__Link2$3e$__["Link2"], {
                                    size: 17,
                                    style: {
                                        color: PRIMARY
                                    }
                                }, void 0, false, {
                                    fileName: "[project]/components/IntegrationsModal.tsx",
                                    lineNumber: 477,
                                    columnNumber: 13
                                }, this),
                                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("span", {
                                    style: {
                                        fontFamily: "var(--font-mono)",
                                        fontSize: 11,
                                        letterSpacing: "0.22em",
                                        color: PRIMARY
                                    },
                                    children: isFirstRunStep ? `STEP 2 OF 3 · OPTIONAL INTEGRATIONS` : `${assistantName.toUpperCase()} · INTEGRATIONS & ACCOUNTS`
                                }, void 0, false, {
                                    fileName: "[project]/components/IntegrationsModal.tsx",
                                    lineNumber: 478,
                                    columnNumber: 13
                                }, this)
                            ]
                        }, void 0, true, {
                            fileName: "[project]/components/IntegrationsModal.tsx",
                            lineNumber: 476,
                            columnNumber: 11
                        }, this),
                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                            style: {
                                display: "flex",
                                alignItems: "center",
                                gap: 6
                            },
                            children: [
                                [
                                    "male",
                                    "female"
                                ].map((pKey)=>{
                                    const pTheme = __TURBOPACK__imported__module__$5b$project$5d2f$components$2f$theme$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["PERSONA_THEMES"][pKey];
                                    const isAct = activePersona === pKey;
                                    return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("button", {
                                        type: "button",
                                        onClick: ()=>personaChosen ? choosePersona(pKey) : setPreviewPersona(pKey),
                                        title: `Switch theme to ${pTheme.label}`,
                                        style: {
                                            display: "inline-flex",
                                            alignItems: "center",
                                            gap: 5,
                                            fontFamily: "var(--font-mono)",
                                            fontSize: 9.5,
                                            letterSpacing: "0.14em",
                                            padding: "4px 9px",
                                            borderRadius: 999,
                                            border: `1px solid ${isAct ? pTheme.primary : "rgba(255,255,255,0.14)"}`,
                                            background: isAct ? `${pTheme.primary}22` : "transparent",
                                            color: isAct ? pTheme.primary : "rgba(240,237,232,0.62)",
                                            cursor: "pointer"
                                        },
                                        children: [
                                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$sparkles$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__Sparkles$3e$__["Sparkles"], {
                                                size: 10
                                            }, void 0, false, {
                                                fileName: "[project]/components/IntegrationsModal.tsx",
                                                lineNumber: 521,
                                                columnNumber: 19
                                            }, this),
                                            pKey === "female" ? "♀ FEMALE" : "♂ MALE"
                                        ]
                                    }, pKey, true, {
                                        fileName: "[project]/components/IntegrationsModal.tsx",
                                        lineNumber: 497,
                                        columnNumber: 17
                                    }, this);
                                }),
                                !isFirstRunStep && /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("button", {
                                    type: "button",
                                    onClick: ()=>setIntegrationsModalOpen(false),
                                    "aria-label": "Close integrations modal",
                                    style: {
                                        background: "none",
                                        border: "none",
                                        color: "rgba(255,255,255,0.5)",
                                        cursor: "pointer",
                                        marginLeft: 4
                                    },
                                    children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$x$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__X$3e$__["X"], {
                                        size: 18
                                    }, void 0, false, {
                                        fileName: "[project]/components/IntegrationsModal.tsx",
                                        lineNumber: 540,
                                        columnNumber: 17
                                    }, this)
                                }, void 0, false, {
                                    fileName: "[project]/components/IntegrationsModal.tsx",
                                    lineNumber: 528,
                                    columnNumber: 15
                                }, this)
                            ]
                        }, void 0, true, {
                            fileName: "[project]/components/IntegrationsModal.tsx",
                            lineNumber: 492,
                            columnNumber: 11
                        }, this)
                    ]
                }, void 0, true, {
                    fileName: "[project]/components/IntegrationsModal.tsx",
                    lineNumber: 467,
                    columnNumber: 9
                }, this),
                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                    style: {
                        fontSize: 12,
                        lineHeight: 1.5,
                        color: "rgba(240,237,232,0.74)"
                    },
                    children: [
                        "Set up only the accounts you want ",
                        assistantName,
                        " to use in both",
                        " ",
                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("strong", {
                            children: "Male"
                        }, void 0, false, {
                            fileName: "[project]/components/IntegrationsModal.tsx",
                            lineNumber: 554,
                            columnNumber: 11
                        }, this),
                        " and ",
                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("strong", {
                            children: "Female"
                        }, void 0, false, {
                            fileName: "[project]/components/IntegrationsModal.tsx",
                            lineNumber: 554,
                            columnNumber: 37
                        }, this),
                        " editions. Click",
                        " ",
                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("strong", {
                            children: "IGNORE"
                        }, void 0, false, {
                            fileName: "[project]/components/IntegrationsModal.tsx",
                            lineNumber: 555,
                            columnNumber: 11
                        }, this),
                        " on anything you don't use, or leave it blank — nothing here is forced."
                    ]
                }, void 0, true, {
                    fileName: "[project]/components/IntegrationsModal.tsx",
                    lineNumber: 546,
                    columnNumber: 9
                }, this),
                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                    style: {
                        overflowY: "auto",
                        display: "flex",
                        flexDirection: "column",
                        gap: 11,
                        paddingRight: 4
                    },
                    children: [
                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                            style: cardWrap(Boolean(ignoredMap.email), Boolean(svcs.email?.connected)),
                            children: [
                                renderCardHeader("email", "EMAIL · DIRECT IMAP / SMTP", "Read & send real emails instantly with a Gmail 16-char App Password, Outlook, iCloud, or custom mail.", Boolean(svcs.email?.connected)),
                                !ignoredMap.email && /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                    style: {
                                        display: "grid",
                                        gridTemplateColumns: "repeat(auto-fit, minmax(210px, 1fr))",
                                        gap: 8
                                    },
                                    children: [
                                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("input", {
                                            type: "email",
                                            value: emailAddr,
                                            onChange: (e)=>setEmailAddr(e.target.value),
                                            placeholder: "Email address (e.g. you@gmail.com)",
                                            style: inputStyle
                                        }, void 0, false, {
                                            fileName: "[project]/components/IntegrationsModal.tsx",
                                            lineNumber: 590,
                                            columnNumber: 17
                                        }, this),
                                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("input", {
                                            type: "password",
                                            value: emailAppPw,
                                            onChange: (e)=>setEmailAppPw(e.target.value),
                                            placeholder: "App Password (16-char Gmail/iCloud)",
                                            style: inputStyle
                                        }, void 0, false, {
                                            fileName: "[project]/components/IntegrationsModal.tsx",
                                            lineNumber: 597,
                                            columnNumber: 17
                                        }, this),
                                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("input", {
                                            type: "text",
                                            value: imapHost,
                                            onChange: (e)=>setImapHost(e.target.value),
                                            placeholder: "IMAP host (auto-detected if blank)",
                                            style: inputStyle
                                        }, void 0, false, {
                                            fileName: "[project]/components/IntegrationsModal.tsx",
                                            lineNumber: 604,
                                            columnNumber: 17
                                        }, this),
                                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("input", {
                                            type: "text",
                                            value: smtpHost,
                                            onChange: (e)=>setSmtpHost(e.target.value),
                                            placeholder: "SMTP host (auto-detected if blank)",
                                            style: inputStyle
                                        }, void 0, false, {
                                            fileName: "[project]/components/IntegrationsModal.tsx",
                                            lineNumber: 611,
                                            columnNumber: 17
                                        }, this)
                                    ]
                                }, void 0, true, {
                                    fileName: "[project]/components/IntegrationsModal.tsx",
                                    lineNumber: 583,
                                    columnNumber: 15
                                }, this)
                            ]
                        }, void 0, true, {
                            fileName: "[project]/components/IntegrationsModal.tsx",
                            lineNumber: 570,
                            columnNumber: 11
                        }, this),
                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                            style: cardWrap(Boolean(ignoredMap.google), isGoogleConnected),
                            children: [
                                renderCardHeader("google", "GOOGLE WORKSPACE · DRIVE, GMAIL & CALENDAR", "Direct Google Drive upload/search/download, Calendar events, and Gmail API via OAuth.", isGoogleConnected, "google"),
                                !ignoredMap.google && /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                    style: {
                                        display: "flex",
                                        flexDirection: "column",
                                        gap: 8
                                    },
                                    children: [
                                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                            style: {
                                                display: "grid",
                                                gridTemplateColumns: "repeat(auto-fit, minmax(210px, 1fr))",
                                                gap: 8
                                            },
                                            children: [
                                                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("input", {
                                                    type: "text",
                                                    value: googleClientId,
                                                    onChange: (e)=>setGoogleClientId(e.target.value),
                                                    placeholder: "Google OAuth Client ID (optional)",
                                                    style: inputStyle
                                                }, void 0, false, {
                                                    fileName: "[project]/components/IntegrationsModal.tsx",
                                                    lineNumber: 640,
                                                    columnNumber: 19
                                                }, this),
                                                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("input", {
                                                    type: "password",
                                                    value: googleClientSecret,
                                                    onChange: (e)=>setGoogleClientSecret(e.target.value),
                                                    placeholder: "Google OAuth Client Secret (optional)",
                                                    style: inputStyle
                                                }, void 0, false, {
                                                    fileName: "[project]/components/IntegrationsModal.tsx",
                                                    lineNumber: 647,
                                                    columnNumber: 19
                                                }, this),
                                                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("input", {
                                                    type: "password",
                                                    value: googleToken,
                                                    onChange: (e)=>setGoogleToken(e.target.value),
                                                    placeholder: "Or paste OAuth Access Token (ya29...)",
                                                    style: inputStyle
                                                }, void 0, false, {
                                                    fileName: "[project]/components/IntegrationsModal.tsx",
                                                    lineNumber: 654,
                                                    columnNumber: 19
                                                }, this),
                                                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("input", {
                                                    type: "password",
                                                    value: googleRefreshToken,
                                                    onChange: (e)=>setGoogleRefreshToken(e.target.value),
                                                    placeholder: "Optional Refresh Token (1//...)",
                                                    style: inputStyle
                                                }, void 0, false, {
                                                    fileName: "[project]/components/IntegrationsModal.tsx",
                                                    lineNumber: 661,
                                                    columnNumber: 19
                                                }, this)
                                            ]
                                        }, void 0, true, {
                                            fileName: "[project]/components/IntegrationsModal.tsx",
                                            lineNumber: 633,
                                            columnNumber: 17
                                        }, this),
                                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                            style: {
                                                display: "flex",
                                                alignItems: "center",
                                                gap: 10,
                                                flexWrap: "wrap"
                                            },
                                            children: [
                                                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("button", {
                                                    type: "button",
                                                    onClick: onOAuthClick,
                                                    style: {
                                                        display: "inline-flex",
                                                        alignItems: "center",
                                                        gap: 6,
                                                        fontFamily: "var(--font-mono)",
                                                        fontSize: 10,
                                                        letterSpacing: "0.13em",
                                                        padding: "6px 12px",
                                                        borderRadius: 999,
                                                        border: `1px solid ${PRIMARY}66`,
                                                        background: `${PRIMARY}1a`,
                                                        color: PRIMARY,
                                                        cursor: "pointer"
                                                    },
                                                    children: [
                                                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$external$2d$link$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__ExternalLink$3e$__["ExternalLink"], {
                                                            size: 11
                                                        }, void 0, false, {
                                                            fileName: "[project]/components/IntegrationsModal.tsx",
                                                            lineNumber: 688,
                                                            columnNumber: 21
                                                        }, this),
                                                        "AUTHORIZE GOOGLE IN BROWSER"
                                                    ]
                                                }, void 0, true, {
                                                    fileName: "[project]/components/IntegrationsModal.tsx",
                                                    lineNumber: 670,
                                                    columnNumber: 19
                                                }, this),
                                                oauthMsg && /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("span", {
                                                    style: {
                                                        fontSize: 11,
                                                        color: SECONDARY
                                                    },
                                                    children: oauthMsg
                                                }, void 0, false, {
                                                    fileName: "[project]/components/IntegrationsModal.tsx",
                                                    lineNumber: 692,
                                                    columnNumber: 21
                                                }, this)
                                            ]
                                        }, void 0, true, {
                                            fileName: "[project]/components/IntegrationsModal.tsx",
                                            lineNumber: 669,
                                            columnNumber: 17
                                        }, this)
                                    ]
                                }, void 0, true, {
                                    fileName: "[project]/components/IntegrationsModal.tsx",
                                    lineNumber: 632,
                                    columnNumber: 15
                                }, this)
                            ]
                        }, void 0, true, {
                            fileName: "[project]/components/IntegrationsModal.tsx",
                            lineNumber: 623,
                            columnNumber: 11
                        }, this),
                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                            style: cardWrap(Boolean(ignoredMap.github), Boolean(svcs.github?.connected)),
                            children: [
                                renderCardHeader("github", "GITHUB", "Manage repos, issues, pull requests & CI runs.", Boolean(svcs.github?.connected)),
                                !ignoredMap.github && /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("input", {
                                    type: "password",
                                    value: githubToken,
                                    onChange: (e)=>setGithubToken(e.target.value),
                                    placeholder: "GitHub Personal Access Token (ghp_... / github_pat_...)",
                                    style: inputStyle
                                }, void 0, false, {
                                    fileName: "[project]/components/IntegrationsModal.tsx",
                                    lineNumber: 715,
                                    columnNumber: 15
                                }, this)
                            ]
                        }, void 0, true, {
                            fileName: "[project]/components/IntegrationsModal.tsx",
                            lineNumber: 702,
                            columnNumber: 11
                        }, this),
                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                            style: cardWrap(Boolean(ignoredMap.notion), Boolean(svcs.notion?.connected)),
                            children: [
                                renderCardHeader("notion", "NOTION", "Search, read, create, and append pages & databases.", Boolean(svcs.notion?.connected)),
                                !ignoredMap.notion && /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                    style: {
                                        display: "grid",
                                        gridTemplateColumns: "repeat(auto-fit, minmax(210px, 1fr))",
                                        gap: 8
                                    },
                                    children: [
                                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("input", {
                                            type: "password",
                                            value: notionToken,
                                            onChange: (e)=>setNotionToken(e.target.value),
                                            placeholder: "Notion Integration Secret (ntn_... / secret_...)",
                                            style: inputStyle
                                        }, void 0, false, {
                                            fileName: "[project]/components/IntegrationsModal.tsx",
                                            lineNumber: 746,
                                            columnNumber: 17
                                        }, this),
                                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("input", {
                                            type: "text",
                                            value: notionPageId,
                                            onChange: (e)=>setNotionPageId(e.target.value),
                                            placeholder: "Default Parent Page ID (optional)",
                                            style: inputStyle
                                        }, void 0, false, {
                                            fileName: "[project]/components/IntegrationsModal.tsx",
                                            lineNumber: 753,
                                            columnNumber: 17
                                        }, this)
                                    ]
                                }, void 0, true, {
                                    fileName: "[project]/components/IntegrationsModal.tsx",
                                    lineNumber: 739,
                                    columnNumber: 15
                                }, this)
                            ]
                        }, void 0, true, {
                            fileName: "[project]/components/IntegrationsModal.tsx",
                            lineNumber: 726,
                            columnNumber: 11
                        }, this),
                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                            style: cardWrap(Boolean(ignoredMap.slack), Boolean(svcs.slack?.connected)),
                            children: [
                                renderCardHeader("slack", "SLACK", "Send messages, list channels, and read recent Slack threads.", Boolean(svcs.slack?.connected)),
                                !ignoredMap.slack && /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                    style: {
                                        display: "grid",
                                        gridTemplateColumns: "repeat(auto-fit, minmax(180px, 1fr))",
                                        gap: 8
                                    },
                                    children: [
                                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("input", {
                                            type: "password",
                                            value: slackToken,
                                            onChange: (e)=>setSlackToken(e.target.value),
                                            placeholder: "Bot/User Token (xoxb-...)",
                                            style: inputStyle
                                        }, void 0, false, {
                                            fileName: "[project]/components/IntegrationsModal.tsx",
                                            lineNumber: 785,
                                            columnNumber: 17
                                        }, this),
                                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("input", {
                                            type: "password",
                                            value: slackWebhook,
                                            onChange: (e)=>setSlackWebhook(e.target.value),
                                            placeholder: "Or Webhook URL (https://hooks.slack.com/...)",
                                            style: inputStyle
                                        }, void 0, false, {
                                            fileName: "[project]/components/IntegrationsModal.tsx",
                                            lineNumber: 792,
                                            columnNumber: 17
                                        }, this),
                                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("input", {
                                            type: "text",
                                            value: slackChannel,
                                            onChange: (e)=>setSlackChannel(e.target.value),
                                            placeholder: "Default #channel (optional)",
                                            style: inputStyle
                                        }, void 0, false, {
                                            fileName: "[project]/components/IntegrationsModal.tsx",
                                            lineNumber: 799,
                                            columnNumber: 17
                                        }, this)
                                    ]
                                }, void 0, true, {
                                    fileName: "[project]/components/IntegrationsModal.tsx",
                                    lineNumber: 778,
                                    columnNumber: 15
                                }, this)
                            ]
                        }, void 0, true, {
                            fileName: "[project]/components/IntegrationsModal.tsx",
                            lineNumber: 765,
                            columnNumber: 11
                        }, this),
                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                            style: cardWrap(Boolean(ignoredMap.discord), Boolean(svcs.discord?.connected)),
                            children: [
                                renderCardHeader("discord", "DISCORD", "Post updates via Webhook or read/send channels via Discord Bot Token.", Boolean(svcs.discord?.connected)),
                                !ignoredMap.discord && /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                    style: {
                                        display: "grid",
                                        gridTemplateColumns: "repeat(auto-fit, minmax(180px, 1fr))",
                                        gap: 8
                                    },
                                    children: [
                                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("input", {
                                            type: "password",
                                            value: discordWebhook,
                                            onChange: (e)=>setDiscordWebhook(e.target.value),
                                            placeholder: "Webhook URL (https://discord.com/api/webhooks/...)",
                                            style: inputStyle
                                        }, void 0, false, {
                                            fileName: "[project]/components/IntegrationsModal.tsx",
                                            lineNumber: 831,
                                            columnNumber: 17
                                        }, this),
                                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("input", {
                                            type: "password",
                                            value: discordToken,
                                            onChange: (e)=>setDiscordToken(e.target.value),
                                            placeholder: "Or Discord Bot Token",
                                            style: inputStyle
                                        }, void 0, false, {
                                            fileName: "[project]/components/IntegrationsModal.tsx",
                                            lineNumber: 838,
                                            columnNumber: 17
                                        }, this),
                                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("input", {
                                            type: "text",
                                            value: discordChannelId,
                                            onChange: (e)=>setDiscordChannelId(e.target.value),
                                            placeholder: "Default Channel ID (optional)",
                                            style: inputStyle
                                        }, void 0, false, {
                                            fileName: "[project]/components/IntegrationsModal.tsx",
                                            lineNumber: 845,
                                            columnNumber: 17
                                        }, this)
                                    ]
                                }, void 0, true, {
                                    fileName: "[project]/components/IntegrationsModal.tsx",
                                    lineNumber: 824,
                                    columnNumber: 15
                                }, this)
                            ]
                        }, void 0, true, {
                            fileName: "[project]/components/IntegrationsModal.tsx",
                            lineNumber: 811,
                            columnNumber: 11
                        }, this),
                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                            style: cardWrap(Boolean(ignoredMap.telegram), Boolean(svcs.telegram?.connected)),
                            children: [
                                renderCardHeader("telegram", "TELEGRAM REMOTE BOT", "Control JARVIS remotely from your phone via @BotFather token.", Boolean(svcs.telegram?.connected)),
                                !ignoredMap.telegram && /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("input", {
                                    type: "password",
                                    value: telegramToken,
                                    onChange: (e)=>setTelegramToken(e.target.value),
                                    placeholder: "Telegram Bot Token (123456789:ABC...)",
                                    style: inputStyle
                                }, void 0, false, {
                                    fileName: "[project]/components/IntegrationsModal.tsx",
                                    lineNumber: 870,
                                    columnNumber: 15
                                }, this)
                            ]
                        }, void 0, true, {
                            fileName: "[project]/components/IntegrationsModal.tsx",
                            lineNumber: 857,
                            columnNumber: 11
                        }, this),
                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                            style: cardWrap(Boolean(ignoredMap.spotify), Boolean(svcs.spotify?.connected)),
                            children: [
                                renderCardHeader("spotify", "SPOTIFY", "Direct Spotify playback & track search.", Boolean(svcs.spotify?.connected)),
                                !ignoredMap.spotify && /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                    style: {
                                        display: "grid",
                                        gridTemplateColumns: "repeat(auto-fit, minmax(210px, 1fr))",
                                        gap: 8
                                    },
                                    children: [
                                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("input", {
                                            type: "text",
                                            value: spotifyId,
                                            onChange: (e)=>setSpotifyId(e.target.value),
                                            placeholder: "Spotify Client ID",
                                            style: inputStyle
                                        }, void 0, false, {
                                            fileName: "[project]/components/IntegrationsModal.tsx",
                                            lineNumber: 900,
                                            columnNumber: 17
                                        }, this),
                                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("input", {
                                            type: "password",
                                            value: spotifySecret,
                                            onChange: (e)=>setSpotifySecret(e.target.value),
                                            placeholder: "Spotify Client Secret",
                                            style: inputStyle
                                        }, void 0, false, {
                                            fileName: "[project]/components/IntegrationsModal.tsx",
                                            lineNumber: 907,
                                            columnNumber: 17
                                        }, this)
                                    ]
                                }, void 0, true, {
                                    fileName: "[project]/components/IntegrationsModal.tsx",
                                    lineNumber: 893,
                                    columnNumber: 15
                                }, this)
                            ]
                        }, void 0, true, {
                            fileName: "[project]/components/IntegrationsModal.tsx",
                            lineNumber: 880,
                            columnNumber: 11
                        }, this),
                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                            style: cardWrap(Boolean(ignoredMap.trello), Boolean(svcs.trello?.connected)),
                            children: [
                                renderCardHeader("trello", "TRELLO", "Read boards and create Trello task cards.", Boolean(svcs.trello?.connected)),
                                !ignoredMap.trello && /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                    style: {
                                        display: "grid",
                                        gridTemplateColumns: "repeat(auto-fit, minmax(210px, 1fr))",
                                        gap: 8
                                    },
                                    children: [
                                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("input", {
                                            type: "text",
                                            value: trelloKey,
                                            onChange: (e)=>setTrelloKey(e.target.value),
                                            placeholder: "Trello API Key",
                                            style: inputStyle
                                        }, void 0, false, {
                                            fileName: "[project]/components/IntegrationsModal.tsx",
                                            lineNumber: 938,
                                            columnNumber: 17
                                        }, this),
                                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("input", {
                                            type: "password",
                                            value: trelloToken,
                                            onChange: (e)=>setTrelloToken(e.target.value),
                                            placeholder: "Trello Token",
                                            style: inputStyle
                                        }, void 0, false, {
                                            fileName: "[project]/components/IntegrationsModal.tsx",
                                            lineNumber: 945,
                                            columnNumber: 17
                                        }, this)
                                    ]
                                }, void 0, true, {
                                    fileName: "[project]/components/IntegrationsModal.tsx",
                                    lineNumber: 931,
                                    columnNumber: 15
                                }, this)
                            ]
                        }, void 0, true, {
                            fileName: "[project]/components/IntegrationsModal.tsx",
                            lineNumber: 918,
                            columnNumber: 11
                        }, this),
                        [
                            {
                                key: "linear",
                                title: "10 · LINEAR",
                                sub: "Linear GraphQL API — list & create engineering issues",
                                val: linearToken,
                                setVal: setLinearToken,
                                ph: "Linear API Key (lin_api_...)",
                                extraVal: linearTeamId,
                                setExtra: setLinearTeamId,
                                extraPh: "Optional Default Team ID"
                            },
                            {
                                key: "outlook",
                                title: "11 · MICROSOFT OUTLOOK / GRAPH",
                                sub: "Outlook Mail & Calendar via Microsoft Graph v1.0",
                                val: outlookToken,
                                setVal: setOutlookToken,
                                ph: "Microsoft Graph Access Token"
                            },
                            {
                                key: "dropbox",
                                title: "12 · DROPBOX",
                                sub: "Dropbox API v2 — list & search cloud folders",
                                val: dropboxToken,
                                setVal: setDropboxToken,
                                ph: "Dropbox Access Token (sl....)"
                            },
                            {
                                key: "hubspot",
                                title: "13 · HUBSPOT CRM",
                                sub: "HubSpot CRM v3 — contacts & pipeline deals",
                                val: hubspotToken,
                                setVal: setHubspotToken,
                                ph: "HubSpot Private App Token (pat-...)"
                            },
                            {
                                key: "calendly",
                                title: "14 · CALENDLY",
                                sub: "Calendly API v2 — upcoming scheduled meetings",
                                val: calendlyToken,
                                setVal: setCalendlyToken,
                                ph: "Calendly Personal Access Token"
                            }
                        ].map((item)=>{
                            const isConn = Boolean(integrations.services?.[item.key]?.connected);
                            const isIgn = Boolean(ignoredMap[item.key]);
                            return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                style: cardWrap(isIgn, isConn),
                                children: [
                                    renderCardHeader(item.key, item.title, item.sub, isConn, item.key),
                                    !isIgn && /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                        style: {
                                            display: "grid",
                                            gridTemplateColumns: "repeat(auto-fit, minmax(210px, 1fr))",
                                            gap: 8
                                        },
                                        children: [
                                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("input", {
                                                type: "password",
                                                value: item.val,
                                                onChange: (e)=>item.setVal(e.target.value),
                                                placeholder: item.ph,
                                                style: inputStyle
                                            }, void 0, false, {
                                                fileName: "[project]/components/IntegrationsModal.tsx",
                                                lineNumber: 1017,
                                                columnNumber: 21
                                            }, this),
                                            "extraVal" in item && item.setExtra && /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("input", {
                                                type: "text",
                                                value: item.extraVal,
                                                onChange: (e)=>item.setExtra(e.target.value),
                                                placeholder: item.extraPh,
                                                style: inputStyle
                                            }, void 0, false, {
                                                fileName: "[project]/components/IntegrationsModal.tsx",
                                                lineNumber: 1025,
                                                columnNumber: 23
                                            }, this)
                                        ]
                                    }, void 0, true, {
                                        fileName: "[project]/components/IntegrationsModal.tsx",
                                        lineNumber: 1010,
                                        columnNumber: 19
                                    }, this)
                                ]
                            }, item.key, true, {
                                fileName: "[project]/components/IntegrationsModal.tsx",
                                lineNumber: 1007,
                                columnNumber: 15
                            }, this);
                        }),
                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                            style: {
                                marginTop: 6,
                                padding: "6px 4px 2px",
                                borderTop: "1px solid rgba(255,255,255,0.08)",
                                fontFamily: "var(--font-mono)",
                                fontSize: 10,
                                letterSpacing: "0.18em",
                                color: SECONDARY,
                                textTransform: "uppercase"
                            },
                            children: "PERSONAL SOCIALS · PERSISTENT SESSION & ASK-BEFORE-SEND GATE"
                        }, void 0, false, {
                            fileName: "[project]/components/IntegrationsModal.tsx",
                            lineNumber: 1040,
                            columnNumber: 11
                        }, this),
                        [
                            {
                                key: "instagram",
                                title: "15 · INSTAGRAM",
                                sub: "Direct DMs, unread notifications, Reels & feed control (AES-256-GCM session)",
                                canImportCookies: true
                            },
                            {
                                key: "snapchat",
                                title: "16 · SNAPCHAT WEB",
                                sub: "web.snapchat.com — unread Snaps, chats & replies with HUD confirmation",
                                canImportCookies: true
                            },
                            {
                                key: "tiktok",
                                title: "17 · TIKTOK",
                                sub: "Messages, notifications & hands-free For You Reel scrolling/liking",
                                canImportCookies: true
                            },
                            {
                                key: "x",
                                title: "18 · X / TWITTER",
                                sub: "Direct Messages, notifications, timeline & confirmation-gated posts",
                                canImportCookies: true
                            },
                            {
                                key: "whatsapp",
                                title: "19 · WHATSAPP WEB",
                                sub: "web.whatsapp.com — persistent QR sign-in, unread chats & safe replies",
                                canImportCookies: false
                            },
                            {
                                key: "reddit",
                                title: "20 · REDDIT",
                                sub: "Chat / Inbox, notifications & confirmation-gated replies",
                                canImportCookies: true
                            }
                        ].map((soc)=>{
                            const svcInfo = integrations.services?.[soc.key];
                            const isConn = Boolean(svcInfo?.connected);
                            const isIgn = Boolean(ignoredMap[soc.key]);
                            const curHandle = socialHandles[soc.key] || "";
                            const curPerm = socialPerms[soc.key] || "ask";
                            const statusNote = socialMsg[soc.key] || "";
                            return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                "data-testid": `social-card-${soc.key}`,
                                style: cardWrap(isIgn, isConn),
                                children: [
                                    renderCardHeader(soc.key, soc.title, soc.sub, isConn, soc.key),
                                    !isIgn && /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                        style: {
                                            display: "flex",
                                            flexDirection: "column",
                                            gap: 8
                                        },
                                        children: [
                                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                                style: {
                                                    display: "grid",
                                                    gridTemplateColumns: "repeat(auto-fit, minmax(185px, 1fr))",
                                                    gap: 8
                                                },
                                                children: [
                                                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("input", {
                                                        type: "text",
                                                        value: curHandle,
                                                        onChange: (e)=>setSocialHandles((prev)=>({
                                                                    ...prev,
                                                                    [soc.key]: e.target.value
                                                                })),
                                                        placeholder: "Optional @username / label",
                                                        style: inputStyle
                                                    }, void 0, false, {
                                                        fileName: "[project]/components/IntegrationsModal.tsx",
                                                        lineNumber: 1118,
                                                        columnNumber: 23
                                                    }, this),
                                                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("select", {
                                                        value: curPerm,
                                                        onChange: (e)=>setSocialPerms((prev)=>({
                                                                    ...prev,
                                                                    [soc.key]: e.target.value
                                                                })),
                                                        style: {
                                                            ...inputStyle,
                                                            cursor: "pointer"
                                                        },
                                                        children: [
                                                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("option", {
                                                                value: "ask",
                                                                style: {
                                                                    background: "#08101c"
                                                                },
                                                                children: "Policy: Ask Before Sending (Safe)"
                                                            }, void 0, false, {
                                                                fileName: "[project]/components/IntegrationsModal.tsx",
                                                                lineNumber: 1140,
                                                                columnNumber: 25
                                                            }, this),
                                                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("option", {
                                                                value: "readonly",
                                                                style: {
                                                                    background: "#08101c"
                                                                },
                                                                children: "Policy: Read-Only (Inbox & Feed)"
                                                            }, void 0, false, {
                                                                fileName: "[project]/components/IntegrationsModal.tsx",
                                                                lineNumber: 1143,
                                                                columnNumber: 25
                                                            }, this),
                                                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("option", {
                                                                value: "full",
                                                                style: {
                                                                    background: "#08101c"
                                                                },
                                                                children: "Policy: Full Auto (No Prompt)"
                                                            }, void 0, false, {
                                                                fileName: "[project]/components/IntegrationsModal.tsx",
                                                                lineNumber: 1146,
                                                                columnNumber: 25
                                                            }, this),
                                                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("option", {
                                                                value: "paused",
                                                                style: {
                                                                    background: "#08101c"
                                                                },
                                                                children: "Policy: Paused"
                                                            }, void 0, false, {
                                                                fileName: "[project]/components/IntegrationsModal.tsx",
                                                                lineNumber: 1149,
                                                                columnNumber: 25
                                                            }, this)
                                                        ]
                                                    }, void 0, true, {
                                                        fileName: "[project]/components/IntegrationsModal.tsx",
                                                        lineNumber: 1130,
                                                        columnNumber: 23
                                                    }, this)
                                                ]
                                            }, void 0, true, {
                                                fileName: "[project]/components/IntegrationsModal.tsx",
                                                lineNumber: 1111,
                                                columnNumber: 21
                                            }, this),
                                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                                style: {
                                                    display: "flex",
                                                    alignItems: "center",
                                                    gap: 8,
                                                    flexWrap: "wrap"
                                                },
                                                children: [
                                                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("button", {
                                                        type: "button",
                                                        onClick: async ()=>{
                                                            setSocialMsg((p)=>({
                                                                    ...p,
                                                                    [soc.key]: "Opening inside JARVIS HUD…"
                                                                }));
                                                            const r = await openSocialHud(soc.key, isConn ? "feed" : "login");
                                                            if (r.ok && integrationsReady && personaChosen) {
                                                                setIntegrationsModalOpen(false);
                                                            } else {
                                                                setSocialMsg((p)=>({
                                                                        ...p,
                                                                        [soc.key]: r.error || "Opened inside JARVIS HUD."
                                                                    }));
                                                            }
                                                        },
                                                        style: {
                                                            display: "inline-flex",
                                                            alignItems: "center",
                                                            gap: 6,
                                                            padding: "6px 12px",
                                                            borderRadius: 999,
                                                            border: `1px solid ${PRIMARY}`,
                                                            background: `${PRIMARY}26`,
                                                            color: "#ffffff",
                                                            fontFamily: "var(--font-mono)",
                                                            fontSize: 10,
                                                            letterSpacing: "0.10em",
                                                            cursor: "pointer"
                                                        },
                                                        children: [
                                                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$sparkles$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__Sparkles$3e$__["Sparkles"], {
                                                                size: 11
                                                            }, void 0, false, {
                                                                fileName: "[project]/components/IntegrationsModal.tsx",
                                                                lineNumber: 1192,
                                                                columnNumber: 25
                                                            }, this),
                                                            "OPEN IN HUD"
                                                        ]
                                                    }, void 0, true, {
                                                        fileName: "[project]/components/IntegrationsModal.tsx",
                                                        lineNumber: 1156,
                                                        columnNumber: 23
                                                    }, this),
                                                    !isConn && /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("button", {
                                                        type: "button",
                                                        onClick: async ()=>{
                                                            setSocialMsg((p)=>({
                                                                    ...p,
                                                                    [soc.key]: "Opening one-time sign-in popup…"
                                                                }));
                                                            const r = await connectSocialWeb(soc.key, curHandle, curPerm);
                                                            setSocialMsg((p)=>({
                                                                    ...p,
                                                                    [soc.key]: r.message || r.error || "Sign-in window launched."
                                                                }));
                                                        },
                                                        style: {
                                                            display: "inline-flex",
                                                            alignItems: "center",
                                                            gap: 6,
                                                            padding: "6px 12px",
                                                            borderRadius: 999,
                                                            border: `1px solid ${PRIMARY}66`,
                                                            background: "rgba(255,255,255,0.04)",
                                                            color: "rgba(240,237,232,0.92)",
                                                            fontFamily: "var(--font-mono)",
                                                            fontSize: 10,
                                                            letterSpacing: "0.10em",
                                                            cursor: "pointer"
                                                        },
                                                        children: [
                                                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$external$2d$link$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__ExternalLink$3e$__["ExternalLink"], {
                                                                size: 11
                                                            }, void 0, false, {
                                                                fileName: "[project]/components/IntegrationsModal.tsx",
                                                                lineNumber: 1226,
                                                                columnNumber: 27
                                                            }, this),
                                                            soc.key === "whatsapp" ? "SCAN QR POPUP" : "ONE-TIME SIGN IN"
                                                        ]
                                                    }, void 0, true, {
                                                        fileName: "[project]/components/IntegrationsModal.tsx",
                                                        lineNumber: 1197,
                                                        columnNumber: 25
                                                    }, this),
                                                    soc.canImportCookies && !isConn && /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("button", {
                                                        type: "button",
                                                        onClick: async ()=>{
                                                            setSocialMsg((p)=>({
                                                                    ...p,
                                                                    [soc.key]: "Scanning local browsers for active session…"
                                                                }));
                                                            const r = await importSocialCookies(soc.key, "auto", curHandle, curPerm);
                                                            setSocialMsg((p)=>({
                                                                    ...p,
                                                                    [soc.key]: r.ok ? r.message || `Connected via ${r.browser} (${r.cookie_count} cookies encrypted)!` : r.error || "Opened sign-in window."
                                                                }));
                                                        },
                                                        style: {
                                                            display: "inline-flex",
                                                            alignItems: "center",
                                                            gap: 6,
                                                            padding: "6px 12px",
                                                            borderRadius: 999,
                                                            border: `1px solid ${SECONDARY}88`,
                                                            background: `${SECONDARY}18`,
                                                            color: SECONDARY,
                                                            fontFamily: "var(--font-mono)",
                                                            fontSize: 10,
                                                            letterSpacing: "0.10em",
                                                            cursor: "pointer"
                                                        },
                                                        children: [
                                                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$link$2d$2$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__Link2$3e$__["Link2"], {
                                                                size: 11
                                                            }, void 0, false, {
                                                                fileName: "[project]/components/IntegrationsModal.tsx",
                                                                lineNumber: 1268,
                                                                columnNumber: 27
                                                            }, this),
                                                            "IMPORT BROWSER SESSION"
                                                        ]
                                                    }, void 0, true, {
                                                        fileName: "[project]/components/IntegrationsModal.tsx",
                                                        lineNumber: 1232,
                                                        columnNumber: 25
                                                    }, this),
                                                    isConn && svcInfo?.auth_mode && /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("span", {
                                                        style: {
                                                            fontFamily: "var(--font-mono)",
                                                            fontSize: 9.5,
                                                            color: GREEN,
                                                            opacity: 0.9
                                                        },
                                                        children: [
                                                            svcInfo.session_health === "authenticated" ? "✓ Live session verified" : "◌ Session saved — not live-verified",
                                                            " (",
                                                            svcInfo.auth_mode,
                                                            svcInfo.cookies_browser ? ` · ${svcInfo.cookies_browser}` : "",
                                                            ")"
                                                        ]
                                                    }, void 0, true, {
                                                        fileName: "[project]/components/IntegrationsModal.tsx",
                                                        lineNumber: 1274,
                                                        columnNumber: 25
                                                    }, this)
                                                ]
                                            }, void 0, true, {
                                                fileName: "[project]/components/IntegrationsModal.tsx",
                                                lineNumber: 1155,
                                                columnNumber: 21
                                            }, this),
                                            (isConn || statusNote || svcInfo?.session_health === "login_required" || svcInfo?.session_health === "challenge_required") && /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                                style: {
                                                    fontSize: 11,
                                                    color: isConn ? GREEN : "rgba(240,237,232,0.84)",
                                                    lineHeight: 1.4
                                                },
                                                children: svcInfo?.session_health === "login_required" || svcInfo?.session_health === "challenge_required" ? "Sign in or complete the security check using OPEN IN HUD. Your permission policy has not changed." : isConn && (!statusNote || statusNote.includes("Log in once")) ? svcInfo?.session_health === "authenticated" ? "✓ Session verified. Sends still require a server acknowledgment; saved credentials alone never prove delivery." : "Session saved. Open DMs in the HUD or check the inbox to verify the live login." : statusNote
                                            }, void 0, false, {
                                                fileName: "[project]/components/IntegrationsModal.tsx",
                                                lineNumber: 1289,
                                                columnNumber: 23
                                            }, this)
                                        ]
                                    }, void 0, true, {
                                        fileName: "[project]/components/IntegrationsModal.tsx",
                                        lineNumber: 1110,
                                        columnNumber: 19
                                    }, this)
                                ]
                            }, soc.key, true, {
                                fileName: "[project]/components/IntegrationsModal.tsx",
                                lineNumber: 1103,
                                columnNumber: 15
                            }, this);
                        })
                    ]
                }, void 0, true, {
                    fileName: "[project]/components/IntegrationsModal.tsx",
                    lineNumber: 560,
                    columnNumber: 9
                }, this),
                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                    style: {
                        display: "flex",
                        alignItems: "center",
                        justifyContent: "space-between",
                        gap: 10,
                        paddingTop: 8,
                        borderTop: "1px solid rgba(255,255,255,0.09)",
                        flexWrap: "wrap"
                    },
                    children: [
                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("button", {
                            type: "button",
                            onClick: ()=>skipIntegrations(),
                            style: {
                                display: "inline-flex",
                                alignItems: "center",
                                gap: 7,
                                fontFamily: "var(--font-mono)",
                                fontSize: 10.5,
                                letterSpacing: "0.16em",
                                padding: "9px 15px",
                                borderRadius: 999,
                                border: "1px solid rgba(240,237,232,0.22)",
                                background: "rgba(255,255,255,0.03)",
                                color: "rgba(240,237,232,0.78)",
                                cursor: "pointer"
                            },
                            children: isFirstRunStep ? "IGNORE ALL / SKIP FOR NOW" : "CLOSE"
                        }, void 0, false, {
                            fileName: "[project]/components/IntegrationsModal.tsx",
                            lineNumber: 1324,
                            columnNumber: 11
                        }, this),
                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("button", {
                            type: "submit",
                            disabled: saving,
                            style: {
                                display: "inline-flex",
                                alignItems: "center",
                                gap: 8,
                                fontFamily: "var(--font-mono)",
                                fontSize: 10.5,
                                letterSpacing: "0.16em",
                                padding: "10px 18px",
                                borderRadius: 999,
                                border: `1px solid ${PRIMARY}`,
                                background: `${PRIMARY}28`,
                                color: "#ffffff",
                                fontWeight: 600,
                                cursor: "pointer"
                            },
                            children: [
                                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$mail$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__Mail$3e$__["Mail"], {
                                    size: 13
                                }, void 0, false, {
                                    fileName: "[project]/components/IntegrationsModal.tsx",
                                    lineNumber: 1364,
                                    columnNumber: 13
                                }, this),
                                saving ? "SAVING..." : isFirstRunStep ? "SAVE SELECTED & CHOOSE EDITION →" : "SAVE INTEGRATIONS"
                            ]
                        }, void 0, true, {
                            fileName: "[project]/components/IntegrationsModal.tsx",
                            lineNumber: 1345,
                            columnNumber: 11
                        }, this)
                    ]
                }, void 0, true, {
                    fileName: "[project]/components/IntegrationsModal.tsx",
                    lineNumber: 1313,
                    columnNumber: 9
                }, this)
            ]
        }, void 0, true, {
            fileName: "[project]/components/IntegrationsModal.tsx",
            lineNumber: 450,
            columnNumber: 7
        }, this)
    }, void 0, false, {
        fileName: "[project]/components/IntegrationsModal.tsx",
        lineNumber: 431,
        columnNumber: 5
    }, this);
}
_s(IntegrationsModal, "KNU1GBiMZRzm+LSAmD/u2BKAopE=", false, function() {
    return [
        __TURBOPACK__imported__module__$5b$project$5d2f$components$2f$JarvisBridge$2e$tsx__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useJarvis"]
    ];
});
_c = IntegrationsModal;
var _c;
__turbopack_context__.k.register(_c, "IntegrationsModal");
if (typeof globalThis.$RefreshHelpers$ === 'object' && globalThis.$RefreshHelpers !== null) {
    __turbopack_context__.k.registerExports(__turbopack_context__.m, globalThis.$RefreshHelpers$);
}
}),
]);

//# sourceMappingURL=components_IntegrationsModal_tsx_1m7svzvyo3yy6._.js.map