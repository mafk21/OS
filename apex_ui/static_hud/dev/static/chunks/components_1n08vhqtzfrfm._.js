(()=>{"use strict";(globalThis["TURBOPACK"] || (globalThis["TURBOPACK"] = [])).push([typeof document === "object" ? document.currentScript : undefined,
"[project]/components/ApexOverviewPanel.tsx [app-client] (ecmascript)", ((__turbopack_context__) => {
"use strict";

__turbopack_context__.s([
    "default",
    ()=>ApexOverviewPanel
]);
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/next/dist/compiled/react/jsx-dev-runtime.js [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/next/dist/compiled/react/index.js [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$terminal$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__Terminal$3e$__ = __turbopack_context__.i("[project]/node_modules/lucide-react/dist/esm/icons/terminal.js [app-client] (ecmascript) <export default as Terminal>");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$sliders$2d$vertical$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__Sliders$3e$__ = __turbopack_context__.i("[project]/node_modules/lucide-react/dist/esm/icons/sliders-vertical.js [app-client] (ecmascript) <export default as Sliders>");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$scan$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__Scan$3e$__ = __turbopack_context__.i("[project]/node_modules/lucide-react/dist/esm/icons/scan.js [app-client] (ecmascript) <export default as Scan>");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$smartphone$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__Smartphone$3e$__ = __turbopack_context__.i("[project]/node_modules/lucide-react/dist/esm/icons/smartphone.js [app-client] (ecmascript) <export default as Smartphone>");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$mic$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__Mic$3e$__ = __turbopack_context__.i("[project]/node_modules/lucide-react/dist/esm/icons/mic.js [app-client] (ecmascript) <export default as Mic>");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$mic$2d$off$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__MicOff$3e$__ = __turbopack_context__.i("[project]/node_modules/lucide-react/dist/esm/icons/mic-off.js [app-client] (ecmascript) <export default as MicOff>");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$sparkles$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__Sparkles$3e$__ = __turbopack_context__.i("[project]/node_modules/lucide-react/dist/esm/icons/sparkles.js [app-client] (ecmascript) <export default as Sparkles>");
var __TURBOPACK__imported__module__$5b$project$5d2f$components$2f$JarvisBridge$2e$tsx__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/components/JarvisBridge.tsx [app-client] (ecmascript)");
;
var _s = __turbopack_context__.k.signature(), _s1 = __turbopack_context__.k.signature();
"use client";
;
;
;
const WCODE = {
    0: "Clear",
    1: "Mainly clear",
    2: "Partly cloudy",
    3: "Overcast",
    45: "Fog",
    48: "Fog",
    51: "Drizzle",
    53: "Drizzle",
    55: "Drizzle",
    61: "Rain",
    63: "Rain",
    65: "Heavy rain",
    71: "Snow",
    73: "Snow",
    75: "Snow",
    80: "Showers",
    81: "Showers",
    82: "Showers",
    95: "Storm",
    96: "Storm",
    99: "Storm"
};
function Clock({ compact = false }) {
    _s();
    const { assistantName, theme } = (0, __TURBOPACK__imported__module__$5b$project$5d2f$components$2f$JarvisBridge$2e$tsx__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useJarvis"])();
    const ACCENT = theme.primary;
    const [now, setNow] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])(null);
    const [wx, setWx] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])(null);
    (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useEffect"])({
        "Clock.useEffect": ()=>{
            setNow(new Date());
            const id = setInterval({
                "Clock.useEffect.id": ()=>setNow(new Date())
            }["Clock.useEffect.id"], 15000);
            return ({
                "Clock.useEffect": ()=>clearInterval(id)
            })["Clock.useEffect"];
        }
    }["Clock.useEffect"], []);
    (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useEffect"])({
        "Clock.useEffect": ()=>{
            let ok = true;
            const load = {
                "Clock.useEffect.load": ()=>fetch("/api/weather").then({
                        "Clock.useEffect.load": (r)=>r.ok ? r.json() : null
                    }["Clock.useEffect.load"]).then({
                        "Clock.useEffect.load": (d)=>{
                            if (ok && d) {
                                setWx({
                                    temp: d.current?.temperature_2m ?? null,
                                    code: d.current?.weather_code ?? null,
                                    city: d.city || assistantName
                                });
                            }
                        }
                    }["Clock.useEffect.load"]).catch({
                        "Clock.useEffect.load": ()=>{
                            if (ok) setWx({
                                temp: null,
                                code: null,
                                city: assistantName
                            });
                        }
                    }["Clock.useEffect.load"])
            }["Clock.useEffect.load"];
            load();
            const id = setInterval(load, 900000);
            return ({
                "Clock.useEffect": ()=>{
                    ok = false;
                    clearInterval(id);
                }
            })["Clock.useEffect"];
        }
    }["Clock.useEffect"], [
        assistantName
    ]);
    if (!now) return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
        style: {
            height: compact ? 30 : 48
        }
    }, void 0, false, {
        fileName: "[project]/components/ApexOverviewPanel.tsx",
        lineNumber: 80,
        columnNumber: 20
    }, this);
    const time = now.toLocaleTimeString("en-GB", {
        hour: "2-digit",
        minute: "2-digit"
    });
    const date = now.toLocaleDateString("en-US", {
        weekday: "short",
        month: "short",
        day: "numeric"
    });
    if (compact) {
        return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
            style: {
                display: "flex",
                alignItems: "baseline",
                gap: 10
            },
            children: [
                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("span", {
                    style: {
                        fontSize: 18,
                        fontWeight: 300,
                        letterSpacing: "0.08em",
                        color: "rgba(240,237,232,0.82)",
                        lineHeight: 1
                    },
                    children: time
                }, void 0, false, {
                    fileName: "[project]/components/ApexOverviewPanel.tsx",
                    lineNumber: 94,
                    columnNumber: 9
                }, this),
                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("span", {
                    style: {
                        fontFamily: "var(--font-mono)",
                        fontSize: 9,
                        letterSpacing: "0.22em",
                        color: "rgba(180,215,240,0.48)",
                        textTransform: "uppercase"
                    },
                    children: [
                        date,
                        wx?.temp != null ? ` · ${Math.round(wx.temp)}°C` : ""
                    ]
                }, void 0, true, {
                    fileName: "[project]/components/ApexOverviewPanel.tsx",
                    lineNumber: 105,
                    columnNumber: 9
                }, this)
            ]
        }, void 0, true, {
            fileName: "[project]/components/ApexOverviewPanel.tsx",
            lineNumber: 93,
            columnNumber: 7
        }, this);
    }
    return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
        style: {
            display: "flex",
            alignItems: "flex-end",
            gap: 26,
            flexWrap: "wrap"
        },
        children: [
            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                children: [
                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                        style: {
                            fontSize: 34,
                            fontWeight: 300,
                            letterSpacing: "0.04em",
                            color: "#f0ede8",
                            lineHeight: 1,
                            textShadow: `0 0 22px ${ACCENT}44`
                        },
                        children: time
                    }, void 0, false, {
                        fileName: "[project]/components/ApexOverviewPanel.tsx",
                        lineNumber: 124,
                        columnNumber: 9
                    }, this),
                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                        style: {
                            fontSize: 10.5,
                            letterSpacing: "0.2em",
                            color: "rgba(240,237,232,0.55)",
                            marginTop: 4,
                            textTransform: "uppercase"
                        },
                        children: date
                    }, void 0, false, {
                        fileName: "[project]/components/ApexOverviewPanel.tsx",
                        lineNumber: 136,
                        columnNumber: 9
                    }, this)
                ]
            }, void 0, true, {
                fileName: "[project]/components/ApexOverviewPanel.tsx",
                lineNumber: 123,
                columnNumber: 7
            }, this),
            wx && /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                children: [
                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                        style: {
                            fontSize: 22,
                            fontWeight: 300,
                            color: `${ACCENT}ee`
                        },
                        children: wx.temp != null ? Math.round(wx.temp) + "°C" : "ONLINE"
                    }, void 0, false, {
                        fileName: "[project]/components/ApexOverviewPanel.tsx",
                        lineNumber: 150,
                        columnNumber: 11
                    }, this),
                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                        style: {
                            fontSize: 9.5,
                            letterSpacing: "0.12em",
                            color: "rgba(240,237,232,0.5)",
                            marginTop: 2,
                            textTransform: "uppercase"
                        },
                        children: [
                            (wx.city || assistantName).toUpperCase(),
                            wx.city && wx.code != null ? " · " : "",
                            wx.code != null ? (WCODE[wx.code] || "").toUpperCase() : ""
                        ]
                    }, void 0, true, {
                        fileName: "[project]/components/ApexOverviewPanel.tsx",
                        lineNumber: 153,
                        columnNumber: 11
                    }, this)
                ]
            }, void 0, true, {
                fileName: "[project]/components/ApexOverviewPanel.tsx",
                lineNumber: 149,
                columnNumber: 9
            }, this)
        ]
    }, void 0, true, {
        fileName: "[project]/components/ApexOverviewPanel.tsx",
        lineNumber: 122,
        columnNumber: 5
    }, this);
}
_s(Clock, "iJv5talgxFtI9t3t3jSf7EuRo/E=", false, function() {
    return [
        __TURBOPACK__imported__module__$5b$project$5d2f$components$2f$JarvisBridge$2e$tsx__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useJarvis"]
    ];
});
_c = Clock;
function ApexOverviewPanel() {
    _s1();
    const [open, setOpen] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])(false);
    const { assistantName, activePersona, theme, muted, toggleMute, setConsoleOpen, setSettingsOpen, setPersonaModalOpen, captureRegion, openRemoteQr } = (0, __TURBOPACK__imported__module__$5b$project$5d2f$components$2f$JarvisBridge$2e$tsx__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useJarvis"])();
    const ACCENT = theme.primary;
    const tileStyle = {
        display: "flex",
        alignItems: "center",
        gap: 11,
        padding: "10px 14px",
        background: theme.tileBg,
        border: `1px solid ${ACCENT}33`,
        borderRadius: 10,
        cursor: "pointer",
        textAlign: "left",
        backdropFilter: "blur(10px)",
        transition: "all .2s",
        color: "rgba(240,237,232,0.92)",
        width: "100%",
        fontFamily: "inherit"
    };
    return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
        className: "apex-overview",
        style: {
            pointerEvents: "none"
        },
        children: [
            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                onClick: ()=>setOpen((o)=>!o),
                onKeyDown: (e)=>{
                    if (e.key === "Enter" || e.key === " ") {
                        e.preventDefault();
                        setOpen((o)=>!o);
                    }
                },
                role: "button",
                tabIndex: 0,
                "aria-label": "Toggle overview panel",
                "aria-expanded": open,
                style: {
                    marginLeft: 14,
                    marginTop: 10,
                    width: "fit-content",
                    cursor: "pointer",
                    pointerEvents: "auto",
                    userSelect: "none",
                    display: "flex",
                    flexDirection: "column",
                    gap: 5
                },
                children: [
                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                        style: {
                            display: "flex",
                            alignItems: "center",
                            gap: 7
                        },
                        children: [
                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("span", {
                                style: {
                                    width: 5,
                                    height: 5,
                                    borderRadius: "50%",
                                    background: ACCENT,
                                    boxShadow: `0 0 8px ${ACCENT}`,
                                    opacity: open ? 1 : 0.72
                                }
                            }, void 0, false, {
                                fileName: "[project]/components/ApexOverviewPanel.tsx",
                                lineNumber: 233,
                                columnNumber: 11
                            }, this),
                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("span", {
                                style: {
                                    fontFamily: "var(--font-mono)",
                                    fontSize: 9,
                                    letterSpacing: "0.32em",
                                    color: open ? ACCENT : `rgba(${theme.filamentTextRgb},0.62)`,
                                    transition: "color .3s"
                                },
                                children: [
                                    assistantName.toUpperCase(),
                                    " ",
                                    activePersona === "female" ? "♀" : "♂"
                                ]
                            }, void 0, true, {
                                fileName: "[project]/components/ApexOverviewPanel.tsx",
                                lineNumber: 243,
                                columnNumber: 11
                            }, this)
                        ]
                    }, void 0, true, {
                        fileName: "[project]/components/ApexOverviewPanel.tsx",
                        lineNumber: 232,
                        columnNumber: 9
                    }, this),
                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(Clock, {
                        compact: true
                    }, void 0, false, {
                        fileName: "[project]/components/ApexOverviewPanel.tsx",
                        lineNumber: 255,
                        columnNumber: 9
                    }, this)
                ]
            }, void 0, true, {
                fileName: "[project]/components/ApexOverviewPanel.tsx",
                lineNumber: 208,
                columnNumber: 7
            }, this),
            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                style: {
                    paddingLeft: 14,
                    paddingTop: 0,
                    width: "fit-content",
                    pointerEvents: "auto"
                },
                children: open && /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                    style: {
                        marginTop: 16,
                        width: 268,
                        display: "flex",
                        flexDirection: "column",
                        gap: 8
                    },
                    children: [
                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("button", {
                            type: "button",
                            style: tileStyle,
                            onClick: ()=>{
                                setPersonaModalOpen(true);
                                setOpen(false);
                            },
                            children: [
                                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("span", {
                                    style: {
                                        display: "flex",
                                        color: ACCENT
                                    },
                                    children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$sparkles$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__Sparkles$3e$__["Sparkles"], {
                                        size: 16
                                    }, void 0, false, {
                                        fileName: "[project]/components/ApexOverviewPanel.tsx",
                                        lineNumber: 286,
                                        columnNumber: 17
                                    }, this)
                                }, void 0, false, {
                                    fileName: "[project]/components/ApexOverviewPanel.tsx",
                                    lineNumber: 285,
                                    columnNumber: 15
                                }, this),
                                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("span", {
                                    style: {
                                        flex: 1,
                                        fontSize: 11.5,
                                        letterSpacing: "0.05em"
                                    },
                                    children: "Switch Male / Female Edition"
                                }, void 0, false, {
                                    fileName: "[project]/components/ApexOverviewPanel.tsx",
                                    lineNumber: 288,
                                    columnNumber: 15
                                }, this)
                            ]
                        }, void 0, true, {
                            fileName: "[project]/components/ApexOverviewPanel.tsx",
                            lineNumber: 277,
                            columnNumber: 13
                        }, this),
                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("button", {
                            type: "button",
                            style: tileStyle,
                            onClick: ()=>{
                                toggleMute();
                                setOpen(false);
                            },
                            children: [
                                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("span", {
                                    style: {
                                        display: "flex",
                                        color: muted ? "#ff5b79" : ACCENT
                                    },
                                    children: muted ? /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$mic$2d$off$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__MicOff$3e$__["MicOff"], {
                                        size: 16
                                    }, void 0, false, {
                                        fileName: "[project]/components/ApexOverviewPanel.tsx",
                                        lineNumber: 302,
                                        columnNumber: 26
                                    }, this) : /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$mic$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__Mic$3e$__["Mic"], {
                                        size: 16
                                    }, void 0, false, {
                                        fileName: "[project]/components/ApexOverviewPanel.tsx",
                                        lineNumber: 302,
                                        columnNumber: 49
                                    }, this)
                                }, void 0, false, {
                                    fileName: "[project]/components/ApexOverviewPanel.tsx",
                                    lineNumber: 301,
                                    columnNumber: 15
                                }, this),
                                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("span", {
                                    style: {
                                        flex: 1,
                                        fontSize: 11.5,
                                        letterSpacing: "0.05em"
                                    },
                                    children: muted ? "Unmute Microphone" : "Mute Microphone"
                                }, void 0, false, {
                                    fileName: "[project]/components/ApexOverviewPanel.tsx",
                                    lineNumber: 304,
                                    columnNumber: 15
                                }, this)
                            ]
                        }, void 0, true, {
                            fileName: "[project]/components/ApexOverviewPanel.tsx",
                            lineNumber: 293,
                            columnNumber: 13
                        }, this),
                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("button", {
                            type: "button",
                            style: tileStyle,
                            onClick: ()=>{
                                setConsoleOpen((v)=>!v);
                                setOpen(false);
                            },
                            children: [
                                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("span", {
                                    style: {
                                        display: "flex",
                                        color: ACCENT
                                    },
                                    children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$terminal$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__Terminal$3e$__["Terminal"], {
                                        size: 16
                                    }, void 0, false, {
                                        fileName: "[project]/components/ApexOverviewPanel.tsx",
                                        lineNumber: 318,
                                        columnNumber: 17
                                    }, this)
                                }, void 0, false, {
                                    fileName: "[project]/components/ApexOverviewPanel.tsx",
                                    lineNumber: 317,
                                    columnNumber: 15
                                }, this),
                                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("span", {
                                    style: {
                                        flex: 1,
                                        fontSize: 11.5,
                                        letterSpacing: "0.05em"
                                    },
                                    children: "Live Transcript & Logs"
                                }, void 0, false, {
                                    fileName: "[project]/components/ApexOverviewPanel.tsx",
                                    lineNumber: 320,
                                    columnNumber: 15
                                }, this)
                            ]
                        }, void 0, true, {
                            fileName: "[project]/components/ApexOverviewPanel.tsx",
                            lineNumber: 309,
                            columnNumber: 13
                        }, this),
                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("button", {
                            type: "button",
                            style: tileStyle,
                            onClick: ()=>{
                                captureRegion();
                                setOpen(false);
                            },
                            children: [
                                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("span", {
                                    style: {
                                        display: "flex",
                                        color: ACCENT
                                    },
                                    children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$scan$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__Scan$3e$__["Scan"], {
                                        size: 16
                                    }, void 0, false, {
                                        fileName: "[project]/components/ApexOverviewPanel.tsx",
                                        lineNumber: 334,
                                        columnNumber: 17
                                    }, this)
                                }, void 0, false, {
                                    fileName: "[project]/components/ApexOverviewPanel.tsx",
                                    lineNumber: 333,
                                    columnNumber: 15
                                }, this),
                                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("span", {
                                    style: {
                                        flex: 1,
                                        fontSize: 11.5,
                                        letterSpacing: "0.05em"
                                    },
                                    children: "Capture Screen Region"
                                }, void 0, false, {
                                    fileName: "[project]/components/ApexOverviewPanel.tsx",
                                    lineNumber: 336,
                                    columnNumber: 15
                                }, this)
                            ]
                        }, void 0, true, {
                            fileName: "[project]/components/ApexOverviewPanel.tsx",
                            lineNumber: 325,
                            columnNumber: 13
                        }, this),
                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("button", {
                            type: "button",
                            style: tileStyle,
                            onClick: ()=>{
                                setSettingsOpen(true);
                                setOpen(false);
                            },
                            children: [
                                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("span", {
                                    style: {
                                        display: "flex",
                                        color: ACCENT
                                    },
                                    children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$sliders$2d$vertical$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__Sliders$3e$__["Sliders"], {
                                        size: 16
                                    }, void 0, false, {
                                        fileName: "[project]/components/ApexOverviewPanel.tsx",
                                        lineNumber: 350,
                                        columnNumber: 17
                                    }, this)
                                }, void 0, false, {
                                    fileName: "[project]/components/ApexOverviewPanel.tsx",
                                    lineNumber: 349,
                                    columnNumber: 15
                                }, this),
                                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("span", {
                                    style: {
                                        flex: 1,
                                        fontSize: 11.5,
                                        letterSpacing: "0.05em"
                                    },
                                    children: "Voice, Audio & HUD Settings"
                                }, void 0, false, {
                                    fileName: "[project]/components/ApexOverviewPanel.tsx",
                                    lineNumber: 352,
                                    columnNumber: 15
                                }, this)
                            ]
                        }, void 0, true, {
                            fileName: "[project]/components/ApexOverviewPanel.tsx",
                            lineNumber: 341,
                            columnNumber: 13
                        }, this),
                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("button", {
                            type: "button",
                            style: tileStyle,
                            onClick: ()=>{
                                openRemoteQr();
                                setOpen(false);
                            },
                            children: [
                                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("span", {
                                    style: {
                                        display: "flex",
                                        color: ACCENT
                                    },
                                    children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$smartphone$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__Smartphone$3e$__["Smartphone"], {
                                        size: 16
                                    }, void 0, false, {
                                        fileName: "[project]/components/ApexOverviewPanel.tsx",
                                        lineNumber: 366,
                                        columnNumber: 17
                                    }, this)
                                }, void 0, false, {
                                    fileName: "[project]/components/ApexOverviewPanel.tsx",
                                    lineNumber: 365,
                                    columnNumber: 15
                                }, this),
                                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("span", {
                                    style: {
                                        flex: 1,
                                        fontSize: 11.5,
                                        letterSpacing: "0.05em"
                                    },
                                    children: "Connect Phone Remote"
                                }, void 0, false, {
                                    fileName: "[project]/components/ApexOverviewPanel.tsx",
                                    lineNumber: 368,
                                    columnNumber: 15
                                }, this)
                            ]
                        }, void 0, true, {
                            fileName: "[project]/components/ApexOverviewPanel.tsx",
                            lineNumber: 357,
                            columnNumber: 13
                        }, this)
                    ]
                }, void 0, true, {
                    fileName: "[project]/components/ApexOverviewPanel.tsx",
                    lineNumber: 268,
                    columnNumber: 11
                }, this)
            }, void 0, false, {
                fileName: "[project]/components/ApexOverviewPanel.tsx",
                lineNumber: 258,
                columnNumber: 7
            }, this)
        ]
    }, void 0, true, {
        fileName: "[project]/components/ApexOverviewPanel.tsx",
        lineNumber: 207,
        columnNumber: 5
    }, this);
}
_s1(ApexOverviewPanel, "vjE3jopEnBomVU/C1ejZstOmY9g=", false, function() {
    return [
        __TURBOPACK__imported__module__$5b$project$5d2f$components$2f$JarvisBridge$2e$tsx__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useJarvis"]
    ];
});
_c1 = ApexOverviewPanel;
var _c, _c1;
__turbopack_context__.k.register(_c, "Clock");
__turbopack_context__.k.register(_c1, "ApexOverviewPanel");
if (typeof globalThis.$RefreshHelpers$ === 'object' && globalThis.$RefreshHelpers !== null) {
    __turbopack_context__.k.registerExports(__turbopack_context__.m, globalThis.$RefreshHelpers$);
}
}),
"[project]/components/ApexWorld.tsx [app-client] (ecmascript)", ((__turbopack_context__) => {
"use strict";

__turbopack_context__.s([
    "AgentOverview",
    ()=>AgentOverview,
    "INFO",
    ()=>INFO,
    "ROSTER",
    ()=>ROSTER,
    "default",
    ()=>ApexWorld
]);
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/next/dist/compiled/react/jsx-dev-runtime.js [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$shared$2f$lib$2f$app$2d$dynamic$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/next/dist/shared/lib/app-dynamic.js [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/next/dist/compiled/react/index.js [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$components$2f$ReasoningWeb$2e$jsx__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/components/ReasoningWeb.jsx [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$components$2f$JarvisBridge$2e$tsx__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/components/JarvisBridge.tsx [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$components$2f$WorkerOrbsLayer$2e$tsx__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/components/WorkerOrbsLayer.tsx [app-client] (ecmascript)");
;
;
;
var _s = __turbopack_context__.k.signature(), _s1 = __turbopack_context__.k.signature();
"use client";
;
;
;
;
;
const ApexMaleHumanoid = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$shared$2f$lib$2f$app$2d$dynamic$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["default"])(_c = ()=>__turbopack_context__.A("[project]/components/ApexMaleHumanoid.tsx [app-client] (ecmascript, next/dynamic entry, async loader)"), {
    loadableGenerated: {
        modules: [
            "[project]/components/ApexMaleHumanoid.tsx [app-client] (ecmascript, next/dynamic entry)"
        ]
    },
    ssr: false
});
_c1 = ApexMaleHumanoid;
const ApexFemaleHumanoid = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$shared$2f$lib$2f$app$2d$dynamic$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["default"])(_c2 = ()=>__turbopack_context__.A("[project]/components/ApexFemaleHumanoid.tsx [app-client] (ecmascript, next/dynamic entry, async loader)"), {
    loadableGenerated: {
        modules: [
            "[project]/components/ApexFemaleHumanoid.tsx [app-client] (ecmascript, next/dynamic entry)"
        ]
    },
    ssr: false
});
_c3 = ApexFemaleHumanoid;
const ReasoningWeb = __TURBOPACK__imported__module__$5b$project$5d2f$components$2f$ReasoningWeb$2e$jsx__$5b$app$2d$client$5d$__$28$ecmascript$29$__["default"];
const ROSTER = [
    {
        key: "chief_of_staff",
        name: "Chief of staff",
        color: "#00e5ff"
    },
    {
        key: "memory",
        name: "Memory",
        color: "#00e5ff"
    },
    {
        key: "strategist",
        name: "Strategist",
        color: "#00e5ff"
    },
    {
        key: "researcher",
        name: "Researcher",
        color: "#00e5ff"
    },
    {
        key: "finance",
        name: "Finance",
        color: "#00e5ff"
    },
    {
        key: "editor",
        name: "Editor",
        color: "#00e5ff"
    },
    {
        key: "sales",
        name: "Sales",
        color: "#f5a623"
    },
    {
        key: "marketing",
        name: "Marketing",
        color: "#f5a623"
    },
    {
        key: "ops",
        name: "Ops",
        color: "#f5a623"
    },
    {
        key: "social_media",
        name: "Social",
        color: "#f5a623"
    },
    {
        key: "engineering",
        name: "Engineering",
        color: "#f5a623"
    },
    {
        key: "design",
        name: "Design",
        color: "#f5a623"
    },
    {
        key: "developer",
        name: "Developer",
        color: "#f5a623"
    },
    {
        key: "analytics",
        name: "Analytics",
        color: "#7f9bb3"
    },
    {
        key: "crm",
        name: "CRM",
        color: "#7f9bb3"
    },
    {
        key: "calendar",
        name: "Calendar",
        color: "#7f9bb3"
    },
    {
        key: "email",
        name: "Email",
        color: "#7f9bb3"
    },
    {
        key: "drive",
        name: "Drive",
        color: "#7f9bb3"
    }
];
const INFO = {
    chief_of_staff: {
        role: "Core orchestrator · Morning Briefing & Focus",
        status: "online",
        caps: [
            "Routes every voice & text command to the right JARVIS tool",
            "Delivers daily morning briefings, weather & top priorities",
            "Focus Guardian deep-work sessions & distraction control"
        ],
        asks: [
            "Give me my morning briefing",
            "Start a 25 minute focus session"
        ]
    },
    memory: {
        role: "Long-term memory · Smart Notes & Lectures",
        status: "online",
        caps: [
            "Persistent semantic recall of facts, preferences & past sessions",
            "Smart Notes vault with instant tagging and search",
            "Lecture Capture & structured takeaway extraction"
        ],
        asks: [
            "What do you remember about me?",
            "List my recent smart notes"
        ]
    },
    strategist: {
        role: "Autonomous multi-step planner",
        status: "online",
        caps: [
            "Breaks complex goals into verified sequential tool steps",
            "Tracks session context across multi-turn reasoning",
            "Proactive follow-through and undoable execution"
        ],
        asks: [
            "Plan my priorities for today",
            "Summarize what we worked on"
        ]
    },
    researcher: {
        role: "Live Web Search & YouTube Intelligence",
        status: "online",
        caps: [
            "Real-time DuckDuckGo & web page extraction",
            "YouTube video search, HUD playback & transcript summaries",
            "Fact-checked synthesis with live sources"
        ],
        asks: [
            "Search the web for latest AI news",
            "Summarize this topic for me"
        ]
    },
    finance: {
        role: "Spreadsheets & quantitative analysis",
        status: "online",
        caps: [
            "Generates formatted Excel (.xlsx) workbooks on disk",
            "Budget, pricing & numerical sanity checks",
            "CSV and tabular document inspection"
        ],
        asks: [
            "Create an Excel expense tracker on my Desktop"
        ]
    },
    editor: {
        role: "Clipboard Intelligence & Document Processor",
        status: "online",
        caps: [
            "Reads, rewrites, translates & cleans clipboard text or code",
            "Processes PDF, DOCX and PPTX documents locally",
            "Drafts crisp emails, summaries and reports"
        ],
        asks: [
            "Summarize what is on my clipboard",
            "Polish my clipboard text"
        ]
    },
    sales: {
        role: "Messaging & Phone Relay",
        status: "online",
        caps: [
            "WhatsApp automation & quick message drafting",
            "Encrypted LAN phone dashboard & remote voice relay",
            "Follow-up reminders and contact coordination"
        ],
        asks: [
            "Open phone remote connection"
        ]
    },
    marketing: {
        role: "Content & Briefing Studio",
        status: "online",
        caps: [
            "Brainstorms hooks, scripts and structured outlines",
            "Combines live web research with local notes",
            "Exports clean drafts straight to files or clipboard"
        ],
        asks: [
            "Draft a short launch announcement"
        ]
    },
    ops: {
        role: "OS & Device Management",
        status: "online",
        caps: [
            "Opens & closes real desktop apps, PowerShell, Terminal & Explorer",
            "Controls system volume, brightness, Wi-Fi, window snapping & shortcuts",
            "Unforgeable HUD confirmation gate for shutdown & restart"
        ],
        asks: [
            "Open PowerShell",
            "What windows are open right now?"
        ]
    },
    social_media: {
        role: "Playwright Browser Automation",
        status: "online",
        caps: [
            "Drives a real browser: navigate, click, type & read pages",
            "Opens websites, dashboards and web apps by voice",
            "Extracts live page state back into conversation"
        ],
        asks: [
            "Open GitHub in the browser",
            "Search Google for Three.js docs"
        ]
    },
    engineering: {
        role: "System Doctor & Hardware Telemetry",
        status: "online",
        caps: [
            "Live CPU, RAM, disk, battery, network & NVIDIA GPU diagnostics",
            "Top resource-hog process inspection & health checks",
            "Smart home (Tuya) & 3D printer MQTT hooks"
        ],
        asks: [
            "Run a full system health check",
            "How much RAM and CPU am I using?"
        ]
    },
    design: {
        role: "Screen Vision, Camera & Region Capture",
        status: "online",
        caps: [
            "Instant full-screen or rubber-band region vision analysis",
            "Live webcam awareness piped into Gemini Live",
            "Reads UI errors, diagrams and visual layouts on screen"
        ],
        asks: [
            "What is on my screen right now?"
        ]
    },
    developer: {
        role: "Code Helper & Terminal Execution",
        status: "online",
        caps: [
            "Inspects git status, diffs, branches & project structure",
            "Runs safe shell/Python diagnostics and explains tracebacks",
            "Assists with debugging, refactoring and test runs"
        ],
        asks: [
            "Check git status of this project",
            "Help debug clipboard error"
        ]
    },
    analytics: {
        role: "System & Session Telemetry",
        status: "integration",
        caps: [
            "Monitors real-time voice latency, echo guard & model health",
            "Tracks live tool executions across the session"
        ],
        asks: [
            "Give me a system performance report"
        ]
    },
    crm: {
        role: "Personal Context & Preferences",
        status: "integration",
        caps: [
            "Adapts to your workflow, projects and communication style",
            "Persists custom preferences across restarts"
        ]
    },
    calendar: {
        role: "Google Calendar & Reminders",
        status: "integration",
        caps: [
            "Reads upcoming schedule & creates calendar events",
            "Local desktop timers and reminders"
        ],
        asks: [
            "Set a reminder in 10 minutes to stretch"
        ]
    },
    email: {
        role: "Gmail Integration",
        status: "integration",
        caps: [
            "Triages unread inbox threads & drafts replies via OAuth",
            "Summarizes important messages on request"
        ]
    },
    drive: {
        role: "File Controller & Local Storage",
        status: "integration",
        caps: [
            "Finds, creates, moves, renames & safely recycles local files",
            "Full undo stack for reversible file & setting actions"
        ],
        asks: [
            "List files in my Downloads folder"
        ]
    }
};
const STATUS_LINE = {
    online: {
        color: "#34d399",
        text: "Online · JARVIS routes to this capability automatically"
    },
    standby: {
        color: "#c9a84c",
        text: "Standby · Available on demand"
    },
    integration: {
        color: "#7f9bb3",
        text: "Integrated · Wired into JARVIS core"
    }
};
function AgentOverview({ sel, onClose }) {
    _s();
    const { sendText, fireLocalTrace } = (0, __TURBOPACK__imported__module__$5b$project$5d2f$components$2f$JarvisBridge$2e$tsx__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useJarvis"])();
    const [pos, setPos] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])(null);
    const dragRef = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useRef"])(null);
    const info = INFO[sel.key] ?? {
        role: "Specialist",
        status: "online",
        caps: [
            "Part of the JARVIS core"
        ]
    };
    const c = sel.color;
    const status = STATUS_LINE[info.status];
    (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useEffect"])({
        "AgentOverview.useEffect": ()=>{
            setPos({
                x: Math.max(8, window.innerWidth / 2 - 175),
                y: Math.max(86, window.innerHeight * 0.16)
            });
            const onKey = {
                "AgentOverview.useEffect.onKey": (e)=>{
                    if (e.key === "Escape") onClose();
                }
            }["AgentOverview.useEffect.onKey"];
            window.addEventListener("keydown", onKey);
            return ({
                "AgentOverview.useEffect": ()=>window.removeEventListener("keydown", onKey)
            })["AgentOverview.useEffect"];
        }
    }["AgentOverview.useEffect"], [
        onClose
    ]);
    const panelRef = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useRef"])(null);
    (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useEffect"])({
        "AgentOverview.useEffect": ()=>{
            if (!pos) return;
            const opener = document.activeElement;
            panelRef.current?.querySelector("button")?.focus();
            return ({
                "AgentOverview.useEffect": ()=>{
                    if (opener && document.contains(opener)) opener.focus();
                }
            })["AgentOverview.useEffect"];
        }
    }["AgentOverview.useEffect"], [
        pos
    ]);
    const onMouseDown = (e)=>{
        if (!pos) return;
        dragRef.current = {
            sx: e.clientX - pos.x,
            sy: e.clientY - pos.y
        };
        const move = (ev)=>{
            if (dragRef.current) {
                setPos({
                    x: ev.clientX - dragRef.current.sx,
                    y: ev.clientY - dragRef.current.sy
                });
            }
        };
        const up = ()=>{
            dragRef.current = null;
            document.removeEventListener("mousemove", move);
            document.removeEventListener("mouseup", up);
        };
        document.addEventListener("mousemove", move);
        document.addEventListener("mouseup", up);
    };
    if (!pos) return null;
    return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
        ref: panelRef,
        role: "dialog",
        "aria-modal": "true",
        "aria-label": `${sel.name} overview`,
        style: {
            position: "fixed",
            left: pos.x,
            top: pos.y,
            width: "min(356px, 92vw)",
            zIndex: 60,
            background: "rgba(4,3,12,0.92)",
            backdropFilter: "blur(24px)",
            border: `1px solid ${c}44`,
            borderRadius: 16,
            boxShadow: `0 0 40px ${c}18, 0 8px 32px rgba(0,0,0,0.6)`,
            overflow: "hidden"
        },
        children: [
            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                onMouseDown: onMouseDown,
                style: {
                    display: "flex",
                    alignItems: "center",
                    gap: 10,
                    padding: "14px 16px",
                    borderBottom: `1px solid ${c}22`,
                    cursor: "grab",
                    userSelect: "none",
                    background: `linear-gradient(135deg, ${c}0a 0%, transparent 100%)`
                },
                children: [
                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                        style: {
                            width: 36,
                            height: 36,
                            borderRadius: "50%",
                            background: `${c}14`,
                            border: `1px solid ${c}44`,
                            display: "flex",
                            alignItems: "center",
                            justifyContent: "center",
                            flexShrink: 0
                        },
                        children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("span", {
                            style: {
                                width: 10,
                                height: 10,
                                borderRadius: "50%",
                                background: c,
                                boxShadow: `0 0 10px ${c}`
                            }
                        }, void 0, false, {
                            fileName: "[project]/components/ApexWorld.tsx",
                            lineNumber: 348,
                            columnNumber: 11
                        }, this)
                    }, void 0, false, {
                        fileName: "[project]/components/ApexWorld.tsx",
                        lineNumber: 335,
                        columnNumber: 9
                    }, this),
                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                        children: [
                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                style: {
                                    fontSize: 13,
                                    fontWeight: 600,
                                    letterSpacing: "0.08em",
                                    color: c
                                },
                                children: sel.name.toUpperCase()
                            }, void 0, false, {
                                fileName: "[project]/components/ApexWorld.tsx",
                                lineNumber: 359,
                                columnNumber: 11
                            }, this),
                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                style: {
                                    fontSize: 10,
                                    color: "rgba(255,255,255,0.42)",
                                    letterSpacing: "0.05em",
                                    textTransform: "uppercase"
                                },
                                children: info.role
                            }, void 0, false, {
                                fileName: "[project]/components/ApexWorld.tsx",
                                lineNumber: 369,
                                columnNumber: 11
                            }, this)
                        ]
                    }, void 0, true, {
                        fileName: "[project]/components/ApexWorld.tsx",
                        lineNumber: 358,
                        columnNumber: 9
                    }, this),
                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("button", {
                        onClick: onClose,
                        "aria-label": "Close",
                        style: {
                            marginLeft: "auto",
                            background: "none",
                            border: "none",
                            color: "rgba(255,255,255,0.35)",
                            cursor: "pointer",
                            fontSize: 18,
                            lineHeight: 1,
                            padding: "6px 8px",
                            transition: "color 0.2s"
                        },
                        onMouseEnter: (e)=>e.currentTarget.style.color = "rgba(255,255,255,0.8)",
                        onMouseLeave: (e)=>e.currentTarget.style.color = "rgba(255,255,255,0.35)",
                        children: "×"
                    }, void 0, false, {
                        fileName: "[project]/components/ApexWorld.tsx",
                        lineNumber: 380,
                        columnNumber: 9
                    }, this)
                ]
            }, void 0, true, {
                fileName: "[project]/components/ApexWorld.tsx",
                lineNumber: 322,
                columnNumber: 7
            }, this),
            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                style: {
                    padding: "14px 16px",
                    display: "flex",
                    flexDirection: "column",
                    gap: 16
                },
                children: [
                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                        children: [
                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                style: {
                                    fontSize: 9,
                                    letterSpacing: "0.14em",
                                    color: `${c}99`,
                                    marginBottom: 8,
                                    fontFamily: "var(--font-mono)"
                                },
                                children: "WHAT JARVIS HANDLES HERE"
                            }, void 0, false, {
                                fileName: "[project]/components/ApexWorld.tsx",
                                lineNumber: 414,
                                columnNumber: 11
                            }, this),
                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                style: {
                                    display: "flex",
                                    flexDirection: "column",
                                    gap: 5
                                },
                                children: info.caps.map((cap)=>/*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                        style: {
                                            display: "flex",
                                            alignItems: "flex-start",
                                            gap: 7
                                        },
                                        children: [
                                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                                style: {
                                                    width: 3,
                                                    height: 3,
                                                    borderRadius: "50%",
                                                    background: `${c}99`,
                                                    marginTop: 6,
                                                    flexShrink: 0
                                                }
                                            }, void 0, false, {
                                                fileName: "[project]/components/ApexWorld.tsx",
                                                lineNumber: 431,
                                                columnNumber: 17
                                            }, this),
                                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("span", {
                                                style: {
                                                    fontSize: 11.5,
                                                    color: "rgba(255,255,255,0.68)",
                                                    lineHeight: 1.5
                                                },
                                                children: cap
                                            }, void 0, false, {
                                                fileName: "[project]/components/ApexWorld.tsx",
                                                lineNumber: 441,
                                                columnNumber: 17
                                            }, this)
                                        ]
                                    }, cap, true, {
                                        fileName: "[project]/components/ApexWorld.tsx",
                                        lineNumber: 427,
                                        columnNumber: 15
                                    }, this))
                            }, void 0, false, {
                                fileName: "[project]/components/ApexWorld.tsx",
                                lineNumber: 425,
                                columnNumber: 11
                            }, this)
                        ]
                    }, void 0, true, {
                        fileName: "[project]/components/ApexWorld.tsx",
                        lineNumber: 413,
                        columnNumber: 9
                    }, this),
                    info.asks && info.asks.length > 0 && /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                        children: [
                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                style: {
                                    fontSize: 9,
                                    letterSpacing: "0.14em",
                                    color: `${c}99`,
                                    marginBottom: 8,
                                    fontFamily: "var(--font-mono)"
                                },
                                children: "CLICK TO RUN WITH JARVIS"
                            }, void 0, false, {
                                fileName: "[project]/components/ApexWorld.tsx",
                                lineNumber: 457,
                                columnNumber: 13
                            }, this),
                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                style: {
                                    display: "flex",
                                    flexWrap: "wrap",
                                    gap: 6
                                },
                                children: info.asks.map((task)=>/*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("button", {
                                        type: "button",
                                        onClick: ()=>{
                                            fireLocalTrace([
                                                sel.key
                                            ]);
                                            sendText(task, sel.key);
                                            onClose();
                                        },
                                        style: {
                                            padding: "5px 11px",
                                            background: `${c}12`,
                                            border: `1px solid ${c}38`,
                                            borderRadius: 20,
                                            fontSize: 10.5,
                                            color: `${c}ee`,
                                            cursor: "pointer",
                                            fontFamily: "inherit",
                                            transition: "all 0.18s"
                                        },
                                        children: [
                                            task,
                                            " ↗"
                                        ]
                                    }, task, true, {
                                        fileName: "[project]/components/ApexWorld.tsx",
                                        lineNumber: 470,
                                        columnNumber: 17
                                    }, this))
                            }, void 0, false, {
                                fileName: "[project]/components/ApexWorld.tsx",
                                lineNumber: 468,
                                columnNumber: 13
                            }, this)
                        ]
                    }, void 0, true, {
                        fileName: "[project]/components/ApexWorld.tsx",
                        lineNumber: 456,
                        columnNumber: 11
                    }, this),
                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                        style: {
                            display: "flex",
                            alignItems: "center",
                            gap: 7,
                            borderTop: `1px solid ${c}1a`,
                            paddingTop: 12
                        },
                        children: [
                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("span", {
                                style: {
                                    width: 7,
                                    height: 7,
                                    borderRadius: "50%",
                                    background: status.color,
                                    boxShadow: `0 0 8px ${status.color}`
                                }
                            }, void 0, false, {
                                fileName: "[project]/components/ApexWorld.tsx",
                                lineNumber: 506,
                                columnNumber: 11
                            }, this),
                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("span", {
                                style: {
                                    fontSize: 9.5,
                                    letterSpacing: "0.08em",
                                    color: "rgba(255,255,255,0.48)",
                                    textTransform: "uppercase"
                                },
                                children: status.text
                            }, void 0, false, {
                                fileName: "[project]/components/ApexWorld.tsx",
                                lineNumber: 515,
                                columnNumber: 11
                            }, this)
                        ]
                    }, void 0, true, {
                        fileName: "[project]/components/ApexWorld.tsx",
                        lineNumber: 497,
                        columnNumber: 9
                    }, this)
                ]
            }, void 0, true, {
                fileName: "[project]/components/ApexWorld.tsx",
                lineNumber: 405,
                columnNumber: 7
            }, this)
        ]
    }, void 0, true, {
        fileName: "[project]/components/ApexWorld.tsx",
        lineNumber: 303,
        columnNumber: 5
    }, this);
}
_s(AgentOverview, "sLAChQ4Xj9axbe2vR+Z5PpMoowo=", false, function() {
    return [
        __TURBOPACK__imported__module__$5b$project$5d2f$components$2f$JarvisBridge$2e$tsx__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useJarvis"]
    ];
});
_c4 = AgentOverview;
function ApexWorld() {
    _s1();
    const { activePersona, theme, orbState, rawState, lastSubtitle, trace, tapOrb, fireLocalTrace } = (0, __TURBOPACK__imported__module__$5b$project$5d2f$components$2f$JarvisBridge$2e$tsx__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useJarvis"])();
    const [selected, setSelected] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])(null);
    const [reduced, setReduced] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])(false);
    const [cam, setCam] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])({
        x: 0,
        y: 0,
        zoom: 1,
        tiltX: 0,
        tiltY: 0
    });
    const [maleWebVisible, setMaleWebVisible] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])(false);
    const [humanoidPulse, setHumanoidPulse] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])(0);
    const isMale = activePersona === "male";
    const HumanoidFigure = isMale ? ApexMaleHumanoid : ApexFemaleHumanoid;
    const handleCoreTap = ()=>{
        setHumanoidPulse((p)=>p + 1);
        tapOrb();
    };
    const openAgent = (n)=>{
        fireLocalTrace([
            n.key
        ]);
        setSelected(n);
    };
    (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useEffect"])({
        "ApexWorld.useEffect": ()=>{
            const mq = window.matchMedia("(prefers-reduced-motion: reduce)");
            const apply = {
                "ApexWorld.useEffect.apply": ()=>setReduced(mq.matches)
            }["ApexWorld.useEffect.apply"];
            apply();
            mq.addEventListener("change", apply);
            return ({
                "ApexWorld.useEffect": ()=>mq.removeEventListener("change", apply)
            })["ApexWorld.useEffect"];
        }
    }["ApexWorld.useEffect"], []);
    // Keyboard 3D World Navigation (WASD / Arrow pan+tilt, +/- zoom, 0/Home reset)
    (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useEffect"])({
        "ApexWorld.useEffect": ()=>{
            const onKey = {
                "ApexWorld.useEffect.onKey": (e)=>{
                    const el = e.target;
                    if (el && (el.tagName === "INPUT" || el.tagName === "TEXTAREA" || el.tagName === "SELECT" || el.isContentEditable)) {
                        return;
                    }
                    if (e.metaKey || e.ctrlKey || e.altKey) return;
                    switch(e.key){
                        case "ArrowLeft":
                        case "a":
                        case "A":
                            setCam({
                                "ApexWorld.useEffect.onKey": (c)=>({
                                        ...c,
                                        x: Math.min(180, c.x + 22),
                                        tiltY: Math.max(-14, c.tiltY - 2)
                                    })
                            }["ApexWorld.useEffect.onKey"]);
                            break;
                        case "ArrowRight":
                        case "d":
                        case "D":
                            setCam({
                                "ApexWorld.useEffect.onKey": (c)=>({
                                        ...c,
                                        x: Math.max(-180, c.x - 22),
                                        tiltY: Math.min(14, c.tiltY + 2)
                                    })
                            }["ApexWorld.useEffect.onKey"]);
                            break;
                        case "ArrowUp":
                        case "w":
                        case "W":
                            setCam({
                                "ApexWorld.useEffect.onKey": (c)=>({
                                        ...c,
                                        y: Math.min(140, c.y + 18),
                                        tiltX: Math.min(12, c.tiltX + 1.8)
                                    })
                            }["ApexWorld.useEffect.onKey"]);
                            break;
                        case "ArrowDown":
                        case "s":
                        case "S":
                            setCam({
                                "ApexWorld.useEffect.onKey": (c)=>({
                                        ...c,
                                        y: Math.max(-140, c.y - 18),
                                        tiltX: Math.max(-12, c.tiltX - 1.8)
                                    })
                            }["ApexWorld.useEffect.onKey"]);
                            break;
                        case "+":
                        case "=":
                            setCam({
                                "ApexWorld.useEffect.onKey": (c)=>({
                                        ...c,
                                        zoom: Math.min(1.36, +(c.zoom + 0.08).toFixed(2))
                                    })
                            }["ApexWorld.useEffect.onKey"]);
                            break;
                        case "-":
                        case "_":
                            setCam({
                                "ApexWorld.useEffect.onKey": (c)=>({
                                        ...c,
                                        zoom: Math.max(0.8, +(c.zoom - 0.08).toFixed(2))
                                    })
                            }["ApexWorld.useEffect.onKey"]);
                            break;
                        case "0":
                        case "Home":
                            setCam({
                                x: 0,
                                y: 0,
                                zoom: 1,
                                tiltX: 0,
                                tiltY: 0
                            });
                            break;
                        default:
                            break;
                    }
                }
            }["ApexWorld.useEffect.onKey"];
            window.addEventListener("keydown", onKey);
            return ({
                "ApexWorld.useEffect": ()=>window.removeEventListener("keydown", onKey)
            })["ApexWorld.useEffect"];
        }
    }["ApexWorld.useEffect"], []);
    const camShifted = cam.x !== 0 || cam.y !== 0 || cam.zoom !== 1 || cam.tiltX !== 0 || cam.tiltY !== 0;
    const webState = orbState === "thinking" ? "processing" : orbState === "speaking" ? "speaking" : orbState === "listening" ? "listening" : "standby";
    return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
        style: {
            position: "absolute",
            inset: 0,
            overflow: "hidden",
            userSelect: "none"
        },
        children: [
            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                "aria-hidden": "true",
                style: {
                    position: "absolute",
                    inset: 0,
                    background: isMale ? "#02050a" : "#08030a",
                    transition: "background 0.65s ease"
                }
            }, void 0, false, {
                fileName: "[project]/components/ApexWorld.tsx",
                lineNumber: 661,
                columnNumber: 7
            }, this),
            isMale && /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                "aria-hidden": "true",
                "data-testid": "male-neural-landscape",
                style: {
                    position: "absolute",
                    inset: 0,
                    zIndex: 0,
                    pointerEvents: "none",
                    backgroundImage: "linear-gradient(to bottom, rgba(1,4,8,0.1) 0%, rgba(1,4,8,0) 54%, rgba(1,4,8,0.25) 100%), url('/hologram/male_neural_landscape.png')",
                    backgroundPosition: "center bottom",
                    backgroundRepeat: "no-repeat",
                    backgroundSize: "cover",
                    opacity: orbState === "speaking" ? 0.92 : orbState === "thinking" ? 0.86 : 0.78,
                    filter: orbState === "speaking" ? "saturate(1.14) brightness(1.06)" : "saturate(0.96) brightness(0.88)",
                    transform: "scale(1.015)",
                    transition: "opacity 0.7s ease, filter 0.7s ease"
                }
            }, void 0, false, {
                fileName: "[project]/components/ApexWorld.tsx",
                lineNumber: 674,
                columnNumber: 9
            }, this),
            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                "aria-hidden": "true",
                style: {
                    position: "absolute",
                    inset: 0,
                    zIndex: 1,
                    pointerEvents: "none",
                    mixBlendMode: "screen",
                    background: `radial-gradient(circle at 50% 44%, rgba(${theme.orbGlowRgb},${orbState === "speaking" ? 0.09 : 0.04}) 0%, transparent 56%)`,
                    transition: "background 0.6s ease"
                }
            }, void 0, false, {
                fileName: "[project]/components/ApexWorld.tsx",
                lineNumber: 698,
                columnNumber: 7
            }, this),
            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                style: {
                    position: "absolute",
                    inset: 0,
                    zIndex: 2,
                    transform: camShifted ? `perspective(1200px) translate3d(${cam.x}px, ${cam.y}px, 0) scale(${cam.zoom}) rotateX(${cam.tiltX}deg) rotateY(${cam.tiltY}deg)` : undefined,
                    transition: "transform 0.28s cubic-bezier(0.22, 1, 0.36, 1)",
                    transformStyle: "preserve-3d"
                },
                children: [
                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                        style: {
                            position: "absolute",
                            inset: 0,
                            zIndex: 2,
                            pointerEvents: "none"
                        },
                        children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(HumanoidFigure, {
                            state: orbState,
                            trace: trace,
                            reducedMotion: reduced,
                            constellationVisible: maleWebVisible,
                            onToggleConstellation: ()=>setMaleWebVisible((v)=>!v),
                            pulseSignal: humanoidPulse
                        }, void 0, false, {
                            fileName: "[project]/components/ApexWorld.tsx",
                            lineNumber: 733,
                            columnNumber: 13
                        }, this)
                    }, void 0, false, {
                        fileName: "[project]/components/ApexWorld.tsx",
                        lineNumber: 725,
                        columnNumber: 9
                    }, this),
                    maleWebVisible && /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                        "aria-hidden": "true",
                        style: {
                            position: "absolute",
                            inset: 0,
                            zIndex: 1,
                            opacity: 0.72,
                            pointerEvents: "none"
                        },
                        children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(ReasoningWeb, {
                            persona: activePersona,
                            state: webState,
                            trace: trace,
                            mode: "full",
                            coreless: true,
                            onSelect: (n)=>{
                                openAgent(n);
                            }
                        }, activePersona, false, {
                            fileName: "[project]/components/ApexWorld.tsx",
                            lineNumber: 754,
                            columnNumber: 13
                        }, this)
                    }, void 0, false, {
                        fileName: "[project]/components/ApexWorld.tsx",
                        lineNumber: 744,
                        columnNumber: 11
                    }, this),
                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                        role: "button",
                        tabIndex: 0,
                        "aria-label": "JARVIS core - tap to interrupt or wake",
                        onClick: handleCoreTap,
                        onKeyDown: (e)=>{
                            if (e.key === "Enter" || e.key === " ") {
                                e.preventDefault();
                                handleCoreTap();
                            }
                        },
                        onMouseDown: (e)=>e.preventDefault(),
                        style: {
                            position: "absolute",
                            left: "50%",
                            top: "46%",
                            transform: "translate(-50%, -50%)",
                            width: "min(250px, 26vw)",
                            height: "min(310px, 40vh)",
                            borderRadius: "50%",
                            zIndex: 4,
                            cursor: "pointer",
                            background: "transparent",
                            border: "none",
                            userSelect: "none"
                        }
                    }, void 0, false, {
                        fileName: "[project]/components/ApexWorld.tsx",
                        lineNumber: 769,
                        columnNumber: 9
                    }, this),
                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$components$2f$WorkerOrbsLayer$2e$tsx__$5b$app$2d$client$5d$__$28$ecmascript$29$__["WorkerOrbsLayer"], {}, void 0, false, {
                        fileName: "[project]/components/ApexWorld.tsx",
                        lineNumber: 797,
                        columnNumber: 9
                    }, this)
                ]
            }, void 0, true, {
                fileName: "[project]/components/ApexWorld.tsx",
                lineNumber: 713,
                columnNumber: 7
            }, this),
            camShifted && /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("button", {
                type: "button",
                onClick: ()=>setCam({
                        x: 0,
                        y: 0,
                        zoom: 1,
                        tiltX: 0,
                        tiltY: 0
                    }),
                style: {
                    position: "fixed",
                    left: 16,
                    bottom: 54,
                    zIndex: 35,
                    padding: "5px 11px",
                    borderRadius: 999,
                    border: `1px solid ${theme.primary}44`,
                    background: "rgba(5, 11, 22, 0.78)",
                    color: theme.primary,
                    fontFamily: "var(--font-mono)",
                    fontSize: 9.5,
                    letterSpacing: "0.1em",
                    cursor: "pointer"
                },
                children: [
                    "CAM ",
                    Math.round(cam.zoom * 100),
                    "% · PRESS 0 TO RESET"
                ]
            }, void 0, true, {
                fileName: "[project]/components/ApexWorld.tsx",
                lineNumber: 801,
                columnNumber: 9
            }, this),
            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("nav", {
                className: "visually-hidden",
                "aria-label": "JARVIS agents",
                children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("ul", {
                    children: ROSTER.map((a)=>/*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("li", {
                            children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("button", {
                                type: "button",
                                onClick: ()=>openAgent({
                                        key: a.key,
                                        name: a.name,
                                        color: a.color === "#00e5ff" ? theme.primary : a.color === "#f5a623" ? theme.secondary : theme.toolNode
                                    }),
                                children: [
                                    a.name,
                                    " - ",
                                    INFO[a.key]?.role ?? "Specialist"
                                ]
                            }, void 0, true, {
                                fileName: "[project]/components/ApexWorld.tsx",
                                lineNumber: 828,
                                columnNumber: 15
                            }, this)
                        }, a.key, false, {
                            fileName: "[project]/components/ApexWorld.tsx",
                            lineNumber: 827,
                            columnNumber: 13
                        }, this))
                }, void 0, false, {
                    fileName: "[project]/components/ApexWorld.tsx",
                    lineNumber: 825,
                    columnNumber: 9
                }, this)
            }, void 0, false, {
                fileName: "[project]/components/ApexWorld.tsx",
                lineNumber: 824,
                columnNumber: 7
            }, this),
            selected && /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(AgentOverview, {
                sel: selected,
                onClose: ()=>setSelected(null)
            }, void 0, false, {
                fileName: "[project]/components/ApexWorld.tsx",
                lineNumber: 851,
                columnNumber: 9
            }, this)
        ]
    }, void 0, true, {
        fileName: "[project]/components/ApexWorld.tsx",
        lineNumber: 653,
        columnNumber: 5
    }, this);
}
_s1(ApexWorld, "Bx4BIbJ5lqpET4AnM++Wtd0ljp4=", false, function() {
    return [
        __TURBOPACK__imported__module__$5b$project$5d2f$components$2f$JarvisBridge$2e$tsx__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useJarvis"]
    ];
});
_c5 = ApexWorld;
var _c, _c1, _c2, _c3, _c4, _c5;
__turbopack_context__.k.register(_c, "ApexMaleHumanoid$dynamic");
__turbopack_context__.k.register(_c1, "ApexMaleHumanoid");
__turbopack_context__.k.register(_c2, "ApexFemaleHumanoid$dynamic");
__turbopack_context__.k.register(_c3, "ApexFemaleHumanoid");
__turbopack_context__.k.register(_c4, "AgentOverview");
__turbopack_context__.k.register(_c5, "ApexWorld");
if (typeof globalThis.$RefreshHelpers$ === 'object' && globalThis.$RefreshHelpers !== null) {
    __turbopack_context__.k.registerExports(__turbopack_context__.m, globalThis.$RefreshHelpers$);
}
}),
"[project]/components/AutomationsModal.tsx [app-client] (ecmascript)", ((__turbopack_context__) => {
"use strict";

__turbopack_context__.s([
    "default",
    ()=>AutomationsModal
]);
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/next/dist/compiled/react/jsx-dev-runtime.js [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/next/dist/compiled/react/index.js [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$clock$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__Clock$3e$__ = __turbopack_context__.i("[project]/node_modules/lucide-react/dist/esm/icons/clock.js [app-client] (ecmascript) <export default as Clock>");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$pause$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__Pause$3e$__ = __turbopack_context__.i("[project]/node_modules/lucide-react/dist/esm/icons/pause.js [app-client] (ecmascript) <export default as Pause>");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$play$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__Play$3e$__ = __turbopack_context__.i("[project]/node_modules/lucide-react/dist/esm/icons/play.js [app-client] (ecmascript) <export default as Play>");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$plug$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__Plug$3e$__ = __turbopack_context__.i("[project]/node_modules/lucide-react/dist/esm/icons/plug.js [app-client] (ecmascript) <export default as Plug>");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$refresh$2d$cw$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__RefreshCw$3e$__ = __turbopack_context__.i("[project]/node_modules/lucide-react/dist/esm/icons/refresh-cw.js [app-client] (ecmascript) <export default as RefreshCw>");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$server$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__Server$3e$__ = __turbopack_context__.i("[project]/node_modules/lucide-react/dist/esm/icons/server.js [app-client] (ecmascript) <export default as Server>");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$trash$2d$2$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__Trash2$3e$__ = __turbopack_context__.i("[project]/node_modules/lucide-react/dist/esm/icons/trash-2.js [app-client] (ecmascript) <export default as Trash2>");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$x$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__X$3e$__ = __turbopack_context__.i("[project]/node_modules/lucide-react/dist/esm/icons/x.js [app-client] (ecmascript) <export default as X>");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$zap$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__Zap$3e$__ = __turbopack_context__.i("[project]/node_modules/lucide-react/dist/esm/icons/zap.js [app-client] (ecmascript) <export default as Zap>");
var __TURBOPACK__imported__module__$5b$project$5d2f$components$2f$JarvisBridge$2e$tsx__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/components/JarvisBridge.tsx [app-client] (ecmascript)");
;
var _s = __turbopack_context__.k.signature();
"use client";
;
;
;
const GREEN = "#3be38a";
const RED = "#ff5d6c";
function AutomationsModal() {
    _s();
    const { automationsModalOpen, setAutomationsModalOpen, theme } = (0, __TURBOPACK__imported__module__$5b$project$5d2f$components$2f$JarvisBridge$2e$tsx__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useJarvis"])();
    const [tab, setTab] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])("automations");
    const [autos, setAutos] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])([]);
    const [rests, setRests] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])([]);
    const [mcps, setMcps] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])([]);
    const [tools, setTools] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])([]);
    const [statusMsg, setStatusMsg] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])("");
    const [testOutput, setTestOutput] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])("");
    // Automation form
    const [autoName, setAutoName] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])("");
    const [schedType, setSchedType] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])("interval");
    const [everyMins, setEveryMins] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])(60);
    const [dailyAt, setDailyAt] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])("09:00");
    const [stepTool, setStepTool] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])("cloud_integrations");
    const [stepJson, setStepJson] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])('{"action": "status"}');
    // REST connector form
    const [rName, setRName] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])("");
    const [rDesc, setRDesc] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])("");
    const [rMethod, setRMethod] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])("GET");
    const [rUrl, setRUrl] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])("");
    const [rToken, setRToken] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])("");
    const [rBody, setRBody] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])("");
    // MCP server form
    const [mName, setMName] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])("");
    const [mTransport, setMTransport] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])("http");
    const [mUrl, setMUrl] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])("");
    const [mCmd, setMCmd] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])("");
    const applyData = (j)=>{
        if (Array.isArray(j.automations)) setAutos(j.automations);
        if (Array.isArray(j.rest_connectors)) setRests(j.rest_connectors);
        if (Array.isArray(j.mcp_servers)) setMcps(j.mcp_servers);
        if (Array.isArray(j.available_tools)) setTools(j.available_tools);
    };
    const refresh = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useCallback"])({
        "AutomationsModal.useCallback[refresh]": async ()=>{
            try {
                const r = await fetch("/api/hud/automations");
                if (r.ok) applyData(await r.json());
            } catch  {}
        }
    }["AutomationsModal.useCallback[refresh]"], []);
    (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useEffect"])({
        "AutomationsModal.useEffect": ()=>{
            if (automationsModalOpen) {
                refresh();
                setStatusMsg("");
                setTestOutput("");
            }
        }
    }["AutomationsModal.useEffect"], [
        automationsModalOpen,
        refresh
    ]);
    if (!automationsModalOpen) return null;
    const PRIMARY = theme.primary;
    const SECONDARY = theme.secondary;
    const post = async (payload)=>{
        const r = await fetch("/api/hud/action", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(payload)
        });
        const j = await r.json();
        applyData(j);
        return j;
    };
    const onSaveAuto = async (e)=>{
        e.preventDefault();
        let parsedParams = {};
        try {
            parsedParams = stepJson.trim() ? JSON.parse(stepJson) : {};
        } catch  {
            setStatusMsg("Step parameters must be valid JSON.");
            return;
        }
        const j = await post({
            action: "auto_save",
            automation: {
                name: autoName,
                schedule_type: schedType,
                every_minutes: everyMins,
                daily_at: dailyAt,
                steps: [
                    {
                        tool: stepTool,
                        params: parsedParams
                    }
                ]
            }
        });
        if (j.ok) {
            setAutoName("");
            setStatusMsg(`Saved automation "${j.automation?.name}".`);
        } else if (j.error) {
            setStatusMsg(j.error);
        }
    };
    const onSaveRest = async (e)=>{
        e.preventDefault();
        const j = await post({
            action: "rest_save",
            connector: {
                name: rName,
                description: rDesc,
                method: rMethod,
                url: rUrl,
                bearer_token: rToken,
                body_template: rBody
            }
        });
        if (j.ok) {
            setRName("");
            setRDesc("");
            setRUrl("");
            setRToken("");
            setRBody("");
            setStatusMsg(`Saved REST connector "${j.connector?.name}".`);
        } else if (j.error) {
            setStatusMsg(j.error);
        }
    };
    const onSaveMcp = async (e)=>{
        e.preventDefault();
        const j = await post({
            action: "mcp_save",
            server: {
                name: mName,
                transport: mTransport,
                url: mUrl,
                command: mCmd
            }
        });
        if (j.ok) {
            setMName("");
            setMUrl("");
            setMCmd("");
            setStatusMsg(`Registered MCP server "${j.server?.name}".`);
        } else if (j.error) {
            setStatusMsg(j.error);
        }
    };
    return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
        role: "dialog",
        "aria-modal": "true",
        "aria-label": "Automations, APIs & MCP Center",
        style: {
            position: "fixed",
            inset: 0,
            zIndex: 83,
            background: "rgba(2, 5, 12, 0.78)",
            backdropFilter: "blur(18px)",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            padding: 18
        },
        children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
            style: {
                width: "min(960px, 96vw)",
                height: "min(730px, 90vh)",
                background: theme.drawerBg,
                border: `1px solid ${PRIMARY}44`,
                borderRadius: 20,
                boxShadow: "0 24px 80px rgba(0,0,0,0.82)",
                display: "flex",
                flexDirection: "column",
                overflow: "hidden"
            },
            children: [
                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                    style: {
                        display: "flex",
                        alignItems: "center",
                        gap: 10,
                        padding: "15px 22px",
                        borderBottom: `1px solid ${PRIMARY}26`
                    },
                    children: [
                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$zap$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__Zap$3e$__["Zap"], {
                            size: 17,
                            color: PRIMARY
                        }, void 0, false, {
                            fileName: "[project]/components/AutomationsModal.tsx",
                            lineNumber: 242,
                            columnNumber: 11
                        }, this),
                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                            style: {
                                flex: 1
                            },
                            children: [
                                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                    style: {
                                        fontFamily: "var(--font-mono)",
                                        fontSize: 11,
                                        letterSpacing: "0.24em",
                                        color: PRIMARY
                                    },
                                    children: "AUTOMATIONS · CUSTOM REST/WEBHOOKS & MCP BRIDGE"
                                }, void 0, false, {
                                    fileName: "[project]/components/AutomationsModal.tsx",
                                    lineNumber: 244,
                                    columnNumber: 13
                                }, this),
                                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                    style: {
                                        fontSize: 11.5,
                                        color: "rgba(240,237,232,0.58)",
                                        marginTop: 2
                                    },
                                    children: "Schedule recurring multi-app workflows, build custom REST tools & connect MCP servers."
                                }, void 0, false, {
                                    fileName: "[project]/components/AutomationsModal.tsx",
                                    lineNumber: 254,
                                    columnNumber: 13
                                }, this)
                            ]
                        }, void 0, true, {
                            fileName: "[project]/components/AutomationsModal.tsx",
                            lineNumber: 243,
                            columnNumber: 11
                        }, this),
                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("button", {
                            type: "button",
                            onClick: ()=>setAutomationsModalOpen(false),
                            style: {
                                background: "none",
                                border: "none",
                                color: "rgba(240,237,232,0.6)",
                                cursor: "pointer"
                            },
                            children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$x$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__X$3e$__["X"], {
                                size: 18
                            }, void 0, false, {
                                fileName: "[project]/components/AutomationsModal.tsx",
                                lineNumber: 268,
                                columnNumber: 13
                            }, this)
                        }, void 0, false, {
                            fileName: "[project]/components/AutomationsModal.tsx",
                            lineNumber: 258,
                            columnNumber: 11
                        }, this)
                    ]
                }, void 0, true, {
                    fileName: "[project]/components/AutomationsModal.tsx",
                    lineNumber: 233,
                    columnNumber: 9
                }, this),
                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                    style: {
                        display: "flex",
                        gap: 8,
                        padding: "10px 22px",
                        borderBottom: "1px solid rgba(255,255,255,0.07)"
                    },
                    children: [
                        [
                            {
                                id: "automations",
                                label: `AUTOMATIONS (${autos.length})`,
                                icon: __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$clock$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__Clock$3e$__["Clock"]
                            },
                            {
                                id: "rest",
                                label: `REST / WEBHOOKS (${rests.length})`,
                                icon: __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$plug$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__Plug$3e$__["Plug"]
                            },
                            {
                                id: "mcp",
                                label: `MCP SERVERS (${mcps.length})`,
                                icon: __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$server$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__Server$3e$__["Server"]
                            }
                        ].map((t)=>{
                            const Icon = t.icon;
                            const active = tab === t.id;
                            return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("button", {
                                type: "button",
                                onClick: ()=>setTab(t.id),
                                style: {
                                    display: "inline-flex",
                                    alignItems: "center",
                                    gap: 6,
                                    padding: "7px 13px",
                                    borderRadius: 999,
                                    border: `1px solid ${active ? PRIMARY : "rgba(255,255,255,0.12)"}`,
                                    background: active ? `${PRIMARY}22` : "transparent",
                                    color: active ? PRIMARY : "rgba(240,237,232,0.7)",
                                    fontFamily: "var(--font-mono)",
                                    fontSize: 10,
                                    letterSpacing: "0.12em",
                                    cursor: "pointer"
                                },
                                children: [
                                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(Icon, {
                                        size: 12
                                    }, void 0, false, {
                                        fileName: "[project]/components/AutomationsModal.tsx",
                                        lineNumber: 310,
                                        columnNumber: 17
                                    }, this),
                                    t.label
                                ]
                            }, t.id, true, {
                                fileName: "[project]/components/AutomationsModal.tsx",
                                lineNumber: 291,
                                columnNumber: 15
                            }, this);
                        }),
                        statusMsg && /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("span", {
                            style: {
                                marginLeft: "auto",
                                alignSelf: "center",
                                fontFamily: "var(--font-mono)",
                                fontSize: 10,
                                color: GREEN
                            },
                            children: statusMsg
                        }, void 0, false, {
                            fileName: "[project]/components/AutomationsModal.tsx",
                            lineNumber: 316,
                            columnNumber: 13
                        }, this)
                    ]
                }, void 0, true, {
                    fileName: "[project]/components/AutomationsModal.tsx",
                    lineNumber: 273,
                    columnNumber: 9
                }, this),
                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                    style: {
                        flex: 1,
                        overflowY: "auto",
                        padding: "18px 22px"
                    },
                    children: [
                        tab === "automations" && /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                            style: {
                                display: "grid",
                                gridTemplateColumns: "1.1fr 1fr",
                                gap: 18
                            },
                            children: [
                                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                    style: {
                                        display: "flex",
                                        flexDirection: "column",
                                        gap: 10
                                    },
                                    children: autos.length === 0 ? /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                        style: {
                                            fontSize: 12,
                                            color: "rgba(240,237,232,0.45)",
                                            padding: 20
                                        },
                                        children: "No recurring automations yet. Create one on the right to run intervals or daily briefings."
                                    }, void 0, false, {
                                        fileName: "[project]/components/AutomationsModal.tsx",
                                        lineNumber: 336,
                                        columnNumber: 19
                                    }, this) : autos.map((a)=>/*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                            style: {
                                                padding: "12px 14px",
                                                borderRadius: 12,
                                                border: `1px solid ${a.enabled ? `${PRIMARY}44` : "rgba(255,255,255,0.08)"}`,
                                                background: "rgba(255,255,255,0.025)"
                                            },
                                            children: [
                                                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                                    style: {
                                                        display: "flex",
                                                        alignItems: "center",
                                                        gap: 8
                                                    },
                                                    children: [
                                                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("span", {
                                                            style: {
                                                                fontWeight: 600,
                                                                fontSize: 12.5
                                                            },
                                                            children: a.name
                                                        }, void 0, false, {
                                                            fileName: "[project]/components/AutomationsModal.tsx",
                                                            lineNumber: 351,
                                                            columnNumber: 25
                                                        }, this),
                                                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("span", {
                                                            style: {
                                                                fontFamily: "var(--font-mono)",
                                                                fontSize: 9,
                                                                color: a.enabled ? GREEN : "rgba(240,237,232,0.48)"
                                                            },
                                                            children: a.schedule_type === "interval" ? `EVERY ${a.every_minutes}M` : a.schedule_type === "daily" ? `DAILY ${a.daily_at}` : "MANUAL"
                                                        }, void 0, false, {
                                                            fileName: "[project]/components/AutomationsModal.tsx",
                                                            lineNumber: 352,
                                                            columnNumber: 25
                                                        }, this),
                                                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("span", {
                                                            style: {
                                                                flex: 1
                                                            }
                                                        }, void 0, false, {
                                                            fileName: "[project]/components/AutomationsModal.tsx",
                                                            lineNumber: 365,
                                                            columnNumber: 25
                                                        }, this),
                                                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("button", {
                                                            type: "button",
                                                            onClick: async ()=>{
                                                                const j = await post({
                                                                    action: "auto_run_now",
                                                                    id: a.id
                                                                });
                                                                if (j.run?.output) setTestOutput(j.run.output);
                                                            },
                                                            title: "Run automation immediately",
                                                            style: {
                                                                padding: "4px 9px",
                                                                borderRadius: 999,
                                                                border: `1px solid ${PRIMARY}66`,
                                                                background: `${PRIMARY}1f`,
                                                                color: PRIMARY,
                                                                fontFamily: "var(--font-mono)",
                                                                fontSize: 9,
                                                                cursor: "pointer"
                                                            },
                                                            children: "RUN NOW"
                                                        }, void 0, false, {
                                                            fileName: "[project]/components/AutomationsModal.tsx",
                                                            lineNumber: 366,
                                                            columnNumber: 25
                                                        }, this),
                                                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("button", {
                                                            type: "button",
                                                            onClick: ()=>post({
                                                                    action: "auto_toggle",
                                                                    id: a.id
                                                                }),
                                                            style: {
                                                                background: "none",
                                                                border: "none",
                                                                color: SECONDARY,
                                                                cursor: "pointer"
                                                            },
                                                            children: a.enabled ? /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$pause$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__Pause$3e$__["Pause"], {
                                                                size: 13
                                                            }, void 0, false, {
                                                                fileName: "[project]/components/AutomationsModal.tsx",
                                                                lineNumber: 396,
                                                                columnNumber: 40
                                                            }, this) : /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$play$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__Play$3e$__["Play"], {
                                                                size: 13
                                                            }, void 0, false, {
                                                                fileName: "[project]/components/AutomationsModal.tsx",
                                                                lineNumber: 396,
                                                                columnNumber: 62
                                                            }, this)
                                                        }, void 0, false, {
                                                            fileName: "[project]/components/AutomationsModal.tsx",
                                                            lineNumber: 386,
                                                            columnNumber: 25
                                                        }, this),
                                                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("button", {
                                                            type: "button",
                                                            onClick: ()=>post({
                                                                    action: "auto_delete",
                                                                    id: a.id
                                                                }),
                                                            style: {
                                                                background: "none",
                                                                border: "none",
                                                                color: RED,
                                                                cursor: "pointer"
                                                            },
                                                            children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$trash$2d$2$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__Trash2$3e$__["Trash2"], {
                                                                size: 13
                                                            }, void 0, false, {
                                                                fileName: "[project]/components/AutomationsModal.tsx",
                                                                lineNumber: 408,
                                                                columnNumber: 27
                                                            }, this)
                                                        }, void 0, false, {
                                                            fileName: "[project]/components/AutomationsModal.tsx",
                                                            lineNumber: 398,
                                                            columnNumber: 25
                                                        }, this)
                                                    ]
                                                }, void 0, true, {
                                                    fileName: "[project]/components/AutomationsModal.tsx",
                                                    lineNumber: 350,
                                                    columnNumber: 23
                                                }, this),
                                                a.runs && a.runs.length > 0 && /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                                    style: {
                                                        fontFamily: "var(--font-mono)",
                                                        fontSize: 9.5,
                                                        color: "rgba(240,237,232,0.58)",
                                                        marginTop: 6
                                                    },
                                                    children: [
                                                        "Last run: ",
                                                        a.runs[a.runs.length - 1].ts,
                                                        " ·",
                                                        " ",
                                                        a.runs[a.runs.length - 1].status,
                                                        " (",
                                                        a.runs[a.runs.length - 1].duration_ms,
                                                        "ms)"
                                                    ]
                                                }, void 0, true, {
                                                    fileName: "[project]/components/AutomationsModal.tsx",
                                                    lineNumber: 412,
                                                    columnNumber: 25
                                                }, this)
                                            ]
                                        }, a.id, true, {
                                            fileName: "[project]/components/AutomationsModal.tsx",
                                            lineNumber: 341,
                                            columnNumber: 21
                                        }, this))
                                }, void 0, false, {
                                    fileName: "[project]/components/AutomationsModal.tsx",
                                    lineNumber: 334,
                                    columnNumber: 15
                                }, this),
                                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("form", {
                                    onSubmit: onSaveAuto,
                                    style: {
                                        padding: 15,
                                        borderRadius: 14,
                                        background: "rgba(255,255,255,0.025)",
                                        border: "1px solid rgba(255,255,255,0.09)",
                                        display: "flex",
                                        flexDirection: "column",
                                        gap: 9
                                    },
                                    children: [
                                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                            style: {
                                                fontFamily: "var(--font-mono)",
                                                fontSize: 10,
                                                letterSpacing: "0.16em",
                                                color: PRIMARY
                                            },
                                            children: "+ NEW RECURRING AUTOMATION"
                                        }, void 0, false, {
                                            fileName: "[project]/components/AutomationsModal.tsx",
                                            lineNumber: 441,
                                            columnNumber: 17
                                        }, this),
                                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("input", {
                                            value: autoName,
                                            onChange: (e)=>setAutoName(e.target.value),
                                            placeholder: "Workflow Name (e.g. Morning Inbox & Calendar Sync)",
                                            style: {
                                                padding: "8px 11px",
                                                borderRadius: 8,
                                                border: "1px solid rgba(255,255,255,0.14)",
                                                background: "rgba(0,0,0,0.35)",
                                                color: "#f0ede8",
                                                fontSize: 12
                                            }
                                        }, void 0, false, {
                                            fileName: "[project]/components/AutomationsModal.tsx",
                                            lineNumber: 451,
                                            columnNumber: 17
                                        }, this),
                                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                            style: {
                                                display: "flex",
                                                gap: 8
                                            },
                                            children: [
                                                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("select", {
                                                    value: schedType,
                                                    onChange: (e)=>setSchedType(e.target.value),
                                                    style: {
                                                        flex: 1,
                                                        padding: "8px",
                                                        borderRadius: 8,
                                                        border: "1px solid rgba(255,255,255,0.14)",
                                                        background: "rgba(0,0,0,0.45)",
                                                        color: "#f0ede8",
                                                        fontSize: 12
                                                    },
                                                    children: [
                                                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("option", {
                                                            value: "interval",
                                                            children: "Every N Minutes"
                                                        }, void 0, false, {
                                                            fileName: "[project]/components/AutomationsModal.tsx",
                                                            lineNumber: 480,
                                                            columnNumber: 21
                                                        }, this),
                                                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("option", {
                                                            value: "daily",
                                                            children: "Daily at HH:MM"
                                                        }, void 0, false, {
                                                            fileName: "[project]/components/AutomationsModal.tsx",
                                                            lineNumber: 481,
                                                            columnNumber: 21
                                                        }, this),
                                                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("option", {
                                                            value: "manual",
                                                            children: "Manual Trigger Only"
                                                        }, void 0, false, {
                                                            fileName: "[project]/components/AutomationsModal.tsx",
                                                            lineNumber: 482,
                                                            columnNumber: 21
                                                        }, this)
                                                    ]
                                                }, void 0, true, {
                                                    fileName: "[project]/components/AutomationsModal.tsx",
                                                    lineNumber: 465,
                                                    columnNumber: 19
                                                }, this),
                                                schedType === "interval" && /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("input", {
                                                    type: "number",
                                                    min: 1,
                                                    value: everyMins,
                                                    onChange: (e)=>setEveryMins(Number(e.target.value) || 60),
                                                    style: {
                                                        width: 100,
                                                        padding: "8px",
                                                        borderRadius: 8,
                                                        border: "1px solid rgba(255,255,255,0.14)",
                                                        background: "rgba(0,0,0,0.35)",
                                                        color: "#f0ede8",
                                                        fontSize: 12
                                                    }
                                                }, void 0, false, {
                                                    fileName: "[project]/components/AutomationsModal.tsx",
                                                    lineNumber: 485,
                                                    columnNumber: 21
                                                }, this),
                                                schedType === "daily" && /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("input", {
                                                    type: "time",
                                                    value: dailyAt,
                                                    onChange: (e)=>setDailyAt(e.target.value),
                                                    style: {
                                                        width: 120,
                                                        padding: "8px",
                                                        borderRadius: 8,
                                                        border: "1px solid rgba(255,255,255,0.14)",
                                                        background: "rgba(0,0,0,0.35)",
                                                        color: "#f0ede8",
                                                        fontSize: 12
                                                    }
                                                }, void 0, false, {
                                                    fileName: "[project]/components/AutomationsModal.tsx",
                                                    lineNumber: 502,
                                                    columnNumber: 21
                                                }, this)
                                            ]
                                        }, void 0, true, {
                                            fileName: "[project]/components/AutomationsModal.tsx",
                                            lineNumber: 464,
                                            columnNumber: 17
                                        }, this),
                                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("select", {
                                            value: stepTool,
                                            onChange: (e)=>setStepTool(e.target.value),
                                            style: {
                                                padding: "8px",
                                                borderRadius: 8,
                                                border: "1px solid rgba(255,255,255,0.14)",
                                                background: "rgba(0,0,0,0.45)",
                                                color: "#f0ede8",
                                                fontSize: 12
                                            },
                                            children: tools.map((t)=>/*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("option", {
                                                    value: t,
                                                    children: [
                                                        "Action: ",
                                                        t
                                                    ]
                                                }, t, true, {
                                                    fileName: "[project]/components/AutomationsModal.tsx",
                                                    lineNumber: 531,
                                                    columnNumber: 21
                                                }, this))
                                        }, void 0, false, {
                                            fileName: "[project]/components/AutomationsModal.tsx",
                                            lineNumber: 518,
                                            columnNumber: 17
                                        }, this),
                                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("textarea", {
                                            value: stepJson,
                                            onChange: (e)=>setStepJson(e.target.value),
                                            rows: 4,
                                            placeholder: '{"action": "email_unread"}',
                                            style: {
                                                padding: "8px 11px",
                                                borderRadius: 8,
                                                border: "1px solid rgba(255,255,255,0.14)",
                                                background: "rgba(0,0,0,0.35)",
                                                color: "#f0ede8",
                                                fontFamily: "var(--font-mono)",
                                                fontSize: 11.5
                                            }
                                        }, void 0, false, {
                                            fileName: "[project]/components/AutomationsModal.tsx",
                                            lineNumber: 536,
                                            columnNumber: 17
                                        }, this),
                                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("button", {
                                            type: "submit",
                                            style: {
                                                padding: "9px 14px",
                                                borderRadius: 9,
                                                border: `1px solid ${PRIMARY}66`,
                                                background: `${PRIMARY}22`,
                                                color: PRIMARY,
                                                fontFamily: "var(--font-mono)",
                                                fontSize: 10,
                                                cursor: "pointer"
                                            },
                                            children: "SAVE AUTOMATION"
                                        }, void 0, false, {
                                            fileName: "[project]/components/AutomationsModal.tsx",
                                            lineNumber: 551,
                                            columnNumber: 17
                                        }, this)
                                    ]
                                }, void 0, true, {
                                    fileName: "[project]/components/AutomationsModal.tsx",
                                    lineNumber: 429,
                                    columnNumber: 15
                                }, this)
                            ]
                        }, void 0, true, {
                            fileName: "[project]/components/AutomationsModal.tsx",
                            lineNumber: 333,
                            columnNumber: 13
                        }, this),
                        tab === "rest" && /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                            style: {
                                display: "grid",
                                gridTemplateColumns: "1fr 1fr",
                                gap: 18
                            },
                            children: [
                                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                    style: {
                                        display: "flex",
                                        flexDirection: "column",
                                        gap: 8
                                    },
                                    children: rests.map((c)=>/*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                            style: {
                                                padding: "11px 14px",
                                                borderRadius: 11,
                                                background: "rgba(255,255,255,0.025)",
                                                border: "1px solid rgba(255,255,255,0.09)"
                                            },
                                            children: [
                                                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                                    style: {
                                                        display: "flex",
                                                        alignItems: "center",
                                                        gap: 8
                                                    },
                                                    children: [
                                                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("span", {
                                                            style: {
                                                                fontFamily: "var(--font-mono)",
                                                                fontSize: 9,
                                                                color: SECONDARY
                                                            },
                                                            children: c.method
                                                        }, void 0, false, {
                                                            fileName: "[project]/components/AutomationsModal.tsx",
                                                            lineNumber: 584,
                                                            columnNumber: 23
                                                        }, this),
                                                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("span", {
                                                            style: {
                                                                fontWeight: 600,
                                                                fontSize: 12.5,
                                                                flex: 1
                                                            },
                                                            children: c.name
                                                        }, void 0, false, {
                                                            fileName: "[project]/components/AutomationsModal.tsx",
                                                            lineNumber: 593,
                                                            columnNumber: 23
                                                        }, this),
                                                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("button", {
                                                            type: "button",
                                                            onClick: async ()=>{
                                                                const j = await post({
                                                                    action: "rest_test",
                                                                    id: c.id
                                                                });
                                                                setTestOutput(j.output || j.error || "");
                                                            },
                                                            style: {
                                                                padding: "3px 9px",
                                                                borderRadius: 999,
                                                                border: `1px solid ${PRIMARY}55`,
                                                                background: "transparent",
                                                                color: PRIMARY,
                                                                fontFamily: "var(--font-mono)",
                                                                fontSize: 9,
                                                                cursor: "pointer"
                                                            },
                                                            children: "TEST"
                                                        }, void 0, false, {
                                                            fileName: "[project]/components/AutomationsModal.tsx",
                                                            lineNumber: 594,
                                                            columnNumber: 23
                                                        }, this),
                                                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("button", {
                                                            type: "button",
                                                            onClick: ()=>post({
                                                                    action: "rest_delete",
                                                                    id: c.id
                                                                }),
                                                            style: {
                                                                background: "none",
                                                                border: "none",
                                                                color: RED,
                                                                cursor: "pointer"
                                                            },
                                                            children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$trash$2d$2$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__Trash2$3e$__["Trash2"], {
                                                                size: 13
                                                            }, void 0, false, {
                                                                fileName: "[project]/components/AutomationsModal.tsx",
                                                                lineNumber: 623,
                                                                columnNumber: 25
                                                            }, this)
                                                        }, void 0, false, {
                                                            fileName: "[project]/components/AutomationsModal.tsx",
                                                            lineNumber: 613,
                                                            columnNumber: 23
                                                        }, this)
                                                    ]
                                                }, void 0, true, {
                                                    fileName: "[project]/components/AutomationsModal.tsx",
                                                    lineNumber: 583,
                                                    columnNumber: 21
                                                }, this),
                                                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                                    style: {
                                                        fontSize: 11,
                                                        color: "rgba(240,237,232,0.58)",
                                                        marginTop: 4
                                                    },
                                                    children: c.url
                                                }, void 0, false, {
                                                    fileName: "[project]/components/AutomationsModal.tsx",
                                                    lineNumber: 626,
                                                    columnNumber: 21
                                                }, this)
                                            ]
                                        }, c.id, true, {
                                            fileName: "[project]/components/AutomationsModal.tsx",
                                            lineNumber: 574,
                                            columnNumber: 19
                                        }, this))
                                }, void 0, false, {
                                    fileName: "[project]/components/AutomationsModal.tsx",
                                    lineNumber: 572,
                                    columnNumber: 15
                                }, this),
                                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("form", {
                                    onSubmit: onSaveRest,
                                    style: {
                                        padding: 15,
                                        borderRadius: 14,
                                        background: "rgba(255,255,255,0.025)",
                                        border: "1px solid rgba(255,255,255,0.09)",
                                        display: "flex",
                                        flexDirection: "column",
                                        gap: 8
                                    },
                                    children: [
                                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                            style: {
                                                fontFamily: "var(--font-mono)",
                                                fontSize: 10,
                                                letterSpacing: "0.16em",
                                                color: PRIMARY
                                            },
                                            children: "+ CUSTOM REST / WEBHOOK CONNECTOR"
                                        }, void 0, false, {
                                            fileName: "[project]/components/AutomationsModal.tsx",
                                            lineNumber: 645,
                                            columnNumber: 17
                                        }, this),
                                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("input", {
                                            value: rName,
                                            onChange: (e)=>setRName(e.target.value),
                                            placeholder: "Connector Name (e.g. deploy_webhook)",
                                            style: {
                                                padding: "8px 11px",
                                                borderRadius: 8,
                                                border: "1px solid rgba(255,255,255,0.14)",
                                                background: "rgba(0,0,0,0.35)",
                                                color: "#f0ede8",
                                                fontSize: 12
                                            }
                                        }, void 0, false, {
                                            fileName: "[project]/components/AutomationsModal.tsx",
                                            lineNumber: 655,
                                            columnNumber: 17
                                        }, this),
                                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                            style: {
                                                display: "flex",
                                                gap: 8
                                            },
                                            children: [
                                                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("select", {
                                                    value: rMethod,
                                                    onChange: (e)=>setRMethod(e.target.value),
                                                    style: {
                                                        width: 95,
                                                        padding: "8px",
                                                        borderRadius: 8,
                                                        border: "1px solid rgba(255,255,255,0.14)",
                                                        background: "rgba(0,0,0,0.45)",
                                                        color: "#f0ede8",
                                                        fontSize: 12
                                                    },
                                                    children: [
                                                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("option", {
                                                            children: "GET"
                                                        }, void 0, false, {
                                                            fileName: "[project]/components/AutomationsModal.tsx",
                                                            lineNumber: 682,
                                                            columnNumber: 21
                                                        }, this),
                                                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("option", {
                                                            children: "POST"
                                                        }, void 0, false, {
                                                            fileName: "[project]/components/AutomationsModal.tsx",
                                                            lineNumber: 683,
                                                            columnNumber: 21
                                                        }, this),
                                                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("option", {
                                                            children: "PUT"
                                                        }, void 0, false, {
                                                            fileName: "[project]/components/AutomationsModal.tsx",
                                                            lineNumber: 684,
                                                            columnNumber: 21
                                                        }, this),
                                                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("option", {
                                                            children: "DELETE"
                                                        }, void 0, false, {
                                                            fileName: "[project]/components/AutomationsModal.tsx",
                                                            lineNumber: 685,
                                                            columnNumber: 21
                                                        }, this)
                                                    ]
                                                }, void 0, true, {
                                                    fileName: "[project]/components/AutomationsModal.tsx",
                                                    lineNumber: 669,
                                                    columnNumber: 19
                                                }, this),
                                                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("input", {
                                                    value: rUrl,
                                                    onChange: (e)=>setRUrl(e.target.value),
                                                    placeholder: "https://api.example.com/v1/items?q={{query}}",
                                                    style: {
                                                        flex: 1,
                                                        padding: "8px 11px",
                                                        borderRadius: 8,
                                                        border: "1px solid rgba(255,255,255,0.14)",
                                                        background: "rgba(0,0,0,0.35)",
                                                        color: "#f0ede8",
                                                        fontSize: 12
                                                    }
                                                }, void 0, false, {
                                                    fileName: "[project]/components/AutomationsModal.tsx",
                                                    lineNumber: 687,
                                                    columnNumber: 19
                                                }, this)
                                            ]
                                        }, void 0, true, {
                                            fileName: "[project]/components/AutomationsModal.tsx",
                                            lineNumber: 668,
                                            columnNumber: 17
                                        }, this),
                                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("input", {
                                            type: "password",
                                            value: rToken,
                                            onChange: (e)=>setRToken(e.target.value),
                                            placeholder: "Optional Bearer Token",
                                            style: {
                                                padding: "8px 11px",
                                                borderRadius: 8,
                                                border: "1px solid rgba(255,255,255,0.14)",
                                                background: "rgba(0,0,0,0.35)",
                                                color: "#f0ede8",
                                                fontSize: 12
                                            }
                                        }, void 0, false, {
                                            fileName: "[project]/components/AutomationsModal.tsx",
                                            lineNumber: 702,
                                            columnNumber: 17
                                        }, this),
                                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("textarea", {
                                            value: rBody,
                                            onChange: (e)=>setRBody(e.target.value),
                                            rows: 3,
                                            placeholder: 'Optional JSON body template, e.g. {"event": "{{message}}"}',
                                            style: {
                                                padding: "8px 11px",
                                                borderRadius: 8,
                                                border: "1px solid rgba(255,255,255,0.14)",
                                                background: "rgba(0,0,0,0.35)",
                                                color: "#f0ede8",
                                                fontFamily: "var(--font-mono)",
                                                fontSize: 11.5
                                            }
                                        }, void 0, false, {
                                            fileName: "[project]/components/AutomationsModal.tsx",
                                            lineNumber: 716,
                                            columnNumber: 17
                                        }, this),
                                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("button", {
                                            type: "submit",
                                            style: {
                                                padding: "9px 14px",
                                                borderRadius: 9,
                                                border: `1px solid ${PRIMARY}66`,
                                                background: `${PRIMARY}22`,
                                                color: PRIMARY,
                                                fontFamily: "var(--font-mono)",
                                                fontSize: 10,
                                                cursor: "pointer"
                                            },
                                            children: "SAVE REST CONNECTOR"
                                        }, void 0, false, {
                                            fileName: "[project]/components/AutomationsModal.tsx",
                                            lineNumber: 731,
                                            columnNumber: 17
                                        }, this)
                                    ]
                                }, void 0, true, {
                                    fileName: "[project]/components/AutomationsModal.tsx",
                                    lineNumber: 633,
                                    columnNumber: 15
                                }, this)
                            ]
                        }, void 0, true, {
                            fileName: "[project]/components/AutomationsModal.tsx",
                            lineNumber: 571,
                            columnNumber: 13
                        }, this),
                        tab === "mcp" && /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                            style: {
                                display: "grid",
                                gridTemplateColumns: "1fr 1fr",
                                gap: 18
                            },
                            children: [
                                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                    style: {
                                        display: "flex",
                                        flexDirection: "column",
                                        gap: 8
                                    },
                                    children: mcps.map((s)=>/*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                            style: {
                                                padding: "11px 14px",
                                                borderRadius: 11,
                                                background: "rgba(255,255,255,0.025)",
                                                border: "1px solid rgba(255,255,255,0.09)"
                                            },
                                            children: [
                                                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                                    style: {
                                                        display: "flex",
                                                        alignItems: "center",
                                                        gap: 8
                                                    },
                                                    children: [
                                                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("span", {
                                                            style: {
                                                                fontFamily: "var(--font-mono)",
                                                                fontSize: 9,
                                                                color: SECONDARY
                                                            },
                                                            children: [
                                                                "MCP/",
                                                                s.transport.toUpperCase()
                                                            ]
                                                        }, void 0, true, {
                                                            fileName: "[project]/components/AutomationsModal.tsx",
                                                            lineNumber: 764,
                                                            columnNumber: 23
                                                        }, this),
                                                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("span", {
                                                            style: {
                                                                fontWeight: 600,
                                                                fontSize: 12.5,
                                                                flex: 1
                                                            },
                                                            children: s.name
                                                        }, void 0, false, {
                                                            fileName: "[project]/components/AutomationsModal.tsx",
                                                            lineNumber: 773,
                                                            columnNumber: 23
                                                        }, this),
                                                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("button", {
                                                            type: "button",
                                                            onClick: ()=>post({
                                                                    action: "mcp_discover",
                                                                    id: s.id
                                                                }),
                                                            style: {
                                                                display: "inline-flex",
                                                                alignItems: "center",
                                                                gap: 4,
                                                                padding: "3px 9px",
                                                                borderRadius: 999,
                                                                border: `1px solid ${PRIMARY}55`,
                                                                background: "transparent",
                                                                color: PRIMARY,
                                                                fontFamily: "var(--font-mono)",
                                                                fontSize: 9,
                                                                cursor: "pointer"
                                                            },
                                                            children: [
                                                                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$refresh$2d$cw$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__RefreshCw$3e$__["RefreshCw"], {
                                                                    size: 10
                                                                }, void 0, false, {
                                                                    fileName: "[project]/components/AutomationsModal.tsx",
                                                                    lineNumber: 791,
                                                                    columnNumber: 25
                                                                }, this),
                                                                " DISCOVER"
                                                            ]
                                                        }, void 0, true, {
                                                            fileName: "[project]/components/AutomationsModal.tsx",
                                                            lineNumber: 774,
                                                            columnNumber: 23
                                                        }, this),
                                                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("button", {
                                                            type: "button",
                                                            onClick: ()=>post({
                                                                    action: "mcp_delete",
                                                                    id: s.id
                                                                }),
                                                            style: {
                                                                background: "none",
                                                                border: "none",
                                                                color: RED,
                                                                cursor: "pointer"
                                                            },
                                                            children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$trash$2d$2$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__Trash2$3e$__["Trash2"], {
                                                                size: 13
                                                            }, void 0, false, {
                                                                fileName: "[project]/components/AutomationsModal.tsx",
                                                                lineNumber: 803,
                                                                columnNumber: 25
                                                            }, this)
                                                        }, void 0, false, {
                                                            fileName: "[project]/components/AutomationsModal.tsx",
                                                            lineNumber: 793,
                                                            columnNumber: 23
                                                        }, this)
                                                    ]
                                                }, void 0, true, {
                                                    fileName: "[project]/components/AutomationsModal.tsx",
                                                    lineNumber: 763,
                                                    columnNumber: 21
                                                }, this),
                                                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                                    style: {
                                                        fontSize: 11,
                                                        color: "rgba(240,237,232,0.58)",
                                                        marginTop: 4
                                                    },
                                                    children: s.transport === "http" ? s.url : s.command
                                                }, void 0, false, {
                                                    fileName: "[project]/components/AutomationsModal.tsx",
                                                    lineNumber: 806,
                                                    columnNumber: 21
                                                }, this),
                                                s.tools && s.tools.length > 0 && /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                                    style: {
                                                        fontFamily: "var(--font-mono)",
                                                        fontSize: 9.5,
                                                        color: GREEN,
                                                        marginTop: 5
                                                    },
                                                    children: [
                                                        "Tools (",
                                                        s.tools.length,
                                                        "): ",
                                                        s.tools.map((t)=>t.name).join(", ")
                                                    ]
                                                }, void 0, true, {
                                                    fileName: "[project]/components/AutomationsModal.tsx",
                                                    lineNumber: 810,
                                                    columnNumber: 23
                                                }, this)
                                            ]
                                        }, s.id, true, {
                                            fileName: "[project]/components/AutomationsModal.tsx",
                                            lineNumber: 754,
                                            columnNumber: 19
                                        }, this))
                                }, void 0, false, {
                                    fileName: "[project]/components/AutomationsModal.tsx",
                                    lineNumber: 752,
                                    columnNumber: 15
                                }, this),
                                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("form", {
                                    onSubmit: onSaveMcp,
                                    style: {
                                        padding: 15,
                                        borderRadius: 14,
                                        background: "rgba(255,255,255,0.025)",
                                        border: "1px solid rgba(255,255,255,0.09)",
                                        display: "flex",
                                        flexDirection: "column",
                                        gap: 8
                                    },
                                    children: [
                                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                            style: {
                                                fontFamily: "var(--font-mono)",
                                                fontSize: 10,
                                                letterSpacing: "0.16em",
                                                color: PRIMARY
                                            },
                                            children: "+ REGISTER MCP SERVER (JSON-RPC 2.0)"
                                        }, void 0, false, {
                                            fileName: "[project]/components/AutomationsModal.tsx",
                                            lineNumber: 837,
                                            columnNumber: 17
                                        }, this),
                                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("input", {
                                            value: mName,
                                            onChange: (e)=>setMName(e.target.value),
                                            placeholder: "Server Name (e.g. filesystem-mcp, composio-mcp)",
                                            style: {
                                                padding: "8px 11px",
                                                borderRadius: 8,
                                                border: "1px solid rgba(255,255,255,0.14)",
                                                background: "rgba(0,0,0,0.35)",
                                                color: "#f0ede8",
                                                fontSize: 12
                                            }
                                        }, void 0, false, {
                                            fileName: "[project]/components/AutomationsModal.tsx",
                                            lineNumber: 847,
                                            columnNumber: 17
                                        }, this),
                                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("select", {
                                            value: mTransport,
                                            onChange: (e)=>setMTransport(e.target.value === "stdio" ? "stdio" : "http"),
                                            style: {
                                                padding: "8px",
                                                borderRadius: 8,
                                                border: "1px solid rgba(255,255,255,0.14)",
                                                background: "rgba(0,0,0,0.45)",
                                                color: "#f0ede8",
                                                fontSize: 12
                                            },
                                            children: [
                                                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("option", {
                                                    value: "http",
                                                    children: "HTTP JSON-RPC Endpoint"
                                                }, void 0, false, {
                                                    fileName: "[project]/components/AutomationsModal.tsx",
                                                    lineNumber: 872,
                                                    columnNumber: 19
                                                }, this),
                                                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("option", {
                                                    value: "stdio",
                                                    children: "Local Stdio Command"
                                                }, void 0, false, {
                                                    fileName: "[project]/components/AutomationsModal.tsx",
                                                    lineNumber: 873,
                                                    columnNumber: 19
                                                }, this)
                                            ]
                                        }, void 0, true, {
                                            fileName: "[project]/components/AutomationsModal.tsx",
                                            lineNumber: 860,
                                            columnNumber: 17
                                        }, this),
                                        mTransport === "http" ? /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("input", {
                                            value: mUrl,
                                            onChange: (e)=>setMUrl(e.target.value),
                                            placeholder: "https://mcp.example.com/rpc",
                                            style: {
                                                padding: "8px 11px",
                                                borderRadius: 8,
                                                border: "1px solid rgba(255,255,255,0.14)",
                                                background: "rgba(0,0,0,0.35)",
                                                color: "#f0ede8",
                                                fontSize: 12
                                            }
                                        }, void 0, false, {
                                            fileName: "[project]/components/AutomationsModal.tsx",
                                            lineNumber: 876,
                                            columnNumber: 19
                                        }, this) : /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("input", {
                                            value: mCmd,
                                            onChange: (e)=>setMCmd(e.target.value),
                                            placeholder: "npx -y @modelcontextprotocol/server-filesystem /tmp",
                                            style: {
                                                padding: "8px 11px",
                                                borderRadius: 8,
                                                border: "1px solid rgba(255,255,255,0.14)",
                                                background: "rgba(0,0,0,0.35)",
                                                color: "#f0ede8",
                                                fontFamily: "var(--font-mono)",
                                                fontSize: 11.5
                                            }
                                        }, void 0, false, {
                                            fileName: "[project]/components/AutomationsModal.tsx",
                                            lineNumber: 890,
                                            columnNumber: 19
                                        }, this),
                                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("button", {
                                            type: "submit",
                                            style: {
                                                padding: "9px 14px",
                                                borderRadius: 9,
                                                border: `1px solid ${PRIMARY}66`,
                                                background: `${PRIMARY}22`,
                                                color: PRIMARY,
                                                fontFamily: "var(--font-mono)",
                                                fontSize: 10,
                                                cursor: "pointer"
                                            },
                                            children: "SAVE MCP SERVER"
                                        }, void 0, false, {
                                            fileName: "[project]/components/AutomationsModal.tsx",
                                            lineNumber: 905,
                                            columnNumber: 17
                                        }, this)
                                    ]
                                }, void 0, true, {
                                    fileName: "[project]/components/AutomationsModal.tsx",
                                    lineNumber: 825,
                                    columnNumber: 15
                                }, this)
                            ]
                        }, void 0, true, {
                            fileName: "[project]/components/AutomationsModal.tsx",
                            lineNumber: 751,
                            columnNumber: 13
                        }, this),
                        testOutput && /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("pre", {
                            style: {
                                marginTop: 14,
                                padding: 12,
                                borderRadius: 10,
                                background: "rgba(0,0,0,0.45)",
                                border: `1px solid ${PRIMARY}33`,
                                fontFamily: "var(--font-mono)",
                                fontSize: 11,
                                whiteSpace: "pre-wrap",
                                color: "#f0ede8"
                            },
                            children: testOutput
                        }, void 0, false, {
                            fileName: "[project]/components/AutomationsModal.tsx",
                            lineNumber: 925,
                            columnNumber: 13
                        }, this)
                    ]
                }, void 0, true, {
                    fileName: "[project]/components/AutomationsModal.tsx",
                    lineNumber: 331,
                    columnNumber: 9
                }, this)
            ]
        }, void 0, true, {
            fileName: "[project]/components/AutomationsModal.tsx",
            lineNumber: 219,
            columnNumber: 7
        }, this)
    }, void 0, false, {
        fileName: "[project]/components/AutomationsModal.tsx",
        lineNumber: 203,
        columnNumber: 5
    }, this);
}
_s(AutomationsModal, "P1bzOPne1rzpkb8zQ/DNY7dxN5o=", false, function() {
    return [
        __TURBOPACK__imported__module__$5b$project$5d2f$components$2f$JarvisBridge$2e$tsx__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useJarvis"]
    ];
});
_c = AutomationsModal;
var _c;
__turbopack_context__.k.register(_c, "AutomationsModal");
if (typeof globalThis.$RefreshHelpers$ === 'object' && globalThis.$RefreshHelpers !== null) {
    __turbopack_context__.k.registerExports(__turbopack_context__.m, globalThis.$RefreshHelpers$);
}
}),
"[project]/components/BackgroundCornerDock.tsx [app-client] (ecmascript)", ((__turbopack_context__) => {
"use strict";

__turbopack_context__.s([
    "default",
    ()=>BackgroundCornerDock
]);
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/next/dist/compiled/react/jsx-dev-runtime.js [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/next/dist/compiled/react/index.js [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$chevron$2d$down$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__ChevronDown$3e$__ = __turbopack_context__.i("[project]/node_modules/lucide-react/dist/esm/icons/chevron-down.js [app-client] (ecmascript) <export default as ChevronDown>");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$maximize$2d$2$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__Maximize2$3e$__ = __turbopack_context__.i("[project]/node_modules/lucide-react/dist/esm/icons/maximize-2.js [app-client] (ecmascript) <export default as Maximize2>");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$mic$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__Mic$3e$__ = __turbopack_context__.i("[project]/node_modules/lucide-react/dist/esm/icons/mic.js [app-client] (ecmascript) <export default as Mic>");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$mic$2d$off$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__MicOff$3e$__ = __turbopack_context__.i("[project]/node_modules/lucide-react/dist/esm/icons/mic-off.js [app-client] (ecmascript) <export default as MicOff>");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$send$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__Send$3e$__ = __turbopack_context__.i("[project]/node_modules/lucide-react/dist/esm/icons/send.js [app-client] (ecmascript) <export default as Send>");
var __TURBOPACK__imported__module__$5b$project$5d2f$components$2f$JarvisBridge$2e$tsx__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/components/JarvisBridge.tsx [app-client] (ecmascript)");
;
var _s = __turbopack_context__.k.signature();
"use client";
;
;
;
const RED = "#ff5b79";
const GREEN = "#34d399";
function BackgroundCornerDock() {
    _s();
    const { activePersona, theme, assistantName, rawState, muted, paused, logs, sendText, toggleMute, tapOrb, exitBackgroundMode } = (0, __TURBOPACK__imported__module__$5b$project$5d2f$components$2f$JarvisBridge$2e$tsx__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useJarvis"])();
    const audioLevel = (0, __TURBOPACK__imported__module__$5b$project$5d2f$components$2f$JarvisBridge$2e$tsx__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useJarvisAudioLevel"])();
    const [expanded, setExpanded] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])(false);
    const [hovered, setHovered] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])(false);
    const [text, setText] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])("");
    const inputRef = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useRef"])(null);
    const feedEndRef = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useRef"])(null);
    const isFemale = activePersona === "female";
    const primary = theme.primary;
    const secondary = theme.secondary;
    const st = (rawState || "LISTENING").toUpperCase();
    const isSpeaking = st === "SPEAKING";
    const isThinking = st === "THINKING" || st === "PROCESSING";
    const isMuted = muted || st === "MUTED";
    const activeAccent = isMuted ? RED : isSpeaking || isThinking ? secondary : primary;
    const statusLabel = isMuted ? "● MIC MUTED" : paused ? "● PAUSED" : isSpeaking ? "● SPEAKING · VOICE ACTIVE" : isThinking ? "● THINKING…" : "● LISTENING · VOICE ACTIVE";
    const statusColor = isMuted ? RED : isSpeaking || isThinking ? secondary : GREEN;
    (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useEffect"])({
        "BackgroundCornerDock.useEffect": ()=>{
            if (expanded) {
                const t = setTimeout({
                    "BackgroundCornerDock.useEffect.t": ()=>{
                        inputRef.current?.focus();
                    }
                }["BackgroundCornerDock.useEffect.t"], 60);
                return ({
                    "BackgroundCornerDock.useEffect": ()=>clearTimeout(t)
                })["BackgroundCornerDock.useEffect"];
            }
        }
    }["BackgroundCornerDock.useEffect"], [
        expanded
    ]);
    (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useEffect"])({
        "BackgroundCornerDock.useEffect": ()=>{
            if (expanded) {
                feedEndRef.current?.scrollIntoView({
                    behavior: "smooth"
                });
            }
        }
    }["BackgroundCornerDock.useEffect"], [
        logs,
        expanded
    ]);
    (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useEffect"])({
        "BackgroundCornerDock.useEffect": ()=>{
            if (!expanded) return;
            const onKey = {
                "BackgroundCornerDock.useEffect.onKey": (ev)=>{
                    if (ev.key === "Escape") {
                        setExpanded(false);
                    }
                }
            }["BackgroundCornerDock.useEffect.onKey"];
            window.addEventListener("keydown", onKey);
            return ({
                "BackgroundCornerDock.useEffect": ()=>window.removeEventListener("keydown", onKey)
            })["BackgroundCornerDock.useEffect"];
        }
    }["BackgroundCornerDock.useEffect"], [
        expanded
    ]);
    const handleSubmit = (e)=>{
        e.preventDefault();
        const trimmed = text.trim();
        if (!trimmed) return;
        sendText(trimmed);
        setText("");
        inputRef.current?.focus();
    };
    const recentLogs = logs.slice(-10);
    const pulseScale = 1 + Math.min(0.28, audioLevel * 0.42);
    if (!expanded) {
        return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
            "data-testid": "bg-corner-dock-collapsed",
            style: {
                position: "fixed",
                right: 20,
                bottom: 20,
                zIndex: 1200,
                display: "flex",
                alignItems: "center",
                gap: 10,
                pointerEvents: "auto"
            },
            children: [
                hovered && /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                    style: {
                        padding: "6px 12px",
                        borderRadius: 999,
                        background: isFemale ? "rgba(18, 6, 22, 0.90)" : "rgba(4, 11, 20, 0.90)",
                        border: `1px solid rgba(${theme.orbGlowRgb}, 0.35)`,
                        backdropFilter: "blur(14px)",
                        color: "#eef3f8",
                        fontFamily: "var(--font-mono), monospace",
                        fontSize: 10,
                        letterSpacing: "0.10em",
                        whiteSpace: "nowrap",
                        boxShadow: "0 8px 24px rgba(0,0,0,0.45)"
                    },
                    children: [
                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("span", {
                            style: {
                                color: statusColor
                            },
                            children: "●"
                        }, void 0, false, {
                            fileName: "[project]/components/BackgroundCornerDock.tsx",
                            lineNumber: 134,
                            columnNumber: 13
                        }, this),
                        " ",
                        assistantName.toUpperCase(),
                        " · VOICE ACTIVE — CLICK TO TYPE"
                    ]
                }, void 0, true, {
                    fileName: "[project]/components/BackgroundCornerDock.tsx",
                    lineNumber: 117,
                    columnNumber: 11
                }, this),
                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("button", {
                    type: "button",
                    "aria-label": `Expand ${assistantName} quick input`,
                    title: `${assistantName} running in background (listening & speaking) — Click to expand & type`,
                    onClick: ()=>setExpanded(true),
                    onMouseEnter: ()=>setHovered(true),
                    onMouseLeave: ()=>setHovered(false),
                    style: {
                        position: "relative",
                        width: 62,
                        height: 62,
                        borderRadius: "50%",
                        border: `1.5px solid ${activeAccent}`,
                        background: isFemale ? "radial-gradient(circle at 38% 34%, rgba(36, 12, 42, 0.96), rgba(10, 4, 14, 0.97))" : "radial-gradient(circle at 38% 34%, rgba(8, 22, 38, 0.96), rgba(3, 8, 16, 0.97))",
                        boxShadow: `0 10px 30px rgba(0, 0, 0, 0.55), 0 0 ${hovered ? 26 : 18}px ${activeAccent}55`,
                        cursor: "pointer",
                        display: "flex",
                        alignItems: "center",
                        justifyContent: "center",
                        padding: 0,
                        transform: hovered ? "scale(1.06)" : "scale(1)",
                        transition: "transform 170ms cubic-bezier(0.22, 1, 0.36, 1), box-shadow 170ms ease, border-color 170ms ease"
                    },
                    children: [
                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("span", {
                            style: {
                                position: "absolute",
                                inset: 6,
                                borderRadius: "50%",
                                border: `1.4px dashed ${activeAccent}88`,
                                animation: "spin 9s linear infinite",
                                pointerEvents: "none"
                            }
                        }, void 0, false, {
                            fileName: "[project]/components/BackgroundCornerDock.tsx",
                            lineNumber: 169,
                            columnNumber: 11
                        }, this),
                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("span", {
                            style: {
                                width: 22,
                                height: 22,
                                borderRadius: "50%",
                                background: `radial-gradient(circle, #ffffff 0%, ${activeAccent} 55%, transparent 100%)`,
                                boxShadow: `0 0 16px ${activeAccent}`,
                                transform: `scale(${pulseScale.toFixed(3)})`,
                                transition: "transform 75ms linear",
                                pointerEvents: "none"
                            }
                        }, void 0, false, {
                            fileName: "[project]/components/BackgroundCornerDock.tsx",
                            lineNumber: 180,
                            columnNumber: 11
                        }, this)
                    ]
                }, void 0, true, {
                    fileName: "[project]/components/BackgroundCornerDock.tsx",
                    lineNumber: 139,
                    columnNumber: 9
                }, this),
                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("style", {
                    children: `@keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }`
                }, void 0, false, {
                    fileName: "[project]/components/BackgroundCornerDock.tsx",
                    lineNumber: 193,
                    columnNumber: 9
                }, this)
            ]
        }, void 0, true, {
            fileName: "[project]/components/BackgroundCornerDock.tsx",
            lineNumber: 103,
            columnNumber: 7
        }, this);
    }
    return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
        "data-testid": "bg-corner-dock-expanded",
        style: {
            position: "fixed",
            right: 20,
            bottom: 20,
            width: "min(392px, calc(100vw - 32px))",
            height: 352,
            zIndex: 1200,
            display: "flex",
            flexDirection: "column",
            borderRadius: 22,
            background: isFemale ? "linear-gradient(165deg, rgba(18, 7, 24, 0.95), rgba(9, 4, 13, 0.97))" : "linear-gradient(165deg, rgba(5, 13, 24, 0.95), rgba(2, 7, 14, 0.97))",
            border: `1px solid rgba(${theme.orbGlowRgb}, 0.38)`,
            boxShadow: `0 22px 54px rgba(0, 0, 0, 0.68), 0 0 32px rgba(${theme.orbGlowRgb}, 0.14)`,
            backdropFilter: "blur(22px)",
            padding: "13px 14px",
            gap: 10,
            pointerEvents: "auto",
            animation: "bgDockExpand 180ms cubic-bezier(0.22, 1, 0.36, 1)"
        },
        children: [
            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                style: {
                    display: "flex",
                    alignItems: "center",
                    gap: 9
                },
                children: [
                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("button", {
                        type: "button",
                        onClick: tapOrb,
                        title: "Tap to interrupt speech or wake",
                        style: {
                            width: 30,
                            height: 30,
                            borderRadius: "50%",
                            border: `1px solid ${activeAccent}99`,
                            background: "rgba(255,255,255,0.03)",
                            display: "flex",
                            alignItems: "center",
                            justifyContent: "center",
                            cursor: "pointer",
                            padding: 0,
                            flexShrink: 0
                        },
                        children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("span", {
                            style: {
                                width: 12,
                                height: 12,
                                borderRadius: "50%",
                                background: activeAccent,
                                boxShadow: `0 0 12px ${activeAccent}`,
                                transform: `scale(${pulseScale.toFixed(3)})`,
                                transition: "transform 75ms linear"
                            }
                        }, void 0, false, {
                            fileName: "[project]/components/BackgroundCornerDock.tsx",
                            lineNumber: 249,
                            columnNumber: 11
                        }, this)
                    }, void 0, false, {
                        fileName: "[project]/components/BackgroundCornerDock.tsx",
                        lineNumber: 231,
                        columnNumber: 9
                    }, this),
                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                        style: {
                            flex: 1,
                            minWidth: 0
                        },
                        children: [
                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                style: {
                                    fontFamily: "var(--font-display), sans-serif",
                                    fontSize: 11,
                                    fontWeight: 600,
                                    letterSpacing: "0.20em",
                                    color: "#f2efe9"
                                },
                                children: assistantName.toUpperCase()
                            }, void 0, false, {
                                fileName: "[project]/components/BackgroundCornerDock.tsx",
                                lineNumber: 263,
                                columnNumber: 11
                            }, this),
                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                style: {
                                    fontFamily: "var(--font-mono), monospace",
                                    fontSize: 9,
                                    letterSpacing: "0.08em",
                                    color: statusColor,
                                    whiteSpace: "nowrap",
                                    overflow: "hidden",
                                    textOverflow: "ellipsis"
                                },
                                children: statusLabel
                            }, void 0, false, {
                                fileName: "[project]/components/BackgroundCornerDock.tsx",
                                lineNumber: 274,
                                columnNumber: 11
                            }, this)
                        ]
                    }, void 0, true, {
                        fileName: "[project]/components/BackgroundCornerDock.tsx",
                        lineNumber: 262,
                        columnNumber: 9
                    }, this),
                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("button", {
                        type: "button",
                        onClick: toggleMute,
                        title: isMuted ? "Unmute microphone" : "Mute microphone",
                        style: miniActionBtnStyle(isMuted ? RED : primary, isMuted ? "rgba(255, 91, 121, 0.16)" : "rgba(255,255,255,0.04)"),
                        children: isMuted ? /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$mic$2d$off$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__MicOff$3e$__["MicOff"], {
                            size: 12
                        }, void 0, false, {
                            fileName: "[project]/components/BackgroundCornerDock.tsx",
                            lineNumber: 298,
                            columnNumber: 22
                        }, this) : /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$mic$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__Mic$3e$__["Mic"], {
                            size: 12
                        }, void 0, false, {
                            fileName: "[project]/components/BackgroundCornerDock.tsx",
                            lineNumber: 298,
                            columnNumber: 45
                        }, this)
                    }, void 0, false, {
                        fileName: "[project]/components/BackgroundCornerDock.tsx",
                        lineNumber: 289,
                        columnNumber: 9
                    }, this),
                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("button", {
                        type: "button",
                        onClick: ()=>{
                            setExpanded(false);
                            exitBackgroundMode();
                        },
                        title: "Restore full 3D JARVIS HUD",
                        style: miniActionBtnStyle(primary, "rgba(255,255,255,0.04)"),
                        children: [
                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$maximize$2d$2$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__Maximize2$3e$__["Maximize2"], {
                                size: 11
                            }, void 0, false, {
                                fileName: "[project]/components/BackgroundCornerDock.tsx",
                                lineNumber: 310,
                                columnNumber: 11
                            }, this),
                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("span", {
                                children: "FULL"
                            }, void 0, false, {
                                fileName: "[project]/components/BackgroundCornerDock.tsx",
                                lineNumber: 311,
                                columnNumber: 11
                            }, this)
                        ]
                    }, void 0, true, {
                        fileName: "[project]/components/BackgroundCornerDock.tsx",
                        lineNumber: 301,
                        columnNumber: 9
                    }, this),
                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("button", {
                        type: "button",
                        onClick: ()=>setExpanded(false),
                        title: "Collapse to bottom-right corner button",
                        style: miniActionBtnStyle("#cbd5e1", "rgba(255,255,255,0.04)"),
                        children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$chevron$2d$down$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__ChevronDown$3e$__["ChevronDown"], {
                            size: 13
                        }, void 0, false, {
                            fileName: "[project]/components/BackgroundCornerDock.tsx",
                            lineNumber: 320,
                            columnNumber: 11
                        }, this)
                    }, void 0, false, {
                        fileName: "[project]/components/BackgroundCornerDock.tsx",
                        lineNumber: 314,
                        columnNumber: 9
                    }, this)
                ]
            }, void 0, true, {
                fileName: "[project]/components/BackgroundCornerDock.tsx",
                lineNumber: 224,
                columnNumber: 7
            }, this),
            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                style: {
                    flex: 1,
                    minHeight: 0,
                    overflowY: "auto",
                    display: "flex",
                    flexDirection: "column",
                    gap: 6,
                    padding: "4px 2px"
                },
                children: [
                    recentLogs.length === 0 ? /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                        style: {
                            margin: "auto 0",
                            textAlign: "center",
                            fontFamily: "var(--font-mono), monospace",
                            fontSize: 10.5,
                            lineHeight: 1.55,
                            color: "rgba(226, 234, 245, 0.48)",
                            padding: "0 14px"
                        },
                        children: [
                            assistantName,
                            " is active in the background — speak anytime or type a command below."
                        ]
                    }, void 0, true, {
                        fileName: "[project]/components/BackgroundCornerDock.tsx",
                        lineNumber: 337,
                        columnNumber: 11
                    }, this) : recentLogs.map((entry)=>{
                        const accent = entry.role === "user" ? primary : entry.role === "jarvis" ? secondary : "#7f9bb3";
                        const bg = entry.role === "user" ? `rgba(${theme.orbGlowRgb}, 0.11)` : entry.role === "jarvis" ? `rgba(${theme.orbGlow2Rgb}, 0.10)` : "rgba(255,255,255,0.035)";
                        return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                            style: {
                                padding: "6px 9px",
                                borderRadius: 10,
                                borderLeft: `2px solid ${accent}`,
                                background: bg,
                                color: "rgba(242, 245, 250, 0.92)",
                                fontSize: 11.5,
                                lineHeight: 1.42,
                                wordBreak: "break-word"
                            },
                            children: entry.line
                        }, entry.id, false, {
                            fileName: "[project]/components/BackgroundCornerDock.tsx",
                            lineNumber: 366,
                            columnNumber: 15
                        }, this);
                    }),
                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                        ref: feedEndRef
                    }, void 0, false, {
                        fileName: "[project]/components/BackgroundCornerDock.tsx",
                        lineNumber: 384,
                        columnNumber: 9
                    }, this)
                ]
            }, void 0, true, {
                fileName: "[project]/components/BackgroundCornerDock.tsx",
                lineNumber: 325,
                columnNumber: 7
            }, this),
            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("form", {
                onSubmit: handleSubmit,
                style: {
                    display: "flex",
                    alignItems: "center",
                    gap: 7
                },
                children: [
                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("input", {
                        ref: inputRef,
                        type: "text",
                        value: text,
                        onChange: (e)=>setText(e.target.value),
                        placeholder: `Type to ${assistantName}… (voice stays active)`,
                        style: {
                            flex: 1,
                            height: 36,
                            borderRadius: 999,
                            border: `1px solid rgba(${theme.orbGlowRgb}, 0.34)`,
                            background: "rgba(255, 255, 255, 0.055)",
                            padding: "0 13px",
                            color: "#f5f7fb",
                            fontSize: 12,
                            outline: "none"
                        }
                    }, void 0, false, {
                        fileName: "[project]/components/BackgroundCornerDock.tsx",
                        lineNumber: 396,
                        columnNumber: 9
                    }, this),
                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("button", {
                        type: "submit",
                        disabled: !text.trim(),
                        title: "Send message",
                        style: {
                            width: 36,
                            height: 36,
                            borderRadius: "50%",
                            border: `1px solid rgba(${theme.orbGlowRgb}, ${text.trim() ? 0.65 : 0.22})`,
                            background: text.trim() ? `rgba(${theme.orbGlowRgb}, 0.22)` : "rgba(255, 255, 255, 0.03)",
                            color: text.trim() ? primary : "rgba(220, 230, 242, 0.35)",
                            display: "flex",
                            alignItems: "center",
                            justifyContent: "center",
                            cursor: text.trim() ? "pointer" : "default",
                            padding: 0,
                            flexShrink: 0
                        },
                        children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$send$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__Send$3e$__["Send"], {
                            size: 13
                        }, void 0, false, {
                            fileName: "[project]/components/BackgroundCornerDock.tsx",
                            lineNumber: 437,
                            columnNumber: 11
                        }, this)
                    }, void 0, false, {
                        fileName: "[project]/components/BackgroundCornerDock.tsx",
                        lineNumber: 414,
                        columnNumber: 9
                    }, this)
                ]
            }, void 0, true, {
                fileName: "[project]/components/BackgroundCornerDock.tsx",
                lineNumber: 388,
                columnNumber: 7
            }, this),
            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("style", {
                children: `
        @keyframes bgDockExpand {
          from { opacity: 0; transform: translate(12px, 12px) scale(0.88); }
          to { opacity: 1; transform: translate(0, 0) scale(1); }
        }
      `
            }, void 0, false, {
                fileName: "[project]/components/BackgroundCornerDock.tsx",
                lineNumber: 441,
                columnNumber: 7
            }, this)
        ]
    }, void 0, true, {
        fileName: "[project]/components/BackgroundCornerDock.tsx",
        lineNumber: 199,
        columnNumber: 5
    }, this);
}
_s(BackgroundCornerDock, "kTYIlTUBgomPuxT07oOYQsCdYes=", false, function() {
    return [
        __TURBOPACK__imported__module__$5b$project$5d2f$components$2f$JarvisBridge$2e$tsx__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useJarvis"],
        __TURBOPACK__imported__module__$5b$project$5d2f$components$2f$JarvisBridge$2e$tsx__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useJarvisAudioLevel"]
    ];
});
_c = BackgroundCornerDock;
function miniActionBtnStyle(color, bg) {
    return {
        height: 26,
        padding: "0 8px",
        borderRadius: 999,
        border: `1px solid ${color}44`,
        background: bg,
        color,
        fontFamily: "var(--font-mono), monospace",
        fontSize: 9,
        letterSpacing: "0.08em",
        display: "inline-flex",
        alignItems: "center",
        gap: 4,
        cursor: "pointer",
        flexShrink: 0
    };
}
var _c;
__turbopack_context__.k.register(_c, "BackgroundCornerDock");
if (typeof globalThis.$RefreshHelpers$ === 'object' && globalThis.$RefreshHelpers !== null) {
    __turbopack_context__.k.registerExports(__turbopack_context__.m, globalThis.$RefreshHelpers$);
}
}),
"[project]/components/DevWorkspaceModal.tsx [app-client] (ecmascript)", ((__turbopack_context__) => {
"use strict";

__turbopack_context__.s([
    "default",
    ()=>DevWorkspaceModal
]);
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/next/dist/compiled/react/jsx-dev-runtime.js [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/next/dist/compiled/react/index.js [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$code$2d$xml$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__Code2$3e$__ = __turbopack_context__.i("[project]/node_modules/lucide-react/dist/esm/icons/code-xml.js [app-client] (ecmascript) <export default as Code2>");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$file$2d$code$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__FileCode$3e$__ = __turbopack_context__.i("[project]/node_modules/lucide-react/dist/esm/icons/file-code.js [app-client] (ecmascript) <export default as FileCode>");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$folder$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__Folder$3e$__ = __turbopack_context__.i("[project]/node_modules/lucide-react/dist/esm/icons/folder.js [app-client] (ecmascript) <export default as Folder>");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$folder$2d$tree$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__FolderTree$3e$__ = __turbopack_context__.i("[project]/node_modules/lucide-react/dist/esm/icons/folder-tree.js [app-client] (ecmascript) <export default as FolderTree>");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$git$2d$compare$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__GitCompare$3e$__ = __turbopack_context__.i("[project]/node_modules/lucide-react/dist/esm/icons/git-compare.js [app-client] (ecmascript) <export default as GitCompare>");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$play$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__Play$3e$__ = __turbopack_context__.i("[project]/node_modules/lucide-react/dist/esm/icons/play.js [app-client] (ecmascript) <export default as Play>");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$refresh$2d$cw$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__RefreshCw$3e$__ = __turbopack_context__.i("[project]/node_modules/lucide-react/dist/esm/icons/refresh-cw.js [app-client] (ecmascript) <export default as RefreshCw>");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$square$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__Square$3e$__ = __turbopack_context__.i("[project]/node_modules/lucide-react/dist/esm/icons/square.js [app-client] (ecmascript) <export default as Square>");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$square$2d$terminal$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__TerminalSquare$3e$__ = __turbopack_context__.i("[project]/node_modules/lucide-react/dist/esm/icons/square-terminal.js [app-client] (ecmascript) <export default as TerminalSquare>");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$x$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__X$3e$__ = __turbopack_context__.i("[project]/node_modules/lucide-react/dist/esm/icons/x.js [app-client] (ecmascript) <export default as X>");
var __TURBOPACK__imported__module__$5b$project$5d2f$components$2f$JarvisBridge$2e$tsx__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/components/JarvisBridge.tsx [app-client] (ecmascript)");
;
var _s = __turbopack_context__.k.signature();
"use client";
;
;
;
const GREEN = "#3be38a";
const RED = "#ff5d6c";
function DevWorkspaceModal() {
    _s();
    const { devModalOpen, setDevModalOpen, terminalSessions, setTerminalSessions, theme } = (0, __TURBOPACK__imported__module__$5b$project$5d2f$components$2f$JarvisBridge$2e$tsx__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useJarvis"])();
    const [tab, setTab] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])("terminal");
    const [rootDir, setRootDir] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])("");
    const [cmdInput, setCmdInput] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])("");
    const [stdinInput, setStdinInput] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])("");
    const [selectedSessionId, setSelectedSessionId] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])(null);
    const [treeEntries, setTreeEntries] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])([]);
    const [treeFilter, setTreeFilter] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])("");
    const [activeFilePath, setActiveFilePath] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])("");
    const [activeFileContent, setActiveFileContent] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])("");
    const [diffFiles, setDiffFiles] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])([]);
    const [activeDiff, setActiveDiff] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])(null);
    const refresh = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useCallback"])({
        "DevWorkspaceModal.useCallback[refresh]": async ()=>{
            try {
                const q = rootDir.trim() ? `?root_dir=${encodeURIComponent(rootDir.trim())}` : "";
                const r = await fetch(`/api/hud/dev${q}`);
                if (!r.ok) return;
                const j = await r.json();
                if (Array.isArray(j.sessions)) {
                    setTerminalSessions(j.sessions);
                }
                if (j.tree?.entries) {
                    setTreeEntries(j.tree.entries);
                    if (!rootDir && j.tree.root) setRootDir(j.tree.root);
                }
                if (j.diffs?.files) {
                    setDiffFiles(j.diffs.files);
                    setActiveDiff({
                        "DevWorkspaceModal.useCallback[refresh]": (prev)=>prev || j.diffs.files[0] || null
                    }["DevWorkspaceModal.useCallback[refresh]"]);
                }
            } catch  {}
        }
    }["DevWorkspaceModal.useCallback[refresh]"], [
        rootDir,
        setTerminalSessions
    ]);
    (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useEffect"])({
        "DevWorkspaceModal.useEffect": ()=>{
            if (devModalOpen) refresh();
        }
    }["DevWorkspaceModal.useEffect"], [
        devModalOpen,
        refresh
    ]);
    if (!devModalOpen) return null;
    const PRIMARY = theme.primary;
    const SECONDARY = theme.secondary;
    const activeSession = terminalSessions.find((s)=>s.id === selectedSessionId) || terminalSessions[0] || null;
    const onRunCmd = async (e)=>{
        e.preventDefault();
        if (!cmdInput.trim()) return;
        const cmd = cmdInput.trim();
        setCmdInput("");
        const r = await fetch("/api/hud/action", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                action: "dev_run",
                command: cmd,
                cwd: rootDir
            })
        });
        const j = await r.json();
        if (j.session) {
            setSelectedSessionId(j.session.id);
            if (Array.isArray(j.sessions)) setTerminalSessions(j.sessions);
        }
    };
    const onStopSession = async (sid)=>{
        await fetch("/api/hud/action", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                action: "dev_stop",
                session_id: sid
            })
        });
    };
    const onSendStdin = async (e)=>{
        e.preventDefault();
        if (!activeSession || !stdinInput) return;
        const txt = stdinInput;
        setStdinInput("");
        await fetch("/api/hud/action", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                action: "dev_stdin",
                session_id: activeSession.id,
                text: txt
            })
        });
    };
    const openFile = async (relPath)=>{
        setActiveFilePath(relPath);
        const r = await fetch("/api/hud/action", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                action: "dev_read_file",
                root_dir: rootDir,
                path: relPath
            })
        });
        const j = await r.json();
        if (j.file) setActiveFileContent(j.file.content || "");
    };
    const filteredTree = treeFilter.trim() ? treeEntries.filter((e)=>e.path.toLowerCase().includes(treeFilter.toLowerCase())) : treeEntries;
    return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
        role: "dialog",
        "aria-modal": "true",
        "aria-label": "Live Dev Terminal, Codebase Map & Diffs",
        style: {
            position: "fixed",
            inset: 0,
            zIndex: 84,
            background: "rgba(2, 5, 12, 0.8)",
            backdropFilter: "blur(18px)",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            padding: 18
        },
        children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
            style: {
                width: "min(1040px, 96vw)",
                height: "min(760px, 91vh)",
                background: theme.drawerBg,
                border: `1px solid ${PRIMARY}44`,
                borderRadius: 20,
                boxShadow: "0 24px 80px rgba(0,0,0,0.85)",
                display: "flex",
                flexDirection: "column",
                overflow: "hidden"
            },
            children: [
                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                    style: {
                        display: "flex",
                        alignItems: "center",
                        gap: 10,
                        padding: "14px 20px",
                        borderBottom: `1px solid ${PRIMARY}26`
                    },
                    children: [
                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$code$2d$xml$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__Code2$3e$__["Code2"], {
                            size: 17,
                            color: PRIMARY
                        }, void 0, false, {
                            fileName: "[project]/components/DevWorkspaceModal.tsx",
                            lineNumber: 198,
                            columnNumber: 11
                        }, this),
                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                            style: {
                                flex: 1
                            },
                            children: [
                                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                    style: {
                                        fontFamily: "var(--font-mono)",
                                        fontSize: 11,
                                        letterSpacing: "0.24em",
                                        color: PRIMARY
                                    },
                                    children: "DEV WORKSPACE · LIVE STREAMING TERMINAL, CODEBASE MAP & DIFFS"
                                }, void 0, false, {
                                    fileName: "[project]/components/DevWorkspaceModal.tsx",
                                    lineNumber: 200,
                                    columnNumber: 13
                                }, this),
                                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                    style: {
                                        fontFamily: "var(--font-mono)",
                                        fontSize: 10,
                                        color: "rgba(240,237,232,0.5)",
                                        marginTop: 2
                                    },
                                    children: [
                                        "Root: ",
                                        rootDir || "."
                                    ]
                                }, void 0, true, {
                                    fileName: "[project]/components/DevWorkspaceModal.tsx",
                                    lineNumber: 210,
                                    columnNumber: 13
                                }, this)
                            ]
                        }, void 0, true, {
                            fileName: "[project]/components/DevWorkspaceModal.tsx",
                            lineNumber: 199,
                            columnNumber: 11
                        }, this),
                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("button", {
                            type: "button",
                            onClick: refresh,
                            style: {
                                display: "inline-flex",
                                alignItems: "center",
                                gap: 5,
                                padding: "5px 11px",
                                borderRadius: 999,
                                border: `1px solid ${PRIMARY}44`,
                                background: "transparent",
                                color: PRIMARY,
                                fontFamily: "var(--font-mono)",
                                fontSize: 9.5,
                                cursor: "pointer"
                            },
                            children: [
                                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$refresh$2d$cw$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__RefreshCw$3e$__["RefreshCw"], {
                                    size: 11
                                }, void 0, false, {
                                    fileName: "[project]/components/DevWorkspaceModal.tsx",
                                    lineNumber: 238,
                                    columnNumber: 13
                                }, this),
                                " REFRESH"
                            ]
                        }, void 0, true, {
                            fileName: "[project]/components/DevWorkspaceModal.tsx",
                            lineNumber: 221,
                            columnNumber: 11
                        }, this),
                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("button", {
                            type: "button",
                            onClick: ()=>setDevModalOpen(false),
                            style: {
                                background: "none",
                                border: "none",
                                color: "rgba(240,237,232,0.6)",
                                cursor: "pointer"
                            },
                            children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$x$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__X$3e$__["X"], {
                                size: 18
                            }, void 0, false, {
                                fileName: "[project]/components/DevWorkspaceModal.tsx",
                                lineNumber: 250,
                                columnNumber: 13
                            }, this)
                        }, void 0, false, {
                            fileName: "[project]/components/DevWorkspaceModal.tsx",
                            lineNumber: 240,
                            columnNumber: 11
                        }, this)
                    ]
                }, void 0, true, {
                    fileName: "[project]/components/DevWorkspaceModal.tsx",
                    lineNumber: 189,
                    columnNumber: 9
                }, this),
                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                    style: {
                        display: "flex",
                        gap: 8,
                        padding: "10px 20px",
                        borderBottom: "1px solid rgba(255,255,255,0.07)"
                    },
                    children: [
                        {
                            id: "terminal",
                            label: `LIVE TERMINAL (${terminalSessions.length})`,
                            icon: __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$square$2d$terminal$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__TerminalSquare$3e$__["TerminalSquare"]
                        },
                        {
                            id: "tree",
                            label: `CODEBASE MAP (${treeEntries.length})`,
                            icon: __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$folder$2d$tree$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__FolderTree$3e$__["FolderTree"]
                        },
                        {
                            id: "diffs",
                            label: `COLORIZED DIFFS (${diffFiles.length})`,
                            icon: __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$git$2d$compare$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__GitCompare$3e$__["GitCompare"]
                        }
                    ].map((t)=>{
                        const Icon = t.icon;
                        const active = tab === t.id;
                        return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("button", {
                            type: "button",
                            onClick: ()=>setTab(t.id),
                            style: {
                                display: "inline-flex",
                                alignItems: "center",
                                gap: 6,
                                padding: "7px 13px",
                                borderRadius: 999,
                                border: `1px solid ${active ? PRIMARY : "rgba(255,255,255,0.12)"}`,
                                background: active ? `${PRIMARY}22` : "transparent",
                                color: active ? PRIMARY : "rgba(240,237,232,0.7)",
                                fontFamily: "var(--font-mono)",
                                fontSize: 10,
                                letterSpacing: "0.12em",
                                cursor: "pointer"
                            },
                            children: [
                                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(Icon, {
                                    size: 12
                                }, void 0, false, {
                                    fileName: "[project]/components/DevWorkspaceModal.tsx",
                                    lineNumber: 304,
                                    columnNumber: 17
                                }, this),
                                t.label
                            ]
                        }, t.id, true, {
                            fileName: "[project]/components/DevWorkspaceModal.tsx",
                            lineNumber: 285,
                            columnNumber: 15
                        }, this);
                    })
                }, void 0, false, {
                    fileName: "[project]/components/DevWorkspaceModal.tsx",
                    lineNumber: 255,
                    columnNumber: 9
                }, this),
                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                    style: {
                        flex: 1,
                        minHeight: 0,
                        display: "flex",
                        flexDirection: "column"
                    },
                    children: [
                        tab === "terminal" && /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                            style: {
                                flex: 1,
                                minHeight: 0,
                                display: "flex",
                                flexDirection: "column",
                                padding: "14px 20px",
                                gap: 10
                            },
                            children: [
                                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("form", {
                                    onSubmit: onRunCmd,
                                    style: {
                                        display: "flex",
                                        gap: 8
                                    },
                                    children: [
                                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("input", {
                                            value: cmdInput,
                                            onChange: (e)=>setCmdInput(e.target.value),
                                            placeholder: "Run streaming shell command (e.g. pytest -v, git status, npm run build)…",
                                            style: {
                                                flex: 1,
                                                padding: "9px 13px",
                                                borderRadius: 9,
                                                border: `1px solid ${PRIMARY}44`,
                                                background: "rgba(0,0,0,0.45)",
                                                color: "#f0ede8",
                                                fontFamily: "var(--font-mono)",
                                                fontSize: 12,
                                                outline: "none"
                                            }
                                        }, void 0, false, {
                                            fileName: "[project]/components/DevWorkspaceModal.tsx",
                                            lineNumber: 316,
                                            columnNumber: 17
                                        }, this),
                                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("button", {
                                            type: "submit",
                                            style: {
                                                display: "inline-flex",
                                                alignItems: "center",
                                                gap: 5,
                                                padding: "9px 16px",
                                                borderRadius: 9,
                                                border: `1px solid ${PRIMARY}77`,
                                                background: `${PRIMARY}22`,
                                                color: PRIMARY,
                                                fontFamily: "var(--font-mono)",
                                                fontSize: 10,
                                                cursor: "pointer"
                                            },
                                            children: [
                                                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$play$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__Play$3e$__["Play"], {
                                                    size: 12
                                                }, void 0, false, {
                                                    fileName: "[project]/components/DevWorkspaceModal.tsx",
                                                    lineNumber: 348,
                                                    columnNumber: 19
                                                }, this),
                                                " RUN"
                                            ]
                                        }, void 0, true, {
                                            fileName: "[project]/components/DevWorkspaceModal.tsx",
                                            lineNumber: 332,
                                            columnNumber: 17
                                        }, this)
                                    ]
                                }, void 0, true, {
                                    fileName: "[project]/components/DevWorkspaceModal.tsx",
                                    lineNumber: 315,
                                    columnNumber: 15
                                }, this),
                                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                    style: {
                                        flex: 1,
                                        minHeight: 0,
                                        display: "grid",
                                        gridTemplateColumns: "240px 1fr",
                                        gap: 12
                                    },
                                    children: [
                                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                            style: {
                                                overflowY: "auto",
                                                display: "flex",
                                                flexDirection: "column",
                                                gap: 6
                                            },
                                            children: terminalSessions.map((s)=>{
                                                const sel = activeSession?.id === s.id;
                                                const col = s.status === "running" ? PRIMARY : s.status === "completed" ? GREEN : RED;
                                                return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                                    onClick: ()=>setSelectedSessionId(s.id),
                                                    style: {
                                                        padding: "8px 10px",
                                                        borderRadius: 9,
                                                        border: `1px solid ${sel ? PRIMARY : "rgba(255,255,255,0.09)"}`,
                                                        background: sel ? `${PRIMARY}14` : "rgba(255,255,255,0.025)",
                                                        cursor: "pointer"
                                                    },
                                                    children: [
                                                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                                            style: {
                                                                display: "flex",
                                                                alignItems: "center",
                                                                gap: 6
                                                            },
                                                            children: [
                                                                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("span", {
                                                                    style: {
                                                                        fontFamily: "var(--font-mono)",
                                                                        fontSize: 9,
                                                                        color: col
                                                                    },
                                                                    children: s.status.toUpperCase()
                                                                }, void 0, false, {
                                                                    fileName: "[project]/components/DevWorkspaceModal.tsx",
                                                                    lineNumber: 375,
                                                                    columnNumber: 27
                                                                }, this),
                                                                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("span", {
                                                                    style: {
                                                                        flex: 1
                                                                    }
                                                                }, void 0, false, {
                                                                    fileName: "[project]/components/DevWorkspaceModal.tsx",
                                                                    lineNumber: 378,
                                                                    columnNumber: 27
                                                                }, this),
                                                                s.status === "running" && /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("button", {
                                                                    type: "button",
                                                                    onClick: (e)=>{
                                                                        e.stopPropagation();
                                                                        onStopSession(s.id);
                                                                    },
                                                                    style: {
                                                                        background: "none",
                                                                        border: "none",
                                                                        color: RED,
                                                                        cursor: "pointer"
                                                                    },
                                                                    children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$square$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__Square$3e$__["Square"], {
                                                                        size: 11
                                                                    }, void 0, false, {
                                                                        fileName: "[project]/components/DevWorkspaceModal.tsx",
                                                                        lineNumber: 393,
                                                                        columnNumber: 31
                                                                    }, this)
                                                                }, void 0, false, {
                                                                    fileName: "[project]/components/DevWorkspaceModal.tsx",
                                                                    lineNumber: 380,
                                                                    columnNumber: 29
                                                                }, this)
                                                            ]
                                                        }, void 0, true, {
                                                            fileName: "[project]/components/DevWorkspaceModal.tsx",
                                                            lineNumber: 374,
                                                            columnNumber: 25
                                                        }, this),
                                                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                                            style: {
                                                                fontFamily: "var(--font-mono)",
                                                                fontSize: 10.5,
                                                                marginTop: 3,
                                                                overflow: "hidden",
                                                                textOverflow: "ellipsis",
                                                                whiteSpace: "nowrap"
                                                            },
                                                            children: [
                                                                "$ ",
                                                                s.command
                                                            ]
                                                        }, void 0, true, {
                                                            fileName: "[project]/components/DevWorkspaceModal.tsx",
                                                            lineNumber: 397,
                                                            columnNumber: 25
                                                        }, this)
                                                    ]
                                                }, s.id, true, {
                                                    fileName: "[project]/components/DevWorkspaceModal.tsx",
                                                    lineNumber: 363,
                                                    columnNumber: 23
                                                }, this);
                                            })
                                        }, void 0, false, {
                                            fileName: "[project]/components/DevWorkspaceModal.tsx",
                                            lineNumber: 353,
                                            columnNumber: 17
                                        }, this),
                                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                            style: {
                                                display: "flex",
                                                flexDirection: "column",
                                                borderRadius: 12,
                                                border: "1px solid rgba(255,255,255,0.1)",
                                                background: "rgba(0,0,0,0.58)",
                                                overflow: "hidden"
                                            },
                                            children: [
                                                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("pre", {
                                                    style: {
                                                        flex: 1,
                                                        margin: 0,
                                                        padding: 14,
                                                        overflowY: "auto",
                                                        fontFamily: "var(--font-mono)",
                                                        fontSize: 11.5,
                                                        lineHeight: 1.55,
                                                        color: "#e6edf3",
                                                        whiteSpace: "pre-wrap"
                                                    },
                                                    children: activeSession ? activeSession.output || "Waiting for output…" : "Run a command above (or invoke shell_agent by voice) to stream live stdout/stderr here."
                                                }, void 0, false, {
                                                    fileName: "[project]/components/DevWorkspaceModal.tsx",
                                                    lineNumber: 424,
                                                    columnNumber: 19
                                                }, this),
                                                activeSession?.status === "running" && /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("form", {
                                                    onSubmit: onSendStdin,
                                                    style: {
                                                        display: "flex",
                                                        gap: 8,
                                                        padding: 8,
                                                        borderTop: "1px solid rgba(255,255,255,0.08)"
                                                    },
                                                    children: [
                                                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("input", {
                                                            value: stdinInput,
                                                            onChange: (e)=>setStdinInput(e.target.value),
                                                            placeholder: "Send stdin line to running process…",
                                                            style: {
                                                                flex: 1,
                                                                padding: "6px 10px",
                                                                borderRadius: 6,
                                                                border: "1px solid rgba(255,255,255,0.14)",
                                                                background: "rgba(0,0,0,0.45)",
                                                                color: "#f0ede8",
                                                                fontFamily: "var(--font-mono)",
                                                                fontSize: 11.5
                                                            }
                                                        }, void 0, false, {
                                                            fileName: "[project]/components/DevWorkspaceModal.tsx",
                                                            lineNumber: 451,
                                                            columnNumber: 23
                                                        }, this),
                                                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("button", {
                                                            type: "button",
                                                            onClick: ()=>onStopSession(activeSession.id),
                                                            style: {
                                                                padding: "6px 12px",
                                                                borderRadius: 6,
                                                                border: `1px solid ${RED}66`,
                                                                background: `${RED}1f`,
                                                                color: RED,
                                                                fontFamily: "var(--font-mono)",
                                                                fontSize: 9.5,
                                                                cursor: "pointer"
                                                            },
                                                            children: "STOP"
                                                        }, void 0, false, {
                                                            fileName: "[project]/components/DevWorkspaceModal.tsx",
                                                            lineNumber: 466,
                                                            columnNumber: 23
                                                        }, this)
                                                    ]
                                                }, void 0, true, {
                                                    fileName: "[project]/components/DevWorkspaceModal.tsx",
                                                    lineNumber: 442,
                                                    columnNumber: 21
                                                }, this)
                                            ]
                                        }, void 0, true, {
                                            fileName: "[project]/components/DevWorkspaceModal.tsx",
                                            lineNumber: 414,
                                            columnNumber: 17
                                        }, this)
                                    ]
                                }, void 0, true, {
                                    fileName: "[project]/components/DevWorkspaceModal.tsx",
                                    lineNumber: 352,
                                    columnNumber: 15
                                }, this)
                            ]
                        }, void 0, true, {
                            fileName: "[project]/components/DevWorkspaceModal.tsx",
                            lineNumber: 314,
                            columnNumber: 13
                        }, this),
                        tab === "tree" && /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                            style: {
                                flex: 1,
                                minHeight: 0,
                                display: "grid",
                                gridTemplateColumns: "310px 1fr"
                            },
                            children: [
                                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                    style: {
                                        borderRight: "1px solid rgba(255,255,255,0.08)",
                                        padding: 12,
                                        overflowY: "auto",
                                        display: "flex",
                                        flexDirection: "column",
                                        gap: 6
                                    },
                                    children: [
                                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("input", {
                                            value: treeFilter,
                                            onChange: (e)=>setTreeFilter(e.target.value),
                                            placeholder: "Filter files…",
                                            style: {
                                                padding: "7px 10px",
                                                borderRadius: 8,
                                                border: "1px solid rgba(255,255,255,0.14)",
                                                background: "rgba(0,0,0,0.35)",
                                                color: "#f0ede8",
                                                fontSize: 11.5
                                            }
                                        }, void 0, false, {
                                            fileName: "[project]/components/DevWorkspaceModal.tsx",
                                            lineNumber: 501,
                                            columnNumber: 17
                                        }, this),
                                        filteredTree.map((e)=>/*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("button", {
                                                type: "button",
                                                onClick: ()=>e.type === "file" && openFile(e.path),
                                                style: {
                                                    display: "flex",
                                                    alignItems: "center",
                                                    gap: 6,
                                                    padding: "4px 8px",
                                                    paddingLeft: 8 + e.depth * 12,
                                                    borderRadius: 6,
                                                    border: "none",
                                                    background: activeFilePath === e.path ? `${PRIMARY}22` : "transparent",
                                                    color: e.type === "dir" ? SECONDARY : activeFilePath === e.path ? PRIMARY : "rgba(240,237,232,0.82)",
                                                    fontFamily: "var(--font-mono)",
                                                    fontSize: 11,
                                                    textAlign: "left",
                                                    cursor: e.type === "file" ? "pointer" : "default"
                                                },
                                                children: [
                                                    e.type === "dir" ? /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$folder$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__Folder$3e$__["Folder"], {
                                                        size: 12
                                                    }, void 0, false, {
                                                        fileName: "[project]/components/DevWorkspaceModal.tsx",
                                                        lineNumber: 541,
                                                        columnNumber: 41
                                                    }, this) : /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$file$2d$code$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__FileCode$3e$__["FileCode"], {
                                                        size: 12
                                                    }, void 0, false, {
                                                        fileName: "[project]/components/DevWorkspaceModal.tsx",
                                                        lineNumber: 541,
                                                        columnNumber: 64
                                                    }, this),
                                                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("span", {
                                                        style: {
                                                            overflow: "hidden",
                                                            textOverflow: "ellipsis",
                                                            whiteSpace: "nowrap"
                                                        },
                                                        children: e.name
                                                    }, void 0, false, {
                                                        fileName: "[project]/components/DevWorkspaceModal.tsx",
                                                        lineNumber: 542,
                                                        columnNumber: 21
                                                    }, this)
                                                ]
                                            }, e.path, true, {
                                                fileName: "[project]/components/DevWorkspaceModal.tsx",
                                                lineNumber: 515,
                                                columnNumber: 19
                                            }, this))
                                    ]
                                }, void 0, true, {
                                    fileName: "[project]/components/DevWorkspaceModal.tsx",
                                    lineNumber: 491,
                                    columnNumber: 15
                                }, this),
                                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("pre", {
                                    style: {
                                        margin: 0,
                                        padding: 16,
                                        overflowY: "auto",
                                        background: "rgba(0,0,0,0.48)",
                                        fontFamily: "var(--font-mono)",
                                        fontSize: 11.5,
                                        lineHeight: 1.55,
                                        color: "#e6edf3",
                                        whiteSpace: "pre-wrap"
                                    },
                                    children: activeFilePath ? `// ${activeFilePath}\n\n${activeFileContent}` : "Select any file in the Codebase Map on the left to inspect its source."
                                }, void 0, false, {
                                    fileName: "[project]/components/DevWorkspaceModal.tsx",
                                    lineNumber: 554,
                                    columnNumber: 15
                                }, this)
                            ]
                        }, void 0, true, {
                            fileName: "[project]/components/DevWorkspaceModal.tsx",
                            lineNumber: 490,
                            columnNumber: 13
                        }, this),
                        tab === "diffs" && /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                            style: {
                                flex: 1,
                                minHeight: 0,
                                display: "grid",
                                gridTemplateColumns: "300px 1fr"
                            },
                            children: [
                                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                    style: {
                                        borderRight: "1px solid rgba(255,255,255,0.08)",
                                        padding: 12,
                                        overflowY: "auto",
                                        display: "flex",
                                        flexDirection: "column",
                                        gap: 6
                                    },
                                    children: diffFiles.length === 0 ? /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                        style: {
                                            fontSize: 11.5,
                                            color: "rgba(240,237,232,0.45)",
                                            padding: 14
                                        },
                                        children: "Working tree clean — no uncommitted file changes."
                                    }, void 0, false, {
                                        fileName: "[project]/components/DevWorkspaceModal.tsx",
                                        lineNumber: 587,
                                        columnNumber: 19
                                    }, this) : diffFiles.map((df)=>/*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("button", {
                                            type: "button",
                                            onClick: ()=>setActiveDiff(df),
                                            style: {
                                                display: "flex",
                                                alignItems: "center",
                                                gap: 8,
                                                padding: "8px 10px",
                                                borderRadius: 8,
                                                border: `1px solid ${activeDiff?.path === df.path ? PRIMARY : "rgba(255,255,255,0.08)"}`,
                                                background: activeDiff?.path === df.path ? `${PRIMARY}18` : "rgba(255,255,255,0.02)",
                                                color: "#f0ede8",
                                                fontFamily: "var(--font-mono)",
                                                fontSize: 11,
                                                textAlign: "left",
                                                cursor: "pointer"
                                            },
                                            children: [
                                                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("span", {
                                                    style: {
                                                        flex: 1,
                                                        overflow: "hidden",
                                                        textOverflow: "ellipsis"
                                                    },
                                                    children: df.path
                                                }, void 0, false, {
                                                    fileName: "[project]/components/DevWorkspaceModal.tsx",
                                                    lineNumber: 618,
                                                    columnNumber: 23
                                                }, this),
                                                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("span", {
                                                    style: {
                                                        color: GREEN,
                                                        fontSize: 10
                                                    },
                                                    children: [
                                                        "+",
                                                        df.additions
                                                    ]
                                                }, void 0, true, {
                                                    fileName: "[project]/components/DevWorkspaceModal.tsx",
                                                    lineNumber: 621,
                                                    columnNumber: 23
                                                }, this),
                                                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("span", {
                                                    style: {
                                                        color: RED,
                                                        fontSize: 10
                                                    },
                                                    children: [
                                                        "-",
                                                        df.deletions
                                                    ]
                                                }, void 0, true, {
                                                    fileName: "[project]/components/DevWorkspaceModal.tsx",
                                                    lineNumber: 622,
                                                    columnNumber: 23
                                                }, this)
                                            ]
                                        }, df.path, true, {
                                            fileName: "[project]/components/DevWorkspaceModal.tsx",
                                            lineNumber: 592,
                                            columnNumber: 21
                                        }, this))
                                }, void 0, false, {
                                    fileName: "[project]/components/DevWorkspaceModal.tsx",
                                    lineNumber: 576,
                                    columnNumber: 15
                                }, this),
                                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                    style: {
                                        overflowY: "auto",
                                        padding: 14,
                                        background: "rgba(0,0,0,0.52)",
                                        fontFamily: "var(--font-mono)",
                                        fontSize: 11.5,
                                        lineHeight: 1.55
                                    },
                                    children: activeDiff ? (activeDiff.patch || "").split("\n").map((ln, idx)=>{
                                        const isAdd = ln.startsWith("+") && !ln.startsWith("+++");
                                        const isDel = ln.startsWith("-") && !ln.startsWith("---");
                                        const isHunk = ln.startsWith("@@");
                                        return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                            style: {
                                                padding: "1px 8px",
                                                background: isAdd ? "rgba(59, 227, 138, 0.13)" : isDel ? "rgba(255, 93, 108, 0.14)" : isHunk ? `${PRIMARY}14` : "transparent",
                                                color: isAdd ? GREEN : isDel ? RED : isHunk ? PRIMARY : "rgba(230,237,243,0.85)",
                                                whiteSpace: "pre-wrap"
                                            },
                                            children: ln || " "
                                        }, idx, false, {
                                            fileName: "[project]/components/DevWorkspaceModal.tsx",
                                            lineNumber: 644,
                                            columnNumber: 23
                                        }, this);
                                    }) : /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                        style: {
                                            color: "rgba(240,237,232,0.45)"
                                        },
                                        children: "No modified files to display."
                                    }, void 0, false, {
                                        fileName: "[project]/components/DevWorkspaceModal.tsx",
                                        lineNumber: 670,
                                        columnNumber: 19
                                    }, this)
                                }, void 0, false, {
                                    fileName: "[project]/components/DevWorkspaceModal.tsx",
                                    lineNumber: 628,
                                    columnNumber: 15
                                }, this)
                            ]
                        }, void 0, true, {
                            fileName: "[project]/components/DevWorkspaceModal.tsx",
                            lineNumber: 575,
                            columnNumber: 13
                        }, this)
                    ]
                }, void 0, true, {
                    fileName: "[project]/components/DevWorkspaceModal.tsx",
                    lineNumber: 312,
                    columnNumber: 9
                }, this)
            ]
        }, void 0, true, {
            fileName: "[project]/components/DevWorkspaceModal.tsx",
            lineNumber: 175,
            columnNumber: 7
        }, this)
    }, void 0, false, {
        fileName: "[project]/components/DevWorkspaceModal.tsx",
        lineNumber: 159,
        columnNumber: 5
    }, this);
}
_s(DevWorkspaceModal, "EQRMWFqsHuGioR2dKGc/bp9TwQM=", false, function() {
    return [
        __TURBOPACK__imported__module__$5b$project$5d2f$components$2f$JarvisBridge$2e$tsx__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useJarvis"]
    ];
});
_c = DevWorkspaceModal;
var _c;
__turbopack_context__.k.register(_c, "DevWorkspaceModal");
if (typeof globalThis.$RefreshHelpers$ === 'object' && globalThis.$RefreshHelpers !== null) {
    __turbopack_context__.k.registerExports(__turbopack_context__.m, globalThis.$RefreshHelpers$);
}
}),
"[project]/components/DualMonitorConsole.tsx [app-client] (ecmascript)", ((__turbopack_context__) => {
"use strict";

__turbopack_context__.s([
    "default",
    ()=>DualMonitorConsole
]);
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/next/dist/compiled/react/jsx-dev-runtime.js [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/next/dist/compiled/react/index.js [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$activity$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__Activity$3e$__ = __turbopack_context__.i("[project]/node_modules/lucide-react/dist/esm/icons/activity.js [app-client] (ecmascript) <export default as Activity>");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$mic$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__Mic$3e$__ = __turbopack_context__.i("[project]/node_modules/lucide-react/dist/esm/icons/mic.js [app-client] (ecmascript) <export default as Mic>");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$mic$2d$off$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__MicOff$3e$__ = __turbopack_context__.i("[project]/node_modules/lucide-react/dist/esm/icons/mic-off.js [app-client] (ecmascript) <export default as MicOff>");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$send$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__Send$3e$__ = __turbopack_context__.i("[project]/node_modules/lucide-react/dist/esm/icons/send.js [app-client] (ecmascript) <export default as Send>");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$square$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__Square$3e$__ = __turbopack_context__.i("[project]/node_modules/lucide-react/dist/esm/icons/square.js [app-client] (ecmascript) <export default as Square>");
var __TURBOPACK__imported__module__$5b$project$5d2f$components$2f$JarvisBridge$2e$tsx__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/components/JarvisBridge.tsx [app-client] (ecmascript)");
;
var _s = __turbopack_context__.k.signature();
"use client";
;
;
;
const GREEN = "#3be38a";
const RED = "#ff5d6c";
function DualMonitorConsole() {
    _s();
    const { connected, assistantName, activePersona, theme, logs, workers, muted, toggleMute, sendText, cancelWorker } = (0, __TURBOPACK__imported__module__$5b$project$5d2f$components$2f$JarvisBridge$2e$tsx__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useJarvis"])();
    const [cmd, setCmd] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])("");
    const endRef = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useRef"])(null);
    (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useEffect"])({
        "DualMonitorConsole.useEffect": ()=>{
            endRef.current?.scrollIntoView({
                behavior: "smooth"
            });
        }
    }["DualMonitorConsole.useEffect"], [
        logs.length
    ]);
    const PRIMARY = theme.primary;
    const SECONDARY = theme.secondary;
    const onSubmit = (e)=>{
        e.preventDefault();
        if (!cmd.trim()) return;
        sendText(cmd);
        setCmd("");
    };
    return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("main", {
        style: {
            height: "100vh",
            background: theme.pageBg,
            color: "#f0ede8",
            display: "flex",
            flexDirection: "column",
            overflow: "hidden"
        },
        children: [
            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("header", {
                style: {
                    display: "flex",
                    alignItems: "center",
                    gap: 10,
                    padding: "12px 18px",
                    borderBottom: `1px solid ${PRIMARY}33`,
                    background: theme.drawerBg
                },
                children: [
                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("span", {
                        style: {
                            width: 8,
                            height: 8,
                            borderRadius: "50%",
                            background: connected ? GREEN : RED,
                            boxShadow: `0 0 10px ${connected ? GREEN : RED}`
                        }
                    }, void 0, false, {
                        fileName: "[project]/components/DualMonitorConsole.tsx",
                        lineNumber: 68,
                        columnNumber: 9
                    }, this),
                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("span", {
                        style: {
                            fontFamily: "var(--font-mono)",
                            fontSize: 11,
                            letterSpacing: "0.22em",
                            color: PRIMARY,
                            flex: 1
                        },
                        children: [
                            assistantName.toUpperCase(),
                            " · DUAL-MONITOR CONSOLE (",
                            activePersona.toUpperCase(),
                            ")"
                        ]
                    }, void 0, true, {
                        fileName: "[project]/components/DualMonitorConsole.tsx",
                        lineNumber: 77,
                        columnNumber: 9
                    }, this)
                ]
            }, void 0, true, {
                fileName: "[project]/components/DualMonitorConsole.tsx",
                lineNumber: 58,
                columnNumber: 7
            }, this),
            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                style: {
                    flex: 1,
                    display: "flex",
                    minHeight: 0
                },
                children: [
                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("section", {
                        style: {
                            flex: 1,
                            overflowY: "auto",
                            padding: "16px 18px",
                            display: "flex",
                            flexDirection: "column",
                            gap: 9
                        },
                        children: [
                            logs.map((entry)=>{
                                const accent = entry.role === "user" ? PRIMARY : entry.role === "jarvis" ? SECONDARY : "rgba(160,185,205,0.65)";
                                return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                    style: {
                                        padding: "10px 13px",
                                        borderRadius: 10,
                                        background: entry.role === "user" ? theme.primarySoftBg : entry.role === "jarvis" ? theme.secondarySoftBg : "rgba(255,255,255,0.03)",
                                        borderLeft: `2px solid ${accent}`,
                                        fontSize: 12.5,
                                        lineHeight: 1.55
                                    },
                                    children: entry.line
                                }, entry.id, false, {
                                    fileName: "[project]/components/DualMonitorConsole.tsx",
                                    lineNumber: 110,
                                    columnNumber: 15
                                }, this);
                            }),
                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                ref: endRef
                            }, void 0, false, {
                                fileName: "[project]/components/DualMonitorConsole.tsx",
                                lineNumber: 130,
                                columnNumber: 11
                            }, this)
                        ]
                    }, void 0, true, {
                        fileName: "[project]/components/DualMonitorConsole.tsx",
                        lineNumber: 92,
                        columnNumber: 9
                    }, this),
                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("aside", {
                        style: {
                            width: "min(300px, 38vw)",
                            borderLeft: `1px solid ${PRIMARY}24`,
                            padding: "14px",
                            overflowY: "auto",
                            background: "rgba(0,0,0,0.22)"
                        },
                        children: [
                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                style: {
                                    display: "flex",
                                    alignItems: "center",
                                    gap: 6,
                                    fontFamily: "var(--font-mono)",
                                    fontSize: 10,
                                    letterSpacing: "0.16em",
                                    color: SECONDARY,
                                    marginBottom: 10
                                },
                                children: [
                                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$activity$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__Activity$3e$__["Activity"], {
                                        size: 12
                                    }, void 0, false, {
                                        fileName: "[project]/components/DualMonitorConsole.tsx",
                                        lineNumber: 154,
                                        columnNumber: 13
                                    }, this),
                                    "LIVE WORKERS (",
                                    workers.length,
                                    ")"
                                ]
                            }, void 0, true, {
                                fileName: "[project]/components/DualMonitorConsole.tsx",
                                lineNumber: 142,
                                columnNumber: 11
                            }, this),
                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                style: {
                                    display: "flex",
                                    flexDirection: "column",
                                    gap: 8
                                },
                                children: workers.map((w)=>/*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                        style: {
                                            padding: "8px 10px",
                                            borderRadius: 9,
                                            border: `1px solid ${PRIMARY}2a`,
                                            background: "rgba(255,255,255,0.025)"
                                        },
                                        children: [
                                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                                style: {
                                                    display: "flex",
                                                    alignItems: "center",
                                                    gap: 6
                                                },
                                                children: [
                                                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("span", {
                                                        style: {
                                                            fontFamily: "var(--font-mono)",
                                                            fontSize: 8.5,
                                                            color: w.status === "in_progress" ? PRIMARY : GREEN,
                                                            textTransform: "uppercase"
                                                        },
                                                        children: w.status
                                                    }, void 0, false, {
                                                        fileName: "[project]/components/DualMonitorConsole.tsx",
                                                        lineNumber: 169,
                                                        columnNumber: 19
                                                    }, this),
                                                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("span", {
                                                        style: {
                                                            flex: 1
                                                        }
                                                    }, void 0, false, {
                                                        fileName: "[project]/components/DualMonitorConsole.tsx",
                                                        lineNumber: 179,
                                                        columnNumber: 19
                                                    }, this),
                                                    (w.status === "in_progress" || w.status === "pending") && /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("button", {
                                                        type: "button",
                                                        onClick: ()=>cancelWorker(w.id),
                                                        style: {
                                                            background: "none",
                                                            border: "none",
                                                            color: RED,
                                                            cursor: "pointer"
                                                        },
                                                        children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$square$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__Square$3e$__["Square"], {
                                                            size: 10
                                                        }, void 0, false, {
                                                            fileName: "[project]/components/DualMonitorConsole.tsx",
                                                            lineNumber: 191,
                                                            columnNumber: 23
                                                        }, this)
                                                    }, void 0, false, {
                                                        fileName: "[project]/components/DualMonitorConsole.tsx",
                                                        lineNumber: 181,
                                                        columnNumber: 21
                                                    }, this)
                                                ]
                                            }, void 0, true, {
                                                fileName: "[project]/components/DualMonitorConsole.tsx",
                                                lineNumber: 168,
                                                columnNumber: 17
                                            }, this),
                                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                                style: {
                                                    fontSize: 11.5,
                                                    marginTop: 4
                                                },
                                                children: w.title
                                            }, void 0, false, {
                                                fileName: "[project]/components/DualMonitorConsole.tsx",
                                                lineNumber: 195,
                                                columnNumber: 17
                                            }, this)
                                        ]
                                    }, w.id, true, {
                                        fileName: "[project]/components/DualMonitorConsole.tsx",
                                        lineNumber: 159,
                                        columnNumber: 15
                                    }, this))
                            }, void 0, false, {
                                fileName: "[project]/components/DualMonitorConsole.tsx",
                                lineNumber: 157,
                                columnNumber: 11
                            }, this)
                        ]
                    }, void 0, true, {
                        fileName: "[project]/components/DualMonitorConsole.tsx",
                        lineNumber: 133,
                        columnNumber: 9
                    }, this)
                ]
            }, void 0, true, {
                fileName: "[project]/components/DualMonitorConsole.tsx",
                lineNumber: 91,
                columnNumber: 7
            }, this),
            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("form", {
                onSubmit: onSubmit,
                style: {
                    display: "flex",
                    alignItems: "center",
                    gap: 8,
                    padding: "12px 18px",
                    borderTop: `1px solid ${PRIMARY}28`,
                    background: theme.barBg
                },
                children: [
                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("button", {
                        type: "button",
                        onClick: toggleMute,
                        style: {
                            width: 34,
                            height: 34,
                            borderRadius: "50%",
                            border: `1px solid ${muted ? RED : PRIMARY}66`,
                            background: "transparent",
                            color: muted ? RED : PRIMARY,
                            display: "flex",
                            alignItems: "center",
                            justifyContent: "center",
                            cursor: "pointer"
                        },
                        children: muted ? /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$mic$2d$off$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__MicOff$3e$__["MicOff"], {
                            size: 15
                        }, void 0, false, {
                            fileName: "[project]/components/DualMonitorConsole.tsx",
                            lineNumber: 230,
                            columnNumber: 20
                        }, this) : /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$mic$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__Mic$3e$__["Mic"], {
                            size: 15
                        }, void 0, false, {
                            fileName: "[project]/components/DualMonitorConsole.tsx",
                            lineNumber: 230,
                            columnNumber: 43
                        }, this)
                    }, void 0, false, {
                        fileName: "[project]/components/DualMonitorConsole.tsx",
                        lineNumber: 214,
                        columnNumber: 9
                    }, this),
                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("input", {
                        type: "text",
                        value: cmd,
                        onChange: (e)=>setCmd(e.target.value),
                        placeholder: `Message ${assistantName} from secondary monitor…`,
                        style: {
                            flex: 1,
                            padding: "9px 14px",
                            borderRadius: 999,
                            border: `1px solid ${PRIMARY}44`,
                            background: "rgba(0,0,0,0.35)",
                            color: "#f0ede8",
                            fontSize: 13,
                            outline: "none"
                        }
                    }, void 0, false, {
                        fileName: "[project]/components/DualMonitorConsole.tsx",
                        lineNumber: 232,
                        columnNumber: 9
                    }, this),
                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("button", {
                        type: "submit",
                        style: {
                            padding: "9px 16px",
                            borderRadius: 999,
                            border: `1px solid ${PRIMARY}66`,
                            background: `${PRIMARY}22`,
                            color: PRIMARY,
                            fontFamily: "var(--font-mono)",
                            fontSize: 10,
                            cursor: "pointer",
                            display: "inline-flex",
                            alignItems: "center",
                            gap: 5
                        },
                        children: [
                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$send$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__Send$3e$__["Send"], {
                                size: 12
                            }, void 0, false, {
                                fileName: "[project]/components/DualMonitorConsole.tsx",
                                lineNumber: 264,
                                columnNumber: 11
                            }, this),
                            "SEND"
                        ]
                    }, void 0, true, {
                        fileName: "[project]/components/DualMonitorConsole.tsx",
                        lineNumber: 248,
                        columnNumber: 9
                    }, this)
                ]
            }, void 0, true, {
                fileName: "[project]/components/DualMonitorConsole.tsx",
                lineNumber: 203,
                columnNumber: 7
            }, this)
        ]
    }, void 0, true, {
        fileName: "[project]/components/DualMonitorConsole.tsx",
        lineNumber: 47,
        columnNumber: 5
    }, this);
}
_s(DualMonitorConsole, "ybv6ZAqkv7l4EKj7TP0gKOgGmFU=", false, function() {
    return [
        __TURBOPACK__imported__module__$5b$project$5d2f$components$2f$JarvisBridge$2e$tsx__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useJarvis"]
    ];
});
_c = DualMonitorConsole;
var _c;
__turbopack_context__.k.register(_c, "DualMonitorConsole");
if (typeof globalThis.$RefreshHelpers$ === 'object' && globalThis.$RefreshHelpers !== null) {
    __turbopack_context__.k.registerExports(__turbopack_context__.m, globalThis.$RefreshHelpers$);
}
}),
"[project]/components/HudSocialModal.tsx [app-client] (ecmascript)", ((__turbopack_context__) => {
"use strict";

__turbopack_context__.s([
    "default",
    ()=>HudSocialModal
]);
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/next/dist/compiled/react/jsx-dev-runtime.js [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/next/dist/compiled/react/index.js [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$chevron$2d$down$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__ChevronDown$3e$__ = __turbopack_context__.i("[project]/node_modules/lucide-react/dist/esm/icons/chevron-down.js [app-client] (ecmascript) <export default as ChevronDown>");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$chevron$2d$up$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__ChevronUp$3e$__ = __turbopack_context__.i("[project]/node_modules/lucide-react/dist/esm/icons/chevron-up.js [app-client] (ecmascript) <export default as ChevronUp>");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$external$2d$link$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__ExternalLink$3e$__ = __turbopack_context__.i("[project]/node_modules/lucide-react/dist/esm/icons/external-link.js [app-client] (ecmascript) <export default as ExternalLink>");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$heart$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__Heart$3e$__ = __turbopack_context__.i("[project]/node_modules/lucide-react/dist/esm/icons/heart.js [app-client] (ecmascript) <export default as Heart>");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$maximize$2d$2$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__Maximize2$3e$__ = __turbopack_context__.i("[project]/node_modules/lucide-react/dist/esm/icons/maximize-2.js [app-client] (ecmascript) <export default as Maximize2>");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$minimize$2d$2$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__Minimize2$3e$__ = __turbopack_context__.i("[project]/node_modules/lucide-react/dist/esm/icons/minimize-2.js [app-client] (ecmascript) <export default as Minimize2>");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$refresh$2d$cw$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__RefreshCw$3e$__ = __turbopack_context__.i("[project]/node_modules/lucide-react/dist/esm/icons/refresh-cw.js [app-client] (ecmascript) <export default as RefreshCw>");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$send$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__Send$3e$__ = __turbopack_context__.i("[project]/node_modules/lucide-react/dist/esm/icons/send.js [app-client] (ecmascript) <export default as Send>");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$x$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__X$3e$__ = __turbopack_context__.i("[project]/node_modules/lucide-react/dist/esm/icons/x.js [app-client] (ecmascript) <export default as X>");
var __TURBOPACK__imported__module__$5b$project$5d2f$components$2f$JarvisBridge$2e$tsx__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/components/JarvisBridge.tsx [app-client] (ecmascript)");
;
var _s = __turbopack_context__.k.signature();
"use client";
;
;
;
const PLATFORMS = [
    {
        key: "instagram",
        short: "IG"
    },
    {
        key: "snapchat",
        short: "SNAP"
    },
    {
        key: "tiktok",
        short: "TIKTOK"
    },
    {
        key: "x",
        short: "X"
    },
    {
        key: "whatsapp",
        short: "WA"
    },
    {
        key: "reddit",
        short: "REDDIT"
    }
];
const VIEWS = [
    {
        key: "feed",
        label: "FEED"
    },
    {
        key: "reels",
        label: "REELS"
    },
    {
        key: "inbox",
        label: "DMs"
    },
    {
        key: "notifications",
        label: "ALERTS"
    }
];
const GREEN = "#34d399";
const AMBER = "#f5a623";
function HudSocialModal() {
    _s();
    const { socialHud, theme, openSocialHud, closeSocialHud } = (0, __TURBOPACK__imported__module__$5b$project$5d2f$components$2f$JarvisBridge$2e$tsx__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useJarvis"])();
    const [frameB64, setFrameB64] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])("");
    const [liveUrl, setLiveUrl] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])("");
    const [isConn, setIsConn] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])(false);
    const [loading, setLoading] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])(false);
    const [frameError, setFrameError] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])("");
    const [inputBusy, setInputBusy] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])(false);
    const [sessionHealth, setSessionHealth] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])("unverified");
    const [errMsg, setErrMsg] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])("");
    const [quickText, setQuickText] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])("");
    const [ripple, setRipple] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])(null);
    const activeBoostUntilRef = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useRef"])(0);
    const inFlightRef = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useRef"])(false);
    const epochRef = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useRef"])(0);
    const inputBusyRef = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useRef"])(false);
    const queueRef = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useRef"])(Promise.resolve());
    const viewportRef = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useRef"])(null);
    const boostFps = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useCallback"])({
        "HudSocialModal.useCallback[boostFps]": ()=>{
            activeBoostUntilRef.current = Date.now() + 3200;
        }
    }["HudSocialModal.useCallback[boostFps]"], []);
    const fetchFrame = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useCallback"])({
        "HudSocialModal.useCallback[fetchFrame]": async (plat)=>{
            if (inFlightRef.current) return;
            inFlightRef.current = true;
            const epoch = epochRef.current;
            try {
                const r = await fetch(`/api/hud/social/frame?platform=${encodeURIComponent(plat)}`, {
                    cache: "no-store",
                    signal: AbortSignal.timeout(15000)
                });
                const data = await r.json();
                if (epoch !== epochRef.current) return;
                if (r.ok && data && data.ok && data.image_b64) {
                    setFrameB64(data.image_b64);
                    if (data.url) setLiveUrl(data.url);
                    setIsConn(Boolean(data.connected));
                    setSessionHealth(data.session_health || "unverified");
                    setFrameError("");
                } else {
                    setFrameError(data?.error || "The live frame is unavailable. Use Refresh to reconnect.");
                }
            } catch  {
                if (epoch === epochRef.current) setFrameError("The live stream is unavailable. The image may be stale; wait for reconnection.");
            } finally{
                inFlightRef.current = false;
                if (epoch === epochRef.current) setLoading(false);
            }
        }
    }["HudSocialModal.useCallback[fetchFrame]"], []);
    (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useEffect"])({
        "HudSocialModal.useEffect": ()=>{
            epochRef.current += 1;
            setFrameB64("");
            setLiveUrl("");
            setErrMsg("");
            setFrameError("");
            if (!socialHud || !socialHud.active) {
                setFrameB64("");
                return;
            }
            setLoading(true);
            setIsConn(Boolean(socialHud.connected));
            setSessionHealth(socialHud.session_health || "unverified");
            boostFps();
            let cancelled = false;
            let timer = null;
            const loop = {
                "HudSocialModal.useEffect.loop": async ()=>{
                    if (cancelled || !socialHud?.active) return;
                    await fetchFrame(socialHud.platform);
                    if (cancelled) return;
                    const delay = Date.now() < activeBoostUntilRef.current ? 240 : 650;
                    timer = setTimeout(loop, delay);
                }
            }["HudSocialModal.useEffect.loop"];
            loop();
            return ({
                "HudSocialModal.useEffect": ()=>{
                    cancelled = true;
                    epochRef.current += 1;
                    if (timer) clearTimeout(timer);
                }
            })["HudSocialModal.useEffect"];
        }
    }["HudSocialModal.useEffect"], [
        socialHud?.active,
        socialHud?.platform,
        socialHud?.opened_at,
        boostFps,
        fetchFrame
    ]);
    const sendInteract = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useCallback"])({
        "HudSocialModal.useCallback[sendInteract]": (payload)=>{
            if (!socialHud) return Promise.resolve(false);
            const epoch = epochRef.current;
            const run = {
                "HudSocialModal.useCallback[sendInteract].run": async ()=>{
                    if (epoch !== epochRef.current) return false;
                    boostFps();
                    try {
                        const r = await fetch("/api/hud/social/interact", {
                            method: "POST",
                            headers: {
                                "Content-Type": "application/json"
                            },
                            signal: AbortSignal.timeout(20000),
                            body: JSON.stringify({
                                platform: socialHud.platform,
                                layout: socialHud.layout,
                                opened_at: socialHud.opened_at,
                                ...payload
                            })
                        });
                        const data = await r.json();
                        if (!r.ok || !data?.ok) throw new Error(data?.error || "HUD interaction failed.");
                        if (epoch === epochRef.current) {
                            setErrMsg("");
                            await fetchFrame(socialHud.platform);
                        }
                        return true;
                    } catch (err) {
                        if (epoch === epochRef.current) setErrMsg(`${err instanceof Error ? err.message : "HUD interaction failed."} It may have applied; inspect the chat before retrying a send.`);
                        return false;
                    }
                }
            }["HudSocialModal.useCallback[sendInteract].run"];
            // Preserve click -> focus -> typing -> Enter order, even under latency.
            const task = queueRef.current.then(run, run);
            queueRef.current = task;
            return task;
        }
    }["HudSocialModal.useCallback[sendInteract]"], [
        socialHud,
        boostFps,
        fetchFrame
    ]);
    const insertQuickText = async (submit)=>{
        if (inputBusyRef.current || !quickText) return;
        inputBusyRef.current = true;
        setInputBusy(true);
        const text = quickText;
        try {
            if (await sendInteract({
                kind: "type",
                text,
                submit
            })) {
                setQuickText((current)=>current === text ? "" : current);
            }
        } finally{
            inputBusyRef.current = false;
            setInputBusy(false);
        }
    };
    if (!socialHud || !socialHud.active) return null;
    const PRIMARY = theme.primary;
    const SECONDARY = theme.secondary;
    const isWide = socialHud.layout === "wide";
    const onViewportClick = (e)=>{
        const el = viewportRef.current;
        if (!el || frameError) return;
        el.focus();
        const rect = el.getBoundingClientRect();
        const nx = Math.max(0, Math.min(1, (e.clientX - rect.left) / rect.width));
        const ny = Math.max(0, Math.min(1, (e.clientY - rect.top) / rect.height));
        setRipple({
            x: e.clientX - rect.left,
            y: e.clientY - rect.top,
            id: Date.now()
        });
        sendInteract({
            kind: "click",
            nx,
            ny
        });
    };
    const onViewportWheel = (e)=>{
        e.preventDefault();
        if (frameError) return;
        sendInteract({
            kind: "wheel",
            deltaX: e.deltaX,
            deltaY: Math.max(-780, Math.min(780, e.deltaY * 1.3))
        });
    };
    const onViewportKeyDown = (e)=>{
        if (frameError || e.metaKey || e.ctrlKey || e.altKey) return;
        if ([
            "Enter",
            "Backspace",
            "Tab",
            "Escape",
            "ArrowDown",
            "ArrowUp",
            "ArrowLeft",
            "ArrowRight"
        ].includes(e.key)) {
            e.preventDefault();
            sendInteract({
                kind: "key",
                key: e.key
            });
            return;
        }
        if (e.key.length === 1) {
            e.preventDefault();
            sendInteract({
                kind: "type",
                text: e.key,
                submit: false
            });
        }
    };
    const onQuickSend = (e)=>{
        e.preventDefault();
        if (!quickText || frameError) return;
        void insertQuickText(true);
    };
    const pillBtn = {
        display: "inline-flex",
        alignItems: "center",
        justifyContent: "center",
        gap: 4,
        padding: "4px 8px",
        borderRadius: 999,
        border: `1px solid ${PRIMARY}35`,
        background: "rgba(255,255,255,0.03)",
        color: "rgba(240,237,232,0.88)",
        fontFamily: "var(--font-mono)",
        fontSize: 9.5,
        letterSpacing: "0.08em",
        cursor: "pointer"
    };
    return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
        "data-testid": "hud-social-viewport",
        style: {
            position: "fixed",
            right: 20,
            top: 64,
            bottom: 84,
            width: isWide ? "min(860px, calc(100vw - 40px))" : "min(416px, calc(100vw - 32px))",
            zIndex: 88,
            display: "flex",
            flexDirection: "column",
            borderRadius: 18,
            background: "rgba(6, 12, 22, 0.92)",
            backdropFilter: "blur(24px)",
            border: `1px solid ${PRIMARY}55`,
            boxShadow: `0 22px 60px rgba(0,0,0,0.68), 0 0 36px ${PRIMARY}18`,
            overflow: "hidden"
        },
        children: [
            (errMsg || frameError) && /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                role: "alert",
                style: {
                    padding: "9px 12px",
                    background: "#482b18",
                    color: "#ffcc92",
                    fontSize: 12
                },
                children: errMsg || frameError
            }, void 0, false, {
                fileName: "[project]/components/HudSocialModal.tsx",
                lineNumber: 270,
                columnNumber: 9
            }, this),
            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                style: {
                    padding: "9px 12px 7px",
                    borderBottom: `1px solid ${PRIMARY}26`,
                    display: "flex",
                    flexDirection: "column",
                    gap: 7,
                    background: "rgba(255,255,255,0.02)"
                },
                children: [
                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                        style: {
                            display: "flex",
                            alignItems: "center",
                            justifyContent: "space-between",
                            gap: 8
                        },
                        children: [
                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                style: {
                                    display: "flex",
                                    alignItems: "center",
                                    gap: 7
                                },
                                children: [
                                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("span", {
                                        title: isConn ? "Live signed-in session" : sessionHealth === "login_required" ? "Sign in inside this HUD" : sessionHealth === "challenge_required" ? "Complete Instagram security verification inside this HUD" : "Session not live-verified yet",
                                        style: {
                                            width: 7,
                                            height: 7,
                                            borderRadius: "50%",
                                            background: isConn ? GREEN : AMBER,
                                            boxShadow: `0 0 8px ${isConn ? GREEN : AMBER}`
                                        }
                                    }, void 0, false, {
                                        fileName: "[project]/components/HudSocialModal.tsx",
                                        lineNumber: 294,
                                        columnNumber: 13
                                    }, this),
                                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("span", {
                                        style: {
                                            fontFamily: "var(--font-mono)",
                                            fontSize: 10.5,
                                            fontWeight: 700,
                                            letterSpacing: "0.14em",
                                            color: PRIMARY
                                        },
                                        children: [
                                            (socialHud.label || socialHud.platform).toUpperCase(),
                                            " · HUD LIVE"
                                        ]
                                    }, void 0, true, {
                                        fileName: "[project]/components/HudSocialModal.tsx",
                                        lineNumber: 304,
                                        columnNumber: 13
                                    }, this)
                                ]
                            }, void 0, true, {
                                fileName: "[project]/components/HudSocialModal.tsx",
                                lineNumber: 293,
                                columnNumber: 11
                            }, this),
                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                style: {
                                    display: "flex",
                                    alignItems: "center",
                                    gap: 5
                                },
                                children: [
                                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("button", {
                                        type: "button",
                                        title: "Toggle Compact / Wide HUD View",
                                        onClick: ()=>sendInteract({
                                                kind: "layout",
                                                mode: isWide ? "mobile" : "wide"
                                            }),
                                        style: pillBtn,
                                        children: [
                                            isWide ? /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$minimize$2d$2$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__Minimize2$3e$__["Minimize2"], {
                                                size: 11
                                            }, void 0, false, {
                                                fileName: "[project]/components/HudSocialModal.tsx",
                                                lineNumber: 329,
                                                columnNumber: 25
                                            }, this) : /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$maximize$2d$2$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__Maximize2$3e$__["Maximize2"], {
                                                size: 11
                                            }, void 0, false, {
                                                fileName: "[project]/components/HudSocialModal.tsx",
                                                lineNumber: 329,
                                                columnNumber: 51
                                            }, this),
                                            isWide ? "APP" : "WIDE"
                                        ]
                                    }, void 0, true, {
                                        fileName: "[project]/components/HudSocialModal.tsx",
                                        lineNumber: 318,
                                        columnNumber: 13
                                    }, this),
                                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("button", {
                                        type: "button",
                                        title: "Pop out to standalone window",
                                        onClick: ()=>sendInteract({
                                                kind: "popout"
                                            }),
                                        style: pillBtn,
                                        children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$external$2d$link$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__ExternalLink$3e$__["ExternalLink"], {
                                            size: 11
                                        }, void 0, false, {
                                            fileName: "[project]/components/HudSocialModal.tsx",
                                            lineNumber: 338,
                                            columnNumber: 15
                                        }, this)
                                    }, void 0, false, {
                                        fileName: "[project]/components/HudSocialModal.tsx",
                                        lineNumber: 332,
                                        columnNumber: 13
                                    }, this),
                                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("button", {
                                        type: "button",
                                        title: "Close HUD panel",
                                        onClick: ()=>closeSocialHud(),
                                        style: {
                                            ...pillBtn,
                                            borderColor: "rgba(255,91,121,0.4)",
                                            color: "#ff8098"
                                        },
                                        children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$x$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__X$3e$__["X"], {
                                            size: 12
                                        }, void 0, false, {
                                            fileName: "[project]/components/HudSocialModal.tsx",
                                            lineNumber: 346,
                                            columnNumber: 15
                                        }, this)
                                    }, void 0, false, {
                                        fileName: "[project]/components/HudSocialModal.tsx",
                                        lineNumber: 340,
                                        columnNumber: 13
                                    }, this)
                                ]
                            }, void 0, true, {
                                fileName: "[project]/components/HudSocialModal.tsx",
                                lineNumber: 317,
                                columnNumber: 11
                            }, this)
                        ]
                    }, void 0, true, {
                        fileName: "[project]/components/HudSocialModal.tsx",
                        lineNumber: 285,
                        columnNumber: 9
                    }, this),
                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                        style: {
                            display: "flex",
                            alignItems: "center",
                            justifyContent: "space-between",
                            gap: 6,
                            flexWrap: "wrap"
                        },
                        children: [
                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                style: {
                                    display: "flex",
                                    alignItems: "center",
                                    gap: 4,
                                    flexWrap: "wrap"
                                },
                                children: PLATFORMS.map((p)=>{
                                    const active = p.key === socialHud.platform;
                                    return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("button", {
                                        type: "button",
                                        onClick: async ()=>{
                                            const result = await openSocialHud(p.key, "feed", socialHud.layout);
                                            if (!result.ok) setErrMsg(result.error || "Could not open the social HUD.");
                                        },
                                        style: {
                                            ...pillBtn,
                                            padding: "3px 7px",
                                            fontSize: 9,
                                            borderColor: active ? PRIMARY : "rgba(255,255,255,0.12)",
                                            background: active ? `${PRIMARY}26` : "rgba(255,255,255,0.02)",
                                            color: active ? "#ffffff" : "rgba(240,237,232,0.65)"
                                        },
                                        children: p.short
                                    }, p.key, false, {
                                        fileName: "[project]/components/HudSocialModal.tsx",
                                        lineNumber: 365,
                                        columnNumber: 17
                                    }, this);
                                })
                            }, void 0, false, {
                                fileName: "[project]/components/HudSocialModal.tsx",
                                lineNumber: 361,
                                columnNumber: 11
                            }, this),
                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                style: {
                                    display: "flex",
                                    alignItems: "center",
                                    gap: 4
                                },
                                children: VIEWS.map((v)=>{
                                    const active = socialHud.view === v.key;
                                    return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("button", {
                                        type: "button",
                                        onClick: ()=>sendInteract({
                                                kind: "navigate",
                                                view: v.key
                                            }),
                                        style: {
                                            ...pillBtn,
                                            padding: "3px 7px",
                                            fontSize: 9,
                                            borderColor: active ? SECONDARY : `${SECONDARY}44`,
                                            background: active ? `${SECONDARY}24` : "transparent",
                                            color: active ? "#ffffff" : SECONDARY
                                        },
                                        children: v.label
                                    }, v.key, false, {
                                        fileName: "[project]/components/HudSocialModal.tsx",
                                        lineNumber: 391,
                                        columnNumber: 17
                                    }, this);
                                })
                            }, void 0, false, {
                                fileName: "[project]/components/HudSocialModal.tsx",
                                lineNumber: 387,
                                columnNumber: 11
                            }, this)
                        ]
                    }, void 0, true, {
                        fileName: "[project]/components/HudSocialModal.tsx",
                        lineNumber: 352,
                        columnNumber: 9
                    }, this)
                ]
            }, void 0, true, {
                fileName: "[project]/components/HudSocialModal.tsx",
                lineNumber: 275,
                columnNumber: 7
            }, this),
            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                ref: viewportRef,
                tabIndex: 0,
                onClick: onViewportClick,
                onWheel: onViewportWheel,
                onKeyDown: onViewportKeyDown,
                style: {
                    position: "relative",
                    flex: 1,
                    minHeight: 0,
                    background: "#040811",
                    cursor: "pointer",
                    outline: "none",
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    overflow: "hidden",
                    userSelect: "none"
                },
                children: [
                    frameB64 ? /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("img", {
                        src: `data:image/jpeg;base64,${frameB64}`,
                        alt: socialHud.label,
                        draggable: false,
                        style: {
                            width: "100%",
                            height: "100%",
                            objectFit: "fill",
                            display: "block"
                        }
                    }, void 0, false, {
                        fileName: "[project]/components/HudSocialModal.tsx",
                        lineNumber: 434,
                        columnNumber: 11
                    }, this) : /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                        style: {
                            display: "flex",
                            flexDirection: "column",
                            alignItems: "center",
                            gap: 10,
                            padding: 24,
                            textAlign: "center",
                            color: "rgba(240,237,232,0.75)",
                            fontFamily: "var(--font-mono)",
                            fontSize: 11
                        },
                        children: [
                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$refresh$2d$cw$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__RefreshCw$3e$__["RefreshCw"], {
                                size: 18,
                                style: {
                                    color: PRIMARY
                                }
                            }, void 0, false, {
                                fileName: "[project]/components/HudSocialModal.tsx",
                                lineNumber: 459,
                                columnNumber: 13
                            }, this),
                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                children: errMsg || frameError ? errMsg || frameError : loading ? `Connecting live ${socialHud.label} stream inside HUD…` : `Preparing ${socialHud.label}…`
                            }, void 0, false, {
                                fileName: "[project]/components/HudSocialModal.tsx",
                                lineNumber: 460,
                                columnNumber: 13
                            }, this)
                        ]
                    }, void 0, true, {
                        fileName: "[project]/components/HudSocialModal.tsx",
                        lineNumber: 446,
                        columnNumber: 11
                    }, this),
                    ripple && /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("span", {
                        style: {
                            position: "absolute",
                            left: ripple.x - 12,
                            top: ripple.y - 12,
                            width: 24,
                            height: 24,
                            borderRadius: "50%",
                            border: `2px solid ${PRIMARY}`,
                            background: `${PRIMARY}33`,
                            pointerEvents: "none",
                            opacity: 0.75
                        }
                    }, ripple.id, false, {
                        fileName: "[project]/components/HudSocialModal.tsx",
                        lineNumber: 472,
                        columnNumber: 11
                    }, this),
                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                        onClick: (e)=>e.stopPropagation(),
                        style: {
                            position: "absolute",
                            right: 8,
                            bottom: 10,
                            display: "flex",
                            flexDirection: "column",
                            gap: 5
                        },
                        children: [
                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("button", {
                                type: "button",
                                title: "Previous Reel / Scroll Up",
                                onClick: ()=>sendInteract({
                                        kind: "navigate",
                                        view: "previous"
                                    }),
                                style: {
                                    ...pillBtn,
                                    padding: 6,
                                    background: "rgba(6,12,22,0.82)"
                                },
                                children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$chevron$2d$up$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__ChevronUp$3e$__["ChevronUp"], {
                                    size: 13
                                }, void 0, false, {
                                    fileName: "[project]/components/HudSocialModal.tsx",
                                    lineNumber: 507,
                                    columnNumber: 13
                                }, this)
                            }, void 0, false, {
                                fileName: "[project]/components/HudSocialModal.tsx",
                                lineNumber: 501,
                                columnNumber: 11
                            }, this),
                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("button", {
                                type: "button",
                                title: "Next Reel / Scroll Down",
                                onClick: ()=>sendInteract({
                                        kind: "navigate",
                                        view: "next"
                                    }),
                                style: {
                                    ...pillBtn,
                                    padding: 6,
                                    background: "rgba(6,12,22,0.82)"
                                },
                                children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$chevron$2d$down$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__ChevronDown$3e$__["ChevronDown"], {
                                    size: 13
                                }, void 0, false, {
                                    fileName: "[project]/components/HudSocialModal.tsx",
                                    lineNumber: 515,
                                    columnNumber: 13
                                }, this)
                            }, void 0, false, {
                                fileName: "[project]/components/HudSocialModal.tsx",
                                lineNumber: 509,
                                columnNumber: 11
                            }, this),
                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("button", {
                                type: "button",
                                title: "Like Active Post / Reel",
                                onClick: ()=>sendInteract({
                                        kind: "navigate",
                                        view: "like"
                                    }),
                                style: {
                                    ...pillBtn,
                                    padding: 6,
                                    background: "rgba(6,12,22,0.82)",
                                    color: "#ff5b79",
                                    borderColor: "rgba(255,91,121,0.45)"
                                },
                                children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$heart$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__Heart$3e$__["Heart"], {
                                    size: 13
                                }, void 0, false, {
                                    fileName: "[project]/components/HudSocialModal.tsx",
                                    lineNumber: 529,
                                    columnNumber: 13
                                }, this)
                            }, void 0, false, {
                                fileName: "[project]/components/HudSocialModal.tsx",
                                lineNumber: 517,
                                columnNumber: 11
                            }, this)
                        ]
                    }, void 0, true, {
                        fileName: "[project]/components/HudSocialModal.tsx",
                        lineNumber: 490,
                        columnNumber: 9
                    }, this)
                ]
            }, void 0, true, {
                fileName: "[project]/components/HudSocialModal.tsx",
                lineNumber: 413,
                columnNumber: 7
            }, this),
            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("form", {
                onSubmit: onQuickSend,
                style: {
                    display: "flex",
                    alignItems: "center",
                    gap: 6,
                    padding: "8px 10px",
                    borderTop: `1px solid ${PRIMARY}26`,
                    background: "rgba(255,255,255,0.025)"
                },
                children: [
                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("input", {
                        type: "text",
                        value: quickText,
                        onChange: (e)=>setQuickText(e.target.value),
                        placeholder: liveUrl.toLowerCase().includes("login") ? "Click field above, then type username / password / 2FA…" : "Click input above or type DM / @search & press Enter…",
                        style: {
                            flex: 1,
                            background: "rgba(0,0,0,0.35)",
                            color: "#f0ede8",
                            border: `1px solid ${PRIMARY}38`,
                            borderRadius: 999,
                            padding: "6px 11px",
                            fontSize: 11,
                            fontFamily: "var(--font-mono)",
                            outline: "none"
                        }
                    }, void 0, false, {
                        fileName: "[project]/components/HudSocialModal.tsx",
                        lineNumber: 546,
                        columnNumber: 9
                    }, this),
                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("button", {
                        type: "button",
                        title: "Insert text without pressing Enter",
                        disabled: inputBusy || Boolean(frameError),
                        onClick: ()=>void insertQuickText(false),
                        style: {
                            ...pillBtn,
                            padding: "6px 9px"
                        },
                        children: "TYPE"
                    }, void 0, false, {
                        fileName: "[project]/components/HudSocialModal.tsx",
                        lineNumber: 567,
                        columnNumber: 9
                    }, this),
                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("button", {
                        type: "submit",
                        disabled: inputBusy || Boolean(frameError) || !quickText,
                        title: "Type & press Enter / Send",
                        style: {
                            ...pillBtn,
                            padding: "6px 10px",
                            background: `${PRIMARY}28`,
                            borderColor: PRIMARY,
                            color: "#ffffff"
                        },
                        children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$send$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__Send$3e$__["Send"], {
                            size: 11
                        }, void 0, false, {
                            fileName: "[project]/components/HudSocialModal.tsx",
                            lineNumber: 588,
                            columnNumber: 11
                        }, this)
                    }, void 0, false, {
                        fileName: "[project]/components/HudSocialModal.tsx",
                        lineNumber: 576,
                        columnNumber: 9
                    }, this)
                ]
            }, void 0, true, {
                fileName: "[project]/components/HudSocialModal.tsx",
                lineNumber: 535,
                columnNumber: 7
            }, this)
        ]
    }, void 0, true, {
        fileName: "[project]/components/HudSocialModal.tsx",
        lineNumber: 250,
        columnNumber: 5
    }, this);
}
_s(HudSocialModal, "4I4Vw59yxCF3uTnxI428U3FXrlg=", false, function() {
    return [
        __TURBOPACK__imported__module__$5b$project$5d2f$components$2f$JarvisBridge$2e$tsx__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useJarvis"]
    ];
});
_c = HudSocialModal;
var _c;
__turbopack_context__.k.register(_c, "HudSocialModal");
if (typeof globalThis.$RefreshHelpers$ === 'object' && globalThis.$RefreshHelpers !== null) {
    __turbopack_context__.k.registerExports(__turbopack_context__.m, globalThis.$RefreshHelpers$);
}
}),
"[project]/components/HudVideoModal.tsx [app-client] (ecmascript)", ((__turbopack_context__) => {
"use strict";

__turbopack_context__.s([
    "default",
    ()=>HudVideoModal
]);
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/next/dist/compiled/react/jsx-dev-runtime.js [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/next/dist/compiled/react/index.js [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$external$2d$link$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__ExternalLink$3e$__ = __turbopack_context__.i("[project]/node_modules/lucide-react/dist/esm/icons/external-link.js [app-client] (ecmascript) <export default as ExternalLink>");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$list$2d$music$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__ListMusic$3e$__ = __turbopack_context__.i("[project]/node_modules/lucide-react/dist/esm/icons/list-music.js [app-client] (ecmascript) <export default as ListMusic>");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$skip$2d$back$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__SkipBack$3e$__ = __turbopack_context__.i("[project]/node_modules/lucide-react/dist/esm/icons/skip-back.js [app-client] (ecmascript) <export default as SkipBack>");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$skip$2d$forward$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__SkipForward$3e$__ = __turbopack_context__.i("[project]/node_modules/lucide-react/dist/esm/icons/skip-forward.js [app-client] (ecmascript) <export default as SkipForward>");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$volume$2d$2$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__Volume2$3e$__ = __turbopack_context__.i("[project]/node_modules/lucide-react/dist/esm/icons/volume-2.js [app-client] (ecmascript) <export default as Volume2>");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$volume$2d$x$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__VolumeX$3e$__ = __turbopack_context__.i("[project]/node_modules/lucide-react/dist/esm/icons/volume-x.js [app-client] (ecmascript) <export default as VolumeX>");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$x$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__X$3e$__ = __turbopack_context__.i("[project]/node_modules/lucide-react/dist/esm/icons/x.js [app-client] (ecmascript) <export default as X>");
var __TURBOPACK__imported__module__$5b$project$5d2f$components$2f$JarvisBridge$2e$tsx__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/components/JarvisBridge.tsx [app-client] (ecmascript)");
;
var _s = __turbopack_context__.k.signature();
"use client";
;
;
;
function formatSec(sec) {
    if (!sec || sec <= 0) return "";
    const m = Math.floor(sec / 60);
    const s = Math.floor(sec % 60);
    return `${m}:${String(s).padStart(2, "0")}`;
}
function HudVideoModal() {
    _s();
    const { video, theme, activePersona, closeVideo, setVideoMuted, nextVideo, prevVideo, jumpVideo } = (0, __TURBOPACK__imported__module__$5b$project$5d2f$components$2f$JarvisBridge$2e$tsx__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useJarvis"])();
    const videoRef = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useRef"])(null);
    const audioRef = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useRef"])(null);
    const [queueOpen, setQueueOpen] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])(false);
    (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useEffect"])({
        "HudVideoModal.useEffect": ()=>{
            const v = videoRef.current;
            const a = audioRef.current;
            if (!v || !video) return;
            const hasSplitAudio = Boolean(video.audio_url && a);
            v.muted = hasSplitAudio ? true : Boolean(video.muted);
            if (a) {
                a.muted = Boolean(video.muted);
            }
            const syncPlay = {
                "HudVideoModal.useEffect.syncPlay": ()=>{
                    if (a && hasSplitAudio) {
                        if (Math.abs(a.currentTime - v.currentTime) > 0.28) {
                            a.currentTime = v.currentTime;
                        }
                        a.play().catch({
                            "HudVideoModal.useEffect.syncPlay": ()=>{}
                        }["HudVideoModal.useEffect.syncPlay"]);
                    }
                }
            }["HudVideoModal.useEffect.syncPlay"];
            const syncPause = {
                "HudVideoModal.useEffect.syncPause": ()=>{
                    if (a && hasSplitAudio) a.pause();
                }
            }["HudVideoModal.useEffect.syncPause"];
            const syncSeek = {
                "HudVideoModal.useEffect.syncSeek": ()=>{
                    if (a && hasSplitAudio) {
                        a.currentTime = v.currentTime;
                    }
                }
            }["HudVideoModal.useEffect.syncSeek"];
            v.addEventListener("play", syncPlay);
            v.addEventListener("playing", syncPlay);
            v.addEventListener("pause", syncPause);
            v.addEventListener("seeked", syncSeek);
            return ({
                "HudVideoModal.useEffect": ()=>{
                    v.removeEventListener("play", syncPlay);
                    v.removeEventListener("playing", syncPlay);
                    v.removeEventListener("pause", syncPause);
                    v.removeEventListener("seeked", syncSeek);
                }
            })["HudVideoModal.useEffect"];
        }
    }["HudVideoModal.useEffect"], [
        video
    ]);
    if (!video) return null;
    const isFemale = activePersona === "female";
    const primary = theme.primary;
    const secondary = theme.secondary;
    const platformLabel = (video.platform || "VIDEO").toUpperCase();
    const queue = Array.isArray(video.queue) ? video.queue : [];
    const queueTotal = video.queue_total || queue.length;
    const queueIndex = video.queue_index || 0;
    const hasQueue = queueTotal > 1;
    const reportEnded = ()=>{
        // This is the browser's real HTMLMediaElement ended event—not a duration
        // estimate. Retry the local handoff because a dropped completion event is
        // worse than a duplicate (the durable manager deduplicates by task state).
        const payload = JSON.stringify({
            action: "video_ended",
            video_id: video.id,
            webpage_url: video.webpage_url || "",
            playlist_url: video.playlist_url || "",
            queue_index: queueIndex,
            queue_total: queueTotal,
            terminal: !hasQueue || queueIndex >= queueTotal - 1
        });
        const send = async ()=>{
            for (const waitMs of [
                0,
                250,
                750
            ]){
                if (waitMs) await new Promise((resolve)=>setTimeout(resolve, waitMs));
                try {
                    const response = await fetch("/api/hud/action", {
                        method: "POST",
                        headers: {
                            "Content-Type": "application/json"
                        },
                        body: payload
                    });
                    if (response.ok) return;
                } catch  {}
            }
        };
        void send();
    };
    return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
        "data-testid": "hud-video-player",
        style: {
            position: "fixed",
            top: "50%",
            left: "50%",
            transform: "translate(-50%, -50%)",
            width: "min(780px, calc(100vw - 40px))",
            maxHeight: "calc(100vh - 120px)",
            zIndex: 85,
            display: "flex",
            flexDirection: "column",
            borderRadius: 20,
            background: isFemale ? "linear-gradient(165deg, rgba(18, 7, 24, 0.94), rgba(8, 3, 12, 0.96))" : "linear-gradient(165deg, rgba(4, 12, 22, 0.94), rgba(2, 6, 13, 0.96))",
            border: `1px solid rgba(${theme.orbGlowRgb}, 0.42)`,
            boxShadow: `0 28px 70px rgba(0, 0, 0, 0.78), 0 0 42px rgba(${theme.orbGlowRgb}, 0.16)`,
            backdropFilter: "blur(22px)",
            overflow: "hidden"
        },
        children: [
            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                style: {
                    display: "flex",
                    alignItems: "center",
                    gap: 8,
                    padding: "10px 14px",
                    borderBottom: "1px solid rgba(255,255,255,0.08)"
                },
                children: [
                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("span", {
                        style: {
                            padding: "3px 9px",
                            borderRadius: 999,
                            background: `rgba(${theme.orbGlowRgb}, 0.16)`,
                            border: `1px solid rgba(${theme.orbGlowRgb}, 0.45)`,
                            color: primary,
                            fontFamily: "var(--font-mono), monospace",
                            fontSize: 9.5,
                            letterSpacing: "0.14em",
                            flexShrink: 0
                        },
                        children: platformLabel
                    }, void 0, false, {
                        fileName: "[project]/components/HudVideoModal.tsx",
                        lineNumber: 150,
                        columnNumber: 9
                    }, this),
                    hasQueue && /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("span", {
                        "data-testid": "hud-video-mix-badge",
                        title: video.playlist_title || "Active Mix / Playlist",
                        style: {
                            padding: "3px 9px",
                            borderRadius: 999,
                            background: `rgba(${theme.orbGlow2Rgb}, 0.16)`,
                            border: `1px solid rgba(${theme.orbGlow2Rgb}, 0.45)`,
                            color: secondary,
                            fontFamily: "var(--font-mono), monospace",
                            fontSize: 9.5,
                            letterSpacing: "0.10em",
                            flexShrink: 0
                        },
                        children: [
                            "MIX · ",
                            queueIndex + 1,
                            "/",
                            queueTotal
                        ]
                    }, void 0, true, {
                        fileName: "[project]/components/HudVideoModal.tsx",
                        lineNumber: 167,
                        columnNumber: 11
                    }, this),
                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                        style: {
                            flex: 1,
                            minWidth: 0,
                            color: "#f2efe9",
                            fontSize: 12.5,
                            fontWeight: 500,
                            whiteSpace: "nowrap",
                            overflow: "hidden",
                            textOverflow: "ellipsis"
                        },
                        title: video.title,
                        children: video.title
                    }, void 0, false, {
                        fileName: "[project]/components/HudVideoModal.tsx",
                        lineNumber: 186,
                        columnNumber: 9
                    }, this),
                    hasQueue && /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["Fragment"], {
                        children: [
                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("button", {
                                type: "button",
                                onClick: ()=>prevVideo(),
                                title: "Previous track in Mix",
                                style: {
                                    width: 28,
                                    height: 28,
                                    borderRadius: "50%",
                                    border: "1px solid rgba(255,255,255,0.18)",
                                    background: "rgba(255,255,255,0.05)",
                                    color: "#e2e8f0",
                                    display: "flex",
                                    alignItems: "center",
                                    justifyContent: "center",
                                    cursor: "pointer",
                                    padding: 0,
                                    flexShrink: 0
                                },
                                children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$skip$2d$back$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__SkipBack$3e$__["SkipBack"], {
                                    size: 12
                                }, void 0, false, {
                                    fileName: "[project]/components/HudVideoModal.tsx",
                                    lineNumber: 223,
                                    columnNumber: 15
                                }, this)
                            }, void 0, false, {
                                fileName: "[project]/components/HudVideoModal.tsx",
                                lineNumber: 204,
                                columnNumber: 13
                            }, this),
                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("button", {
                                type: "button",
                                onClick: ()=>nextVideo(),
                                title: "Next track in Mix",
                                style: {
                                    width: 28,
                                    height: 28,
                                    borderRadius: "50%",
                                    border: "1px solid rgba(255,255,255,0.18)",
                                    background: "rgba(255,255,255,0.05)",
                                    color: "#e2e8f0",
                                    display: "flex",
                                    alignItems: "center",
                                    justifyContent: "center",
                                    cursor: "pointer",
                                    padding: 0,
                                    flexShrink: 0
                                },
                                children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$skip$2d$forward$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__SkipForward$3e$__["SkipForward"], {
                                    size: 12
                                }, void 0, false, {
                                    fileName: "[project]/components/HudVideoModal.tsx",
                                    lineNumber: 245,
                                    columnNumber: 15
                                }, this)
                            }, void 0, false, {
                                fileName: "[project]/components/HudVideoModal.tsx",
                                lineNumber: 226,
                                columnNumber: 13
                            }, this),
                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("button", {
                                type: "button",
                                onClick: ()=>setQueueOpen((prev)=>!prev),
                                title: "Toggle Mix tracklist",
                                style: {
                                    height: 28,
                                    padding: "0 9px",
                                    borderRadius: 999,
                                    border: `1px solid ${queueOpen ? primary : "rgba(255,255,255,0.18)"}`,
                                    background: queueOpen ? `rgba(${theme.orbGlowRgb}, 0.18)` : "rgba(255,255,255,0.05)",
                                    color: queueOpen ? primary : "#dbe6f2",
                                    fontFamily: "var(--font-mono), monospace",
                                    fontSize: 9.5,
                                    letterSpacing: "0.08em",
                                    display: "inline-flex",
                                    alignItems: "center",
                                    gap: 4,
                                    cursor: "pointer",
                                    flexShrink: 0
                                },
                                children: [
                                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$list$2d$music$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__ListMusic$3e$__["ListMusic"], {
                                        size: 12
                                    }, void 0, false, {
                                        fileName: "[project]/components/HudVideoModal.tsx",
                                        lineNumber: 271,
                                        columnNumber: 15
                                    }, this),
                                    "QUEUE"
                                ]
                            }, void 0, true, {
                                fileName: "[project]/components/HudVideoModal.tsx",
                                lineNumber: 248,
                                columnNumber: 13
                            }, this)
                        ]
                    }, void 0, true, {
                        fileName: "[project]/components/HudVideoModal.tsx",
                        lineNumber: 203,
                        columnNumber: 11
                    }, this),
                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("button", {
                        type: "button",
                        onClick: ()=>setVideoMuted(!video.muted),
                        title: video.muted ? "Turn video sound on" : "Mute video sound",
                        style: {
                            height: 28,
                            padding: "0 10px",
                            borderRadius: 999,
                            border: `1px solid ${video.muted ? `${secondary}66` : `${primary}66`}`,
                            background: video.muted ? `rgba(${theme.orbGlow2Rgb}, 0.14)` : `rgba(${theme.orbGlowRgb}, 0.16)`,
                            color: video.muted ? secondary : primary,
                            fontFamily: "var(--font-mono), monospace",
                            fontSize: 9.5,
                            letterSpacing: "0.10em",
                            display: "inline-flex",
                            alignItems: "center",
                            gap: 5,
                            cursor: "pointer",
                            flexShrink: 0
                        },
                        children: [
                            video.muted ? /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$volume$2d$x$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__VolumeX$3e$__["VolumeX"], {
                                size: 12
                            }, void 0, false, {
                                fileName: "[project]/components/HudVideoModal.tsx",
                                lineNumber: 300,
                                columnNumber: 26
                            }, this) : /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$volume$2d$2$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__Volume2$3e$__["Volume2"], {
                                size: 12
                            }, void 0, false, {
                                fileName: "[project]/components/HudVideoModal.tsx",
                                lineNumber: 300,
                                columnNumber: 50
                            }, this),
                            video.muted ? "MUTED" : "SOUND ON"
                        ]
                    }, void 0, true, {
                        fileName: "[project]/components/HudVideoModal.tsx",
                        lineNumber: 277,
                        columnNumber: 9
                    }, this),
                    video.webpage_url && /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("a", {
                        href: video.webpage_url,
                        target: "_blank",
                        rel: "noopener noreferrer",
                        title: "Open original page",
                        style: {
                            height: 28,
                            padding: "0 9px",
                            borderRadius: 999,
                            border: "1px solid rgba(255,255,255,0.16)",
                            background: "rgba(255,255,255,0.04)",
                            color: "#dbe6f2",
                            fontFamily: "var(--font-mono), monospace",
                            fontSize: 9.5,
                            display: "inline-flex",
                            alignItems: "center",
                            gap: 4,
                            textDecoration: "none",
                            flexShrink: 0
                        },
                        children: [
                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$external$2d$link$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__ExternalLink$3e$__["ExternalLink"], {
                                size: 11
                            }, void 0, false, {
                                fileName: "[project]/components/HudVideoModal.tsx",
                                lineNumber: 326,
                                columnNumber: 13
                            }, this),
                            "SOURCE"
                        ]
                    }, void 0, true, {
                        fileName: "[project]/components/HudVideoModal.tsx",
                        lineNumber: 305,
                        columnNumber: 11
                    }, this),
                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("button", {
                        type: "button",
                        onClick: ()=>closeVideo(),
                        title: "Close video",
                        style: {
                            width: 28,
                            height: 28,
                            borderRadius: "50%",
                            border: "1px solid rgba(255,255,255,0.16)",
                            background: "rgba(255,255,255,0.05)",
                            color: "#e2e8f0",
                            display: "flex",
                            alignItems: "center",
                            justifyContent: "center",
                            cursor: "pointer",
                            padding: 0,
                            flexShrink: 0
                        },
                        children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$x$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__X$3e$__["X"], {
                            size: 13
                        }, void 0, false, {
                            fileName: "[project]/components/HudVideoModal.tsx",
                            lineNumber: 350,
                            columnNumber: 11
                        }, this)
                    }, void 0, false, {
                        fileName: "[project]/components/HudVideoModal.tsx",
                        lineNumber: 331,
                        columnNumber: 9
                    }, this)
                ]
            }, void 0, true, {
                fileName: "[project]/components/HudVideoModal.tsx",
                lineNumber: 141,
                columnNumber: 7
            }, this),
            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                style: {
                    position: "relative",
                    background: "#000",
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    maxHeight: queueOpen && hasQueue ? "calc(100vh - 340px)" : "calc(100vh - 190px)"
                },
                children: [
                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("video", {
                        ref: videoRef,
                        src: video.video_url,
                        autoPlay: true,
                        playsInline: true,
                        controls: true,
                        muted: Boolean(video.audio_url) ? true : video.muted,
                        onEnded: ()=>{
                            reportEnded();
                            if (hasQueue) {
                                nextVideo();
                            }
                        },
                        style: {
                            width: "100%",
                            maxHeight: queueOpen && hasQueue ? "calc(100vh - 340px)" : "calc(100vh - 190px)",
                            objectFit: "contain",
                            display: "block"
                        }
                    }, video.id, false, {
                        fileName: "[project]/components/HudVideoModal.tsx",
                        lineNumber: 365,
                        columnNumber: 9
                    }, this),
                    video.audio_url && /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("audio", {
                        ref: audioRef,
                        src: video.audio_url,
                        autoPlay: true,
                        muted: video.muted,
                        style: {
                            display: "none"
                        }
                    }, `${video.id}-aud`, false, {
                        fileName: "[project]/components/HudVideoModal.tsx",
                        lineNumber: 387,
                        columnNumber: 11
                    }, this)
                ]
            }, void 0, true, {
                fileName: "[project]/components/HudVideoModal.tsx",
                lineNumber: 355,
                columnNumber: 7
            }, this),
            hasQueue && queueOpen && /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                "data-testid": "hud-video-queue-drawer",
                style: {
                    maxHeight: 165,
                    overflowY: "auto",
                    borderTop: "1px solid rgba(255,255,255,0.08)",
                    background: "rgba(2, 6, 14, 0.86)",
                    padding: "6px 10px"
                },
                children: [
                    video.playlist_title && /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                        style: {
                            padding: "4px 6px 6px",
                            color: secondary,
                            fontFamily: "var(--font-mono), monospace",
                            fontSize: 9.5,
                            letterSpacing: "0.12em",
                            textTransform: "uppercase"
                        },
                        children: video.playlist_title
                    }, void 0, false, {
                        fileName: "[project]/components/HudVideoModal.tsx",
                        lineNumber: 411,
                        columnNumber: 13
                    }, this),
                    queue.map((item, idx)=>{
                        const active = idx === queueIndex;
                        return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("button", {
                            type: "button",
                            onClick: ()=>jumpVideo(idx),
                            style: {
                                width: "100%",
                                display: "flex",
                                alignItems: "center",
                                gap: 10,
                                padding: "6px 8px",
                                borderRadius: 8,
                                border: active ? `1px solid rgba(${theme.orbGlowRgb}, 0.45)` : "1px solid transparent",
                                background: active ? `rgba(${theme.orbGlowRgb}, 0.14)` : "transparent",
                                color: active ? primary : "#dbe6f2",
                                fontSize: 11.5,
                                textAlign: "left",
                                cursor: "pointer"
                            },
                            children: [
                                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("span", {
                                    style: {
                                        width: 24,
                                        fontFamily: "var(--font-mono), monospace",
                                        fontSize: 10,
                                        opacity: 0.72,
                                        flexShrink: 0
                                    },
                                    children: String(idx + 1).padStart(2, "0")
                                }, void 0, false, {
                                    fileName: "[project]/components/HudVideoModal.tsx",
                                    lineNumber: 450,
                                    columnNumber: 17
                                }, this),
                                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("span", {
                                    style: {
                                        flex: 1,
                                        minWidth: 0,
                                        whiteSpace: "nowrap",
                                        overflow: "hidden",
                                        textOverflow: "ellipsis"
                                    },
                                    children: [
                                        item.title,
                                        item.uploader ? /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("span", {
                                            style: {
                                                opacity: 0.62,
                                                marginLeft: 6
                                            },
                                            children: [
                                                "· ",
                                                item.uploader
                                            ]
                                        }, void 0, true, {
                                            fileName: "[project]/components/HudVideoModal.tsx",
                                            lineNumber: 472,
                                            columnNumber: 21
                                        }, this) : null
                                    ]
                                }, void 0, true, {
                                    fileName: "[project]/components/HudVideoModal.tsx",
                                    lineNumber: 461,
                                    columnNumber: 17
                                }, this),
                                item.duration ? /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("span", {
                                    style: {
                                        fontFamily: "var(--font-mono), monospace",
                                        fontSize: 10,
                                        opacity: 0.65,
                                        flexShrink: 0
                                    },
                                    children: formatSec(item.duration)
                                }, void 0, false, {
                                    fileName: "[project]/components/HudVideoModal.tsx",
                                    lineNumber: 478,
                                    columnNumber: 19
                                }, this) : null
                            ]
                        }, `${item.id || idx}-${idx}`, true, {
                            fileName: "[project]/components/HudVideoModal.tsx",
                            lineNumber: 427,
                            columnNumber: 15
                        }, this);
                    })
                ]
            }, void 0, true, {
                fileName: "[project]/components/HudVideoModal.tsx",
                lineNumber: 400,
                columnNumber: 9
            }, this)
        ]
    }, void 0, true, {
        fileName: "[project]/components/HudVideoModal.tsx",
        lineNumber: 118,
        columnNumber: 5
    }, this);
}
_s(HudVideoModal, "avXYeGFWZihdZDuxfrHDbpLKHDs=", false, function() {
    return [
        __TURBOPACK__imported__module__$5b$project$5d2f$components$2f$JarvisBridge$2e$tsx__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useJarvis"]
    ];
});
_c = HudVideoModal;
var _c;
__turbopack_context__.k.register(_c, "HudVideoModal");
if (typeof globalThis.$RefreshHelpers$ === 'object' && globalThis.$RefreshHelpers !== null) {
    __turbopack_context__.k.registerExports(__turbopack_context__.m, globalThis.$RefreshHelpers$);
}
}),
"[project]/components/JarvisBridge.tsx [app-client] (ecmascript)", ((__turbopack_context__) => {
"use strict";

__turbopack_context__.s([
    "JarvisProvider",
    ()=>JarvisProvider,
    "useJarvis",
    ()=>useJarvis,
    "useJarvisAudioLevel",
    ()=>useJarvisAudioLevel
]);
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/next/dist/compiled/react/jsx-dev-runtime.js [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/next/dist/compiled/react/index.js [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$components$2f$theme$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/components/theme.ts [app-client] (ecmascript)");
;
var _s = __turbopack_context__.k.signature(), _s1 = __turbopack_context__.k.signature(), _s2 = __turbopack_context__.k.signature();
"use client";
;
;
function hexToRgbTuple(hex) {
    const m = /^#([0-9a-fA-F]{6})$/.exec((hex || "").trim());
    if (!m) return null;
    const v = parseInt(m[1], 16);
    return `${v >> 16 & 255}, ${v >> 8 & 255}, ${v & 255}`;
}
const JarvisContext = /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["createContext"])(null);
const JarvisAudioLevelContext = /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["createContext"])(0);
function useJarvisAudioLevel() {
    _s();
    return (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useContext"])(JarvisAudioLevelContext);
}
_s(useJarvisAudioLevel, "gDsCjeeItUuvgOWf1v4qoK9RF6k=");
function mapRawToOrb(raw, muted, paused) {
    const s = (raw || "").toUpperCase();
    if (muted || paused || s === "MUTED" || s === "PAUSED" || s === "SLEEPING") {
        return "idle";
    }
    if (s === "SPEAKING") return "speaking";
    if (s === "THINKING" || s === "PROCESSING") return "thinking";
    if (s === "LISTENING") return "listening";
    return "idle";
}
function classifyLog(line) {
    const trimmed = (line || "").trim();
    if (/^(you|user)\s*:/i.test(trimmed)) {
        return {
            role: "user",
            clean: trimmed.replace(/^(you|user)\s*:\s*/i, "")
        };
    }
    if (/^(sys|net|err)\s*:/i.test(trimmed)) {
        return {
            role: "sys",
            clean: trimmed
        };
    }
    if (/^(tool|action)\s*:/i.test(trimmed)) {
        return {
            role: "tool",
            clean: trimmed
        };
    }
    if (/^[a-z0-9_ -]{2,18}:\s/i.test(trimmed)) {
        return {
            role: "jarvis",
            clean: trimmed.replace(/^[a-z0-9_ -]{2,18}:\s*/i, "")
        };
    }
    return {
        role: "sys",
        clean: trimmed
    };
}
function JarvisProvider({ children }) {
    _s1();
    const [connected, setConnected] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])(false);
    const [ready, setReady] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])(true);
    const [integrationsReady, setIntegrationsReady] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])(true);
    const [integrations, setIntegrations] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])({
        services: {},
        connected_count: 0,
        connected_services: [],
        onboarding_done: true
    });
    const [privacy, setPrivacyState] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])({
        personalization_enabled: true,
        adaptive_learning_enabled: true,
        timeline_persistence_enabled: true
    });
    const [brainCounts, setBrainCounts] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])({
        memories: 0,
        files: 0,
        outputs: 0,
        timeline: 0
    });
    const [persona, setPersona] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])("male");
    const [previewPersona, setPreviewPersona] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])(null);
    const [personaChosen, setPersonaChosen] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])(true);
    const [assistantName, setAssistantName] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])("JARVIS");
    const [rawState, setRawState] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])("STANDBY");
    const [demoState, setDemoState] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])("idle");
    const [audioLevel, setAudioLevel] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])(0);
    const [muted, setMuted] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])(false);
    const [paused, setPaused] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])(false);
    const [offline, setOffline] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])(false);
    const [offlineReason, setOfflineReason] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])("");
    const [voice, setVoiceState] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])("Charon");
    const [voices, setVoices] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])([
        "Charon",
        "Puck",
        "Kore",
        "Fenrir",
        "Aoede"
    ]);
    const [maleVoices, setMaleVoices] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])([
        "Charon",
        "Fenrir",
        "Puck"
    ]);
    const [femaleVoices, setFemaleVoices] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])([
        "Aoede",
        "Kore"
    ]);
    const [bargeEnabled, setBargeEnabled] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])(true);
    const [gracePeriod, setGracePeriod] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])(8);
    const [inputs, setInputs] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])([
        "System default"
    ]);
    const [outputs, setOutputs] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])([
        "System default"
    ]);
    const [currentInput, setCurrentInput] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])("");
    const [currentOutput, setCurrentOutput] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])("");
    const [logs, setLogs] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])([]);
    const [lastSubtitle, setLastSubtitle] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])(null);
    const [trace, setTrace] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])(null);
    const [confirm, setConfirm] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])(null);
    const [content, setContent] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])(null);
    const [video, setVideo] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])(null);
    const [socialHud, setSocialHud] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])(null);
    const [consoleOpen, setConsoleOpen] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])(false);
    const [settingsOpen, setSettingsOpen] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])(false);
    const [setupOpen, setSetupOpen] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])(false);
    const [integrationsModalOpen, setIntegrationsModalOpen] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])(false);
    const [brainModalOpen, setBrainModalOpen] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])(false);
    const [studioModalOpen, setStudioModalOpen] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])(false);
    const [automationsModalOpen, setAutomationsModalOpen] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])(false);
    const [devModalOpen, setDevModalOpen] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])(false);
    const [securityModalOpen, setSecurityModalOpen] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])(false);
    const [activityOpen, setActivityOpen] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])(false);
    const [personaModalOpen, setPersonaModalOpen] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])(false);
    const [backgroundMode, setBackgroundMode] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])(false);
    const [workers, setWorkers] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])([]);
    const [terminalSessions, setTerminalSessions] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])([]);
    const [activeCompanion, setActiveCompanion] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])(null);
    const [themeCustom, setThemeCustom] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])({
        preset: "default",
        custom_primary: "",
        custom_secondary: "",
        effective_primary: "",
        effective_secondary: ""
    });
    const [aiProviders, setAiProviders] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])({
        provider: "auto",
        activeEngine: "gemini",
        hasGeminiKey: false,
        hasOpenaiKey: false,
        geminiKeyMasked: "",
        openaiKeyMasked: "",
        openaiModel: "gpt-4o",
        openaiRealtimeModel: "gpt-4o-realtime-preview",
        openaiBaseUrl: "https://api.openai.com/v1"
    });
    const wsRef = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useRef"])(null);
    const seqRef = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useRef"])(1);
    const logIdRef = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useRef"])(1);
    const demoTimerRef = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useRef"])(null);
    const subtitleTimerRef = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useRef"])(null);
    const targetLevelRef = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useRef"])(0);
    const activePersona = previewPersona ?? persona;
    const theme = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useMemo"])({
        "JarvisProvider.useMemo[theme]": ()=>{
            const base = __TURBOPACK__imported__module__$5b$project$5d2f$components$2f$theme$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["PERSONA_THEMES"][activePersona];
            const pri = themeCustom.effective_primary || "";
            const sec = themeCustom.effective_secondary || "";
            if (!pri && !sec) return base;
            const priRgb = pri ? hexToRgbTuple(pri) : null;
            const secRgb = sec ? hexToRgbTuple(sec) : null;
            return {
                ...base,
                ...pri ? {
                    primary: pri,
                    primaryBright: pri,
                    spokeHot: pri,
                    primarySoftBg: priRgb ? `rgba(${priRgb}, 0.09)` : base.primarySoftBg,
                    primaryBorder: priRgb ? `rgba(${priRgb}, 0.30)` : base.primaryBorder,
                    orbGlowRgb: priRgb || base.orbGlowRgb
                } : {},
                ...sec ? {
                    secondary: sec,
                    secondaryBright: sec,
                    secondarySoftBg: secRgb ? `rgba(${secRgb}, 0.10)` : base.secondarySoftBg
                } : {}
            };
        }
    }["JarvisProvider.useMemo[theme]"], [
        activePersona,
        themeCustom
    ]);
    const pushLogLine = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useCallback"])({
        "JarvisProvider.useCallback[pushLogLine]": (line, ts)=>{
            if (!line || !line.trim()) return;
            const { role, clean } = classifyLog(line);
            const stamp = ts || new Date().toLocaleTimeString("en-GB", {
                hour: "2-digit",
                minute: "2-digit",
                second: "2-digit"
            });
            const id = logIdRef.current++;
            setLogs({
                "JarvisProvider.useCallback[pushLogLine]": (prev)=>{
                    const next = [
                        ...prev,
                        {
                            id,
                            line: line.trim(),
                            role,
                            ts: stamp
                        }
                    ];
                    return next.length > 140 ? next.slice(next.length - 140) : next;
                }
            }["JarvisProvider.useCallback[pushLogLine]"]);
            if (role === "jarvis" || role === "user") {
                setLastSubtitle({
                    role,
                    text: clean
                });
                if (subtitleTimerRef.current) clearTimeout(subtitleTimerRef.current);
                subtitleTimerRef.current = setTimeout({
                    "JarvisProvider.useCallback[pushLogLine]": ()=>{
                        setLastSubtitle(null);
                    }
                }["JarvisProvider.useCallback[pushLogLine]"], 9000);
            }
        }
    }["JarvisProvider.useCallback[pushLogLine]"], []);
    const fireLocalTrace = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useCallback"])({
        "JarvisProvider.useCallback[fireLocalTrace]": (nodes)=>{
            if (!nodes || nodes.length === 0) return;
            const n = seqRef.current++;
            setTrace({
                n,
                trace: nodes.map({
                    "JarvisProvider.useCallback[fireLocalTrace]": (helper)=>({
                            helper
                        })
                }["JarvisProvider.useCallback[fireLocalTrace]"])
            });
        }
    }["JarvisProvider.useCallback[fireLocalTrace]"], []);
    const sendAction = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useCallback"])({
        "JarvisProvider.useCallback[sendAction]": (payload)=>{
            const ws = wsRef.current;
            if (ws && ws.readyState === WebSocket.OPEN) {
                ws.send(JSON.stringify(payload));
                return true;
            }
            fetch("/api/hud/action", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify(payload)
            }).catch({
                "JarvisProvider.useCallback[sendAction]": ()=>{}
            }["JarvisProvider.useCallback[sendAction]"]);
            return false;
        }
    }["JarvisProvider.useCallback[sendAction]"], []);
    // Smooth audio envelope decay isolated in JarvisAudioLevelContext; skips state
    // updates completely when silent so 0 React re-renders occur at rest.
    (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useEffect"])({
        "JarvisProvider.useEffect": ()=>{
            const id = setInterval({
                "JarvisProvider.useEffect.id": ()=>{
                    const tgt = targetLevelRef.current;
                    targetLevelRef.current = tgt < 0.004 ? 0 : tgt * 0.84;
                    setAudioLevel({
                        "JarvisProvider.useEffect.id": (cur)=>{
                            if (cur === 0 && tgt === 0) return 0;
                            const next = cur + (tgt - cur) * 0.45;
                            const clamped = next < 0.005 ? 0 : Math.min(1, next);
                            return Math.abs(clamped - cur) < 0.004 ? cur : clamped;
                        }
                    }["JarvisProvider.useEffect.id"]);
                }
            }["JarvisProvider.useEffect.id"], 40);
            return ({
                "JarvisProvider.useEffect": ()=>clearInterval(id)
            })["JarvisProvider.useEffect"];
        }
    }["JarvisProvider.useEffect"], []);
    const applyBootstrap = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useCallback"])({
        "JarvisProvider.useCallback[applyBootstrap]": (d)=>{
            if (!d || typeof d !== "object") return;
            const isReady = d.ready !== false;
            const isIntegrationsReady = d.integrations_ready !== false;
            const isPersonaChosen = d.persona_chosen !== false;
            setReady(isReady);
            setIntegrationsReady(isIntegrationsReady);
            setPersonaChosen(isPersonaChosen);
            if (d.integrations && typeof d.integrations === "object") {
                setIntegrations(d.integrations);
            }
            if (d.privacy && typeof d.privacy === "object") {
                setPrivacyState(d.privacy);
            }
            if (d.brain_counts && typeof d.brain_counts === "object") {
                setBrainCounts(d.brain_counts);
            }
            if (Array.isArray(d.workers)) {
                setWorkers(d.workers);
            }
            if (d.active_companion && typeof d.active_companion === "object") {
                setActiveCompanion(d.active_companion);
            }
            if (d.theme_custom && typeof d.theme_custom === "object") {
                setThemeCustom(d.theme_custom);
            }
            setAiProviders({
                "JarvisProvider.useCallback[applyBootstrap]": (prev)=>({
                        provider: typeof d.provider === "string" ? d.provider : prev.provider,
                        activeEngine: typeof d.active_engine === "string" ? d.active_engine : prev.activeEngine,
                        hasGeminiKey: typeof d.has_gemini_key === "boolean" ? d.has_gemini_key : prev.hasGeminiKey,
                        hasOpenaiKey: typeof d.has_openai_key === "boolean" ? d.has_openai_key : prev.hasOpenaiKey,
                        geminiKeyMasked: typeof d.gemini_key_masked === "string" ? d.gemini_key_masked : prev.geminiKeyMasked,
                        openaiKeyMasked: typeof d.openai_key_masked === "string" ? d.openai_key_masked : prev.openaiKeyMasked,
                        openaiModel: typeof d.openai_model === "string" ? d.openai_model : prev.openaiModel,
                        openaiRealtimeModel: typeof d.openai_realtime_model === "string" ? d.openai_realtime_model : prev.openaiRealtimeModel,
                        openaiBaseUrl: typeof d.openai_base_url === "string" ? d.openai_base_url : prev.openaiBaseUrl
                    })
            }["JarvisProvider.useCallback[applyBootstrap]"]);
            if (d.persona === "female" || d.persona === "male") {
                setPersona(d.persona);
            }
            if (!isReady) {
                setSetupOpen(true);
                setIntegrationsModalOpen(false);
                setPersonaModalOpen(false);
            } else if (!isIntegrationsReady) {
                setSetupOpen(false);
                setIntegrationsModalOpen(true);
                setPersonaModalOpen(false);
            } else if (!isPersonaChosen) {
                setSetupOpen(false);
                setIntegrationsModalOpen(false);
                setPersonaModalOpen(true);
            }
            if (typeof d.assistant_name === "string" && d.assistant_name) {
                setAssistantName(d.assistant_name);
            }
            if (typeof d.raw_state === "string") setRawState(d.raw_state);
            if (typeof d.muted === "boolean") setMuted(d.muted);
            if (typeof d.paused === "boolean") setPaused(d.paused);
            if (typeof d.offline === "boolean") setOffline(d.offline);
            if (typeof d.offline_reason === "string") setOfflineReason(d.offline_reason);
            if (typeof d.voice === "string") setVoiceState(d.voice);
            if (Array.isArray(d.voices) && d.voices.length > 0) {
                setVoices(d.voices);
            }
            if (Array.isArray(d.male_voices) && d.male_voices.length > 0) {
                setMaleVoices(d.male_voices);
            }
            if (Array.isArray(d.female_voices) && d.female_voices.length > 0) {
                setFemaleVoices(d.female_voices);
            }
            if (typeof d.barge_enabled === "boolean") setBargeEnabled(d.barge_enabled);
            if (typeof d.grace_period === "number") setGracePeriod(d.grace_period);
            if (Array.isArray(d.inputs) && d.inputs.length > 0) {
                setInputs(d.inputs);
            }
            if (Array.isArray(d.outputs) && d.outputs.length > 0) {
                setOutputs(d.outputs);
            }
            if (typeof d.current_input === "string") setCurrentInput(d.current_input);
            if (typeof d.current_output === "string") setCurrentOutput(d.current_output);
            if (Array.isArray(d.logs)) {
                const mapped = d.logs.map({
                    "JarvisProvider.useCallback[applyBootstrap].mapped": (ln)=>{
                        const { role } = classifyLog(String(ln));
                        return {
                            id: logIdRef.current++,
                            line: String(ln),
                            role,
                            ts: ""
                        };
                    }
                }["JarvisProvider.useCallback[applyBootstrap].mapped"]);
                setLogs(mapped.slice(-120));
            }
            if (d.confirm && typeof d.confirm === "object") {
                setConfirm(d.confirm);
            } else {
                setConfirm(null);
            }
            if (d.content && typeof d.content === "object") {
                setContent(d.content);
            }
            if (d.video && typeof d.video === "object") {
                setVideo(d.video);
            } else if (d.video === null) {
                setVideo(null);
            }
            if (d.social_hud && typeof d.social_hud === "object") {
                setSocialHud(d.social_hud);
            } else if (d.social_hud === null) {
                setSocialHud(null);
            }
        }
    }["JarvisProvider.useCallback[applyBootstrap]"], []);
    // Connect WebSocket `/ws/hud` with automatic reconnect
    (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useEffect"])({
        "JarvisProvider.useEffect": ()=>{
            let alive = true;
            let retryTimer = null;
            fetch("/api/hud/bootstrap").then({
                "JarvisProvider.useEffect": (r)=>r.ok ? r.json() : null
            }["JarvisProvider.useEffect"]).then({
                "JarvisProvider.useEffect": (d)=>{
                    if (alive && d) {
                        setConnected(true);
                        applyBootstrap(d);
                    }
                }
            }["JarvisProvider.useEffect"]).catch({
                "JarvisProvider.useEffect": ()=>{}
            }["JarvisProvider.useEffect"]);
            const connectWs = {
                "JarvisProvider.useEffect.connectWs": ()=>{
                    if (!alive || ("TURBOPACK compile-time value", "object") === "undefined") return;
                    const proto = window.location.protocol === "https:" ? "wss:" : "ws:";
                    const url = `${proto}//${window.location.host}/ws/hud`;
                    let ws;
                    try {
                        ws = new WebSocket(url);
                    } catch  {
                        retryTimer = setTimeout(connectWs, 2500);
                        return;
                    }
                    wsRef.current = ws;
                    ws.onopen = ({
                        "JarvisProvider.useEffect.connectWs": ()=>{
                            if (!alive) return;
                            setConnected(true);
                        }
                    })["JarvisProvider.useEffect.connectWs"];
                    ws.onmessage = ({
                        "JarvisProvider.useEffect.connectWs": (ev)=>{
                            if (!alive) return;
                            try {
                                const msg = JSON.parse(ev.data);
                                switch(msg.type){
                                    case "integrations":
                                        if (msg.integrations) setIntegrations(msg.integrations);
                                        break;
                                    case "bootstrap":
                                        applyBootstrap(msg);
                                        break;
                                    case "state":
                                        if (typeof msg.raw_state === "string") setRawState(msg.raw_state);
                                        if (typeof msg.muted === "boolean") setMuted(msg.muted);
                                        if (typeof msg.paused === "boolean") setPaused(msg.paused);
                                        if (typeof msg.offline === "boolean") setOffline(msg.offline);
                                        if (typeof msg.offline_reason === "string") {
                                            setOfflineReason(msg.offline_reason);
                                        }
                                        break;
                                    case "level":
                                        targetLevelRef.current = Math.max(0, Math.min(1, Number(msg.level) || 0));
                                        break;
                                    case "log":
                                        pushLogLine(String(msg.line || ""), msg.ts);
                                        break;
                                    case "trace":
                                        {
                                            const nodes = Array.isArray(msg.nodes) ? msg.nodes : [];
                                            if (nodes.length > 0) {
                                                const n = seqRef.current++;
                                                setTrace({
                                                    n,
                                                    tool: msg.tool,
                                                    trace: nodes.map({
                                                        "JarvisProvider.useEffect.connectWs": (helper)=>({
                                                                helper
                                                            })
                                                    }["JarvisProvider.useEffect.connectWs"])
                                                });
                                            }
                                            break;
                                        }
                                    case "confirm":
                                        setConfirm(msg.confirm || null);
                                        break;
                                    case "content":
                                        setContent(msg.content || null);
                                        break;
                                    case "video":
                                        setVideo(msg.video || null);
                                        break;
                                    case "social_hud":
                                        setSocialHud(msg.social_hud || null);
                                        break;
                                    case "activity":
                                        if (Array.isArray(msg.workers)) {
                                            setWorkers(msg.workers);
                                        }
                                        break;
                                    case "terminal":
                                        if (msg.session && typeof msg.session === "object") {
                                            const incoming = msg.session;
                                            setTerminalSessions({
                                                "JarvisProvider.useEffect.connectWs": (prev)=>{
                                                    const rest = prev.filter({
                                                        "JarvisProvider.useEffect.connectWs.rest": (x)=>x.id !== incoming.id
                                                    }["JarvisProvider.useEffect.connectWs.rest"]);
                                                    return [
                                                        incoming,
                                                        ...rest
                                                    ].slice(0, 20);
                                                }
                                            }["JarvisProvider.useEffect.connectWs"]);
                                        }
                                        break;
                                    case "reconfig":
                                        setReady(false);
                                        setSetupOpen(true);
                                        break;
                                    case "background_mode":
                                        if (typeof msg.active === "boolean") {
                                            setBackgroundMode(msg.active);
                                        }
                                        break;
                                    case "config":
                                        applyBootstrap(msg);
                                        break;
                                    default:
                                        break;
                                }
                            } catch  {
                            // ignore malformed packets
                            }
                        }
                    })["JarvisProvider.useEffect.connectWs"];
                    ws.onclose = ({
                        "JarvisProvider.useEffect.connectWs": ()=>{
                            if (!alive) return;
                            wsRef.current = null;
                            setConnected(false);
                            retryTimer = setTimeout(connectWs, 1800);
                        }
                    })["JarvisProvider.useEffect.connectWs"];
                    ws.onerror = ({
                        "JarvisProvider.useEffect.connectWs": ()=>{
                            try {
                                ws.close();
                            } catch  {}
                        }
                    })["JarvisProvider.useEffect.connectWs"];
                }
            }["JarvisProvider.useEffect.connectWs"];
            connectWs();
            return ({
                "JarvisProvider.useEffect": ()=>{
                    alive = false;
                    if (retryTimer) clearTimeout(retryTimer);
                    if (demoTimerRef.current) clearTimeout(demoTimerRef.current);
                    if (subtitleTimerRef.current) clearTimeout(subtitleTimerRef.current);
                    try {
                        wsRef.current?.close();
                    } catch  {}
                }
            })["JarvisProvider.useEffect"];
        }
    }["JarvisProvider.useEffect"], [
        applyBootstrap,
        pushLogLine
    ]);
    const orbState = connected ? mapRawToOrb(rawState, muted, paused) : demoState;
    const choosePersona = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useCallback"])({
        "JarvisProvider.useCallback[choosePersona]": async (p, voiceName)=>{
            const normalized = p === "female" ? "female" : "male";
            setPersona(normalized);
            setPreviewPersona(null);
            setPersonaChosen(true);
            setPersonaModalOpen(false);
            if (voiceName) {
                setVoiceState(voiceName);
            } else if (normalized === "female" && !femaleVoices.includes(voice)) {
                setVoiceState(__TURBOPACK__imported__module__$5b$project$5d2f$components$2f$theme$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["PERSONA_THEMES"].female.defaultVoice);
            } else if (normalized === "male" && !maleVoices.includes(voice)) {
                setVoiceState(__TURBOPACK__imported__module__$5b$project$5d2f$components$2f$theme$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["PERSONA_THEMES"].male.defaultVoice);
            }
            fireLocalTrace([
                "chief_of_staff",
                "design"
            ]);
            try {
                const res = await fetch("/api/hud/action", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify({
                        action: "set_persona",
                        persona: normalized,
                        ...voiceName ? {
                            voice: voiceName
                        } : {}
                    })
                });
                if (res.ok) {
                    const data = await res.json();
                    if (typeof data.voice === "string") setVoiceState(data.voice);
                }
            } catch  {
                sendAction({
                    action: "set_persona",
                    persona: normalized,
                    ...voiceName ? {
                        voice: voiceName
                    } : {}
                });
            }
        }
    }["JarvisProvider.useCallback[choosePersona]"], [
        femaleVoices,
        fireLocalTrace,
        maleVoices,
        sendAction,
        voice
    ]);
    const tapOrb = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useCallback"])({
        "JarvisProvider.useCallback[tapOrb]": ()=>{
            if (!connected) {
                const next = demoState === "idle" ? "listening" : demoState === "listening" ? "thinking" : demoState === "thinking" ? "speaking" : "idle";
                setDemoState(next);
                if (next === "thinking") {
                    fireLocalTrace([
                        "chief_of_staff",
                        "researcher",
                        "memory"
                    ]);
                } else if (next === "speaking") {
                    targetLevelRef.current = 0.72;
                }
                if (demoTimerRef.current) clearTimeout(demoTimerRef.current);
                demoTimerRef.current = setTimeout({
                    "JarvisProvider.useCallback[tapOrb]": ()=>setDemoState("idle")
                }["JarvisProvider.useCallback[tapOrb]"], 8000);
                return;
            }
            fireLocalTrace([
                "chief_of_staff"
            ]);
            sendAction({
                action: "orb_tap"
            });
        }
    }["JarvisProvider.useCallback[tapOrb]"], [
        connected,
        demoState,
        fireLocalTrace,
        sendAction
    ]);
    const sendText = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useCallback"])({
        "JarvisProvider.useCallback[sendText]": (text, traceNode)=>{
            const clean = text.trim();
            if (!clean) return;
            fireLocalTrace(traceNode ? [
                traceNode,
                "chief_of_staff"
            ] : [
                "chief_of_staff"
            ]);
            if (!connected) {
                pushLogLine(`You: ${clean}`);
                setDemoState("thinking");
                if (demoTimerRef.current) clearTimeout(demoTimerRef.current);
                demoTimerRef.current = setTimeout({
                    "JarvisProvider.useCallback[sendText]": ()=>{
                        setDemoState("idle");
                    }
                }["JarvisProvider.useCallback[sendText]"], 3500);
                return;
            }
            setRawState("THINKING");
            sendAction({
                action: "text_command",
                text: clean
            });
        }
    }["JarvisProvider.useCallback[sendText]"], [
        connected,
        fireLocalTrace,
        pushLogLine,
        sendAction
    ]);
    const toggleMute = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useCallback"])({
        "JarvisProvider.useCallback[toggleMute]": ()=>{
            if (!connected) {
                setMuted({
                    "JarvisProvider.useCallback[toggleMute]": (m)=>!m
                }["JarvisProvider.useCallback[toggleMute]"]);
                return;
            }
            sendAction({
                action: "toggle_mute"
            });
        }
    }["JarvisProvider.useCallback[toggleMute]"], [
        connected,
        sendAction
    ]);
    const togglePause = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useCallback"])({
        "JarvisProvider.useCallback[togglePause]": ()=>{
            if (!connected) {
                setPaused({
                    "JarvisProvider.useCallback[togglePause]": (p)=>!p
                }["JarvisProvider.useCallback[togglePause]"]);
                return;
            }
            sendAction({
                action: "toggle_pause"
            });
        }
    }["JarvisProvider.useCallback[togglePause]"], [
        connected,
        sendAction
    ]);
    const interrupt = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useCallback"])({
        "JarvisProvider.useCallback[interrupt]": ()=>{
            if (!connected) {
                setDemoState("idle");
                return;
            }
            sendAction({
                action: "interrupt"
            });
        }
    }["JarvisProvider.useCallback[interrupt]"], [
        connected,
        sendAction
    ]);
    const stopAll = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useCallback"])({
        "JarvisProvider.useCallback[stopAll]": ()=>{
            sendAction({
                action: "stop_all"
            });
        }
    }["JarvisProvider.useCallback[stopAll]"], [
        sendAction
    ]);
    const captureRegion = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useCallback"])({
        "JarvisProvider.useCallback[captureRegion]": ()=>{
            fireLocalTrace([
                "design"
            ]);
            sendAction({
                action: "region_capture"
            });
        }
    }["JarvisProvider.useCallback[captureRegion]"], [
        fireLocalTrace,
        sendAction
    ]);
    const openRemoteQr = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useCallback"])({
        "JarvisProvider.useCallback[openRemoteQr]": ()=>{
            sendAction({
                action: "remote_qr"
            });
        }
    }["JarvisProvider.useCallback[openRemoteQr]"], [
        sendAction
    ]);
    const setVoice = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useCallback"])({
        "JarvisProvider.useCallback[setVoice]": (v)=>{
            setVoiceState(v);
            sendAction({
                action: "set_voice",
                voice: v
            });
        }
    }["JarvisProvider.useCallback[setVoice]"], [
        sendAction
    ]);
    const setDevices = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useCallback"])({
        "JarvisProvider.useCallback[setDevices]": (inputName, outputName)=>{
            setCurrentInput(inputName);
            setCurrentOutput(outputName);
            sendAction({
                action: "set_audio_devices",
                input_device: inputName,
                output_device: outputName
            });
        }
    }["JarvisProvider.useCallback[setDevices]"], [
        sendAction
    ]);
    const setBarge = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useCallback"])({
        "JarvisProvider.useCallback[setBarge]": (enabled)=>{
            setBargeEnabled(enabled);
            sendAction({
                action: "set_barge",
                enabled
            });
        }
    }["JarvisProvider.useCallback[setBarge]"], [
        sendAction
    ]);
    const setGrace = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useCallback"])({
        "JarvisProvider.useCallback[setGrace]": (seconds)=>{
            setGracePeriod(seconds);
            sendAction({
                action: "set_grace",
                seconds
            });
        }
    }["JarvisProvider.useCallback[setGrace]"], [
        sendAction
    ]);
    const resolveConfirm = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useCallback"])({
        "JarvisProvider.useCallback[resolveConfirm]": (approved)=>{
            setConfirm(null);
            sendAction({
                action: "confirm_decision",
                approved
            });
        }
    }["JarvisProvider.useCallback[resolveConfirm]"], [
        sendAction
    ]);
    const saveApiKey = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useCallback"])({
        "JarvisProvider.useCallback[saveApiKey]": async (keyOrPayload)=>{
            const bodyPayload = typeof keyOrPayload === "string" ? {
                action: "save_api_key",
                key: keyOrPayload.trim()
            } : {
                action: "save_api_key",
                ...keyOrPayload
            };
            try {
                const r = await fetch("/api/hud/action", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify(bodyPayload)
                });
                if (r.ok) {
                    const data = await r.json().catch({
                        "JarvisProvider.useCallback[saveApiKey]": ()=>({})
                    }["JarvisProvider.useCallback[saveApiKey]"]);
                    if (data && data.ok === false) return false;
                    setReady(true);
                    setSetupOpen(false);
                    if (!integrationsReady) {
                        setIntegrationsModalOpen(true);
                    } else if (!personaChosen) {
                        setPersonaModalOpen(true);
                    }
                    return true;
                }
            } catch  {}
            return false;
        }
    }["JarvisProvider.useCallback[saveApiKey]"], [
        integrationsReady,
        personaChosen
    ]);
    const saveIntegrations = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useCallback"])({
        "JarvisProvider.useCallback[saveIntegrations]": async (payload)=>{
            fireLocalTrace([
                "email",
                "drive",
                "calendar"
            ]);
            try {
                const r = await fetch("/api/hud/action", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify({
                        action: "save_integrations",
                        integrations: payload
                    })
                });
                if (r.ok) {
                    const data = await r.json();
                    if (data.summary && typeof data.summary === "object") {
                        setIntegrations(data.summary);
                    }
                    setIntegrationsReady(true);
                    setIntegrationsModalOpen(false);
                    if (!personaChosen) {
                        setPersonaModalOpen(true);
                    }
                    return true;
                }
            } catch  {}
            return false;
        }
    }["JarvisProvider.useCallback[saveIntegrations]"], [
        fireLocalTrace,
        personaChosen
    ]);
    const skipIntegrations = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useCallback"])({
        "JarvisProvider.useCallback[skipIntegrations]": async ()=>{
            setIntegrationsReady(true);
            setIntegrationsModalOpen(false);
            if (!personaChosen) {
                setPersonaModalOpen(true);
            }
            try {
                const r = await fetch("/api/hud/action", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify({
                        action: "skip_integrations"
                    })
                });
                if (r.ok) {
                    const data = await r.json();
                    if (data.summary && typeof data.summary === "object") {
                        setIntegrations(data.summary);
                    }
                }
            } catch  {
                sendAction({
                    action: "skip_integrations"
                });
            }
        }
    }["JarvisProvider.useCallback[skipIntegrations]"], [
        personaChosen,
        sendAction
    ]);
    const disconnectIntegration = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useCallback"])({
        "JarvisProvider.useCallback[disconnectIntegration]": async (service)=>{
            try {
                const r = await fetch("/api/hud/action", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify({
                        action: "disconnect_integration",
                        service
                    })
                });
                if (r.ok) {
                    const data = await r.json();
                    if (data.summary && typeof data.summary === "object") {
                        setIntegrations(data.summary);
                    }
                }
            } catch  {
                sendAction({
                    action: "disconnect_integration",
                    service
                });
            }
        }
    }["JarvisProvider.useCallback[disconnectIntegration]"], [
        sendAction
    ]);
    const startGoogleOAuth = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useCallback"])({
        "JarvisProvider.useCallback[startGoogleOAuth]": async (clientId, clientSecret)=>{
            try {
                const r = await fetch("/api/hud/action", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify({
                        action: "start_google_oauth",
                        client_id: clientId,
                        client_secret: clientSecret
                    })
                });
                const data = await r.json();
                if (data.ok && typeof data.auth_url === "string") {
                    window.open(data.auth_url, "_blank", "noopener,noreferrer");
                }
                return data;
            } catch  {
                return {
                    ok: false,
                    error: "Could not start Google OAuth flow."
                };
            }
        }
    }["JarvisProvider.useCallback[startGoogleOAuth]"], []);
    const connectSocialWeb = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useCallback"])({
        "JarvisProvider.useCallback[connectSocialWeb]": async (platform, handle = "", permission = "ask")=>{
            try {
                const r = await fetch("/api/hud/action", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify({
                        action: "social_connect_web",
                        platform,
                        handle,
                        permission
                    })
                });
                const data = await r.json();
                if (data.summary && typeof data.summary === "object") {
                    setIntegrations(data.summary);
                }
                return data;
            } catch  {
                return {
                    ok: false,
                    error: "Could not start social sign-in session."
                };
            }
        }
    }["JarvisProvider.useCallback[connectSocialWeb]"], []);
    const importSocialCookies = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useCallback"])({
        "JarvisProvider.useCallback[importSocialCookies]": async (platform, browser = "auto", handle = "", permission = "ask")=>{
            try {
                const r = await fetch("/api/hud/action", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify({
                        action: "social_import_cookies",
                        platform,
                        browser,
                        handle,
                        permission
                    })
                });
                const data = await r.json();
                if (data.summary && typeof data.summary === "object") {
                    setIntegrations(data.summary);
                }
                return data;
            } catch  {
                return {
                    ok: false,
                    error: "Could not import browser cookies."
                };
            }
        }
    }["JarvisProvider.useCallback[importSocialCookies]"], []);
    const updatePrivacy = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useCallback"])({
        "JarvisProvider.useCallback[updatePrivacy]": async (patch)=>{
            setPrivacyState({
                "JarvisProvider.useCallback[updatePrivacy]": (prev)=>({
                        ...prev,
                        ...patch
                    })
            }["JarvisProvider.useCallback[updatePrivacy]"]);
            try {
                const r = await fetch("/api/hud/action", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify({
                        action: "brain_set_privacy",
                        ...patch
                    })
                });
                if (r.ok) {
                    const data = await r.json();
                    if (data.privacy && typeof data.privacy === "object") {
                        setPrivacyState(data.privacy);
                    }
                }
            } catch  {
                sendAction({
                    action: "brain_set_privacy",
                    ...patch
                });
            }
        }
    }["JarvisProvider.useCallback[updatePrivacy]"], [
        sendAction
    ]);
    const showContentCard = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useCallback"])({
        "JarvisProvider.useCallback[showContentCard]": (card)=>{
            setContent(card);
        }
    }["JarvisProvider.useCallback[showContentCard]"], []);
    const clearContent = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useCallback"])({
        "JarvisProvider.useCallback[clearContent]": ()=>setContent(null)
    }["JarvisProvider.useCallback[clearContent]"], []);
    const spawnWorker = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useCallback"])({
        "JarvisProvider.useCallback[spawnWorker]": async (goal, tools)=>{
            if (!goal.trim()) return;
            fireLocalTrace([
                "strategist",
                "chief_of_staff"
            ]);
            try {
                const r = await fetch("/api/hud/action", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify({
                        action: "spawn_worker",
                        goal: goal.trim(),
                        tools: tools || [],
                        auto_start: true
                    })
                });
                if (r.ok) {
                    const data = await r.json();
                    if (Array.isArray(data.workers)) setWorkers(data.workers);
                }
            } catch  {
                sendAction({
                    action: "spawn_worker",
                    goal: goal.trim(),
                    tools: tools || []
                });
            }
        }
    }["JarvisProvider.useCallback[spawnWorker]"], [
        fireLocalTrace,
        sendAction
    ]);
    const cancelWorker = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useCallback"])({
        "JarvisProvider.useCallback[cancelWorker]": async (workerId)=>{
            if (!workerId) return;
            try {
                const r = await fetch("/api/hud/action", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify({
                        action: "cancel_worker",
                        worker_id: workerId
                    })
                });
                if (r.ok) {
                    const data = await r.json();
                    if (Array.isArray(data.workers)) setWorkers(data.workers);
                }
            } catch  {
                sendAction({
                    action: "cancel_worker",
                    worker_id: workerId
                });
            }
        }
    }["JarvisProvider.useCallback[cancelWorker]"], [
        sendAction
    ]);
    const clearCompletedWorkers = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useCallback"])({
        "JarvisProvider.useCallback[clearCompletedWorkers]": async ()=>{
            try {
                const r = await fetch("/api/hud/action", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify({
                        action: "clear_completed_workers"
                    })
                });
                if (r.ok) {
                    const data = await r.json();
                    if (Array.isArray(data.workers)) setWorkers(data.workers);
                }
            } catch  {
                sendAction({
                    action: "clear_completed_workers"
                });
            }
        }
    }["JarvisProvider.useCallback[clearCompletedWorkers]"], [
        sendAction
    ]);
    const enterBackgroundMode = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useCallback"])({
        "JarvisProvider.useCallback[enterBackgroundMode]": async ()=>{
            setBackgroundMode(true);
            try {
                const r = await fetch("/api/hud/action", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify({
                        action: "enter_background_mode"
                    })
                });
                if (r.ok) {
                    const data = await r.json();
                    if (data?.native_dock && ("TURBOPACK compile-time value", "object") !== "undefined") {
                        try {
                            window.close();
                        } catch  {}
                    }
                }
            } catch  {
                sendAction({
                    action: "enter_background_mode"
                });
            }
        }
    }["JarvisProvider.useCallback[enterBackgroundMode]"], [
        sendAction
    ]);
    const exitBackgroundMode = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useCallback"])({
        "JarvisProvider.useCallback[exitBackgroundMode]": async ()=>{
            setBackgroundMode(false);
            try {
                await fetch("/api/hud/action", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify({
                        action: "exit_background_mode"
                    })
                });
            } catch  {
                sendAction({
                    action: "exit_background_mode"
                });
            }
        }
    }["JarvisProvider.useCallback[exitBackgroundMode]"], [
        sendAction
    ]);
    const closeVideo = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useCallback"])({
        "JarvisProvider.useCallback[closeVideo]": async ()=>{
            setVideo(null);
            try {
                await fetch("/api/hud/action", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify({
                        action: "video_close"
                    })
                });
            } catch  {
                sendAction({
                    action: "video_close"
                });
            }
        }
    }["JarvisProvider.useCallback[closeVideo]"], [
        sendAction
    ]);
    const setVideoMuted = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useCallback"])({
        "JarvisProvider.useCallback[setVideoMuted]": async (nextMuted)=>{
            setVideo({
                "JarvisProvider.useCallback[setVideoMuted]": (prev)=>prev ? {
                        ...prev,
                        muted: nextMuted
                    } : prev
            }["JarvisProvider.useCallback[setVideoMuted]"]);
            try {
                await fetch("/api/hud/action", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify({
                        action: "video_mute",
                        muted: nextMuted
                    })
                });
            } catch  {
                sendAction({
                    action: "video_mute",
                    muted: nextMuted
                });
            }
        }
    }["JarvisProvider.useCallback[setVideoMuted]"], [
        sendAction
    ]);
    const nextVideo = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useCallback"])({
        "JarvisProvider.useCallback[nextVideo]": async ()=>{
            try {
                await fetch("/api/hud/action", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify({
                        action: "video_next"
                    })
                });
            } catch  {
                sendAction({
                    action: "video_next"
                });
            }
        }
    }["JarvisProvider.useCallback[nextVideo]"], [
        sendAction
    ]);
    const prevVideo = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useCallback"])({
        "JarvisProvider.useCallback[prevVideo]": async ()=>{
            try {
                await fetch("/api/hud/action", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify({
                        action: "video_prev"
                    })
                });
            } catch  {
                sendAction({
                    action: "video_prev"
                });
            }
        }
    }["JarvisProvider.useCallback[prevVideo]"], [
        sendAction
    ]);
    const jumpVideo = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useCallback"])({
        "JarvisProvider.useCallback[jumpVideo]": async (index)=>{
            try {
                await fetch("/api/hud/action", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify({
                        action: "video_jump",
                        index
                    })
                });
            } catch  {
                sendAction({
                    action: "video_jump",
                    index
                });
            }
        }
    }["JarvisProvider.useCallback[jumpVideo]"], [
        sendAction
    ]);
    const openSocialHud = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useCallback"])({
        "JarvisProvider.useCallback[openSocialHud]": async (platform, view = "feed", layout)=>{
            try {
                const r = await fetch("/api/hud/action", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify({
                        action: "social_open_hud",
                        platform,
                        view,
                        layout: layout || ""
                    })
                });
                const data = await r.json();
                if (data.social_hud && typeof data.social_hud === "object") {
                    setSocialHud(data.social_hud);
                }
                if (data.summary && typeof data.summary === "object") {
                    setIntegrations(data.summary);
                }
                return data;
            } catch  {
                return {
                    ok: false,
                    error: "Could not open HUD social viewport."
                };
            }
        }
    }["JarvisProvider.useCallback[openSocialHud]"], []);
    const closeSocialHud = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useCallback"])({
        "JarvisProvider.useCallback[closeSocialHud]": async ()=>{
            setSocialHud(null);
            try {
                await fetch("/api/hud/action", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify({
                        action: "social_close_hud"
                    })
                });
            } catch  {
                sendAction({
                    action: "social_close_hud"
                });
            }
        }
    }["JarvisProvider.useCallback[closeSocialHud]"], [
        sendAction
    ]);
    const value = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useMemo"])({
        "JarvisProvider.useMemo[value]": ()=>({
                connected,
                ready,
                integrationsReady,
                integrations,
                privacy,
                brainCounts,
                workers,
                terminalSessions,
                activeCompanion,
                themeCustom,
                aiProviders,
                persona,
                activePersona,
                theme,
                personaChosen,
                assistantName,
                orbState,
                rawState: connected ? rawState : demoState.toUpperCase(),
                muted,
                paused,
                offline,
                offlineReason,
                voice,
                voices,
                maleVoices,
                femaleVoices,
                bargeEnabled,
                gracePeriod,
                inputs,
                outputs,
                currentInput,
                currentOutput,
                logs,
                lastSubtitle,
                trace,
                confirm,
                content,
                video,
                socialHud,
                consoleOpen,
                settingsOpen,
                setupOpen,
                integrationsModalOpen,
                brainModalOpen,
                studioModalOpen,
                automationsModalOpen,
                devModalOpen,
                securityModalOpen,
                activityOpen,
                personaModalOpen,
                backgroundMode,
                setConsoleOpen,
                setSettingsOpen,
                setSetupOpen,
                setIntegrationsModalOpen,
                setBrainModalOpen,
                setStudioModalOpen,
                setAutomationsModalOpen,
                setDevModalOpen,
                setSecurityModalOpen,
                setTerminalSessions,
                setActivityOpen,
                setPersonaModalOpen,
                setPreviewPersona,
                setThemeCustom,
                choosePersona,
                saveIntegrations,
                skipIntegrations,
                disconnectIntegration,
                startGoogleOAuth,
                connectSocialWeb,
                importSocialCookies,
                updatePrivacy,
                spawnWorker,
                cancelWorker,
                clearCompletedWorkers,
                showContentCard,
                clearContent,
                sendText,
                tapOrb,
                fireLocalTrace,
                toggleMute,
                togglePause,
                interrupt,
                stopAll,
                captureRegion,
                openRemoteQr,
                setVoice,
                setDevices,
                setBarge,
                setGrace,
                resolveConfirm,
                saveApiKey,
                enterBackgroundMode,
                exitBackgroundMode,
                closeVideo,
                setVideoMuted,
                nextVideo,
                prevVideo,
                jumpVideo,
                openSocialHud,
                closeSocialHud
            })
    }["JarvisProvider.useMemo[value]"], [
        connected,
        ready,
        integrationsReady,
        integrations,
        privacy,
        brainCounts,
        workers,
        terminalSessions,
        activeCompanion,
        themeCustom,
        aiProviders,
        persona,
        activePersona,
        theme,
        personaChosen,
        assistantName,
        orbState,
        rawState,
        demoState,
        muted,
        paused,
        offline,
        offlineReason,
        voice,
        voices,
        maleVoices,
        femaleVoices,
        bargeEnabled,
        gracePeriod,
        inputs,
        outputs,
        currentInput,
        currentOutput,
        logs,
        lastSubtitle,
        trace,
        confirm,
        content,
        video,
        socialHud,
        consoleOpen,
        settingsOpen,
        setupOpen,
        integrationsModalOpen,
        brainModalOpen,
        studioModalOpen,
        automationsModalOpen,
        devModalOpen,
        securityModalOpen,
        activityOpen,
        personaModalOpen,
        backgroundMode,
        choosePersona,
        saveIntegrations,
        skipIntegrations,
        disconnectIntegration,
        startGoogleOAuth,
        connectSocialWeb,
        importSocialCookies,
        updatePrivacy,
        spawnWorker,
        cancelWorker,
        clearCompletedWorkers,
        showContentCard,
        clearContent,
        sendText,
        tapOrb,
        fireLocalTrace,
        toggleMute,
        togglePause,
        interrupt,
        stopAll,
        captureRegion,
        openRemoteQr,
        setVoice,
        setDevices,
        setBarge,
        setGrace,
        resolveConfirm,
        saveApiKey,
        enterBackgroundMode,
        exitBackgroundMode,
        closeVideo,
        setVideoMuted,
        nextVideo,
        prevVideo,
        jumpVideo,
        openSocialHud,
        closeSocialHud
    ]);
    return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(JarvisContext.Provider, {
        value: value,
        children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(JarvisAudioLevelContext.Provider, {
            value: audioLevel,
            children: children
        }, void 0, false, {
            fileName: "[project]/components/JarvisBridge.tsx",
            lineNumber: 1655,
            columnNumber: 7
        }, this)
    }, void 0, false, {
        fileName: "[project]/components/JarvisBridge.tsx",
        lineNumber: 1654,
        columnNumber: 5
    }, this);
}
_s1(JarvisProvider, "A0jx+3YS3x2DKY1fK4v3SkCfaP8=");
_c = JarvisProvider;
function useJarvis() {
    _s2();
    const ctx = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useContext"])(JarvisContext);
    if (!ctx) {
        throw new Error("useJarvis must be used inside <JarvisProvider>");
    }
    return ctx;
}
_s2(useJarvis, "/dMy7t63NXD4eYACoT93CePwGrg=");
var _c;
__turbopack_context__.k.register(_c, "JarvisProvider");
if (typeof globalThis.$RefreshHelpers$ === 'object' && globalThis.$RefreshHelpers !== null) {
    __turbopack_context__.k.registerExports(__turbopack_context__.m, globalThis.$RefreshHelpers$);
}
}),
"[project]/components/ReasoningWeb.jsx [app-client] (ecmascript)", ((__turbopack_context__) => {
"use strict";

__turbopack_context__.s([
    "default",
    ()=>ReasoningWeb
]);
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/next/dist/compiled/react/jsx-dev-runtime.js [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/next/dist/compiled/react/index.js [app-client] (ecmascript)");
;
var _s = __turbopack_context__.k.signature();
"use client";
;
// Apex's reasoning web — the lean-orchestrator brain. Two modes:
//   mode="full"  → the whole circuit-brain constellation (front / overview). Orbit rings + PCB
//                  traces + neuron texture + the asymmetric roster, weighted by responsibility
//                  (Chief of staff biggest + closest). On a reasoning turn the consulted nodes
//                  light and cyan particles flow the path.
//   mode="mini"  → chat mode. The core stays calm; only the 1–3 helpers Apex actually consulted
//                  BLOOM out for a beat (pulse + label) then retract. Keeps the corner uncluttered.
// `coreless` hides Apex's own core (used in front mode, layered over the 3D particle orb, so there
// is one bright centre, not two). Driven by the backend `trace` WS event. See APEX_ARCHITECTURE.md.
//
// Aesthetic (ref: navy AI-brain): thin lines, small cyan particles, structured-chaos glow.
// Pure SVG + rAF, built imperatively; decorative (pointer-events none).
// Site adaptation: `roster`, `anchor` and `viewBox` are optional overrides so a
// caller can re-arrange the constellation (the pitch deck parks Apex to one side
// and needs the roster hanging below the core, not wrapped around it). Omit them
// and this behaves exactly as the app copy does.
const NS = 'http://www.w3.org/2000/svg';
const AX_DEFAULT = 340, AY_DEFAULT = 240 // exact viewBox centre = the orb's world-origin anchor (where the 3D particle
;
// ball is centred), so the spoke hub originates from the particle cluster's centre
const COL = {
    consultant: '#00e5ff',
    doer: '#f5a623',
    tool: '#7f9bb3'
};
// Right side re-spaced into a clean vertical ladder (drive→finance→editor→memory→email→design)
// so no label collides with a neighbouring circle. Left/bottom unchanged.
const ROSTER = [
    [
        'chief_of_staff',
        'Chief of staff',
        'consultant',
        250,
        212,
        true,
        18,
        9
    ],
    [
        'memory',
        'Memory',
        'consultant',
        452,
        250,
        true,
        -18,
        8
    ],
    [
        'strategist',
        'Strategist',
        'consultant',
        296,
        118,
        true,
        -22,
        6.5
    ],
    [
        'researcher',
        'Researcher',
        'consultant',
        182,
        150,
        true,
        24,
        6.5
    ],
    [
        'finance',
        'Finance',
        'consultant',
        436,
        148,
        true,
        -20,
        6.5
    ],
    [
        'editor',
        'Editor',
        'consultant',
        584,
        208,
        true,
        -26,
        6.5
    ],
    [
        'sales',
        'Sales',
        'doer',
        158,
        266,
        true,
        22,
        6.5
    ],
    [
        'marketing',
        'Marketing',
        'doer',
        195,
        298,
        true,
        22,
        6.5
    ],
    [
        'ops',
        'Ops',
        'doer',
        232,
        330,
        true,
        20,
        6.5
    ],
    [
        'social_media',
        'Social',
        'doer',
        330,
        374,
        true,
        -16,
        6.5
    ],
    [
        'engineering',
        'Engineering',
        'doer',
        426,
        350,
        true,
        -18,
        6.5
    ],
    [
        'design',
        'Design',
        'doer',
        502,
        312,
        true,
        -22,
        6.5
    ],
    [
        'developer',
        'Developer',
        'doer',
        118,
        356,
        false,
        26,
        6
    ],
    [
        'analytics',
        'Analytics',
        'tool',
        256,
        388,
        false,
        20,
        5.5
    ],
    [
        'crm',
        'CRM',
        'tool',
        414,
        392,
        true,
        -18,
        5.5
    ],
    [
        'calendar',
        'Calendar',
        'tool',
        560,
        356,
        true,
        -24,
        5.5
    ],
    [
        'email',
        'Email',
        'tool',
        608,
        286,
        false,
        -26,
        5.5
    ],
    [
        'drive',
        'Drive',
        'tool',
        582,
        132,
        false,
        24,
        5.5
    ]
];
const META = {};
ROSTER.forEach((r)=>{
    META[r[0]] = {
        label: r[1],
        col: COL[r[2]]
    };
});
const LEVEL = {
    standby: 0.32,
    listening: 0.6,
    processing: 0.85,
    reasoning: 0.95,
    speaking: 0.78
};
function nodeIdFromHelper(h) {
    const s = String(h || '').replace(/^(ask_|call_|run_|fetch_|get_|delegate_to_|delegate_)/, '');
    return ({
        create_visual: 'design',
        render_visual: 'design',
        visual: 'design'
    })[s] || s // a visual lights Design
    ;
}
function ReasoningWeb({ state = 'standby', trace = null, mode = 'full', coreless = false, onSelect = null, light = false, persona = 'male', roster = null, anchor = null, viewBox = null, traces = true }) {
    _s();
    const svgRef = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useRef"])(null);
    const apiRef = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useRef"])(null);
    const stateRef = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useRef"])(state);
    stateRef.current = state;
    const onSelectRef = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useRef"])(onSelect);
    onSelectRef.current = onSelect; // click a node → open its cockpit
    (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useEffect"])({
        "ReasoningWeb.useEffect": ()=>{
            const svg = svgRef.current;
            if (!svg || apiRef.current) return;
            const AX = anchor ? anchor[0] : AX_DEFAULT;
            const AY = anchor ? anchor[1] : AY_DEFAULT;
            const NODES = roster || ROSTER;
            const isFemale = persona === 'female';
            // Day-mode & Male/Female dark-mode palettes — every structural color routes through P.
            const P = light ? {
                ring: '#93a9bb',
                pcb: '#5d7f97',
                pcbDot: '#0e7490',
                fieldMesh: '#9db1c0',
                fieldDot: '#0e7490',
                mesh: '#8ba2b4',
                spoke: '#46708e',
                spokeHot: '#0891b2',
                link: '#0d9488',
                label: '#1f2d3a',
                labelMinor: '#55677a',
                labelDorm: '#8a99a8',
                mote: '#0aa9c8',
                moteHot: '#067a96',
                col: {
                    consultant: '#067a96',
                    doer: '#b26d05',
                    tool: '#64748b'
                }
            } : isFemale ? {
                ring: '#69275c',
                pcb: '#6e2860',
                pcbDot: '#ff73cb',
                fieldMesh: '#4a1d46',
                fieldDot: '#e879f9',
                mesh: '#5c2657',
                spoke: '#6b2c63',
                spokeHot: '#ff7ce5',
                link: '#e879f9',
                label: '#f8e6f5',
                labelMinor: '#cda4cb',
                labelDorm: '#825b82',
                mote: '#ff8ee3',
                moteHot: '#ffe0f7',
                col: {
                    consultant: '#ff4db8',
                    doer: '#c084fc',
                    tool: '#b39ddb'
                }
            } : {
                ring: '#1b5f78',
                pcb: '#1c5f7a',
                pcbDot: '#37d6ef',
                fieldMesh: '#143f4f',
                fieldDot: '#2bd0e6',
                mesh: '#1a5468',
                spoke: '#22566b',
                spokeHot: '#33eaff',
                link: '#5eead4',
                label: '#dfeaf3',
                labelMinor: '#93a8ba',
                labelDorm: '#546a7d',
                mote: '#5fe0f2',
                moteHot: '#bff6ff',
                col: {
                    consultant: '#00e5ff',
                    doer: '#f5a623',
                    tool: '#7f9bb3'
                }
            };
            const mk = {
                "ReasoningWeb.useEffect.mk": (t, a = {})=>{
                    const e = document.createElementNS(NS, t);
                    for(const k in a)e.setAttribute(k, a[k]);
                    return e;
                }
            }["ReasoningWeb.useEffect.mk"];
            const defs = mk('defs');
            defs.innerHTML = '<filter id="rw-glow" x="-80%" y="-80%" width="260%" height="260%"><feGaussianBlur stdDeviation="2.4" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter><filter id="rw-soft" x="-150%" y="-150%" width="400%" height="400%"><feGaussianBlur stdDeviation="9"/></filter><filter id="rw-line" x="-40%" y="-40%" width="180%" height="180%"><feGaussianBlur stdDeviation="1.9" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>';
            const ringsG = mk('g'), pcbG = mk('g'), fillG = mk('g'), meshG = mk('g'), spokesG = mk('g'), pulsesG = mk('g'), nodesG = mk('g'), coreG = mk('g');
            svg.append(defs, pcbG, ringsG, fillG, meshG, spokesG, pulsesG, nodesG, coreG);
            // Soft glow on the connective tissue (lines/traces) so the whole web shimmers (ref look). Text
            // labels live in nodesG (unfiltered) so they stay crisp.
            // Dark mode: glow the connective tissue (the shimmer look). Light mode: NO blur — crisp thin
            // lines read as a blueprint on paper; the glow was what made them look foggy gray (Ruben).
            if (!light) [
                pcbG,
                meshG,
                spokesG
            ].forEach({
                "ReasoningWeb.useEffect": (grp)=>grp.setAttribute('filter', 'url(#rw-line)')
            }["ReasoningWeb.useEffect"]);
            let seed = 11;
            const rnd = {
                "ReasoningWeb.useEffect.rnd": ()=>(seed = (seed * 9301 + 49297) % 233280) / 233280
            }["ReasoningWeb.useEffect.rnd"];
            const pathD = {
                "ReasoningWeb.useEffect.pathD": (bx, by, bend)=>{
                    const mx = (AX + bx) / 2, my = (AY + by) / 2, dx = bx - AX, dy = by - AY, l = Math.hypot(dx, dy) || 1;
                    return `M${AX} ${AY} Q${mx + -dy / l * bend} ${my + dx / l * bend} ${bx} ${by}`;
                }
            }["ReasoningWeb.useEffect.pathD"];
            // ── shared particle system — small cyan particles flowing a spoke ──
            const live = [];
            let allNodes = [] // full-mode roster, for per-node pulsing
            ;
            const spawn = {
                "ReasoningWeb.useEffect.spawn": (spoke, faint)=>{
                    const el = mk('circle', {
                        r: faint ? 0.9 : 1.4,
                        fill: faint ? P.mote : P.moteHot,
                        filter: 'url(#rw-glow)'
                    });
                    pulsesG.append(el);
                    live.push({
                        el,
                        born: performance.now(),
                        spoke,
                        L: spoke.getTotalLength(),
                        faint
                    });
                }
            }["ReasoningWeb.useEffect.spawn"];
            // ── Apex core (unless layered over the 3D orb) ──
            let halo, ring, gold, hot;
            if (!coreless) {
                halo = mk('circle', {
                    cx: AX,
                    cy: AY,
                    r: 30,
                    fill: '#0bd0ff',
                    opacity: 0.14,
                    filter: 'url(#rw-soft)'
                });
                ring = mk('circle', {
                    cx: AX,
                    cy: AY,
                    r: 18,
                    fill: 'none',
                    stroke: '#7df1ff',
                    'stroke-width': 1.2,
                    opacity: 0.6
                });
                gold = mk('circle', {
                    cx: AX,
                    cy: AY,
                    r: 11,
                    fill: '#ffcf6b',
                    filter: 'url(#rw-glow)'
                });
                hot = mk('circle', {
                    cx: AX,
                    cy: AY,
                    r: 4,
                    fill: '#ffffff',
                    filter: 'url(#rw-glow)'
                });
                const lab = mk('text', {
                    x: AX,
                    y: AY + 34,
                    'text-anchor': 'middle',
                    'font-size': 12,
                    'font-family': 'inherit',
                    fill: '#ffcf6b'
                });
                lab.textContent = 'Apex';
                coreG.append(halo, ring, gold, hot, lab);
            }
            let fire;
            if (mode === 'full') {
                // Concentric orbit rings + PCB circuit traces — thin, faint, "structured chaos".
                ;
                [
                    72,
                    128,
                    186
                ].forEach({
                    "ReasoningWeb.useEffect": (r)=>ringsG.append(mk('circle', {
                            cx: AX,
                            cy: AY,
                            r,
                            fill: 'none',
                            stroke: P.ring,
                            opacity: 0.32,
                            'stroke-width': 1,
                            'stroke-dasharray': '1 7'
                        }))
                }["ReasoningWeb.useEffect"]);
                [
                    -1,
                    1
                ].forEach({
                    "ReasoningWeb.useEffect": (side)=>{
                        if (!traces) return;
                        for(let i = 0; i < 6; i++){
                            const y = AY + (i - 2.5) * 52 + (rnd() * 16 - 8);
                            const startX = AX + side * (126 + rnd() * 34);
                            const midX = side < 0 ? 40 + rnd() * 56 : 584 + rnd() * 56;
                            const y2 = y + (rnd() * 30 - 15);
                            const jogX = side < 0 ? 10 + rnd() * 18 : 652 + rnd() * 18;
                            pcbG.append(mk('path', {
                                d: `M${startX} ${y} H${midX} V${y2} H${jogX}`,
                                fill: 'none',
                                stroke: P.pcb,
                                opacity: 0.5,
                                'stroke-width': 1
                            }));
                            pcbG.append(mk('circle', {
                                cx: jogX,
                                cy: y2,
                                r: 2.4,
                                fill: P.pcbDot,
                                opacity: 0.85
                            })); // glowing end (via group glow)
                            pcbG.append(mk('circle', {
                                cx: startX,
                                cy: y,
                                r: 1.3,
                                fill: P.fieldDot,
                                opacity: 0.45
                            }));
                        }
                    }
                }["ReasoningWeb.useEffect"]);
                // Ordered chaos: keep the neuron texture sparse + LOCAL so it never tangles into the spokes.
                const fill = [];
                for(let i = 0; i < 15; i++){
                    const x = 36 + rnd() * 608, y = 34 + rnd() * 412;
                    if (Math.hypot(x - AX, y - AY) > 175) fill.push({
                        x,
                        y
                    });
                }
                fill.forEach({
                    "ReasoningWeb.useEffect": (f)=>{
                        let near = null, nd = 1e9;
                        fill.forEach({
                            "ReasoningWeb.useEffect": (g)=>{
                                if (g !== f) {
                                    const d = Math.hypot(g.x - f.x, g.y - f.y);
                                    if (d < nd) {
                                        nd = d;
                                        near = g;
                                    }
                                }
                            }
                        }["ReasoningWeb.useEffect"]);
                        if (near && nd < 110) meshG.append(mk('line', {
                            x1: f.x,
                            y1: f.y,
                            x2: near.x,
                            y2: near.y,
                            stroke: P.fieldMesh,
                            'stroke-width': 1,
                            opacity: 0.45
                        }));
                        const c = mk('circle', {
                            cx: f.x,
                            cy: f.y,
                            r: 1.1,
                            fill: P.fieldDot
                        });
                        c.style.animation = `rwTwinkle 4s ease-in-out ${(rnd() * 4).toFixed(2)}s infinite`;
                        fillG.append(c);
                    }
                }["ReasoningWeb.useEffect"]);
                const map = {}, pts = [];
                NODES.forEach({
                    "ReasoningWeb.useEffect": (r)=>{
                        const n = {
                            id: r[0],
                            label: r[1],
                            layer: r[2],
                            x: r[3],
                            y: r[4],
                            live: r[5],
                            bend: r[6],
                            r: r[7],
                            col: P.col[r[2]] || COL[r[2]]
                        };
                        map[r[0]] = n;
                        pts.push(n);
                    }
                }["ReasoningWeb.useEffect"]);
                // Keep a clear moat around the centre so no node sits ON the orb — push the inner ring out.
                const MINR = 128;
                pts.forEach({
                    "ReasoningWeb.useEffect": (n)=>{
                        const dx = n.x - AX, dy = n.y - AY, d = Math.hypot(dx, dy) || 1;
                        if (d < MINR) {
                            n.x = AX + dx / d * MINR;
                            n.y = AY + dy / d * MINR;
                        }
                    }
                }["ReasoningWeb.useEffect"]);
                // Only the SINGLE nearest neighbour per node — enough to feel networked without a tangle.
                pts.forEach({
                    "ReasoningWeb.useEffect": (n)=>{
                        const o = pts.filter({
                            "ReasoningWeb.useEffect": (m)=>m !== n
                        }["ReasoningWeb.useEffect"]).map({
                            "ReasoningWeb.useEffect": (m)=>({
                                    m,
                                    d: Math.hypot(m.x - n.x, m.y - n.y)
                                })
                        }["ReasoningWeb.useEffect"]).sort({
                            "ReasoningWeb.useEffect": (a, b)=>a.d - b.d
                        }["ReasoningWeb.useEffect"])[0];
                        if (o && n.id < o.m.id && o.d < 150) meshG.append(mk('line', {
                            x1: n.x,
                            y1: n.y,
                            x2: o.m.x,
                            y2: o.m.y,
                            stroke: P.mesh,
                            'stroke-width': 1,
                            opacity: 0.5
                        }));
                    }
                }["ReasoningWeb.useEffect"]);
                pts.forEach({
                    "ReasoningWeb.useEffect": (n)=>{
                        n.spoke = mk('path', {
                            d: pathD(n.x, n.y, n.bend),
                            fill: 'none',
                            stroke: P.spoke,
                            'stroke-width': 1,
                            opacity: n.live ? 0.78 : 0.4
                        });
                        spokesG.append(n.spoke);
                        // Glowing ring (circumference only) — soft halo behind (pulses on its own phase), hollow ring on top.
                        const rr = n.live ? n.r : 5.5;
                        n.haloR = rr + 1.5;
                        n.phase = rnd() * 6.283;
                        n.halo = mk('circle', {
                            cx: n.x,
                            cy: n.y,
                            r: n.haloR,
                            fill: n.col,
                            filter: 'url(#rw-glow)',
                            opacity: n.live ? 0.34 : 0.2
                        });
                        nodesG.append(n.halo);
                        n.circ = mk('circle', {
                            cx: n.x,
                            cy: n.y,
                            r: rr,
                            fill: 'none',
                            stroke: n.col,
                            'stroke-width': n.live ? 2 : 1.3,
                            opacity: n.live ? 1 : 0.6
                        });
                        if (!n.live) n.circ.setAttribute('stroke-dasharray', '2 2');
                        nodesG.append(n.circ);
                        const dx = n.x - AX, dy = n.y - AY, d = Math.hypot(dx, dy) || 1, ux = dx / d, uy = dy / d, off = rr + 11;
                        // Bottom-most nodes: label ABOVE the node so it doesn't drop into the STANDBY bar below.
                        const above = uy > 0.82;
                        // Visual hierarchy (UI sweep): tool dorms + unbuilt nodes must not carry the same label weight
                        // as live AGENTS — a dashed "Drive" reading as big as "Design" was misleading the map.
                        const minor = !n.live || n.layer === 'tool';
                        const t = mk('text', {
                            x: above ? n.x : n.x + ux * off,
                            y: above ? n.y - (rr + 9) : n.y + uy * off + (Math.abs(uy) < 0.3 ? 4 : 0),
                            'text-anchor': above ? 'middle' : ux > 0.3 ? 'start' : ux < -0.3 ? 'end' : 'middle',
                            'font-size': minor ? 9.5 : 12,
                            'font-family': 'inherit',
                            fill: !n.live ? P.labelDorm : minor ? P.labelMinor : P.label,
                            opacity: !n.live ? 0.75 : 1
                        });
                        t.textContent = n.label;
                        nodesG.append(t);
                        // Clickable: a generous transparent hit target over the node opens its cockpit. The SVG is
                        // pointer-events:none (decorative), but this child re-enables events for itself only.
                        const hit = mk('circle', {
                            cx: n.x,
                            cy: n.y,
                            r: Math.max(rr + 13, 17),
                            fill: 'transparent'
                        });
                        hit.style.pointerEvents = 'all';
                        hit.style.cursor = 'pointer'; // 'all' captures over a transparent fill ('auto' needs visible paint)
                        hit.addEventListener('click', {
                            "ReasoningWeb.useEffect": ()=>onSelectRef.current && onSelectRef.current({
                                    name: n.label,
                                    key: n.id,
                                    color: n.col
                                })
                        }["ReasoningWeb.useEffect"]);
                        nodesG.append(hit);
                    }
                }["ReasoningWeb.useEffect"]);
                fire = ({
                    "ReasoningWeb.useEffect": (ids)=>{
                        ids.forEach({
                            "ReasoningWeb.useEffect": (id, k)=>{
                                const n = map[id];
                                if (!n) return;
                                setTimeout({
                                    "ReasoningWeb.useEffect": ()=>{
                                        n.spoke.setAttribute('stroke', P.spokeHot);
                                        n.spoke.setAttribute('stroke-width', 1.6);
                                        n.spoke.setAttribute('opacity', 0.7);
                                        n._until = performance.now() + 1150;
                                        const stream = {
                                            "ReasoningWeb.useEffect.stream": ()=>{
                                                if (performance.now() < n._until) {
                                                    spawn(n.spoke, false);
                                                    setTimeout(stream, 105);
                                                }
                                            }
                                        }["ReasoningWeb.useEffect.stream"];
                                        stream();
                                        setTimeout({
                                            "ReasoningWeb.useEffect": ()=>{
                                                n.circ.setAttribute('filter', 'url(#rw-glow)');
                                                n.circ.setAttribute('r', (n.live ? n.r : 5.5) + 3);
                                                n.circ.setAttribute('stroke-width', n.live ? 3 : 2);
                                                n.circ.setAttribute('opacity', 1);
                                            }
                                        }["ReasoningWeb.useEffect"], 560);
                                        setTimeout({
                                            "ReasoningWeb.useEffect": ()=>{
                                                n.spoke.setAttribute('stroke', P.spoke);
                                                n.spoke.setAttribute('stroke-width', 1);
                                                n.spoke.setAttribute('opacity', n.live ? 0.78 : 0.4);
                                                n.circ.removeAttribute('filter');
                                                n.circ.setAttribute('r', n.live ? n.r : 5.5);
                                                n.circ.setAttribute('stroke-width', n.live ? 2 : 1.3);
                                                n.circ.setAttribute('opacity', n.live ? 1 : 0.6);
                                            }
                                        }["ReasoningWeb.useEffect"], 2050);
                                    }
                                }["ReasoningWeb.useEffect"], k * 210);
                            }
                        }["ReasoningWeb.useEffect"]);
                        // connections between co-active agents — a transient link so multiple agents working the same turn
                        // READ as collaborating (not just Apex→each). Auto-removed after ~2.4s.
                        const co = ids.map({
                            "ReasoningWeb.useEffect.co": (id)=>map[id]
                        }["ReasoningWeb.useEffect.co"]).filter(Boolean);
                        for(let i = 0; i < co.length - 1; i++){
                            const a = co[i], b = co[i + 1];
                            const ln = mk('line', {
                                x1: +a.circ.getAttribute('cx'),
                                y1: +a.circ.getAttribute('cy'),
                                x2: +b.circ.getAttribute('cx'),
                                y2: +b.circ.getAttribute('cy'),
                                stroke: P.link,
                                'stroke-width': 1.3,
                                opacity: 0
                            });
                            pulsesG.append(ln);
                            setTimeout({
                                "ReasoningWeb.useEffect": ()=>ln.setAttribute('opacity', 0.6)
                            }["ReasoningWeb.useEffect"], 560);
                            setTimeout({
                                "ReasoningWeb.useEffect": ()=>ln.remove()
                            }["ReasoningWeb.useEffect"], 2400);
                        }
                    }
                })["ReasoningWeb.useEffect"];
                allNodes = pts;
                apiRef.current = {
                    fire,
                    liveNodes: pts.filter({
                        "ReasoningWeb.useEffect": (p)=>p.live
                    }["ReasoningWeb.useEffect"]),
                    allSpokes: pts.map({
                        "ReasoningWeb.useEffect": (p)=>p.spoke
                    }["ReasoningWeb.useEffect"])
                };
            } else {
                // mini — calm core, on-demand bloom.
                ;
                [
                    34,
                    64
                ].forEach({
                    "ReasoningWeb.useEffect": (r)=>ringsG.append(mk('circle', {
                            cx: AX,
                            cy: AY,
                            r,
                            fill: 'none',
                            stroke: P.ring,
                            opacity: 0.3,
                            'stroke-width': 1,
                            'stroke-dasharray': '1 7'
                        }))
                }["ReasoningWeb.useEffect"]);
                const bloomEls = [];
                let fadeT = null;
                const bloomOne = {
                    "ReasoningWeb.useEffect.bloomOne": (id, angDeg, store)=>{
                        const info = META[id];
                        if (!info) return;
                        const a = angDeg * Math.PI / 180, R = 98;
                        const nx = AX + R * Math.cos(a), ny = AY + R * Math.sin(a);
                        const cpx = AX + (nx - AX) * 0.5 - (ny - AY) * 0.18, cpy = AY + (ny - AY) * 0.5 + (nx - AX) * 0.18;
                        const sp = mk('path', {
                            d: `M${AX} ${AY} Q${cpx} ${cpy} ${nx} ${ny}`,
                            fill: 'none',
                            stroke: info.col,
                            'stroke-width': 1.6,
                            opacity: 0
                        });
                        spokesG.append(sp);
                        store.push(sp);
                        sp.style.transition = 'opacity .3s';
                        requestAnimationFrame({
                            "ReasoningWeb.useEffect.bloomOne": ()=>sp.setAttribute('opacity', 0.5)
                        }["ReasoningWeb.useEffect.bloomOne"]);
                        const until = performance.now() + 1100;
                        const stream = {
                            "ReasoningWeb.useEffect.bloomOne.stream": ()=>{
                                if (performance.now() < until) {
                                    spawn(sp, false);
                                    setTimeout(stream, 105);
                                }
                            }
                        }["ReasoningWeb.useEffect.bloomOne.stream"];
                        stream();
                        setTimeout({
                            "ReasoningWeb.useEffect.bloomOne": ()=>{
                                const g = mk('circle', {
                                    cx: nx,
                                    cy: ny,
                                    r: 0,
                                    fill: info.col,
                                    filter: 'url(#rw-glow)'
                                });
                                nodesG.append(g);
                                store.push(g);
                                g.style.transition = 'r .3s';
                                requestAnimationFrame({
                                    "ReasoningWeb.useEffect.bloomOne": ()=>g.setAttribute('r', 6.5)
                                }["ReasoningWeb.useEffect.bloomOne"]);
                                const ux = (nx - AX) / R, uy = (ny - AY) / R;
                                const t = mk('text', {
                                    x: nx + ux * 13,
                                    y: ny + uy * 13 + (Math.abs(uy) < 0.3 ? 4 : 0),
                                    'text-anchor': ux > 0.3 ? 'start' : ux < -0.3 ? 'end' : 'middle',
                                    'font-size': 12,
                                    'font-family': 'inherit',
                                    fill: P.label,
                                    opacity: 0
                                });
                                t.textContent = info.label;
                                nodesG.append(t);
                                store.push(t);
                                t.style.transition = 'opacity .35s';
                                requestAnimationFrame({
                                    "ReasoningWeb.useEffect.bloomOne": ()=>t.setAttribute('opacity', 1)
                                }["ReasoningWeb.useEffect.bloomOne"]);
                            }
                        }["ReasoningWeb.useEffect.bloomOne"], 520);
                    }
                }["ReasoningWeb.useEffect.bloomOne"];
                fire = ({
                    "ReasoningWeb.useEffect": (ids)=>{
                        if (fadeT) clearTimeout(fadeT);
                        bloomEls.forEach({
                            "ReasoningWeb.useEffect": (e)=>e.remove()
                        }["ReasoningWeb.useEffect"]);
                        bloomEls.length = 0;
                        const c = ids.length, layouts = {
                            1: [
                                -48
                            ],
                            2: [
                                -74,
                                -20
                            ],
                            3: [
                                -118,
                                -62,
                                -8
                            ]
                        };
                        const angs = layouts[c] || ids.map({
                            "ReasoningWeb.useEffect": (_, j)=>-90 + (j - (c - 1) / 2) * 46
                        }["ReasoningWeb.useEffect"]);
                        ids.forEach({
                            "ReasoningWeb.useEffect": (id, k)=>setTimeout({
                                    "ReasoningWeb.useEffect": ()=>bloomOne(id, angs[k], bloomEls)
                                }["ReasoningWeb.useEffect"], k * 200)
                        }["ReasoningWeb.useEffect"]);
                        fadeT = setTimeout({
                            "ReasoningWeb.useEffect": ()=>{
                                bloomEls.forEach({
                                    "ReasoningWeb.useEffect": (e)=>{
                                        e.style.transition = 'opacity .6s';
                                        e.setAttribute('opacity', 0);
                                    }
                                }["ReasoningWeb.useEffect"]);
                                setTimeout({
                                    "ReasoningWeb.useEffect": ()=>{
                                        bloomEls.forEach({
                                            "ReasoningWeb.useEffect": (e)=>e.remove()
                                        }["ReasoningWeb.useEffect"]);
                                        bloomEls.length = 0;
                                    }
                                }["ReasoningWeb.useEffect"], 650);
                            }
                        }["ReasoningWeb.useEffect"], c * 200 + 2600);
                    }
                })["ReasoningWeb.useEffect"];
                apiRef.current = {
                    fire,
                    liveNodes: []
                };
            }
            let raf = 0, last = performance.now(), phase = 0, nextAmbient = last + 1200;
            const loop = {
                "ReasoningWeb.useEffect.loop": (t)=>{
                    const dt = Math.min(0.05, (t - last) / 1000);
                    last = t;
                    const lvl = LEVEL[stateRef.current] ?? 0.4;
                    const awake = stateRef.current !== 'standby';
                    // One phase clock that runs FASTER when Apex is awake — drives all the glow/pulsing, so the
                    // whole web visibly quickens the moment Apex wakes (no period jump: we accumulate phase).
                    phase += dt * (0.85 + 1.9 * lvl);
                    const k = (Math.sin(phase) + 1) / 2;
                    if (!coreless) {
                        gold.setAttribute('r', 9 + 4 * lvl + (1.4 + 1.8 * lvl) * k);
                        hot.setAttribute('r', 3.4 + 1.2 * lvl + 1 * k);
                        halo.setAttribute('r', 26 + 8 * lvl + 5 * k);
                        halo.setAttribute('opacity', 0.08 + 0.1 * lvl + 0.06 * k);
                        ring.setAttribute('r', 18 + 2.4 * k);
                        ring.setAttribute('opacity', 0.4 + 0.25 * lvl + 0.18 * k);
                    }
                    // Every node breathes on its OWN phase (ordered chaos — never all at once).
                    for(let i = 0; i < allNodes.length; i++){
                        const n = allNodes[i];
                        if (!n.halo) continue;
                        const kk = (Math.sin(phase * 0.85 + n.phase) + 1) / 2;
                        n.halo.setAttribute('opacity', (n.live ? 0.16 : 0.09) + (n.live ? 0.30 : 0.18) * kk);
                        n.halo.setAttribute('r', n.haloR + 2 * kk);
                    }
                    // Ambient "thinking" — a constant gentle drift of faint motes from the core out to ALL parts.
                    // Denser + faster when Apex is awake (two at a time), so the whole web feels alive.
                    if (mode === 'full' && t > nextAmbient && live.length < (awake ? 18 : 8)) {
                        const sp = apiRef.current.allSpokes;
                        if (sp.length) {
                            spawn(sp[Math.random() * sp.length | 0], true);
                            if (awake && Math.random() < 0.6) spawn(sp[Math.random() * sp.length | 0], true);
                        }
                        const base = 470 - 330 * lvl;
                        nextAmbient = t + base * (0.5 + Math.random() * 0.7);
                    }
                    for(let i = live.length - 1; i >= 0; i--){
                        const p = live[i], pr = (t - p.born) / 620;
                        if (pr >= 1) {
                            p.el.remove();
                            live.splice(i, 1);
                            continue;
                        }
                        const q = p.spoke.getPointAtLength(pr * p.L);
                        p.el.setAttribute('cx', q.x);
                        p.el.setAttribute('cy', q.y);
                        p.el.setAttribute('opacity', (p.faint ? 0.4 : 0.9) * Math.sin(pr * Math.PI));
                    }
                    raf = requestAnimationFrame(loop);
                }
            }["ReasoningWeb.useEffect.loop"];
            raf = requestAnimationFrame(loop);
            return ({
                "ReasoningWeb.useEffect": ()=>{
                    cancelAnimationFrame(raf);
                    apiRef.current = null;
                    svg.replaceChildren();
                }
            })["ReasoningWeb.useEffect"];
        }
    }["ReasoningWeb.useEffect"], [
        mode,
        coreless,
        roster,
        anchor,
        viewBox,
        traces
    ]);
    (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useEffect"])({
        "ReasoningWeb.useEffect": ()=>{
            if (!trace || !apiRef.current) return;
            const ids = (trace.trace || []).map({
                "ReasoningWeb.useEffect.ids": (h)=>nodeIdFromHelper(h.helper)
            }["ReasoningWeb.useEffect.ids"]).filter({
                "ReasoningWeb.useEffect.ids": (id)=>META[id]
            }["ReasoningWeb.useEffect.ids"]);
            if (ids.length) apiRef.current.fire(ids);
        }
    }["ReasoningWeb.useEffect"], [
        trace?.n
    ]);
    return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["Fragment"], {
        children: [
            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("style", {
                children: `@keyframes rwTwinkle{0%,100%{opacity:.14}50%{opacity:.42}}@keyframes rwFlow{to{stroke-dashoffset:-14}}`
            }, void 0, false, {
                fileName: "[project]/components/ReasoningWeb.jsx",
                lineNumber: 317,
                columnNumber: 7
            }, this),
            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("svg", {
                ref: svgRef,
                width: "100%",
                height: "100%",
                viewBox: viewBox || "0 0 680 480",
                preserveAspectRatio: "xMidYMid meet",
                style: {
                    fontFamily: 'inherit',
                    pointerEvents: 'none',
                    overflow: 'visible'
                },
                role: "img",
                "aria-label": "Apex reasoning web"
            }, void 0, false, {
                fileName: "[project]/components/ReasoningWeb.jsx",
                lineNumber: 318,
                columnNumber: 7
            }, this)
        ]
    }, void 0, true, {
        fileName: "[project]/components/ReasoningWeb.jsx",
        lineNumber: 316,
        columnNumber: 5
    }, this);
}
_s(ReasoningWeb, "rEmTxabnwYcGxwxqGio9Ha1lENk=");
_c = ReasoningWeb;
var _c;
__turbopack_context__.k.register(_c, "ReasoningWeb");
if (typeof globalThis.$RefreshHelpers$ === 'object' && globalThis.$RefreshHelpers !== null) {
    __turbopack_context__.k.registerExports(__turbopack_context__.m, globalThis.$RefreshHelpers$);
}
}),
"[project]/components/SecurityModal.tsx [app-client] (ecmascript)", ((__turbopack_context__) => {
"use strict";

__turbopack_context__.s([
    "default",
    ()=>SecurityModal
]);
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/next/dist/compiled/react/jsx-dev-runtime.js [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/next/dist/compiled/react/index.js [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$circle$2d$check$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__CheckCircle2$3e$__ = __turbopack_context__.i("[project]/node_modules/lucide-react/dist/esm/icons/circle-check.js [app-client] (ecmascript) <export default as CheckCircle2>");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$copy$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__Copy$3e$__ = __turbopack_context__.i("[project]/node_modules/lucide-react/dist/esm/icons/copy.js [app-client] (ecmascript) <export default as Copy>");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$file$2d$search$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__FileSearch$3e$__ = __turbopack_context__.i("[project]/node_modules/lucide-react/dist/esm/icons/file-search.js [app-client] (ecmascript) <export default as FileSearch>");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$globe$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__Globe$3e$__ = __turbopack_context__.i("[project]/node_modules/lucide-react/dist/esm/icons/globe.js [app-client] (ecmascript) <export default as Globe>");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$key$2d$round$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__KeyRound$3e$__ = __turbopack_context__.i("[project]/node_modules/lucide-react/dist/esm/icons/key-round.js [app-client] (ecmascript) <export default as KeyRound>");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$lock$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__Lock$3e$__ = __turbopack_context__.i("[project]/node_modules/lucide-react/dist/esm/icons/lock.js [app-client] (ecmascript) <export default as Lock>");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$power$2d$off$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__PowerOff$3e$__ = __turbopack_context__.i("[project]/node_modules/lucide-react/dist/esm/icons/power-off.js [app-client] (ecmascript) <export default as PowerOff>");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$shield$2d$check$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__ShieldCheck$3e$__ = __turbopack_context__.i("[project]/node_modules/lucide-react/dist/esm/icons/shield-check.js [app-client] (ecmascript) <export default as ShieldCheck>");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$x$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__X$3e$__ = __turbopack_context__.i("[project]/node_modules/lucide-react/dist/esm/icons/x.js [app-client] (ecmascript) <export default as X>");
var __TURBOPACK__imported__module__$5b$project$5d2f$components$2f$JarvisBridge$2e$tsx__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/components/JarvisBridge.tsx [app-client] (ecmascript)");
;
var _s = __turbopack_context__.k.signature();
"use client";
;
;
;
const GREEN = "#3be38a";
const RED = "#ff5d6c";
function SecurityModal() {
    _s();
    const { securityModalOpen, setSecurityModalOpen, theme } = (0, __TURBOPACK__imported__module__$5b$project$5d2f$components$2f$JarvisBridge$2e$tsx__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useJarvis"])();
    const [tab, setTab] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])("vault");
    const [sec, setSec] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])(null);
    const [auditQuery, setAuditQuery] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])("");
    const [statusMsg, setStatusMsg] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])("");
    // Portal creation form
    const [pTitle, setPTitle] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])("");
    const [pBody, setPBody] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])("");
    const [pHours, setPHours] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])(24);
    const [pMaxViews, setPMaxViews] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])(50);
    const [latestPortalUrl, setLatestPortalUrl] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])("");
    const refresh = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useCallback"])({
        "SecurityModal.useCallback[refresh]": async ()=>{
            try {
                const r = await fetch("/api/hud/security");
                if (r.ok) {
                    const j = await r.json();
                    if (j.security) setSec(j.security);
                }
            } catch  {}
        }
    }["SecurityModal.useCallback[refresh]"], []);
    (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useEffect"])({
        "SecurityModal.useEffect": ()=>{
            if (securityModalOpen) {
                refresh();
                setStatusMsg("");
            }
        }
    }["SecurityModal.useEffect"], [
        securityModalOpen,
        refresh
    ]);
    if (!securityModalOpen) return null;
    const PRIMARY = theme.primary;
    const SECONDARY = theme.secondary;
    const post = async (payload)=>{
        const r = await fetch("/api/hud/action", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(payload)
        });
        const j = await r.json();
        if (j.security) setSec(j.security);
        return j;
    };
    const onSearchAudit = async (e)=>{
        e.preventDefault();
        const j = await post({
            action: "audit_search",
            query: auditQuery
        });
        if (Array.isArray(j.audit_logs) && sec) {
            setSec({
                ...sec,
                audit_logs: j.audit_logs
            });
        }
    };
    const onCreatePortal = async (e)=>{
        e.preventDefault();
        if (!pBody.trim()) return;
        const j = await post({
            action: "portal_create",
            title: pTitle.trim() || "Shared JARVIS Brief",
            content_body: pBody.trim(),
            expires_hours: pHours,
            max_views: pMaxViews
        });
        if (j.ok && j.portal?.path) {
            const fullUrl = `${window.location.origin}${j.portal.path}`;
            setLatestPortalUrl(fullUrl);
            setPTitle("");
            setPBody("");
            setStatusMsg("Created scoped read-only Guest Portal.");
        } else if (j.error) {
            setStatusMsg(j.error);
        }
    };
    return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
        role: "dialog",
        "aria-modal": "true",
        "aria-label": "Security Vault, Audit Log & Guest Portals",
        style: {
            position: "fixed",
            inset: 0,
            zIndex: 85,
            background: "rgba(2, 5, 12, 0.8)",
            backdropFilter: "blur(18px)",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            padding: 18
        },
        children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
            style: {
                width: "min(960px, 96vw)",
                height: "min(730px, 90vh)",
                background: theme.drawerBg,
                border: `1px solid ${PRIMARY}44`,
                borderRadius: 20,
                boxShadow: "0 24px 80px rgba(0,0,0,0.85)",
                display: "flex",
                flexDirection: "column",
                overflow: "hidden"
            },
            children: [
                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                    style: {
                        display: "flex",
                        alignItems: "center",
                        gap: 10,
                        padding: "14px 22px",
                        borderBottom: `1px solid ${PRIMARY}26`
                    },
                    children: [
                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$shield$2d$check$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__ShieldCheck$3e$__["ShieldCheck"], {
                            size: 17,
                            color: PRIMARY
                        }, void 0, false, {
                            fileName: "[project]/components/SecurityModal.tsx",
                            lineNumber: 180,
                            columnNumber: 11
                        }, this),
                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                            style: {
                                flex: 1
                            },
                            children: [
                                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                    style: {
                                        fontFamily: "var(--font-mono)",
                                        fontSize: 11,
                                        letterSpacing: "0.24em",
                                        color: PRIMARY
                                    },
                                    children: "SHIELD · ENCRYPTED VAULT, TAMPER-EVIDENT AUDIT & PORTALS"
                                }, void 0, false, {
                                    fileName: "[project]/components/SecurityModal.tsx",
                                    lineNumber: 182,
                                    columnNumber: 13
                                }, this),
                                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                    style: {
                                        fontSize: 11.5,
                                        color: "rgba(240,237,232,0.58)",
                                        marginTop: 2
                                    },
                                    children: [
                                        "Cipher: ",
                                        sec?.cipher || "AES-256-GCM",
                                        " · Chain:",
                                        " ",
                                        sec?.chain?.valid ? `VERIFIED (${sec.chain.checked} entries)` : "CHECK REQUIRED"
                                    ]
                                }, void 0, true, {
                                    fileName: "[project]/components/SecurityModal.tsx",
                                    lineNumber: 192,
                                    columnNumber: 13
                                }, this)
                            ]
                        }, void 0, true, {
                            fileName: "[project]/components/SecurityModal.tsx",
                            lineNumber: 181,
                            columnNumber: 11
                        }, this),
                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("button", {
                            type: "button",
                            onClick: ()=>setSecurityModalOpen(false),
                            style: {
                                background: "none",
                                border: "none",
                                color: "rgba(240,237,232,0.6)",
                                cursor: "pointer"
                            },
                            children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$x$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__X$3e$__["X"], {
                                size: 18
                            }, void 0, false, {
                                fileName: "[project]/components/SecurityModal.tsx",
                                lineNumber: 209,
                                columnNumber: 13
                            }, this)
                        }, void 0, false, {
                            fileName: "[project]/components/SecurityModal.tsx",
                            lineNumber: 199,
                            columnNumber: 11
                        }, this)
                    ]
                }, void 0, true, {
                    fileName: "[project]/components/SecurityModal.tsx",
                    lineNumber: 171,
                    columnNumber: 9
                }, this),
                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                    style: {
                        display: "flex",
                        gap: 8,
                        padding: "10px 22px",
                        borderBottom: "1px solid rgba(255,255,255,0.07)"
                    },
                    children: [
                        [
                            {
                                id: "vault",
                                label: "CREDENTIAL VAULT",
                                icon: __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$lock$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__Lock$3e$__["Lock"]
                            },
                            {
                                id: "audit",
                                label: `AUDIT CHAIN (${sec?.audit_logs?.length || 0})`,
                                icon: __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$file$2d$search$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__FileSearch$3e$__["FileSearch"]
                            },
                            {
                                id: "portals",
                                label: `GUEST PORTALS (${sec?.portals?.length || 0})`,
                                icon: __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$globe$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__Globe$3e$__["Globe"]
                            }
                        ].map((t)=>{
                            const Icon = t.icon;
                            const active = tab === t.id;
                            return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("button", {
                                type: "button",
                                onClick: ()=>setTab(t.id),
                                style: {
                                    display: "inline-flex",
                                    alignItems: "center",
                                    gap: 6,
                                    padding: "7px 13px",
                                    borderRadius: 999,
                                    border: `1px solid ${active ? PRIMARY : "rgba(255,255,255,0.12)"}`,
                                    background: active ? `${PRIMARY}22` : "transparent",
                                    color: active ? PRIMARY : "rgba(240,237,232,0.7)",
                                    fontFamily: "var(--font-mono)",
                                    fontSize: 10,
                                    letterSpacing: "0.12em",
                                    cursor: "pointer"
                                },
                                children: [
                                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(Icon, {
                                        size: 12
                                    }, void 0, false, {
                                        fileName: "[project]/components/SecurityModal.tsx",
                                        lineNumber: 259,
                                        columnNumber: 17
                                    }, this),
                                    t.label
                                ]
                            }, t.id, true, {
                                fileName: "[project]/components/SecurityModal.tsx",
                                lineNumber: 240,
                                columnNumber: 15
                            }, this);
                        }),
                        statusMsg && /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("span", {
                            style: {
                                marginLeft: "auto",
                                alignSelf: "center",
                                fontFamily: "var(--font-mono)",
                                fontSize: 10,
                                color: GREEN
                            },
                            children: statusMsg
                        }, void 0, false, {
                            fileName: "[project]/components/SecurityModal.tsx",
                            lineNumber: 265,
                            columnNumber: 13
                        }, this)
                    ]
                }, void 0, true, {
                    fileName: "[project]/components/SecurityModal.tsx",
                    lineNumber: 214,
                    columnNumber: 9
                }, this),
                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                    style: {
                        flex: 1,
                        overflowY: "auto",
                        padding: "18px 22px"
                    },
                    children: [
                        tab === "vault" && /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                            style: {
                                display: "flex",
                                flexDirection: "column",
                                gap: 16
                            },
                            children: [
                                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                    style: {
                                        display: "grid",
                                        gridTemplateColumns: "repeat(auto-fit, minmax(240px, 1fr))",
                                        gap: 14
                                    },
                                    children: [
                                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                            style: {
                                                padding: 16,
                                                borderRadius: 14,
                                                background: "rgba(255,255,255,0.025)",
                                                border: `1px solid ${GREEN}44`
                                            },
                                            children: [
                                                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                                    style: {
                                                        fontFamily: "var(--font-mono)",
                                                        fontSize: 10,
                                                        color: GREEN,
                                                        letterSpacing: "0.14em"
                                                    },
                                                    children: "AT-REST CIPHER"
                                                }, void 0, false, {
                                                    fileName: "[project]/components/SecurityModal.tsx",
                                                    lineNumber: 298,
                                                    columnNumber: 19
                                                }, this),
                                                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                                    style: {
                                                        fontSize: 17,
                                                        fontWeight: 600,
                                                        marginTop: 6
                                                    },
                                                    children: sec?.cipher || "AES-256-GCM"
                                                }, void 0, false, {
                                                    fileName: "[project]/components/SecurityModal.tsx",
                                                    lineNumber: 308,
                                                    columnNumber: 19
                                                }, this),
                                                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                                    style: {
                                                        fontSize: 11.5,
                                                        color: "rgba(240,237,232,0.6)",
                                                        marginTop: 4
                                                    },
                                                    children: "256-bit local master key (`0600` permissions) — never leaves your device."
                                                }, void 0, false, {
                                                    fileName: "[project]/components/SecurityModal.tsx",
                                                    lineNumber: 311,
                                                    columnNumber: 19
                                                }, this)
                                            ]
                                        }, void 0, true, {
                                            fileName: "[project]/components/SecurityModal.tsx",
                                            lineNumber: 290,
                                            columnNumber: 17
                                        }, this),
                                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                            style: {
                                                padding: 16,
                                                borderRadius: 14,
                                                background: "rgba(255,255,255,0.025)",
                                                border: `1px solid ${PRIMARY}38`
                                            },
                                            children: [
                                                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                                    style: {
                                                        fontFamily: "var(--font-mono)",
                                                        fontSize: 10,
                                                        color: PRIMARY,
                                                        letterSpacing: "0.14em"
                                                    },
                                                    children: "ENCRYPTED SECRETS ON DISK"
                                                }, void 0, false, {
                                                    fileName: "[project]/components/SecurityModal.tsx",
                                                    lineNumber: 324,
                                                    columnNumber: 19
                                                }, this),
                                                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                                    style: {
                                                        fontSize: 17,
                                                        fontWeight: 600,
                                                        marginTop: 6
                                                    },
                                                    children: [
                                                        (sec?.encrypted_account_secrets || 0) + (sec?.encrypted_config_secrets || 0),
                                                        " ",
                                                        "protected tokens"
                                                    ]
                                                }, void 0, true, {
                                                    fileName: "[project]/components/SecurityModal.tsx",
                                                    lineNumber: 334,
                                                    columnNumber: 19
                                                }, this),
                                                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                                    style: {
                                                        fontSize: 11.5,
                                                        color: "rgba(240,237,232,0.6)",
                                                        marginTop: 4
                                                    },
                                                    children: [
                                                        "Accounts Vault: ",
                                                        sec?.encrypted_account_secrets || 0,
                                                        " · Config Vault:",
                                                        " ",
                                                        sec?.encrypted_config_secrets || 0
                                                    ]
                                                }, void 0, true, {
                                                    fileName: "[project]/components/SecurityModal.tsx",
                                                    lineNumber: 339,
                                                    columnNumber: 19
                                                }, this)
                                            ]
                                        }, void 0, true, {
                                            fileName: "[project]/components/SecurityModal.tsx",
                                            lineNumber: 316,
                                            columnNumber: 17
                                        }, this)
                                    ]
                                }, void 0, true, {
                                    fileName: "[project]/components/SecurityModal.tsx",
                                    lineNumber: 283,
                                    columnNumber: 15
                                }, this),
                                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                    style: {
                                        display: "flex",
                                        flexWrap: "wrap",
                                        gap: 10
                                    },
                                    children: [
                                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("button", {
                                            type: "button",
                                            onClick: async ()=>{
                                                const j = await post({
                                                    action: "vault_rotate_key"
                                                });
                                                setStatusMsg(`Rotated master key & re-encrypted ${j.reencrypted_count ?? 0} secrets.`);
                                            },
                                            style: {
                                                display: "inline-flex",
                                                alignItems: "center",
                                                gap: 7,
                                                padding: "9px 16px",
                                                borderRadius: 999,
                                                border: `1px solid ${PRIMARY}66`,
                                                background: `${PRIMARY}22`,
                                                color: PRIMARY,
                                                fontFamily: "var(--font-mono)",
                                                fontSize: 10,
                                                cursor: "pointer"
                                            },
                                            children: [
                                                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$key$2d$round$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__KeyRound$3e$__["KeyRound"], {
                                                    size: 12
                                                }, void 0, false, {
                                                    fileName: "[project]/components/SecurityModal.tsx",
                                                    lineNumber: 369,
                                                    columnNumber: 19
                                                }, this),
                                                " ROTATE 256-BIT MASTER KEY"
                                            ]
                                        }, void 0, true, {
                                            fileName: "[project]/components/SecurityModal.tsx",
                                            lineNumber: 347,
                                            columnNumber: 17
                                        }, this),
                                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("button", {
                                            type: "button",
                                            onClick: async ()=>{
                                                const enable = (sec?.encrypted_config_secrets || 0) === 0;
                                                await post({
                                                    action: "vault_encrypt_config",
                                                    enabled: enable
                                                });
                                                setStatusMsg(enable ? "Encrypted config/api_keys.json secrets at rest." : "Restored plaintext compatibility on config/api_keys.json.");
                                            },
                                            style: {
                                                display: "inline-flex",
                                                alignItems: "center",
                                                gap: 7,
                                                padding: "9px 16px",
                                                borderRadius: 999,
                                                border: `1px solid ${SECONDARY}66`,
                                                background: `${SECONDARY}1f`,
                                                color: SECONDARY,
                                                fontFamily: "var(--font-mono)",
                                                fontSize: 10,
                                                cursor: "pointer"
                                            },
                                            children: [
                                                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$lock$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__Lock$3e$__["Lock"], {
                                                    size: 12
                                                }, void 0, false, {
                                                    fileName: "[project]/components/SecurityModal.tsx",
                                                    lineNumber: 397,
                                                    columnNumber: 19
                                                }, this),
                                                (sec?.encrypted_config_secrets || 0) > 0 ? "STRICT CONFIG ENCRYPTION: ON" : "ENABLE STRICT API_KEYS.JSON ENCRYPTION"
                                            ]
                                        }, void 0, true, {
                                            fileName: "[project]/components/SecurityModal.tsx",
                                            lineNumber: 372,
                                            columnNumber: 17
                                        }, this)
                                    ]
                                }, void 0, true, {
                                    fileName: "[project]/components/SecurityModal.tsx",
                                    lineNumber: 346,
                                    columnNumber: 15
                                }, this)
                            ]
                        }, void 0, true, {
                            fileName: "[project]/components/SecurityModal.tsx",
                            lineNumber: 282,
                            columnNumber: 13
                        }, this),
                        tab === "audit" && /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                            style: {
                                display: "flex",
                                flexDirection: "column",
                                gap: 12
                            },
                            children: [
                                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                    style: {
                                        display: "flex",
                                        gap: 8,
                                        alignItems: "center"
                                    },
                                    children: [
                                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("form", {
                                            onSubmit: onSearchAudit,
                                            style: {
                                                flex: 1,
                                                display: "flex",
                                                gap: 8
                                            },
                                            children: [
                                                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("input", {
                                                    value: auditQuery,
                                                    onChange: (e)=>setAuditQuery(e.target.value),
                                                    placeholder: "Search tamper-evident action logs…",
                                                    style: {
                                                        flex: 1,
                                                        padding: "8px 12px",
                                                        borderRadius: 8,
                                                        border: "1px solid rgba(255,255,255,0.14)",
                                                        background: "rgba(0,0,0,0.35)",
                                                        color: "#f0ede8",
                                                        fontSize: 12
                                                    }
                                                }, void 0, false, {
                                                    fileName: "[project]/components/SecurityModal.tsx",
                                                    lineNumber: 410,
                                                    columnNumber: 19
                                                }, this),
                                                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("button", {
                                                    type: "submit",
                                                    style: {
                                                        padding: "8px 14px",
                                                        borderRadius: 8,
                                                        border: `1px solid ${PRIMARY}55`,
                                                        background: `${PRIMARY}1c`,
                                                        color: PRIMARY,
                                                        fontFamily: "var(--font-mono)",
                                                        fontSize: 10,
                                                        cursor: "pointer"
                                                    },
                                                    children: "SEARCH"
                                                }, void 0, false, {
                                                    fileName: "[project]/components/SecurityModal.tsx",
                                                    lineNumber: 424,
                                                    columnNumber: 19
                                                }, this)
                                            ]
                                        }, void 0, true, {
                                            fileName: "[project]/components/SecurityModal.tsx",
                                            lineNumber: 409,
                                            columnNumber: 17
                                        }, this),
                                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("button", {
                                            type: "button",
                                            onClick: async ()=>{
                                                const j = await post({
                                                    action: "audit_verify"
                                                });
                                                setStatusMsg(j.chain?.valid ? `SHA-256 Chain Verified (${j.chain.checked} entries intact)` : `TAMPER DETECTED at entry #${j.chain?.broken_at_id}`);
                                            },
                                            style: {
                                                display: "inline-flex",
                                                alignItems: "center",
                                                gap: 6,
                                                padding: "8px 14px",
                                                borderRadius: 8,
                                                border: `1px solid ${GREEN}66`,
                                                background: `${GREEN}1a`,
                                                color: GREEN,
                                                fontFamily: "var(--font-mono)",
                                                fontSize: 10,
                                                cursor: "pointer"
                                            },
                                            children: [
                                                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$circle$2d$check$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__CheckCircle2$3e$__["CheckCircle2"], {
                                                    size: 12
                                                }, void 0, false, {
                                                    fileName: "[project]/components/SecurityModal.tsx",
                                                    lineNumber: 465,
                                                    columnNumber: 19
                                                }, this),
                                                " VERIFY HASH CHAIN"
                                            ]
                                        }, void 0, true, {
                                            fileName: "[project]/components/SecurityModal.tsx",
                                            lineNumber: 441,
                                            columnNumber: 17
                                        }, this)
                                    ]
                                }, void 0, true, {
                                    fileName: "[project]/components/SecurityModal.tsx",
                                    lineNumber: 408,
                                    columnNumber: 15
                                }, this),
                                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                    style: {
                                        display: "flex",
                                        flexDirection: "column",
                                        gap: 6
                                    },
                                    children: (sec?.audit_logs || []).map((row)=>/*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                            style: {
                                                padding: "9px 12px",
                                                borderRadius: 9,
                                                background: "rgba(255,255,255,0.025)",
                                                border: "1px solid rgba(255,255,255,0.08)",
                                                fontFamily: "var(--font-mono)",
                                                fontSize: 11
                                            },
                                            children: [
                                                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                                    style: {
                                                        display: "flex",
                                                        gap: 8,
                                                        alignItems: "center"
                                                    },
                                                    children: [
                                                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("span", {
                                                            style: {
                                                                color: PRIMARY
                                                            },
                                                            children: [
                                                                "#",
                                                                row.id
                                                            ]
                                                        }, void 0, true, {
                                                            fileName: "[project]/components/SecurityModal.tsx",
                                                            lineNumber: 483,
                                                            columnNumber: 23
                                                        }, this),
                                                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("span", {
                                                            style: {
                                                                color: SECONDARY
                                                            },
                                                            children: row.action
                                                        }, void 0, false, {
                                                            fileName: "[project]/components/SecurityModal.tsx",
                                                            lineNumber: 484,
                                                            columnNumber: 23
                                                        }, this),
                                                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("span", {
                                                            style: {
                                                                color: "rgba(240,237,232,0.5)"
                                                            },
                                                            children: [
                                                                "by ",
                                                                row.actor
                                                            ]
                                                        }, void 0, true, {
                                                            fileName: "[project]/components/SecurityModal.tsx",
                                                            lineNumber: 485,
                                                            columnNumber: 23
                                                        }, this),
                                                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("span", {
                                                            style: {
                                                                flex: 1
                                                            }
                                                        }, void 0, false, {
                                                            fileName: "[project]/components/SecurityModal.tsx",
                                                            lineNumber: 486,
                                                            columnNumber: 23
                                                        }, this),
                                                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("span", {
                                                            style: {
                                                                color: "rgba(240,237,232,0.45)",
                                                                fontSize: 10
                                                            },
                                                            children: [
                                                                row.time_str,
                                                                " · sha256:",
                                                                row.entry_hash
                                                            ]
                                                        }, void 0, true, {
                                                            fileName: "[project]/components/SecurityModal.tsx",
                                                            lineNumber: 487,
                                                            columnNumber: 23
                                                        }, this)
                                                    ]
                                                }, void 0, true, {
                                                    fileName: "[project]/components/SecurityModal.tsx",
                                                    lineNumber: 482,
                                                    columnNumber: 21
                                                }, this),
                                                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                                    style: {
                                                        color: "rgba(240,237,232,0.72)",
                                                        marginTop: 4
                                                    },
                                                    children: row.result_summary || row.args_redacted
                                                }, void 0, false, {
                                                    fileName: "[project]/components/SecurityModal.tsx",
                                                    lineNumber: 491,
                                                    columnNumber: 21
                                                }, this)
                                            ]
                                        }, row.id, true, {
                                            fileName: "[project]/components/SecurityModal.tsx",
                                            lineNumber: 471,
                                            columnNumber: 19
                                        }, this))
                                }, void 0, false, {
                                    fileName: "[project]/components/SecurityModal.tsx",
                                    lineNumber: 469,
                                    columnNumber: 15
                                }, this)
                            ]
                        }, void 0, true, {
                            fileName: "[project]/components/SecurityModal.tsx",
                            lineNumber: 407,
                            columnNumber: 13
                        }, this),
                        tab === "portals" && /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                            style: {
                                display: "grid",
                                gridTemplateColumns: "1.1fr 1fr",
                                gap: 18
                            },
                            children: [
                                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                    style: {
                                        display: "flex",
                                        flexDirection: "column",
                                        gap: 10
                                    },
                                    children: [
                                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                            style: {
                                                display: "flex",
                                                alignItems: "center",
                                                gap: 8
                                            },
                                            children: [
                                                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("span", {
                                                    style: {
                                                        fontFamily: "var(--font-mono)",
                                                        fontSize: 10,
                                                        letterSpacing: "0.16em",
                                                        color: SECONDARY,
                                                        flex: 1
                                                    },
                                                    children: "SCOPED EXTERNAL GUEST PORTALS"
                                                }, void 0, false, {
                                                    fileName: "[project]/components/SecurityModal.tsx",
                                                    lineNumber: 504,
                                                    columnNumber: 19
                                                }, this),
                                                (sec?.portals?.length || 0) > 0 && /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("button", {
                                                    type: "button",
                                                    onClick: ()=>post({
                                                            action: "portal_revoke_all"
                                                        }),
                                                    style: {
                                                        display: "inline-flex",
                                                        alignItems: "center",
                                                        gap: 5,
                                                        padding: "4px 10px",
                                                        borderRadius: 999,
                                                        border: `1px solid ${RED}66`,
                                                        background: `${RED}1f`,
                                                        color: RED,
                                                        fontFamily: "var(--font-mono)",
                                                        fontSize: 9,
                                                        cursor: "pointer"
                                                    },
                                                    children: [
                                                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$power$2d$off$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__PowerOff$3e$__["PowerOff"], {
                                                            size: 10
                                                        }, void 0, false, {
                                                            fileName: "[project]/components/SecurityModal.tsx",
                                                            lineNumber: 533,
                                                            columnNumber: 23
                                                        }, this),
                                                        " SHUT OFF ALL"
                                                    ]
                                                }, void 0, true, {
                                                    fileName: "[project]/components/SecurityModal.tsx",
                                                    lineNumber: 516,
                                                    columnNumber: 21
                                                }, this)
                                            ]
                                        }, void 0, true, {
                                            fileName: "[project]/components/SecurityModal.tsx",
                                            lineNumber: 503,
                                            columnNumber: 17
                                        }, this),
                                        (sec?.portals || []).map((p)=>/*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                                style: {
                                                    padding: "11px 14px",
                                                    borderRadius: 11,
                                                    background: "rgba(255,255,255,0.025)",
                                                    border: `1px solid ${p.active ? `${GREEN}55` : "rgba(255,255,255,0.08)"}`
                                                },
                                                children: [
                                                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                                        style: {
                                                            display: "flex",
                                                            alignItems: "center",
                                                            gap: 8
                                                        },
                                                        children: [
                                                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("span", {
                                                                style: {
                                                                    fontWeight: 600,
                                                                    fontSize: 12.5
                                                                },
                                                                children: p.title
                                                            }, void 0, false, {
                                                                fileName: "[project]/components/SecurityModal.tsx",
                                                                lineNumber: 549,
                                                                columnNumber: 23
                                                            }, this),
                                                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("span", {
                                                                style: {
                                                                    fontFamily: "var(--font-mono)",
                                                                    fontSize: 9,
                                                                    color: p.active ? GREEN : RED
                                                                },
                                                                children: p.active ? "LIVE" : p.revoked ? "REVOKED" : "EXPIRED"
                                                            }, void 0, false, {
                                                                fileName: "[project]/components/SecurityModal.tsx",
                                                                lineNumber: 550,
                                                                columnNumber: 23
                                                            }, this),
                                                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("span", {
                                                                style: {
                                                                    flex: 1
                                                                }
                                                            }, void 0, false, {
                                                                fileName: "[project]/components/SecurityModal.tsx",
                                                                lineNumber: 559,
                                                                columnNumber: 23
                                                            }, this),
                                                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("span", {
                                                                style: {
                                                                    fontFamily: "var(--font-mono)",
                                                                    fontSize: 9.5
                                                                },
                                                                children: [
                                                                    "Views: ",
                                                                    p.view_count,
                                                                    "/",
                                                                    p.max_views
                                                                ]
                                                            }, void 0, true, {
                                                                fileName: "[project]/components/SecurityModal.tsx",
                                                                lineNumber: 560,
                                                                columnNumber: 23
                                                            }, this),
                                                            p.active && /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("button", {
                                                                type: "button",
                                                                onClick: ()=>post({
                                                                        action: "portal_revoke",
                                                                        portal_id: p.id
                                                                    }),
                                                                style: {
                                                                    padding: "3px 8px",
                                                                    borderRadius: 999,
                                                                    border: `1px solid ${RED}66`,
                                                                    background: "transparent",
                                                                    color: RED,
                                                                    fontFamily: "var(--font-mono)",
                                                                    fontSize: 8.5,
                                                                    cursor: "pointer"
                                                                },
                                                                children: "REVOKE"
                                                            }, void 0, false, {
                                                                fileName: "[project]/components/SecurityModal.tsx",
                                                                lineNumber: 564,
                                                                columnNumber: 25
                                                            }, this)
                                                        ]
                                                    }, void 0, true, {
                                                        fileName: "[project]/components/SecurityModal.tsx",
                                                        lineNumber: 548,
                                                        columnNumber: 21
                                                    }, this),
                                                    p.visits.length > 0 && /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                                        style: {
                                                            marginTop: 6,
                                                            paddingTop: 6,
                                                            borderTop: "1px solid rgba(255,255,255,0.06)",
                                                            fontFamily: "var(--font-mono)",
                                                            fontSize: 9.5,
                                                            color: "rgba(240,237,232,0.58)"
                                                        },
                                                        children: [
                                                            "Recent visit: ",
                                                            p.visits[0].ip,
                                                            " @ ",
                                                            p.visits[0].ts,
                                                            " (",
                                                            p.visits[0].reason,
                                                            ")"
                                                        ]
                                                    }, void 0, true, {
                                                        fileName: "[project]/components/SecurityModal.tsx",
                                                        lineNumber: 585,
                                                        columnNumber: 23
                                                    }, this)
                                                ]
                                            }, p.id, true, {
                                                fileName: "[project]/components/SecurityModal.tsx",
                                                lineNumber: 539,
                                                columnNumber: 19
                                            }, this))
                                    ]
                                }, void 0, true, {
                                    fileName: "[project]/components/SecurityModal.tsx",
                                    lineNumber: 502,
                                    columnNumber: 15
                                }, this),
                                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("form", {
                                    onSubmit: onCreatePortal,
                                    style: {
                                        padding: 15,
                                        borderRadius: 14,
                                        background: "rgba(255,255,255,0.025)",
                                        border: "1px solid rgba(255,255,255,0.09)",
                                        display: "flex",
                                        flexDirection: "column",
                                        gap: 9
                                    },
                                    children: [
                                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                            style: {
                                                fontFamily: "var(--font-mono)",
                                                fontSize: 10,
                                                letterSpacing: "0.16em",
                                                color: PRIMARY
                                            },
                                            children: "+ CREATE SCOPED GUEST PORTAL"
                                        }, void 0, false, {
                                            fileName: "[project]/components/SecurityModal.tsx",
                                            lineNumber: 614,
                                            columnNumber: 17
                                        }, this),
                                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("input", {
                                            value: pTitle,
                                            onChange: (e)=>setPTitle(e.target.value),
                                            placeholder: "Portal Title (e.g. Q4 Research Brief)",
                                            style: {
                                                padding: "8px 11px",
                                                borderRadius: 8,
                                                border: "1px solid rgba(255,255,255,0.14)",
                                                background: "rgba(0,0,0,0.35)",
                                                color: "#f0ede8",
                                                fontSize: 12
                                            }
                                        }, void 0, false, {
                                            fileName: "[project]/components/SecurityModal.tsx",
                                            lineNumber: 624,
                                            columnNumber: 17
                                        }, this),
                                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                            style: {
                                                display: "flex",
                                                gap: 8
                                            },
                                            children: [
                                                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("input", {
                                                    type: "number",
                                                    min: 1,
                                                    value: pHours,
                                                    onChange: (e)=>setPHours(Number(e.target.value) || 24),
                                                    placeholder: "Expires (hours)",
                                                    style: {
                                                        flex: 1,
                                                        padding: "8px",
                                                        borderRadius: 8,
                                                        border: "1px solid rgba(255,255,255,0.14)",
                                                        background: "rgba(0,0,0,0.35)",
                                                        color: "#f0ede8",
                                                        fontSize: 12
                                                    }
                                                }, void 0, false, {
                                                    fileName: "[project]/components/SecurityModal.tsx",
                                                    lineNumber: 638,
                                                    columnNumber: 19
                                                }, this),
                                                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("input", {
                                                    type: "number",
                                                    min: 1,
                                                    value: pMaxViews,
                                                    onChange: (e)=>setPMaxViews(Number(e.target.value) || 50),
                                                    placeholder: "Max views",
                                                    style: {
                                                        flex: 1,
                                                        padding: "8px",
                                                        borderRadius: 8,
                                                        border: "1px solid rgba(255,255,255,0.14)",
                                                        background: "rgba(0,0,0,0.35)",
                                                        color: "#f0ede8",
                                                        fontSize: 12
                                                    }
                                                }, void 0, false, {
                                                    fileName: "[project]/components/SecurityModal.tsx",
                                                    lineNumber: 654,
                                                    columnNumber: 19
                                                }, this)
                                            ]
                                        }, void 0, true, {
                                            fileName: "[project]/components/SecurityModal.tsx",
                                            lineNumber: 637,
                                            columnNumber: 17
                                        }, this),
                                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("textarea", {
                                            value: pBody,
                                            onChange: (e)=>setPBody(e.target.value),
                                            rows: 5,
                                            placeholder: "Read-only content shared at /portal/<token> (zero OS/tool access granted)…",
                                            style: {
                                                padding: "8px 11px",
                                                borderRadius: 8,
                                                border: "1px solid rgba(255,255,255,0.14)",
                                                background: "rgba(0,0,0,0.35)",
                                                color: "#f0ede8",
                                                fontSize: 12
                                            }
                                        }, void 0, false, {
                                            fileName: "[project]/components/SecurityModal.tsx",
                                            lineNumber: 671,
                                            columnNumber: 17
                                        }, this),
                                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("button", {
                                            type: "submit",
                                            style: {
                                                padding: "9px 14px",
                                                borderRadius: 9,
                                                border: `1px solid ${PRIMARY}66`,
                                                background: `${PRIMARY}22`,
                                                color: PRIMARY,
                                                fontFamily: "var(--font-mono)",
                                                fontSize: 10,
                                                cursor: "pointer"
                                            },
                                            children: "CREATE REVOCABLE PORTAL LINK"
                                        }, void 0, false, {
                                            fileName: "[project]/components/SecurityModal.tsx",
                                            lineNumber: 685,
                                            columnNumber: 17
                                        }, this),
                                        latestPortalUrl && /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                            style: {
                                                display: "flex",
                                                alignItems: "center",
                                                gap: 8,
                                                padding: "8px 10px",
                                                borderRadius: 8,
                                                background: "rgba(0,0,0,0.45)",
                                                border: `1px solid ${GREEN}55`,
                                                fontFamily: "var(--font-mono)",
                                                fontSize: 10.5,
                                                color: GREEN
                                            },
                                            children: [
                                                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("span", {
                                                    style: {
                                                        flex: 1,
                                                        overflow: "hidden",
                                                        textOverflow: "ellipsis"
                                                    },
                                                    children: latestPortalUrl
                                                }, void 0, false, {
                                                    fileName: "[project]/components/SecurityModal.tsx",
                                                    lineNumber: 716,
                                                    columnNumber: 21
                                                }, this),
                                                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("button", {
                                                    type: "button",
                                                    onClick: ()=>navigator.clipboard?.writeText(latestPortalUrl),
                                                    style: {
                                                        background: "none",
                                                        border: "none",
                                                        color: GREEN,
                                                        cursor: "pointer"
                                                    },
                                                    children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$copy$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__Copy$3e$__["Copy"], {
                                                        size: 12
                                                    }, void 0, false, {
                                                        fileName: "[project]/components/SecurityModal.tsx",
                                                        lineNumber: 729,
                                                        columnNumber: 23
                                                    }, this)
                                                }, void 0, false, {
                                                    fileName: "[project]/components/SecurityModal.tsx",
                                                    lineNumber: 719,
                                                    columnNumber: 21
                                                }, this)
                                            ]
                                        }, void 0, true, {
                                            fileName: "[project]/components/SecurityModal.tsx",
                                            lineNumber: 702,
                                            columnNumber: 19
                                        }, this)
                                    ]
                                }, void 0, true, {
                                    fileName: "[project]/components/SecurityModal.tsx",
                                    lineNumber: 602,
                                    columnNumber: 15
                                }, this)
                            ]
                        }, void 0, true, {
                            fileName: "[project]/components/SecurityModal.tsx",
                            lineNumber: 501,
                            columnNumber: 13
                        }, this)
                    ]
                }, void 0, true, {
                    fileName: "[project]/components/SecurityModal.tsx",
                    lineNumber: 280,
                    columnNumber: 9
                }, this)
            ]
        }, void 0, true, {
            fileName: "[project]/components/SecurityModal.tsx",
            lineNumber: 157,
            columnNumber: 7
        }, this)
    }, void 0, false, {
        fileName: "[project]/components/SecurityModal.tsx",
        lineNumber: 141,
        columnNumber: 5
    }, this);
}
_s(SecurityModal, "/k18D0hZBamA0NEM9KiRZPU/uI4=", false, function() {
    return [
        __TURBOPACK__imported__module__$5b$project$5d2f$components$2f$JarvisBridge$2e$tsx__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useJarvis"]
    ];
});
_c = SecurityModal;
var _c;
__turbopack_context__.k.register(_c, "SecurityModal");
if (typeof globalThis.$RefreshHelpers$ === 'object' && globalThis.$RefreshHelpers !== null) {
    __turbopack_context__.k.registerExports(__turbopack_context__.m, globalThis.$RefreshHelpers$);
}
}),
"[project]/components/SoulStudioPanel.tsx [app-client] (ecmascript)", ((__turbopack_context__) => {
"use strict";

__turbopack_context__.s([
    "default",
    ()=>SoulStudioPanel
]);
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/next/dist/compiled/react/jsx-dev-runtime.js [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$styled$2d$jsx$2f$style$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/styled-jsx/style.js [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/next/dist/compiled/react/index.js [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$activity$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__Activity$3e$__ = __turbopack_context__.i("[project]/node_modules/lucide-react/dist/esm/icons/activity.js [app-client] (ecmascript) <export default as Activity>");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$brain$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__Brain$3e$__ = __turbopack_context__.i("[project]/node_modules/lucide-react/dist/esm/icons/brain.js [app-client] (ecmascript) <export default as Brain>");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$clock$2d$3$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__Clock3$3e$__ = __turbopack_context__.i("[project]/node_modules/lucide-react/dist/esm/icons/clock-3.js [app-client] (ecmascript) <export default as Clock3>");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$download$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__Download$3e$__ = __turbopack_context__.i("[project]/node_modules/lucide-react/dist/esm/icons/download.js [app-client] (ecmascript) <export default as Download>");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$heart$2d$handshake$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__HeartHandshake$3e$__ = __turbopack_context__.i("[project]/node_modules/lucide-react/dist/esm/icons/heart-handshake.js [app-client] (ecmascript) <export default as HeartHandshake>");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$history$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__History$3e$__ = __turbopack_context__.i("[project]/node_modules/lucide-react/dist/esm/icons/history.js [app-client] (ecmascript) <export default as History>");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$rotate$2d$ccw$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__RotateCcw$3e$__ = __turbopack_context__.i("[project]/node_modules/lucide-react/dist/esm/icons/rotate-ccw.js [app-client] (ecmascript) <export default as RotateCcw>");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$shield$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__Shield$3e$__ = __turbopack_context__.i("[project]/node_modules/lucide-react/dist/esm/icons/shield.js [app-client] (ecmascript) <export default as Shield>");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$sparkles$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__Sparkles$3e$__ = __turbopack_context__.i("[project]/node_modules/lucide-react/dist/esm/icons/sparkles.js [app-client] (ecmascript) <export default as Sparkles>");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$target$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__Target$3e$__ = __turbopack_context__.i("[project]/node_modules/lucide-react/dist/esm/icons/target.js [app-client] (ecmascript) <export default as Target>");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$trash$2d$2$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__Trash2$3e$__ = __turbopack_context__.i("[project]/node_modules/lucide-react/dist/esm/icons/trash-2.js [app-client] (ecmascript) <export default as Trash2>");
;
var _s = __turbopack_context__.k.signature();
"use client";
;
;
;
const VIEWS = [
    {
        id: "identity",
        label: "IDENTITY",
        icon: __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$sparkles$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__Sparkles$3e$__["Sparkles"]
    },
    {
        id: "affect",
        label: "EXPRESSIVE",
        icon: __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$activity$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__Activity$3e$__["Activity"]
    },
    {
        id: "relationship",
        label: "RELATIONSHIP",
        icon: __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$heart$2d$handshake$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__HeartHandshake$3e$__["HeartHandshake"]
    },
    {
        id: "commitments",
        label: "COMMITMENTS",
        icon: __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$target$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__Target$3e$__["Target"]
    },
    {
        id: "initiative",
        label: "INITIATIVE",
        icon: __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$clock$2d$3$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__Clock3$3e$__["Clock3"]
    },
    {
        id: "traits",
        label: "LEARNED",
        icon: __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$brain$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__Brain$3e$__["Brain"]
    },
    {
        id: "history",
        label: "HISTORY",
        icon: __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$history$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__History$3e$__["History"]
    },
    {
        id: "privacy",
        label: "PRIVACY",
        icon: __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$shield$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__Shield$3e$__["Shield"]
    }
];
function SoulStudioPanel({ primary, secondary }) {
    _s();
    const [view, setView] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])("identity");
    const [soul, setSoul] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])(null);
    const [loading, setLoading] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])(true);
    const [error, setError] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])("");
    const [busy, setBusy] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])(false);
    const refresh = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useCallback"])({
        "SoulStudioPanel.useCallback[refresh]": async ()=>{
            setLoading(true);
            try {
                const r = await fetch("/api/hud/soul");
                const j = await r.json();
                if (!r.ok || !j.ok) throw new Error(j.error || "Soul unavailable");
                setSoul(j.soul);
                setError("");
            } catch (e) {
                setError(e instanceof Error ? e.message : "Soul unavailable");
            } finally{
                setLoading(false);
            }
        }
    }["SoulStudioPanel.useCallback[refresh]"], []);
    (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useEffect"])({
        "SoulStudioPanel.useEffect": ()=>{
            refresh();
        }
    }["SoulStudioPanel.useEffect"], [
        refresh
    ]);
    const mutate = async (payload)=>{
        if (!soul && payload.operation !== "runtime") return;
        setBusy(true);
        try {
            const r = await fetch("/api/hud/soul", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    ...payload,
                    expected_revision: soul?.revision
                })
            });
            const j = await r.json();
            if (r.status === 409) {
                await refresh();
                throw new Error("Soul changed elsewhere. Reloaded the latest revision.");
            }
            if (!r.ok || !j.ok) throw new Error(j.error || "Update failed");
            setSoul(j.soul);
            setError("");
        } catch (e) {
            setError(e instanceof Error ? e.message : "Update failed");
        } finally{
            setBusy(false);
        }
    };
    const card = {
        border: "1px solid rgba(255,255,255,.09)",
        background: "rgba(255,255,255,.025)",
        borderRadius: 12,
        padding: 14
    };
    const button = {
        border: `1px solid ${primary}66`,
        background: `${primary}18`,
        color: primary,
        borderRadius: 8,
        padding: "7px 11px",
        cursor: "pointer",
        fontFamily: "var(--font-mono)",
        fontSize: 10
    };
    if (loading) return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
        style: card,
        children: "LOADING SOUL STATE…"
    }, void 0, false, {
        fileName: "[project]/components/SoulStudioPanel.tsx",
        lineNumber: 39,
        columnNumber: 23
    }, this);
    if (!soul) return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
        style: card,
        children: [
            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                style: {
                    color: "#ff6875"
                },
                children: error || "Soul state unavailable."
            }, void 0, false, {
                fileName: "[project]/components/SoulStudioPanel.tsx",
                lineNumber: 40,
                columnNumber: 39
            }, this),
            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("button", {
                style: button,
                onClick: refresh,
                children: "RETRY"
            }, void 0, false, {
                fileName: "[project]/components/SoulStudioPanel.tsx",
                lineNumber: 40,
                columnNumber: 115
            }, this)
        ]
    }, void 0, true, {
        fileName: "[project]/components/SoulStudioPanel.tsx",
        lineNumber: 40,
        columnNumber: 21
    }, this);
    const traitNames = [
        "warmth",
        "humor",
        "formality",
        "directness",
        "challenge",
        "initiative"
    ];
    return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
        style: {
            display: "grid",
            gridTemplateColumns: "180px minmax(0,1fr)",
            gap: 16,
            minHeight: 500
        },
        className: "jsx-482121ad71d7a176" + " " + "soul-studio-layout",
        children: [
            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("aside", {
                style: {
                    ...card,
                    padding: 8,
                    display: "flex",
                    flexDirection: "column",
                    gap: 5
                },
                className: "jsx-482121ad71d7a176",
                children: [
                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                        style: {
                            padding: 9,
                            color: secondary,
                            fontFamily: "var(--font-mono)",
                            fontSize: 9,
                            letterSpacing: ".15em"
                        },
                        className: "jsx-482121ad71d7a176",
                        children: [
                            soul.presentation.archetype.toUpperCase(),
                            " · REV ",
                            soul.revision
                        ]
                    }, void 0, true, {
                        fileName: "[project]/components/SoulStudioPanel.tsx",
                        lineNumber: 44,
                        columnNumber: 7
                    }, this),
                    VIEWS.map((x)=>{
                        const I = x.icon;
                        const active = view === x.id;
                        return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("button", {
                            onClick: ()=>setView(x.id),
                            style: {
                                display: "flex",
                                gap: 8,
                                alignItems: "center",
                                padding: "9px 10px",
                                borderRadius: 8,
                                border: `1px solid ${active ? primary : "transparent"}`,
                                background: active ? `${primary}18` : "transparent",
                                color: active ? primary : "rgba(240,237,232,.68)",
                                cursor: "pointer",
                                fontSize: 10,
                                fontFamily: "var(--font-mono)"
                            },
                            className: "jsx-482121ad71d7a176",
                            children: [
                                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(I, {
                                    size: 13,
                                    className: "jsx-482121ad71d7a176"
                                }, void 0, false, {
                                    fileName: "[project]/components/SoulStudioPanel.tsx",
                                    lineNumber: 45,
                                    columnNumber: 420
                                }, this),
                                x.label
                            ]
                        }, x.id, true, {
                            fileName: "[project]/components/SoulStudioPanel.tsx",
                            lineNumber: 45,
                            columnNumber: 74
                        }, this);
                    })
                ]
            }, void 0, true, {
                fileName: "[project]/components/SoulStudioPanel.tsx",
                lineNumber: 43,
                columnNumber: 5
            }, this),
            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("section", {
                style: {
                    minWidth: 0
                },
                className: "jsx-482121ad71d7a176",
                children: [
                    (error || soul.recovery || soul.degraded) && /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                        style: {
                            ...card,
                            marginBottom: 10,
                            color: error ? "#ff6875" : "#f3bd58"
                        },
                        className: "jsx-482121ad71d7a176",
                        children: error || soul.recovery || soul.degraded
                    }, void 0, false, {
                        fileName: "[project]/components/SoulStudioPanel.tsx",
                        lineNumber: 48,
                        columnNumber: 53
                    }, this),
                    view === "identity" && /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                        style: {
                            display: "grid",
                            gap: 10
                        },
                        className: "jsx-482121ad71d7a176",
                        children: [
                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                style: card,
                                className: "jsx-482121ad71d7a176",
                                children: [
                                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("b", {
                                        className: "jsx-482121ad71d7a176",
                                        children: soul.presentation.label
                                    }, void 0, false, {
                                        fileName: "[project]/components/SoulStudioPanel.tsx",
                                        lineNumber: 49,
                                        columnNumber: 89
                                    }, this),
                                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("p", {
                                        style: {
                                            opacity: .78
                                        },
                                        className: "jsx-482121ad71d7a176",
                                        children: soul.presentation.identity_summary
                                    }, void 0, false, {
                                        fileName: "[project]/components/SoulStudioPanel.tsx",
                                        lineNumber: 49,
                                        columnNumber: 121
                                    }, this),
                                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                        style: {
                                            color: secondary,
                                            fontSize: 10,
                                            fontFamily: "var(--font-mono)"
                                        },
                                        className: "jsx-482121ad71d7a176",
                                        children: soul.presentation.presence.join(" · ").toUpperCase()
                                    }, void 0, false, {
                                        fileName: "[project]/components/SoulStudioPanel.tsx",
                                        lineNumber: 49,
                                        columnNumber: 186
                                    }, this),
                                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("p", {
                                        style: {
                                            opacity: .62,
                                            fontSize: 11
                                        },
                                        className: "jsx-482121ad71d7a176",
                                        children: soul.presentation.relationship_guidance
                                    }, void 0, false, {
                                        fileName: "[project]/components/SoulStudioPanel.tsx",
                                        lineNumber: 49,
                                        columnNumber: 319
                                    }, this)
                                ]
                            }, void 0, true, {
                                fileName: "[project]/components/SoulStudioPanel.tsx",
                                lineNumber: 49,
                                columnNumber: 71
                            }, this),
                            traitNames.map((name)=>{
                                const x = soul.identity[name];
                                return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("label", {
                                    style: card,
                                    className: "jsx-482121ad71d7a176",
                                    children: [
                                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                            style: {
                                                display: "flex",
                                                justifyContent: "space-between"
                                            },
                                            className: "jsx-482121ad71d7a176",
                                            children: [
                                                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("span", {
                                                    className: "jsx-482121ad71d7a176",
                                                    children: name.toUpperCase()
                                                }, void 0, false, {
                                                    fileName: "[project]/components/SoulStudioPanel.tsx",
                                                    lineNumber: 49,
                                                    columnNumber: 567
                                                }, this),
                                                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("b", {
                                                    style: {
                                                        color: primary
                                                    },
                                                    className: "jsx-482121ad71d7a176",
                                                    children: x.value.toFixed(2)
                                                }, void 0, false, {
                                                    fileName: "[project]/components/SoulStudioPanel.tsx",
                                                    lineNumber: 49,
                                                    columnNumber: 600
                                                }, this)
                                            ]
                                        }, void 0, true, {
                                            fileName: "[project]/components/SoulStudioPanel.tsx",
                                            lineNumber: 49,
                                            columnNumber: 506
                                        }, this),
                                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("input", {
                                            "aria-label": name,
                                            type: "range",
                                            min: x.minimum,
                                            max: x.maximum,
                                            step: "0.01",
                                            value: x.value,
                                            onChange: (e)=>setSoul({
                                                    ...soul,
                                                    identity: {
                                                        ...soul.identity,
                                                        [name]: {
                                                            ...x,
                                                            value: Number(e.target.value)
                                                        }
                                                    }
                                                }),
                                            onMouseUp: ()=>mutate({
                                                    operation: "identity",
                                                    values: {
                                                        [name]: soul.identity[name].value
                                                    }
                                                }),
                                            style: {
                                                width: "100%"
                                            },
                                            className: "jsx-482121ad71d7a176"
                                        }, void 0, false, {
                                            fileName: "[project]/components/SoulStudioPanel.tsx",
                                            lineNumber: 49,
                                            columnNumber: 657
                                        }, this)
                                    ]
                                }, name, true, {
                                    fileName: "[project]/components/SoulStudioPanel.tsx",
                                    lineNumber: 49,
                                    columnNumber: 475
                                }, this);
                            })
                        ]
                    }, void 0, true, {
                        fileName: "[project]/components/SoulStudioPanel.tsx",
                        lineNumber: 49,
                        columnNumber: 31
                    }, this),
                    view === "affect" && /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                        style: {
                            display: "grid",
                            gridTemplateColumns: "repeat(2,minmax(0,1fr))",
                            gap: 10
                        },
                        className: "jsx-482121ad71d7a176",
                        children: [
                            Object.entries(soul.affect.dimensions).map(([name, x])=>/*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                    style: card,
                                    className: "jsx-482121ad71d7a176",
                                    children: [
                                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                            style: {
                                                display: "flex",
                                                justifyContent: "space-between"
                                            },
                                            className: "jsx-482121ad71d7a176",
                                            children: [
                                                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("b", {
                                                    className: "jsx-482121ad71d7a176",
                                                    children: name.toUpperCase()
                                                }, void 0, false, {
                                                    fileName: "[project]/components/SoulStudioPanel.tsx",
                                                    lineNumber: 50,
                                                    columnNumber: 258
                                                }, this),
                                                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("span", {
                                                    style: {
                                                        color: primary
                                                    },
                                                    className: "jsx-482121ad71d7a176",
                                                    children: x.value.toFixed(2)
                                                }, void 0, false, {
                                                    fileName: "[project]/components/SoulStudioPanel.tsx",
                                                    lineNumber: 50,
                                                    columnNumber: 285
                                                }, this)
                                            ]
                                        }, void 0, true, {
                                            fileName: "[project]/components/SoulStudioPanel.tsx",
                                            lineNumber: 50,
                                            columnNumber: 197
                                        }, this),
                                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                            style: {
                                                height: 5,
                                                background: "rgba(255,255,255,.08)",
                                                margin: "10px 0"
                                            },
                                            className: "jsx-482121ad71d7a176",
                                            children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                                style: {
                                                    height: "100%",
                                                    width: `${x.value * 100}%`,
                                                    background: primary
                                                },
                                                className: "jsx-482121ad71d7a176"
                                            }, void 0, false, {
                                                fileName: "[project]/components/SoulStudioPanel.tsx",
                                                lineNumber: 50,
                                                columnNumber: 423
                                            }, this)
                                        }, void 0, false, {
                                            fileName: "[project]/components/SoulStudioPanel.tsx",
                                            lineNumber: 50,
                                            columnNumber: 348
                                        }, this),
                                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("small", {
                                            className: "jsx-482121ad71d7a176",
                                            children: [
                                                "baseline ",
                                                x.baseline.toFixed(2),
                                                " · today ",
                                                x.daily_delta >= 0 ? "+" : "",
                                                x.daily_delta.toFixed(2)
                                            ]
                                        }, void 0, true, {
                                            fileName: "[project]/components/SoulStudioPanel.tsx",
                                            lineNumber: 50,
                                            columnNumber: 502
                                        }, this)
                                    ]
                                }, name, true, {
                                    fileName: "[project]/components/SoulStudioPanel.tsx",
                                    lineNumber: 50,
                                    columnNumber: 168
                                }, this)),
                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                style: {
                                    ...card,
                                    gridColumn: "1/-1"
                                },
                                className: "jsx-482121ad71d7a176",
                                children: [
                                    soul.affect.framing,
                                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                        style: {
                                            opacity: .6,
                                            marginTop: 8
                                        },
                                        className: "jsx-482121ad71d7a176",
                                        children: soul.affect.causes.join(" · ") || "No recorded causes."
                                    }, void 0, false, {
                                        fileName: "[project]/components/SoulStudioPanel.tsx",
                                        lineNumber: 50,
                                        columnNumber: 679
                                    }, this)
                                ]
                            }, void 0, true, {
                                fileName: "[project]/components/SoulStudioPanel.tsx",
                                lineNumber: 50,
                                columnNumber: 617
                            }, this)
                        ]
                    }, void 0, true, {
                        fileName: "[project]/components/SoulStudioPanel.tsx",
                        lineNumber: 50,
                        columnNumber: 29
                    }, this),
                    view === "relationship" && /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                        style: {
                            display: "grid",
                            gap: 8
                        },
                        className: "jsx-482121ad71d7a176",
                        children: [
                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                style: card,
                                className: "jsx-482121ad71d7a176",
                                children: [
                                    "STAGE · ",
                                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("b", {
                                        style: {
                                            color: primary
                                        },
                                        className: "jsx-482121ad71d7a176",
                                        children: soul.relationship.stage.toUpperCase()
                                    }, void 0, false, {
                                        fileName: "[project]/components/SoulStudioPanel.tsx",
                                        lineNumber: 51,
                                        columnNumber: 97
                                    }, this),
                                    " · ",
                                    soul.relationship.contradictions.length,
                                    " contradictions"
                                ]
                            }, void 0, true, {
                                fileName: "[project]/components/SoulStudioPanel.tsx",
                                lineNumber: 51,
                                columnNumber: 71
                            }, this),
                            soul.relationship.claims.length === 0 ? /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                style: card,
                                className: "jsx-482121ad71d7a176",
                                children: "No evidence-backed relationship claims yet."
                            }, void 0, false, {
                                fileName: "[project]/components/SoulStudioPanel.tsx",
                                lineNumber: 51,
                                columnNumber: 269
                            }, this) : soul.relationship.claims.map((c)=>/*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                    style: card,
                                    className: "jsx-482121ad71d7a176",
                                    children: [
                                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                            style: {
                                                display: "flex",
                                                justifyContent: "space-between"
                                            },
                                            className: "jsx-482121ad71d7a176",
                                            children: [
                                                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("b", {
                                                    className: "jsx-482121ad71d7a176",
                                                    children: [
                                                        c.kind,
                                                        " · ",
                                                        c.subject
                                                    ]
                                                }, void 0, true, {
                                                    fileName: "[project]/components/SoulStudioPanel.tsx",
                                                    lineNumber: 51,
                                                    columnNumber: 459
                                                }, this),
                                                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("span", {
                                                    className: "jsx-482121ad71d7a176",
                                                    children: [
                                                        c.status,
                                                        " · ",
                                                        c.confidence.toFixed(2)
                                                    ]
                                                }, void 0, true, {
                                                    fileName: "[project]/components/SoulStudioPanel.tsx",
                                                    lineNumber: 51,
                                                    columnNumber: 488
                                                }, this)
                                            ]
                                        }, void 0, true, {
                                            fileName: "[project]/components/SoulStudioPanel.tsx",
                                            lineNumber: 51,
                                            columnNumber: 398
                                        }, this),
                                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("p", {
                                            className: "jsx-482121ad71d7a176",
                                            children: c.value
                                        }, void 0, false, {
                                            fileName: "[project]/components/SoulStudioPanel.tsx",
                                            lineNumber: 51,
                                            columnNumber: 545
                                        }, this),
                                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("button", {
                                            style: button,
                                            onClick: ()=>mutate({
                                                    operation: "forget_relationship",
                                                    subject: c.subject
                                                }),
                                            className: "jsx-482121ad71d7a176",
                                            children: [
                                                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$trash$2d$2$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__Trash2$3e$__["Trash2"], {
                                                    size: 11
                                                }, void 0, false, {
                                                    fileName: "[project]/components/SoulStudioPanel.tsx",
                                                    lineNumber: 51,
                                                    columnNumber: 658
                                                }, this),
                                                " FORGET SUBJECT"
                                            ]
                                        }, void 0, true, {
                                            fileName: "[project]/components/SoulStudioPanel.tsx",
                                            lineNumber: 51,
                                            columnNumber: 561
                                        }, this)
                                    ]
                                }, c.id, true, {
                                    fileName: "[project]/components/SoulStudioPanel.tsx",
                                    lineNumber: 51,
                                    columnNumber: 369
                                }, this))
                        ]
                    }, void 0, true, {
                        fileName: "[project]/components/SoulStudioPanel.tsx",
                        lineNumber: 51,
                        columnNumber: 35
                    }, this),
                    view === "commitments" && /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                        style: {
                            display: "grid",
                            gap: 8
                        },
                        className: "jsx-482121ad71d7a176",
                        children: (soul.commitments || []).length === 0 ? /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                            style: card,
                            className: "jsx-482121ad71d7a176",
                            children: "No active projected commitments."
                        }, void 0, false, {
                            fileName: "[project]/components/SoulStudioPanel.tsx",
                            lineNumber: 52,
                            columnNumber: 105
                        }, this) : (soul.commitments || []).map((x, i)=>/*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                style: card,
                                className: "jsx-482121ad71d7a176",
                                children: x
                            }, i, false, {
                                fileName: "[project]/components/SoulStudioPanel.tsx",
                                lineNumber: 52,
                                columnNumber: 196
                            }, this))
                    }, void 0, false, {
                        fileName: "[project]/components/SoulStudioPanel.tsx",
                        lineNumber: 52,
                        columnNumber: 34
                    }, this),
                    view === "initiative" && /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                        style: {
                            display: "grid",
                            gap: 10
                        },
                        className: "jsx-482121ad71d7a176",
                        children: [
                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                style: card,
                                className: "jsx-482121ad71d7a176",
                                children: [
                                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("label", {
                                        className: "jsx-482121ad71d7a176",
                                        children: [
                                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("input", {
                                                type: "checkbox",
                                                checked: soul.initiative_policy.enabled,
                                                onChange: (e)=>mutate({
                                                        operation: "initiative",
                                                        values: {
                                                            enabled: e.target.checked
                                                        }
                                                    }),
                                                className: "jsx-482121ad71d7a176"
                                            }, void 0, false, {
                                                fileName: "[project]/components/SoulStudioPanel.tsx",
                                                lineNumber: 53,
                                                columnNumber: 95
                                            }, this),
                                            " ENABLE INITIATIVE"
                                        ]
                                    }, void 0, true, {
                                        fileName: "[project]/components/SoulStudioPanel.tsx",
                                        lineNumber: 53,
                                        columnNumber: 88
                                    }, this),
                                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                        style: {
                                            marginTop: 8
                                        },
                                        className: "jsx-482121ad71d7a176",
                                        children: [
                                            "Used today: ",
                                            soul.initiative_policy.interruptions_today,
                                            "/",
                                            soul.initiative_policy.daily_budget
                                        ]
                                    }, void 0, true, {
                                        fileName: "[project]/components/SoulStudioPanel.tsx",
                                        lineNumber: 53,
                                        columnNumber: 267
                                    }, this)
                                ]
                            }, void 0, true, {
                                fileName: "[project]/components/SoulStudioPanel.tsx",
                                lineNumber: 53,
                                columnNumber: 70
                            }, this),
                            [
                                "timezone",
                                "quiet_start",
                                "quiet_end",
                                "daily_budget"
                            ].map((k)=>/*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("label", {
                                    style: card,
                                    className: "jsx-482121ad71d7a176",
                                    children: [
                                        k.toUpperCase(),
                                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("input", {
                                            value: String(soul.initiative_policy[k] ?? ""),
                                            onChange: (e)=>setSoul({
                                                    ...soul,
                                                    initiative_policy: {
                                                        ...soul.initiative_policy,
                                                        [k]: k === "daily_budget" ? Number(e.target.value) : e.target.value
                                                    }
                                                }),
                                            onBlur: ()=>mutate({
                                                    operation: "initiative",
                                                    values: {
                                                        [k]: soul.initiative_policy[k]
                                                    }
                                                }),
                                            style: {
                                                display: "block",
                                                width: "100%",
                                                marginTop: 7
                                            },
                                            className: "jsx-482121ad71d7a176"
                                        }, void 0, false, {
                                            fileName: "[project]/components/SoulStudioPanel.tsx",
                                            lineNumber: 53,
                                            columnNumber: 507
                                        }, this)
                                    ]
                                }, k, true, {
                                    fileName: "[project]/components/SoulStudioPanel.tsx",
                                    lineNumber: 53,
                                    columnNumber: 462
                                }, this))
                        ]
                    }, void 0, true, {
                        fileName: "[project]/components/SoulStudioPanel.tsx",
                        lineNumber: 53,
                        columnNumber: 33
                    }, this),
                    view === "traits" && /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                        style: {
                            display: "grid",
                            gap: 8
                        },
                        className: "jsx-482121ad71d7a176",
                        children: soul.learned_traits.length === 0 ? /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                            style: card,
                            className: "jsx-482121ad71d7a176",
                            children: "No learned traits."
                        }, void 0, false, {
                            fileName: "[project]/components/SoulStudioPanel.tsx",
                            lineNumber: 54,
                            columnNumber: 97
                        }, this) : soul.learned_traits.map((t)=>/*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                style: card,
                                className: "jsx-482121ad71d7a176",
                                children: [
                                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("b", {
                                        className: "jsx-482121ad71d7a176",
                                        children: t.name
                                    }, void 0, false, {
                                        fileName: "[project]/components/SoulStudioPanel.tsx",
                                        lineNumber: 54,
                                        columnNumber: 196
                                    }, this),
                                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("span", {
                                        style: {
                                            float: "right"
                                        },
                                        className: "jsx-482121ad71d7a176",
                                        children: [
                                            t.status,
                                            " · ",
                                            t.confidence.toFixed(2)
                                        ]
                                    }, void 0, true, {
                                        fileName: "[project]/components/SoulStudioPanel.tsx",
                                        lineNumber: 54,
                                        columnNumber: 211
                                    }, this),
                                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("p", {
                                        className: "jsx-482121ad71d7a176",
                                        children: t.value
                                    }, void 0, false, {
                                        fileName: "[project]/components/SoulStudioPanel.tsx",
                                        lineNumber: 54,
                                        columnNumber: 286
                                    }, this),
                                    t.status === "candidate" && /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                        style: {
                                            display: "flex",
                                            gap: 8
                                        },
                                        className: "jsx-482121ad71d7a176",
                                        children: [
                                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("button", {
                                                style: button,
                                                onClick: ()=>mutate({
                                                        operation: "trait",
                                                        trait_id: t.id,
                                                        decision: "accept"
                                                    }),
                                                className: "jsx-482121ad71d7a176",
                                                children: "ACCEPT"
                                            }, void 0, false, {
                                                fileName: "[project]/components/SoulStudioPanel.tsx",
                                                lineNumber: 54,
                                                columnNumber: 363
                                            }, this),
                                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("button", {
                                                style: {
                                                    ...button,
                                                    color: "#ff6875"
                                                },
                                                onClick: ()=>mutate({
                                                        operation: "trait",
                                                        trait_id: t.id,
                                                        decision: "reject"
                                                    }),
                                                className: "jsx-482121ad71d7a176",
                                                children: "REJECT"
                                            }, void 0, false, {
                                                fileName: "[project]/components/SoulStudioPanel.tsx",
                                                lineNumber: 54,
                                                columnNumber: 475
                                            }, this)
                                        ]
                                    }, void 0, true, {
                                        fileName: "[project]/components/SoulStudioPanel.tsx",
                                        lineNumber: 54,
                                        columnNumber: 327
                                    }, this)
                                ]
                            }, t.id, true, {
                                fileName: "[project]/components/SoulStudioPanel.tsx",
                                lineNumber: 54,
                                columnNumber: 167
                            }, this))
                    }, void 0, false, {
                        fileName: "[project]/components/SoulStudioPanel.tsx",
                        lineNumber: 54,
                        columnNumber: 29
                    }, this),
                    view === "history" && /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                        style: {
                            display: "grid",
                            gap: 7
                        },
                        className: "jsx-482121ad71d7a176",
                        children: soul.history.length === 0 ? /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                            style: card,
                            className: "jsx-482121ad71d7a176",
                            children: "No Soul mutations recorded."
                        }, void 0, false, {
                            fileName: "[project]/components/SoulStudioPanel.tsx",
                            lineNumber: 55,
                            columnNumber: 91
                        }, this) : soul.history.slice().reverse().map((h, i)=>/*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                style: card,
                                className: "jsx-482121ad71d7a176",
                                children: [
                                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("b", {
                                        className: "jsx-482121ad71d7a176",
                                        children: h.event
                                    }, void 0, false, {
                                        fileName: "[project]/components/SoulStudioPanel.tsx",
                                        lineNumber: 55,
                                        columnNumber: 211
                                    }, this),
                                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("span", {
                                        style: {
                                            float: "right",
                                            opacity: .55
                                        },
                                        className: "jsx-482121ad71d7a176",
                                        children: [
                                            "rev ",
                                            h.revision
                                        ]
                                    }, void 0, true, {
                                        fileName: "[project]/components/SoulStudioPanel.tsx",
                                        lineNumber: 55,
                                        columnNumber: 227
                                    }, this),
                                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                        style: {
                                            opacity: .7,
                                            marginTop: 5
                                        },
                                        className: "jsx-482121ad71d7a176",
                                        children: [
                                            h.reason,
                                            " · ",
                                            h.timestamp
                                        ]
                                    }, void 0, true, {
                                        fileName: "[project]/components/SoulStudioPanel.tsx",
                                        lineNumber: 55,
                                        columnNumber: 292
                                    }, this)
                                ]
                            }, i, true, {
                                fileName: "[project]/components/SoulStudioPanel.tsx",
                                lineNumber: 55,
                                columnNumber: 185
                            }, this))
                    }, void 0, false, {
                        fileName: "[project]/components/SoulStudioPanel.tsx",
                        lineNumber: 55,
                        columnNumber: 30
                    }, this),
                    view === "privacy" && /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                        style: {
                            display: "grid",
                            gap: 10
                        },
                        className: "jsx-482121ad71d7a176",
                        children: [
                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                style: card,
                                className: "jsx-482121ad71d7a176",
                                children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("label", {
                                    className: "jsx-482121ad71d7a176",
                                    children: [
                                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("input", {
                                            type: "checkbox",
                                            checked: soul.runtime_enabled,
                                            onChange: (e)=>mutate({
                                                    operation: "runtime",
                                                    enabled: e.target.checked
                                                }),
                                            className: "jsx-482121ad71d7a176"
                                        }, void 0, false, {
                                            fileName: "[project]/components/SoulStudioPanel.tsx",
                                            lineNumber: 56,
                                            columnNumber: 92
                                        }, this),
                                        " SOUL RUNTIME"
                                    ]
                                }, void 0, true, {
                                    fileName: "[project]/components/SoulStudioPanel.tsx",
                                    lineNumber: 56,
                                    columnNumber: 85
                                }, this)
                            }, void 0, false, {
                                fileName: "[project]/components/SoulStudioPanel.tsx",
                                lineNumber: 56,
                                columnNumber: 67
                            }, this),
                            Object.entries(soul.privacy).map(([k, v])=>/*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("label", {
                                    style: card,
                                    className: "jsx-482121ad71d7a176",
                                    children: [
                                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("input", {
                                            type: "checkbox",
                                            checked: v,
                                            onChange: (e)=>mutate({
                                                    operation: "privacy",
                                                    values: {
                                                        [k]: e.target.checked
                                                    }
                                                }),
                                            className: "jsx-482121ad71d7a176"
                                        }, void 0, false, {
                                            fileName: "[project]/components/SoulStudioPanel.tsx",
                                            lineNumber: 56,
                                            columnNumber: 314
                                        }, this),
                                        " ",
                                        k.replaceAll("_", " ").toUpperCase()
                                    ]
                                }, k, true, {
                                    fileName: "[project]/components/SoulStudioPanel.tsx",
                                    lineNumber: 56,
                                    columnNumber: 286
                                }, this)),
                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                style: {
                                    ...card,
                                    display: "flex",
                                    gap: 8,
                                    flexWrap: "wrap"
                                },
                                className: "jsx-482121ad71d7a176",
                                children: [
                                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("button", {
                                        style: button,
                                        onClick: ()=>window.open("/api/hud/soul/export", "_blank"),
                                        className: "jsx-482121ad71d7a176",
                                        children: [
                                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$download$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__Download$3e$__["Download"], {
                                                size: 11
                                            }, void 0, false, {
                                                fileName: "[project]/components/SoulStudioPanel.tsx",
                                                lineNumber: 56,
                                                columnNumber: 614
                                            }, this),
                                            " EXPORT"
                                        ]
                                    }, void 0, true, {
                                        fileName: "[project]/components/SoulStudioPanel.tsx",
                                        lineNumber: 56,
                                        columnNumber: 532
                                    }, this),
                                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("button", {
                                        style: button,
                                        onClick: ()=>mutate({
                                                operation: "undo"
                                            }),
                                        className: "jsx-482121ad71d7a176",
                                        children: [
                                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$rotate$2d$ccw$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__RotateCcw$3e$__["RotateCcw"], {
                                                size: 11
                                            }, void 0, false, {
                                                fileName: "[project]/components/SoulStudioPanel.tsx",
                                                lineNumber: 56,
                                                columnNumber: 715
                                            }, this),
                                            " UNDO"
                                        ]
                                    }, void 0, true, {
                                        fileName: "[project]/components/SoulStudioPanel.tsx",
                                        lineNumber: 56,
                                        columnNumber: 651
                                    }, this),
                                    [
                                        "affect",
                                        "relationship",
                                        "learned_traits",
                                        "all"
                                    ].map((x)=>/*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("button", {
                                            style: {
                                                ...button,
                                                color: x === "all" ? "#ff6875" : primary
                                            },
                                            onClick: ()=>window.confirm(`Reset ${x}?`) && mutate({
                                                    operation: "reset",
                                                    scope: x
                                                }),
                                            className: "jsx-482121ad71d7a176",
                                            children: [
                                                "RESET ",
                                                x.toUpperCase()
                                            ]
                                        }, x, true, {
                                            fileName: "[project]/components/SoulStudioPanel.tsx",
                                            lineNumber: 56,
                                            columnNumber: 808
                                        }, this))
                                ]
                            }, void 0, true, {
                                fileName: "[project]/components/SoulStudioPanel.tsx",
                                lineNumber: 56,
                                columnNumber: 472
                            }, this),
                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("details", {
                                style: card,
                                className: "jsx-482121ad71d7a176",
                                children: [
                                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("summary", {
                                        className: "jsx-482121ad71d7a176",
                                        children: "SOUL DIAGNOSTICS"
                                    }, void 0, false, {
                                        fileName: "[project]/components/SoulStudioPanel.tsx",
                                        lineNumber: 56,
                                        columnNumber: 1021
                                    }, this),
                                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                        style: {
                                            fontFamily: "var(--font-mono)",
                                            fontSize: 10,
                                            lineHeight: 1.8,
                                            marginTop: 8
                                        },
                                        className: "jsx-482121ad71d7a176",
                                        children: [
                                            "SCHEMA ",
                                            soul.diagnostics.schema_version,
                                            " · REVISION ",
                                            soul.diagnostics.revision,
                                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("br", {
                                                className: "jsx-482121ad71d7a176"
                                            }, void 0, false, {
                                                fileName: "[project]/components/SoulStudioPanel.tsx",
                                                lineNumber: 56,
                                                columnNumber: 1219
                                            }, this),
                                            "LAST SAVE ",
                                            soul.diagnostics.last_successful_save,
                                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("br", {
                                                className: "jsx-482121ad71d7a176"
                                            }, void 0, false, {
                                                fileName: "[project]/components/SoulStudioPanel.tsx",
                                                lineNumber: 56,
                                                columnNumber: 1273
                                            }, this),
                                            "LAST BACKUP ",
                                            soul.diagnostics.last_backup || "none",
                                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("br", {
                                                className: "jsx-482121ad71d7a176"
                                            }, void 0, false, {
                                                fileName: "[project]/components/SoulStudioPanel.tsx",
                                                lineNumber: 56,
                                                columnNumber: 1328
                                            }, this),
                                            "LAST REFLECTION ",
                                            soul.diagnostics.last_reflection || "never",
                                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("br", {
                                                className: "jsx-482121ad71d7a176"
                                            }, void 0, false, {
                                                fileName: "[project]/components/SoulStudioPanel.tsx",
                                                lineNumber: 56,
                                                columnNumber: 1392
                                            }, this),
                                            "CONTEXT ",
                                            soul.diagnostics.context_size,
                                            " BYTES",
                                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("br", {
                                                className: "jsx-482121ad71d7a176"
                                            }, void 0, false, {
                                                fileName: "[project]/components/SoulStudioPanel.tsx",
                                                lineNumber: 56,
                                                columnNumber: 1442
                                            }, this),
                                            "MIGRATIONS ",
                                            soul.diagnostics.completed_migrations.join(", ") || "none",
                                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("br", {
                                                className: "jsx-482121ad71d7a176"
                                            }, void 0, false, {
                                                fileName: "[project]/components/SoulStudioPanel.tsx",
                                                lineNumber: 56,
                                                columnNumber: 1516
                                            }, this),
                                            "MODE ",
                                            soul.diagnostics.degraded || "healthy"
                                        ]
                                    }, void 0, true, {
                                        fileName: "[project]/components/SoulStudioPanel.tsx",
                                        lineNumber: 56,
                                        columnNumber: 1056
                                    }, this)
                                ]
                            }, void 0, true, {
                                fileName: "[project]/components/SoulStudioPanel.tsx",
                                lineNumber: 56,
                                columnNumber: 999
                            }, this),
                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("details", {
                                style: card,
                                className: "jsx-482121ad71d7a176",
                                children: [
                                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("summary", {
                                        className: "jsx-482121ad71d7a176",
                                        children: "CANONICAL CONTEXT PREVIEW"
                                    }, void 0, false, {
                                        fileName: "[project]/components/SoulStudioPanel.tsx",
                                        lineNumber: 56,
                                        columnNumber: 1602
                                    }, this),
                                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("pre", {
                                        style: {
                                            whiteSpace: "pre-wrap",
                                            fontSize: 10,
                                            maxHeight: 260,
                                            overflow: "auto"
                                        },
                                        className: "jsx-482121ad71d7a176",
                                        children: soul.context_preview
                                    }, void 0, false, {
                                        fileName: "[project]/components/SoulStudioPanel.tsx",
                                        lineNumber: 56,
                                        columnNumber: 1646
                                    }, this)
                                ]
                            }, void 0, true, {
                                fileName: "[project]/components/SoulStudioPanel.tsx",
                                lineNumber: 56,
                                columnNumber: 1580
                            }, this)
                        ]
                    }, void 0, true, {
                        fileName: "[project]/components/SoulStudioPanel.tsx",
                        lineNumber: 56,
                        columnNumber: 30
                    }, this),
                    busy && /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                        role: "status",
                        "aria-live": "polite",
                        style: {
                            position: "sticky",
                            bottom: 0,
                            padding: 8,
                            background: "rgba(0,0,0,.8)",
                            color: primary
                        },
                        className: "jsx-482121ad71d7a176",
                        children: "SAVING REVISION…"
                    }, void 0, false, {
                        fileName: "[project]/components/SoulStudioPanel.tsx",
                        lineNumber: 57,
                        columnNumber: 14
                    }, this)
                ]
            }, void 0, true, {
                fileName: "[project]/components/SoulStudioPanel.tsx",
                lineNumber: 47,
                columnNumber: 5
            }, this),
            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$styled$2d$jsx$2f$style$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["default"], {
                id: "482121ad71d7a176",
                children: "@media (width<=700px){.soul-studio-layout.jsx-482121ad71d7a176{grid-template-columns:minmax(0,1fr)!important}}"
            }, void 0, false, void 0, this)
        ]
    }, void 0, true, {
        fileName: "[project]/components/SoulStudioPanel.tsx",
        lineNumber: 42,
        columnNumber: 10
    }, this);
}
_s(SoulStudioPanel, "RwFqRM70W9MDNEzVxnMx5p4KhzI=");
_c = SoulStudioPanel;
var _c;
__turbopack_context__.k.register(_c, "SoulStudioPanel");
if (typeof globalThis.$RefreshHelpers$ === 'object' && globalThis.$RefreshHelpers !== null) {
    __turbopack_context__.k.registerExports(__turbopack_context__.m, globalThis.$RefreshHelpers$);
}
}),
"[project]/components/StudioModal.tsx [app-client] (ecmascript)", ((__turbopack_context__) => {
"use strict";

__turbopack_context__.s([
    "default",
    ()=>StudioModal
]);
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/next/dist/compiled/react/jsx-dev-runtime.js [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/next/dist/compiled/react/index.js [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$book$2d$open$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__BookOpen$3e$__ = __turbopack_context__.i("[project]/node_modules/lucide-react/dist/esm/icons/book-open.js [app-client] (ecmascript) <export default as BookOpen>");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$check$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__Check$3e$__ = __turbopack_context__.i("[project]/node_modules/lucide-react/dist/esm/icons/check.js [app-client] (ecmascript) <export default as Check>");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$palette$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__Palette$3e$__ = __turbopack_context__.i("[project]/node_modules/lucide-react/dist/esm/icons/palette.js [app-client] (ecmascript) <export default as Palette>");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$plus$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__Plus$3e$__ = __turbopack_context__.i("[project]/node_modules/lucide-react/dist/esm/icons/plus.js [app-client] (ecmascript) <export default as Plus>");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$sparkles$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__Sparkles$3e$__ = __turbopack_context__.i("[project]/node_modules/lucide-react/dist/esm/icons/sparkles.js [app-client] (ecmascript) <export default as Sparkles>");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$shield$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__Shield$3e$__ = __turbopack_context__.i("[project]/node_modules/lucide-react/dist/esm/icons/shield.js [app-client] (ecmascript) <export default as Shield>");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$trash$2d$2$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__Trash2$3e$__ = __turbopack_context__.i("[project]/node_modules/lucide-react/dist/esm/icons/trash-2.js [app-client] (ecmascript) <export default as Trash2>");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$user$2d$check$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__UserCheck$3e$__ = __turbopack_context__.i("[project]/node_modules/lucide-react/dist/esm/icons/user-check.js [app-client] (ecmascript) <export default as UserCheck>");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$users$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__Users$3e$__ = __turbopack_context__.i("[project]/node_modules/lucide-react/dist/esm/icons/users.js [app-client] (ecmascript) <export default as Users>");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$x$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__X$3e$__ = __turbopack_context__.i("[project]/node_modules/lucide-react/dist/esm/icons/x.js [app-client] (ecmascript) <export default as X>");
var __TURBOPACK__imported__module__$5b$project$5d2f$components$2f$JarvisBridge$2e$tsx__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/components/JarvisBridge.tsx [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$components$2f$SoulStudioPanel$2e$tsx__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/components/SoulStudioPanel.tsx [app-client] (ecmascript)");
;
var _s = __turbopack_context__.k.signature();
"use client";
;
;
;
;
const GREEN = "#3be38a";
const RED = "#ff5d6c";
function StudioModal() {
    _s();
    const { studioModalOpen, setStudioModalOpen, theme, maleVoices, femaleVoices, setThemeCustom } = (0, __TURBOPACK__imported__module__$5b$project$5d2f$components$2f$JarvisBridge$2e$tsx__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useJarvis"])();
    const [tab, setTab] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])("soul");
    const [data, setData] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])(null);
    const [statusMsg, setStatusMsg] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])("");
    // Interview draft
    const [answers, setAnswers] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])({});
    const [newRule, setNewRule] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])("");
    // Companion builder draft
    const [compName, setCompName] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])("");
    const [compRole, setCompRole] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])("");
    const [compPersona, setCompPersona] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])("male");
    const [compVoice, setCompVoice] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])("Charon");
    const [compInstr, setCompInstr] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])("");
    const [compTools, setCompTools] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])([]);
    // Skill author draft
    const [selectedSkill, setSelectedSkill] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])(null);
    const [skillName, setSkillName] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])("");
    const [skillDesc, setSkillDesc] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])("");
    const [skillBody, setSkillBody] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])("## When to use\nTrigger on ...\n\n## Procedure\n1. Step one\n\n## Pitfalls\n- Watch out for ...\n\n## Verification\n- Confirm result");
    const [customPri, setCustomPri] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])("");
    const [customSec, setCustomSec] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])("");
    const refresh = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useCallback"])({
        "StudioModal.useCallback[refresh]": async ()=>{
            try {
                const r = await fetch("/api/hud/studio");
                if (r.ok) {
                    const j = await r.json();
                    if (j.studio) {
                        setData(j.studio);
                        setAnswers(j.studio.interview_answers || {});
                        setCustomPri(j.studio.theme?.custom_primary || "");
                        setCustomSec(j.studio.theme?.custom_secondary || "");
                    }
                }
            } catch  {}
        }
    }["StudioModal.useCallback[refresh]"], []);
    (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useEffect"])({
        "StudioModal.useEffect": ()=>{
            if (studioModalOpen) {
                refresh();
                setStatusMsg("");
            }
        }
    }["StudioModal.useEffect"], [
        studioModalOpen,
        refresh
    ]);
    if (!studioModalOpen) return null;
    const PRIMARY = theme.primary;
    const SECONDARY = theme.secondary;
    const postAction = async (payload)=>{
        const r = await fetch("/api/hud/action", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(payload)
        });
        const j = await r.json();
        if (j.studio) setData(j.studio);
        if (j.theme) setThemeCustom(j.theme);
        return j;
    };
    const onSaveInterview = async ()=>{
        await postAction({
            action: "studio_save_interview",
            answers
        });
        setStatusMsg("Behavior interview saved & synced to Brain.");
    };
    const onAddRule = async (e)=>{
        e.preventDefault();
        if (!newRule.trim()) return;
        await postAction({
            action: "studio_add_rule",
            rule: newRule.trim()
        });
        setNewRule("");
    };
    const onSaveCompanion = async (e)=>{
        e.preventDefault();
        if (!compName.trim()) return;
        const j = await postAction({
            action: "studio_save_companion",
            companion: {
                name: compName.trim(),
                role: compRole.trim() || "Specialist Companion",
                persona: compPersona,
                voice: compVoice,
                instructions: compInstr.trim(),
                allowed_tools: compTools
            }
        });
        if (j.ok) {
            setCompName("");
            setCompRole("");
            setCompInstr("");
            setCompTools([]);
            setStatusMsg(`Saved specialist companion "${j.companion?.name}".`);
        } else if (j.error) {
            setStatusMsg(j.error);
        }
    };
    const onSaveSkill = async (e)=>{
        e.preventDefault();
        const j = await postAction({
            action: "studio_save_skill",
            name: skillName,
            description: skillDesc,
            body: skillBody
        });
        if (j.ok) {
            setStatusMsg(`Saved custom skill "${j.name}".`);
        } else if (j.error) {
            setStatusMsg(j.error);
        }
    };
    const toggleTool = (t)=>{
        setCompTools((prev)=>prev.includes(t) ? prev.filter((x)=>x !== t) : [
                ...prev,
                t
            ]);
    };
    return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
        role: "dialog",
        "aria-modal": "true",
        "aria-label": "Companions, Behavior & Skills Studio",
        style: {
            position: "fixed",
            inset: 0,
            zIndex: 82,
            background: "rgba(2, 5, 12, 0.78)",
            backdropFilter: "blur(18px)",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            padding: 18
        },
        children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
            style: {
                width: "min(960px, 96vw)",
                height: "min(730px, 90vh)",
                background: theme.drawerBg,
                border: `1px solid ${PRIMARY}44`,
                borderRadius: 20,
                boxShadow: "0 24px 80px rgba(0,0,0,0.82)",
                display: "flex",
                flexDirection: "column",
                overflow: "hidden"
            },
            children: [
                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                    style: {
                        display: "flex",
                        alignItems: "center",
                        gap: 10,
                        padding: "15px 22px",
                        borderBottom: `1px solid ${PRIMARY}26`
                    },
                    children: [
                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$sparkles$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__Sparkles$3e$__["Sparkles"], {
                            size: 17,
                            color: PRIMARY
                        }, void 0, false, {
                            fileName: "[project]/components/StudioModal.tsx",
                            lineNumber: 229,
                            columnNumber: 11
                        }, this),
                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                            style: {
                                flex: 1
                            },
                            children: [
                                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                    style: {
                                        fontFamily: "var(--font-mono)",
                                        fontSize: 11,
                                        letterSpacing: "0.24em",
                                        color: PRIMARY
                                    },
                                    children: "STUDIO · COMPANIONS, BEHAVIOR, SKILLS & THEMES"
                                }, void 0, false, {
                                    fileName: "[project]/components/StudioModal.tsx",
                                    lineNumber: 231,
                                    columnNumber: 13
                                }, this),
                                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                    style: {
                                        fontSize: 11.5,
                                        color: "rgba(240,237,232,0.58)",
                                        marginTop: 2
                                    },
                                    children: [
                                        "Active Companion: ",
                                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("strong", {
                                            children: data?.active_companion?.name || "JARVIS"
                                        }, void 0, false, {
                                            fileName: "[project]/components/StudioModal.tsx",
                                            lineNumber: 242,
                                            columnNumber: 33
                                        }, this),
                                        " ·",
                                        " ",
                                        data?.active_companion?.role || "Full-Access"
                                    ]
                                }, void 0, true, {
                                    fileName: "[project]/components/StudioModal.tsx",
                                    lineNumber: 241,
                                    columnNumber: 13
                                }, this)
                            ]
                        }, void 0, true, {
                            fileName: "[project]/components/StudioModal.tsx",
                            lineNumber: 230,
                            columnNumber: 11
                        }, this),
                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("button", {
                            type: "button",
                            onClick: ()=>setStudioModalOpen(false),
                            style: {
                                background: "none",
                                border: "none",
                                color: "rgba(240,237,232,0.6)",
                                cursor: "pointer"
                            },
                            children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$x$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__X$3e$__["X"], {
                                size: 18
                            }, void 0, false, {
                                fileName: "[project]/components/StudioModal.tsx",
                                lineNumber: 256,
                                columnNumber: 13
                            }, this)
                        }, void 0, false, {
                            fileName: "[project]/components/StudioModal.tsx",
                            lineNumber: 246,
                            columnNumber: 11
                        }, this)
                    ]
                }, void 0, true, {
                    fileName: "[project]/components/StudioModal.tsx",
                    lineNumber: 220,
                    columnNumber: 9
                }, this),
                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                    style: {
                        display: "flex",
                        gap: 8,
                        padding: "10px 22px",
                        borderBottom: "1px solid rgba(255,255,255,0.07)"
                    },
                    children: [
                        [
                            {
                                id: "soul",
                                label: "SOUL",
                                icon: __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$shield$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__Shield$3e$__["Shield"]
                            },
                            {
                                id: "companions",
                                label: "COMPANIONS",
                                icon: __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$users$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__Users$3e$__["Users"]
                            },
                            {
                                id: "interview",
                                label: "BEHAVIOR INTERVIEW",
                                icon: __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$user$2d$check$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__UserCheck$3e$__["UserCheck"]
                            },
                            {
                                id: "skills",
                                label: "SKILLS STUDIO",
                                icon: __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$book$2d$open$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__BookOpen$3e$__["BookOpen"]
                            },
                            {
                                id: "themes",
                                label: "THEMES",
                                icon: __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$palette$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__Palette$3e$__["Palette"]
                            }
                        ].map((t)=>{
                            const Icon = t.icon;
                            const active = tab === t.id;
                            return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("button", {
                                type: "button",
                                onClick: ()=>setTab(t.id),
                                style: {
                                    display: "inline-flex",
                                    alignItems: "center",
                                    gap: 6,
                                    padding: "7px 13px",
                                    borderRadius: 999,
                                    border: `1px solid ${active ? PRIMARY : "rgba(255,255,255,0.12)"}`,
                                    background: active ? `${PRIMARY}22` : "transparent",
                                    color: active ? PRIMARY : "rgba(240,237,232,0.7)",
                                    fontFamily: "var(--font-mono)",
                                    fontSize: 10,
                                    letterSpacing: "0.12em",
                                    cursor: "pointer"
                                },
                                children: [
                                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(Icon, {
                                        size: 12
                                    }, void 0, false, {
                                        fileName: "[project]/components/StudioModal.tsx",
                                        lineNumber: 300,
                                        columnNumber: 17
                                    }, this),
                                    t.label
                                ]
                            }, t.id, true, {
                                fileName: "[project]/components/StudioModal.tsx",
                                lineNumber: 281,
                                columnNumber: 15
                            }, this);
                        }),
                        statusMsg && /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("span", {
                            style: {
                                marginLeft: "auto",
                                alignSelf: "center",
                                fontFamily: "var(--font-mono)",
                                fontSize: 10,
                                color: GREEN
                            },
                            children: statusMsg
                        }, void 0, false, {
                            fileName: "[project]/components/StudioModal.tsx",
                            lineNumber: 306,
                            columnNumber: 13
                        }, this)
                    ]
                }, void 0, true, {
                    fileName: "[project]/components/StudioModal.tsx",
                    lineNumber: 261,
                    columnNumber: 9
                }, this),
                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                    style: {
                        flex: 1,
                        overflowY: "auto",
                        padding: "18px 22px"
                    },
                    children: [
                        tab === "soul" && /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$components$2f$SoulStudioPanel$2e$tsx__$5b$app$2d$client$5d$__$28$ecmascript$29$__["default"], {
                            primary: PRIMARY,
                            secondary: SECONDARY
                        }, void 0, false, {
                            fileName: "[project]/components/StudioModal.tsx",
                            lineNumber: 322,
                            columnNumber: 30
                        }, this),
                        tab === "companions" && /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                            style: {
                                display: "grid",
                                gridTemplateColumns: "1fr 1fr",
                                gap: 18
                            },
                            children: [
                                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                    style: {
                                        display: "flex",
                                        flexDirection: "column",
                                        gap: 10
                                    },
                                    children: [
                                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                            style: {
                                                fontFamily: "var(--font-mono)",
                                                fontSize: 10,
                                                letterSpacing: "0.16em",
                                                color: SECONDARY
                                            },
                                            children: "PERSISTENT SPECIALIST ROSTER"
                                        }, void 0, false, {
                                            fileName: "[project]/components/StudioModal.tsx",
                                            lineNumber: 328,
                                            columnNumber: 17
                                        }, this),
                                        (data?.companions || []).map((c)=>{
                                            const isActive = data?.active_companion?.id === c.id;
                                            return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                                style: {
                                                    padding: "12px 14px",
                                                    borderRadius: 12,
                                                    border: `1px solid ${isActive ? `${PRIMARY}77` : "rgba(255,255,255,0.1)"}`,
                                                    background: isActive ? `${PRIMARY}14` : "rgba(255,255,255,0.025)"
                                                },
                                                children: [
                                                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                                        style: {
                                                            display: "flex",
                                                            alignItems: "center",
                                                            gap: 8
                                                        },
                                                        children: [
                                                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("span", {
                                                                style: {
                                                                    fontWeight: 600,
                                                                    fontSize: 13
                                                                },
                                                                children: c.name
                                                            }, void 0, false, {
                                                                fileName: "[project]/components/StudioModal.tsx",
                                                                lineNumber: 353,
                                                                columnNumber: 25
                                                            }, this),
                                                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("span", {
                                                                style: {
                                                                    fontFamily: "var(--font-mono)",
                                                                    fontSize: 9,
                                                                    padding: "2px 7px",
                                                                    borderRadius: 999,
                                                                    background: "rgba(255,255,255,0.08)"
                                                                },
                                                                children: [
                                                                    c.persona.toUpperCase(),
                                                                    " · ",
                                                                    c.voice
                                                                ]
                                                            }, void 0, true, {
                                                                fileName: "[project]/components/StudioModal.tsx",
                                                                lineNumber: 354,
                                                                columnNumber: 25
                                                            }, this),
                                                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("span", {
                                                                style: {
                                                                    flex: 1
                                                                }
                                                            }, void 0, false, {
                                                                fileName: "[project]/components/StudioModal.tsx",
                                                                lineNumber: 365,
                                                                columnNumber: 25
                                                            }, this),
                                                            !isActive ? /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("button", {
                                                                type: "button",
                                                                onClick: ()=>postAction({
                                                                        action: "studio_activate_companion",
                                                                        companion_id: c.id
                                                                    }),
                                                                style: {
                                                                    padding: "4px 10px",
                                                                    borderRadius: 999,
                                                                    border: `1px solid ${PRIMARY}66`,
                                                                    background: `${PRIMARY}1f`,
                                                                    color: PRIMARY,
                                                                    fontFamily: "var(--font-mono)",
                                                                    fontSize: 9.5,
                                                                    cursor: "pointer"
                                                                },
                                                                children: "ACTIVATE"
                                                            }, void 0, false, {
                                                                fileName: "[project]/components/StudioModal.tsx",
                                                                lineNumber: 367,
                                                                columnNumber: 27
                                                            }, this) : /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("span", {
                                                                style: {
                                                                    fontFamily: "var(--font-mono)",
                                                                    fontSize: 9.5,
                                                                    color: GREEN,
                                                                    display: "inline-flex",
                                                                    alignItems: "center",
                                                                    gap: 4
                                                                },
                                                                children: [
                                                                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$check$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__Check$3e$__["Check"], {
                                                                        size: 11
                                                                    }, void 0, false, {
                                                                        fileName: "[project]/components/StudioModal.tsx",
                                                                        lineNumber: 399,
                                                                        columnNumber: 29
                                                                    }, this),
                                                                    " ACTIVE"
                                                                ]
                                                            }, void 0, true, {
                                                                fileName: "[project]/components/StudioModal.tsx",
                                                                lineNumber: 389,
                                                                columnNumber: 27
                                                            }, this),
                                                            !c.builtin && /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("button", {
                                                                type: "button",
                                                                onClick: ()=>postAction({
                                                                        action: "studio_delete_companion",
                                                                        companion_id: c.id
                                                                    }),
                                                                style: {
                                                                    background: "none",
                                                                    border: "none",
                                                                    color: RED,
                                                                    cursor: "pointer"
                                                                },
                                                                children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$trash$2d$2$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__Trash2$3e$__["Trash2"], {
                                                                    size: 13
                                                                }, void 0, false, {
                                                                    fileName: "[project]/components/StudioModal.tsx",
                                                                    lineNumber: 418,
                                                                    columnNumber: 29
                                                                }, this)
                                                            }, void 0, false, {
                                                                fileName: "[project]/components/StudioModal.tsx",
                                                                lineNumber: 403,
                                                                columnNumber: 27
                                                            }, this)
                                                        ]
                                                    }, void 0, true, {
                                                        fileName: "[project]/components/StudioModal.tsx",
                                                        lineNumber: 352,
                                                        columnNumber: 23
                                                    }, this),
                                                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                                        style: {
                                                            fontSize: 11.5,
                                                            color: "rgba(240,237,232,0.68)",
                                                            marginTop: 4
                                                        },
                                                        children: c.role
                                                    }, void 0, false, {
                                                        fileName: "[project]/components/StudioModal.tsx",
                                                        lineNumber: 422,
                                                        columnNumber: 23
                                                    }, this),
                                                    c.allowed_tools && c.allowed_tools.length > 0 && /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                                        style: {
                                                            fontFamily: "var(--font-mono)",
                                                            fontSize: 9.5,
                                                            color: SECONDARY,
                                                            marginTop: 5
                                                        },
                                                        children: [
                                                            "Scoped tools (",
                                                            c.allowed_tools.length,
                                                            "): ",
                                                            c.allowed_tools.join(", ")
                                                        ]
                                                    }, void 0, true, {
                                                        fileName: "[project]/components/StudioModal.tsx",
                                                        lineNumber: 426,
                                                        columnNumber: 25
                                                    }, this)
                                                ]
                                            }, c.id, true, {
                                                fileName: "[project]/components/StudioModal.tsx",
                                                lineNumber: 341,
                                                columnNumber: 21
                                            }, this);
                                        })
                                    ]
                                }, void 0, true, {
                                    fileName: "[project]/components/StudioModal.tsx",
                                    lineNumber: 327,
                                    columnNumber: 15
                                }, this),
                                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("form", {
                                    onSubmit: onSaveCompanion,
                                    style: {
                                        padding: 15,
                                        borderRadius: 14,
                                        background: "rgba(255,255,255,0.025)",
                                        border: "1px solid rgba(255,255,255,0.09)",
                                        display: "flex",
                                        flexDirection: "column",
                                        gap: 9
                                    },
                                    children: [
                                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                            style: {
                                                fontFamily: "var(--font-mono)",
                                                fontSize: 10,
                                                letterSpacing: "0.16em",
                                                color: PRIMARY
                                            },
                                            children: "+ CREATE SPECIALIST COMPANION"
                                        }, void 0, false, {
                                            fileName: "[project]/components/StudioModal.tsx",
                                            lineNumber: 455,
                                            columnNumber: 17
                                        }, this),
                                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("input", {
                                            value: compName,
                                            onChange: (e)=>setCompName(e.target.value),
                                            placeholder: "Name (e.g. ATHENA, ARCHIMEDES, VALKYRIE)",
                                            style: {
                                                padding: "8px 11px",
                                                borderRadius: 8,
                                                border: "1px solid rgba(255,255,255,0.14)",
                                                background: "rgba(0,0,0,0.35)",
                                                color: "#f0ede8",
                                                fontSize: 12
                                            }
                                        }, void 0, false, {
                                            fileName: "[project]/components/StudioModal.tsx",
                                            lineNumber: 465,
                                            columnNumber: 17
                                        }, this),
                                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("input", {
                                            value: compRole,
                                            onChange: (e)=>setCompRole(e.target.value),
                                            placeholder: "Specialist Role (e.g. Security & Code Auditor)",
                                            style: {
                                                padding: "8px 11px",
                                                borderRadius: 8,
                                                border: "1px solid rgba(255,255,255,0.14)",
                                                background: "rgba(0,0,0,0.35)",
                                                color: "#f0ede8",
                                                fontSize: 12
                                            }
                                        }, void 0, false, {
                                            fileName: "[project]/components/StudioModal.tsx",
                                            lineNumber: 478,
                                            columnNumber: 17
                                        }, this),
                                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                            style: {
                                                display: "flex",
                                                gap: 8
                                            },
                                            children: [
                                                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("select", {
                                                    value: compPersona,
                                                    onChange: (e)=>{
                                                        const p = e.target.value === "female" ? "female" : "male";
                                                        setCompPersona(p);
                                                        setCompVoice(p === "female" ? "Aoede" : "Charon");
                                                    },
                                                    style: {
                                                        flex: 1,
                                                        padding: "8px",
                                                        borderRadius: 8,
                                                        border: "1px solid rgba(255,255,255,0.14)",
                                                        background: "rgba(0,0,0,0.45)",
                                                        color: "#f0ede8",
                                                        fontSize: 12
                                                    },
                                                    children: [
                                                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("option", {
                                                            value: "male",
                                                            children: "Male Edition (Cyan/Gold)"
                                                        }, void 0, false, {
                                                            fileName: "[project]/components/StudioModal.tsx",
                                                            lineNumber: 509,
                                                            columnNumber: 21
                                                        }, this),
                                                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("option", {
                                                            value: "female",
                                                            children: "Female Edition (Rose/Orchid)"
                                                        }, void 0, false, {
                                                            fileName: "[project]/components/StudioModal.tsx",
                                                            lineNumber: 510,
                                                            columnNumber: 21
                                                        }, this)
                                                    ]
                                                }, void 0, true, {
                                                    fileName: "[project]/components/StudioModal.tsx",
                                                    lineNumber: 492,
                                                    columnNumber: 19
                                                }, this),
                                                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("select", {
                                                    value: compVoice,
                                                    onChange: (e)=>setCompVoice(e.target.value),
                                                    style: {
                                                        flex: 1,
                                                        padding: "8px",
                                                        borderRadius: 8,
                                                        border: "1px solid rgba(255,255,255,0.14)",
                                                        background: "rgba(0,0,0,0.45)",
                                                        color: "#f0ede8",
                                                        fontSize: 12
                                                    },
                                                    children: (compPersona === "female" ? femaleVoices : maleVoices).map((v)=>/*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("option", {
                                                            value: v,
                                                            children: [
                                                                "Voice: ",
                                                                v
                                                            ]
                                                        }, v, true, {
                                                            fileName: "[project]/components/StudioModal.tsx",
                                                            lineNumber: 526,
                                                            columnNumber: 23
                                                        }, this))
                                                }, void 0, false, {
                                                    fileName: "[project]/components/StudioModal.tsx",
                                                    lineNumber: 512,
                                                    columnNumber: 19
                                                }, this)
                                            ]
                                        }, void 0, true, {
                                            fileName: "[project]/components/StudioModal.tsx",
                                            lineNumber: 491,
                                            columnNumber: 17
                                        }, this),
                                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("textarea", {
                                            value: compInstr,
                                            onChange: (e)=>setCompInstr(e.target.value),
                                            rows: 3,
                                            placeholder: "Specialist system instructions, focus areas & constraints…",
                                            style: {
                                                padding: "8px 11px",
                                                borderRadius: 8,
                                                border: "1px solid rgba(255,255,255,0.14)",
                                                background: "rgba(0,0,0,0.35)",
                                                color: "#f0ede8",
                                                fontSize: 12,
                                                resize: "vertical"
                                            }
                                        }, void 0, false, {
                                            fileName: "[project]/components/StudioModal.tsx",
                                            lineNumber: 532,
                                            columnNumber: 17
                                        }, this),
                                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                            style: {
                                                fontSize: 11,
                                                color: "rgba(240,237,232,0.65)"
                                            },
                                            children: "Scoped Tool Permissions (leave unselected for all tools):"
                                        }, void 0, false, {
                                            fileName: "[project]/components/StudioModal.tsx",
                                            lineNumber: 547,
                                            columnNumber: 17
                                        }, this),
                                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                            style: {
                                                maxHeight: 110,
                                                overflowY: "auto",
                                                display: "flex",
                                                flexWrap: "wrap",
                                                gap: 5
                                            },
                                            children: (data?.available_tools || []).map((t)=>{
                                                const on = compTools.includes(t);
                                                return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("button", {
                                                    type: "button",
                                                    onClick: ()=>toggleTool(t),
                                                    style: {
                                                        padding: "3px 8px",
                                                        borderRadius: 999,
                                                        border: `1px solid ${on ? PRIMARY : "rgba(255,255,255,0.14)"}`,
                                                        background: on ? `${PRIMARY}24` : "transparent",
                                                        color: on ? PRIMARY : "rgba(240,237,232,0.65)",
                                                        fontFamily: "var(--font-mono)",
                                                        fontSize: 9.5,
                                                        cursor: "pointer"
                                                    },
                                                    children: t
                                                }, t, false, {
                                                    fileName: "[project]/components/StudioModal.tsx",
                                                    lineNumber: 562,
                                                    columnNumber: 23
                                                }, this);
                                            })
                                        }, void 0, false, {
                                            fileName: "[project]/components/StudioModal.tsx",
                                            lineNumber: 550,
                                            columnNumber: 17
                                        }, this),
                                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("button", {
                                            type: "submit",
                                            style: {
                                                padding: "9px 14px",
                                                borderRadius: 9,
                                                border: `1px solid ${PRIMARY}66`,
                                                background: `${PRIMARY}22`,
                                                color: PRIMARY,
                                                fontFamily: "var(--font-mono)",
                                                fontSize: 10,
                                                cursor: "pointer"
                                            },
                                            children: "SAVE SPECIALIST COMPANION"
                                        }, void 0, false, {
                                            fileName: "[project]/components/StudioModal.tsx",
                                            lineNumber: 582,
                                            columnNumber: 17
                                        }, this)
                                    ]
                                }, void 0, true, {
                                    fileName: "[project]/components/StudioModal.tsx",
                                    lineNumber: 443,
                                    columnNumber: 15
                                }, this)
                            ]
                        }, void 0, true, {
                            fileName: "[project]/components/StudioModal.tsx",
                            lineNumber: 325,
                            columnNumber: 13
                        }, this),
                        tab === "interview" && /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                            style: {
                                display: "flex",
                                flexDirection: "column",
                                gap: 16
                            },
                            children: [
                                (data?.interview_questions || []).map((q)=>/*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                        style: {
                                            padding: "12px 15px",
                                            borderRadius: 12,
                                            background: "rgba(255,255,255,0.025)",
                                            border: "1px solid rgba(255,255,255,0.08)"
                                        },
                                        children: [
                                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                                style: {
                                                    fontSize: 12.5,
                                                    fontWeight: 600,
                                                    marginBottom: 8
                                                },
                                                children: q.question
                                            }, void 0, false, {
                                                fileName: "[project]/components/StudioModal.tsx",
                                                lineNumber: 613,
                                                columnNumber: 19
                                            }, this),
                                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                                style: {
                                                    display: "flex",
                                                    flexWrap: "wrap",
                                                    gap: 7
                                                },
                                                children: q.options.map((opt)=>{
                                                    const sel = answers[q.id] === opt;
                                                    return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("button", {
                                                        type: "button",
                                                        onClick: ()=>setAnswers((a)=>({
                                                                    ...a,
                                                                    [q.id]: opt
                                                                })),
                                                        style: {
                                                            padding: "6px 12px",
                                                            borderRadius: 999,
                                                            border: `1px solid ${sel ? PRIMARY : "rgba(255,255,255,0.14)"}`,
                                                            background: sel ? `${PRIMARY}24` : "transparent",
                                                            color: sel ? PRIMARY : "rgba(240,237,232,0.75)",
                                                            fontSize: 11.5,
                                                            cursor: "pointer"
                                                        },
                                                        children: opt
                                                    }, opt, false, {
                                                        fileName: "[project]/components/StudioModal.tsx",
                                                        lineNumber: 620,
                                                        columnNumber: 25
                                                    }, this);
                                                })
                                            }, void 0, false, {
                                                fileName: "[project]/components/StudioModal.tsx",
                                                lineNumber: 616,
                                                columnNumber: 19
                                            }, this)
                                        ]
                                    }, q.id, true, {
                                        fileName: "[project]/components/StudioModal.tsx",
                                        lineNumber: 604,
                                        columnNumber: 17
                                    }, this)),
                                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("button", {
                                    type: "button",
                                    onClick: onSaveInterview,
                                    style: {
                                        alignSelf: "flex-start",
                                        padding: "9px 18px",
                                        borderRadius: 999,
                                        border: `1px solid ${PRIMARY}77`,
                                        background: `${PRIMARY}22`,
                                        color: PRIMARY,
                                        fontFamily: "var(--font-mono)",
                                        fontSize: 10.5,
                                        cursor: "pointer"
                                    },
                                    children: "SAVE BEHAVIOR INTERVIEW"
                                }, void 0, false, {
                                    fileName: "[project]/components/StudioModal.tsx",
                                    lineNumber: 641,
                                    columnNumber: 15
                                }, this),
                                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                    style: {
                                        marginTop: 8,
                                        paddingTop: 14,
                                        borderTop: "1px solid rgba(255,255,255,0.08)"
                                    },
                                    children: [
                                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                            style: {
                                                fontFamily: "var(--font-mono)",
                                                fontSize: 10,
                                                letterSpacing: "0.16em",
                                                color: SECONDARY,
                                                marginBottom: 8
                                            },
                                            children: [
                                                "ADAPTIVE LEARNED STYLE RULES (",
                                                data?.learned_rules?.length || 0,
                                                ")"
                                            ]
                                        }, void 0, true, {
                                            fileName: "[project]/components/StudioModal.tsx",
                                            lineNumber: 667,
                                            columnNumber: 17
                                        }, this),
                                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("form", {
                                            onSubmit: onAddRule,
                                            style: {
                                                display: "flex",
                                                gap: 8,
                                                marginBottom: 10
                                            },
                                            children: [
                                                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("input", {
                                                    value: newRule,
                                                    onChange: (e)=>setNewRule(e.target.value),
                                                    placeholder: "Add custom rule (e.g. 'Never use emojis in status reports')…",
                                                    style: {
                                                        flex: 1,
                                                        padding: "8px 12px",
                                                        borderRadius: 8,
                                                        border: "1px solid rgba(255,255,255,0.14)",
                                                        background: "rgba(0,0,0,0.35)",
                                                        color: "#f0ede8",
                                                        fontSize: 12
                                                    }
                                                }, void 0, false, {
                                                    fileName: "[project]/components/StudioModal.tsx",
                                                    lineNumber: 679,
                                                    columnNumber: 19
                                                }, this),
                                                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("button", {
                                                    type: "submit",
                                                    style: {
                                                        padding: "8px 14px",
                                                        borderRadius: 8,
                                                        border: `1px solid ${SECONDARY}66`,
                                                        background: `${SECONDARY}22`,
                                                        color: SECONDARY,
                                                        fontFamily: "var(--font-mono)",
                                                        fontSize: 10,
                                                        cursor: "pointer"
                                                    },
                                                    children: [
                                                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$plus$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__Plus$3e$__["Plus"], {
                                                            size: 12
                                                        }, void 0, false, {
                                                            fileName: "[project]/components/StudioModal.tsx",
                                                            lineNumber: 706,
                                                            columnNumber: 21
                                                        }, this),
                                                        " ADD RULE"
                                                    ]
                                                }, void 0, true, {
                                                    fileName: "[project]/components/StudioModal.tsx",
                                                    lineNumber: 693,
                                                    columnNumber: 19
                                                }, this)
                                            ]
                                        }, void 0, true, {
                                            fileName: "[project]/components/StudioModal.tsx",
                                            lineNumber: 678,
                                            columnNumber: 17
                                        }, this),
                                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                            style: {
                                                display: "flex",
                                                flexDirection: "column",
                                                gap: 6
                                            },
                                            children: (data?.learned_rules || []).map((r)=>/*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                                    style: {
                                                        display: "flex",
                                                        alignItems: "center",
                                                        gap: 10,
                                                        padding: "8px 12px",
                                                        borderRadius: 9,
                                                        background: "rgba(255,255,255,0.025)",
                                                        border: "1px solid rgba(255,255,255,0.08)"
                                                    },
                                                    children: [
                                                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("span", {
                                                            style: {
                                                                flex: 1,
                                                                fontSize: 12
                                                            },
                                                            children: r.rule
                                                        }, void 0, false, {
                                                            fileName: "[project]/components/StudioModal.tsx",
                                                            lineNumber: 723,
                                                            columnNumber: 23
                                                        }, this),
                                                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("span", {
                                                            style: {
                                                                fontSize: 10,
                                                                color: "rgba(240,237,232,0.45)"
                                                            },
                                                            children: r.ts
                                                        }, void 0, false, {
                                                            fileName: "[project]/components/StudioModal.tsx",
                                                            lineNumber: 724,
                                                            columnNumber: 23
                                                        }, this),
                                                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("button", {
                                                            type: "button",
                                                            onClick: ()=>postAction({
                                                                    action: "studio_delete_rule",
                                                                    rule_id: r.id
                                                                }),
                                                            style: {
                                                                background: "none",
                                                                border: "none",
                                                                color: RED,
                                                                cursor: "pointer"
                                                            },
                                                            children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$trash$2d$2$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__Trash2$3e$__["Trash2"], {
                                                                size: 13
                                                            }, void 0, false, {
                                                                fileName: "[project]/components/StudioModal.tsx",
                                                                lineNumber: 737,
                                                                columnNumber: 25
                                                            }, this)
                                                        }, void 0, false, {
                                                            fileName: "[project]/components/StudioModal.tsx",
                                                            lineNumber: 725,
                                                            columnNumber: 23
                                                        }, this)
                                                    ]
                                                }, r.id, true, {
                                                    fileName: "[project]/components/StudioModal.tsx",
                                                    lineNumber: 711,
                                                    columnNumber: 21
                                                }, this))
                                        }, void 0, false, {
                                            fileName: "[project]/components/StudioModal.tsx",
                                            lineNumber: 709,
                                            columnNumber: 17
                                        }, this)
                                    ]
                                }, void 0, true, {
                                    fileName: "[project]/components/StudioModal.tsx",
                                    lineNumber: 660,
                                    columnNumber: 15
                                }, this)
                            ]
                        }, void 0, true, {
                            fileName: "[project]/components/StudioModal.tsx",
                            lineNumber: 602,
                            columnNumber: 13
                        }, this),
                        tab === "skills" && /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                            style: {
                                display: "grid",
                                gridTemplateColumns: "1fr 1.25fr",
                                gap: 18
                            },
                            children: [
                                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                    style: {
                                        display: "flex",
                                        flexDirection: "column",
                                        gap: 8
                                    },
                                    children: [
                                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                            style: {
                                                fontFamily: "var(--font-mono)",
                                                fontSize: 10,
                                                letterSpacing: "0.16em",
                                                color: SECONDARY
                                            },
                                            children: [
                                                "INSTALLED SKILL.MD PLAYBOOKS (",
                                                data?.skills?.length || 0,
                                                ")"
                                            ]
                                        }, void 0, true, {
                                            fileName: "[project]/components/StudioModal.tsx",
                                            lineNumber: 749,
                                            columnNumber: 17
                                        }, this),
                                        (data?.skills || []).map((s)=>/*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                                onClick: ()=>{
                                                    setSelectedSkill(s);
                                                    if (!s.builtin) {
                                                        setSkillName(s.name);
                                                        setSkillDesc(s.description);
                                                        setSkillBody(s.body);
                                                    }
                                                },
                                                style: {
                                                    padding: "10px 12px",
                                                    borderRadius: 10,
                                                    border: `1px solid ${selectedSkill?.name === s.name ? PRIMARY : "rgba(255,255,255,0.09)"}`,
                                                    background: "rgba(255,255,255,0.025)",
                                                    cursor: "pointer"
                                                },
                                                children: [
                                                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                                        style: {
                                                            display: "flex",
                                                            alignItems: "center",
                                                            gap: 6
                                                        },
                                                        children: [
                                                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("span", {
                                                                style: {
                                                                    fontFamily: "var(--font-mono)",
                                                                    fontSize: 11,
                                                                    color: PRIMARY,
                                                                    fontWeight: 600
                                                                },
                                                                children: s.name
                                                            }, void 0, false, {
                                                                fileName: "[project]/components/StudioModal.tsx",
                                                                lineNumber: 783,
                                                                columnNumber: 23
                                                            }, this),
                                                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("span", {
                                                                style: {
                                                                    fontFamily: "var(--font-mono)",
                                                                    fontSize: 8.5,
                                                                    padding: "1px 6px",
                                                                    borderRadius: 999,
                                                                    background: s.builtin ? "rgba(255,255,255,0.08)" : `${SECONDARY}28`,
                                                                    color: s.builtin ? "rgba(240,237,232,0.7)" : SECONDARY
                                                                },
                                                                children: s.builtin ? "CORE" : "CUSTOM"
                                                            }, void 0, false, {
                                                                fileName: "[project]/components/StudioModal.tsx",
                                                                lineNumber: 793,
                                                                columnNumber: 23
                                                            }, this),
                                                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("span", {
                                                                style: {
                                                                    flex: 1
                                                                }
                                                            }, void 0, false, {
                                                                fileName: "[project]/components/StudioModal.tsx",
                                                                lineNumber: 805,
                                                                columnNumber: 23
                                                            }, this),
                                                            !s.builtin && /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("button", {
                                                                type: "button",
                                                                onClick: (e)=>{
                                                                    e.stopPropagation();
                                                                    postAction({
                                                                        action: "studio_delete_skill",
                                                                        name: s.name
                                                                    });
                                                                },
                                                                style: {
                                                                    background: "none",
                                                                    border: "none",
                                                                    color: RED,
                                                                    cursor: "pointer"
                                                                },
                                                                children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$trash$2d$2$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__Trash2$3e$__["Trash2"], {
                                                                    size: 12
                                                                }, void 0, false, {
                                                                    fileName: "[project]/components/StudioModal.tsx",
                                                                    lineNumber: 820,
                                                                    columnNumber: 27
                                                                }, this)
                                                            }, void 0, false, {
                                                                fileName: "[project]/components/StudioModal.tsx",
                                                                lineNumber: 807,
                                                                columnNumber: 25
                                                            }, this)
                                                        ]
                                                    }, void 0, true, {
                                                        fileName: "[project]/components/StudioModal.tsx",
                                                        lineNumber: 782,
                                                        columnNumber: 21
                                                    }, this),
                                                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                                        style: {
                                                            fontSize: 11,
                                                            color: "rgba(240,237,232,0.62)",
                                                            marginTop: 3
                                                        },
                                                        children: s.description
                                                    }, void 0, false, {
                                                        fileName: "[project]/components/StudioModal.tsx",
                                                        lineNumber: 824,
                                                        columnNumber: 21
                                                    }, this)
                                                ]
                                            }, s.name, true, {
                                                fileName: "[project]/components/StudioModal.tsx",
                                                lineNumber: 760,
                                                columnNumber: 19
                                            }, this))
                                    ]
                                }, void 0, true, {
                                    fileName: "[project]/components/StudioModal.tsx",
                                    lineNumber: 748,
                                    columnNumber: 15
                                }, this),
                                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("form", {
                                    onSubmit: onSaveSkill,
                                    style: {
                                        padding: 15,
                                        borderRadius: 14,
                                        background: "rgba(255,255,255,0.025)",
                                        border: "1px solid rgba(255,255,255,0.09)",
                                        display: "flex",
                                        flexDirection: "column",
                                        gap: 9
                                    },
                                    children: [
                                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                            style: {
                                                fontFamily: "var(--font-mono)",
                                                fontSize: 10,
                                                letterSpacing: "0.16em",
                                                color: PRIMARY
                                            },
                                            children: "AUTHOR CUSTOM SKILL.MD PLAYBOOK"
                                        }, void 0, false, {
                                            fileName: "[project]/components/StudioModal.tsx",
                                            lineNumber: 843,
                                            columnNumber: 17
                                        }, this),
                                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("input", {
                                            value: skillName,
                                            onChange: (e)=>setSkillName(e.target.value),
                                            placeholder: "slug-name (lowercase & hyphens, e.g. sprint-review)",
                                            style: {
                                                padding: "8px 11px",
                                                borderRadius: 8,
                                                border: "1px solid rgba(255,255,255,0.14)",
                                                background: "rgba(0,0,0,0.35)",
                                                color: "#f0ede8",
                                                fontFamily: "var(--font-mono)",
                                                fontSize: 11.5
                                            }
                                        }, void 0, false, {
                                            fileName: "[project]/components/StudioModal.tsx",
                                            lineNumber: 853,
                                            columnNumber: 17
                                        }, this),
                                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("input", {
                                            value: skillDesc,
                                            onChange: (e)=>setSkillDesc(e.target.value),
                                            placeholder: "Trigger description (20-160 chars: what it does & when to invoke)",
                                            style: {
                                                padding: "8px 11px",
                                                borderRadius: 8,
                                                border: "1px solid rgba(255,255,255,0.14)",
                                                background: "rgba(0,0,0,0.35)",
                                                color: "#f0ede8",
                                                fontSize: 12
                                            }
                                        }, void 0, false, {
                                            fileName: "[project]/components/StudioModal.tsx",
                                            lineNumber: 867,
                                            columnNumber: 17
                                        }, this),
                                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("textarea", {
                                            value: skillBody,
                                            onChange: (e)=>setSkillBody(e.target.value),
                                            rows: 10,
                                            style: {
                                                padding: "9px 11px",
                                                borderRadius: 8,
                                                border: "1px solid rgba(255,255,255,0.14)",
                                                background: "rgba(0,0,0,0.35)",
                                                color: "#f0ede8",
                                                fontFamily: "var(--font-mono)",
                                                fontSize: 11.5,
                                                resize: "vertical"
                                            }
                                        }, void 0, false, {
                                            fileName: "[project]/components/StudioModal.tsx",
                                            lineNumber: 880,
                                            columnNumber: 17
                                        }, this),
                                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("button", {
                                            type: "submit",
                                            style: {
                                                padding: "9px 14px",
                                                borderRadius: 9,
                                                border: `1px solid ${PRIMARY}66`,
                                                background: `${PRIMARY}22`,
                                                color: PRIMARY,
                                                fontFamily: "var(--font-mono)",
                                                fontSize: 10,
                                                cursor: "pointer"
                                            },
                                            children: "VALIDATE & SAVE SKILL.MD"
                                        }, void 0, false, {
                                            fileName: "[project]/components/StudioModal.tsx",
                                            lineNumber: 895,
                                            columnNumber: 17
                                        }, this)
                                    ]
                                }, void 0, true, {
                                    fileName: "[project]/components/StudioModal.tsx",
                                    lineNumber: 831,
                                    columnNumber: 15
                                }, this)
                            ]
                        }, void 0, true, {
                            fileName: "[project]/components/StudioModal.tsx",
                            lineNumber: 747,
                            columnNumber: 13
                        }, this),
                        tab === "themes" && /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                            style: {
                                display: "flex",
                                flexDirection: "column",
                                gap: 14
                            },
                            children: [
                                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                    style: {
                                        display: "grid",
                                        gridTemplateColumns: "repeat(auto-fill, minmax(240px, 1fr))",
                                        gap: 12
                                    },
                                    children: (data?.theme?.presets || []).map((p)=>{
                                        const active = data?.theme?.preset === p.id;
                                        return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("button", {
                                            type: "button",
                                            onClick: ()=>postAction({
                                                    action: "studio_save_theme",
                                                    preset: p.id,
                                                    custom_primary: "",
                                                    custom_secondary: ""
                                                }),
                                            style: {
                                                textAlign: "left",
                                                padding: "14px",
                                                borderRadius: 13,
                                                border: `1px solid ${active ? PRIMARY : "rgba(255,255,255,0.1)"}`,
                                                background: active ? `${PRIMARY}16` : "rgba(255,255,255,0.025)",
                                                color: "#f0ede8",
                                                cursor: "pointer"
                                            },
                                            children: [
                                                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                                    style: {
                                                        display: "flex",
                                                        alignItems: "center",
                                                        gap: 8
                                                    },
                                                    children: [
                                                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("span", {
                                                            style: {
                                                                width: 14,
                                                                height: 14,
                                                                borderRadius: "50%",
                                                                background: p.primary || PRIMARY
                                                            }
                                                        }, void 0, false, {
                                                            fileName: "[project]/components/StudioModal.tsx",
                                                            lineNumber: 950,
                                                            columnNumber: 25
                                                        }, this),
                                                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("span", {
                                                            style: {
                                                                width: 14,
                                                                height: 14,
                                                                borderRadius: "50%",
                                                                background: p.secondary || SECONDARY
                                                            }
                                                        }, void 0, false, {
                                                            fileName: "[project]/components/StudioModal.tsx",
                                                            lineNumber: 958,
                                                            columnNumber: 25
                                                        }, this),
                                                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("span", {
                                                            style: {
                                                                fontWeight: 600,
                                                                fontSize: 12.5
                                                            },
                                                            children: p.name
                                                        }, void 0, false, {
                                                            fileName: "[project]/components/StudioModal.tsx",
                                                            lineNumber: 966,
                                                            columnNumber: 25
                                                        }, this)
                                                    ]
                                                }, void 0, true, {
                                                    fileName: "[project]/components/StudioModal.tsx",
                                                    lineNumber: 949,
                                                    columnNumber: 23
                                                }, this),
                                                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                                    style: {
                                                        fontSize: 11,
                                                        color: "rgba(240,237,232,0.62)",
                                                        marginTop: 6
                                                    },
                                                    children: p.description
                                                }, void 0, false, {
                                                    fileName: "[project]/components/StudioModal.tsx",
                                                    lineNumber: 968,
                                                    columnNumber: 23
                                                }, this)
                                            ]
                                        }, p.id, true, {
                                            fileName: "[project]/components/StudioModal.tsx",
                                            lineNumber: 926,
                                            columnNumber: 21
                                        }, this);
                                    })
                                }, void 0, false, {
                                    fileName: "[project]/components/StudioModal.tsx",
                                    lineNumber: 916,
                                    columnNumber: 15
                                }, this),
                                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                    style: {
                                        marginTop: 8,
                                        padding: 16,
                                        borderRadius: 14,
                                        background: "rgba(255,255,255,0.025)",
                                        border: "1px solid rgba(255,255,255,0.09)",
                                        display: "flex",
                                        flexWrap: "wrap",
                                        alignItems: "center",
                                        gap: 14
                                    },
                                    children: [
                                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("span", {
                                            style: {
                                                fontFamily: "var(--font-mono)",
                                                fontSize: 10,
                                                letterSpacing: "0.14em",
                                                color: SECONDARY
                                            },
                                            children: "CUSTOM ORB & HUD HEX PALETTE"
                                        }, void 0, false, {
                                            fileName: "[project]/components/StudioModal.tsx",
                                            lineNumber: 996,
                                            columnNumber: 17
                                        }, this),
                                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("label", {
                                            style: {
                                                display: "inline-flex",
                                                alignItems: "center",
                                                gap: 6,
                                                fontSize: 11.5
                                            },
                                            children: [
                                                "Primary:",
                                                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("input", {
                                                    type: "color",
                                                    value: customPri || PRIMARY,
                                                    onChange: (e)=>setCustomPri(e.target.value),
                                                    style: {
                                                        width: 30,
                                                        height: 28,
                                                        border: "none",
                                                        background: "none",
                                                        cursor: "pointer"
                                                    }
                                                }, void 0, false, {
                                                    fileName: "[project]/components/StudioModal.tsx",
                                                    lineNumber: 1008,
                                                    columnNumber: 19
                                                }, this),
                                                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("input", {
                                                    value: customPri,
                                                    onChange: (e)=>setCustomPri(e.target.value),
                                                    placeholder: "#00e5ff",
                                                    style: {
                                                        width: 92,
                                                        padding: "6px 8px",
                                                        borderRadius: 6,
                                                        border: "1px solid rgba(255,255,255,0.14)",
                                                        background: "rgba(0,0,0,0.35)",
                                                        color: "#f0ede8",
                                                        fontFamily: "var(--font-mono)",
                                                        fontSize: 11
                                                    }
                                                }, void 0, false, {
                                                    fileName: "[project]/components/StudioModal.tsx",
                                                    lineNumber: 1014,
                                                    columnNumber: 19
                                                }, this)
                                            ]
                                        }, void 0, true, {
                                            fileName: "[project]/components/StudioModal.tsx",
                                            lineNumber: 1006,
                                            columnNumber: 17
                                        }, this),
                                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("label", {
                                            style: {
                                                display: "inline-flex",
                                                alignItems: "center",
                                                gap: 6,
                                                fontSize: 11.5
                                            },
                                            children: [
                                                "Secondary:",
                                                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("input", {
                                                    type: "color",
                                                    value: customSec || SECONDARY,
                                                    onChange: (e)=>setCustomSec(e.target.value),
                                                    style: {
                                                        width: 30,
                                                        height: 28,
                                                        border: "none",
                                                        background: "none",
                                                        cursor: "pointer"
                                                    }
                                                }, void 0, false, {
                                                    fileName: "[project]/components/StudioModal.tsx",
                                                    lineNumber: 1032,
                                                    columnNumber: 19
                                                }, this),
                                                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("input", {
                                                    value: customSec,
                                                    onChange: (e)=>setCustomSec(e.target.value),
                                                    placeholder: "#f5a623",
                                                    style: {
                                                        width: 92,
                                                        padding: "6px 8px",
                                                        borderRadius: 6,
                                                        border: "1px solid rgba(255,255,255,0.14)",
                                                        background: "rgba(0,0,0,0.35)",
                                                        color: "#f0ede8",
                                                        fontFamily: "var(--font-mono)",
                                                        fontSize: 11
                                                    }
                                                }, void 0, false, {
                                                    fileName: "[project]/components/StudioModal.tsx",
                                                    lineNumber: 1038,
                                                    columnNumber: 19
                                                }, this)
                                            ]
                                        }, void 0, true, {
                                            fileName: "[project]/components/StudioModal.tsx",
                                            lineNumber: 1030,
                                            columnNumber: 17
                                        }, this),
                                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("button", {
                                            type: "button",
                                            onClick: ()=>postAction({
                                                    action: "studio_save_theme",
                                                    preset: data?.theme?.preset || "default",
                                                    custom_primary: customPri,
                                                    custom_secondary: customSec
                                                }),
                                            style: {
                                                padding: "7px 14px",
                                                borderRadius: 999,
                                                border: `1px solid ${PRIMARY}66`,
                                                background: `${PRIMARY}22`,
                                                color: PRIMARY,
                                                fontFamily: "var(--font-mono)",
                                                fontSize: 10,
                                                cursor: "pointer"
                                            },
                                            children: "APPLY CUSTOM HEX"
                                        }, void 0, false, {
                                            fileName: "[project]/components/StudioModal.tsx",
                                            lineNumber: 1054,
                                            columnNumber: 17
                                        }, this)
                                    ]
                                }, void 0, true, {
                                    fileName: "[project]/components/StudioModal.tsx",
                                    lineNumber: 983,
                                    columnNumber: 15
                                }, this)
                            ]
                        }, void 0, true, {
                            fileName: "[project]/components/StudioModal.tsx",
                            lineNumber: 915,
                            columnNumber: 13
                        }, this)
                    ]
                }, void 0, true, {
                    fileName: "[project]/components/StudioModal.tsx",
                    lineNumber: 321,
                    columnNumber: 9
                }, this)
            ]
        }, void 0, true, {
            fileName: "[project]/components/StudioModal.tsx",
            lineNumber: 206,
            columnNumber: 7
        }, this)
    }, void 0, false, {
        fileName: "[project]/components/StudioModal.tsx",
        lineNumber: 190,
        columnNumber: 5
    }, this);
}
_s(StudioModal, "UdQFvx3G/xDr/cfwTia+jVYIKRM=", false, function() {
    return [
        __TURBOPACK__imported__module__$5b$project$5d2f$components$2f$JarvisBridge$2e$tsx__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useJarvis"]
    ];
});
_c = StudioModal;
var _c;
__turbopack_context__.k.register(_c, "StudioModal");
if (typeof globalThis.$RefreshHelpers$ === 'object' && globalThis.$RefreshHelpers !== null) {
    __turbopack_context__.k.registerExports(__turbopack_context__.m, globalThis.$RefreshHelpers$);
}
}),
"[project]/components/WorkerOrbsLayer.tsx [app-client] (ecmascript)", ((__turbopack_context__) => {
"use strict";

__turbopack_context__.s([
    "ActivityTimelineHud",
    ()=>ActivityTimelineHud,
    "WorkerOrbsLayer",
    ()=>WorkerOrbsLayer
]);
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/next/dist/compiled/react/jsx-dev-runtime.js [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/next/dist/compiled/react/index.js [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$activity$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__Activity$3e$__ = __turbopack_context__.i("[project]/node_modules/lucide-react/dist/esm/icons/activity.js [app-client] (ecmascript) <export default as Activity>");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$chevron$2d$down$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__ChevronDown$3e$__ = __turbopack_context__.i("[project]/node_modules/lucide-react/dist/esm/icons/chevron-down.js [app-client] (ecmascript) <export default as ChevronDown>");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$chevron$2d$right$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__ChevronRight$3e$__ = __turbopack_context__.i("[project]/node_modules/lucide-react/dist/esm/icons/chevron-right.js [app-client] (ecmascript) <export default as ChevronRight>");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$plus$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__Plus$3e$__ = __turbopack_context__.i("[project]/node_modules/lucide-react/dist/esm/icons/plus.js [app-client] (ecmascript) <export default as Plus>");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$square$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__Square$3e$__ = __turbopack_context__.i("[project]/node_modules/lucide-react/dist/esm/icons/square.js [app-client] (ecmascript) <export default as Square>");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$trash$2d$2$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__Trash2$3e$__ = __turbopack_context__.i("[project]/node_modules/lucide-react/dist/esm/icons/trash-2.js [app-client] (ecmascript) <export default as Trash2>");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$x$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__X$3e$__ = __turbopack_context__.i("[project]/node_modules/lucide-react/dist/esm/icons/x.js [app-client] (ecmascript) <export default as X>");
var __TURBOPACK__imported__module__$5b$project$5d2f$components$2f$JarvisBridge$2e$tsx__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/components/JarvisBridge.tsx [app-client] (ecmascript)");
;
var _s = __turbopack_context__.k.signature(), _s1 = __turbopack_context__.k.signature();
"use client";
;
;
;
const GREEN = "#3be38a";
const RED = "#ff5d6c";
function liveElapsed(w, nowSec) {
    if (w.status === "completed" || w.status === "failed" || w.status === "cancelled" || w.status === "expired") {
        return `${(w.elapsed_s || 0).toFixed(1)}s`;
    }
    const diff = Math.max(0, nowSec - (w.created_at || nowSec));
    return `${diff.toFixed(1)}s`;
}
function WorkerOrbsLayer() {
    _s();
    const { workers, theme, cancelWorker } = (0, __TURBOPACK__imported__module__$5b$project$5d2f$components$2f$JarvisBridge$2e$tsx__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useJarvis"])();
    const [angleTick, setAngleTick] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])(0);
    const [nowSec, setNowSec] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])({
        "WorkerOrbsLayer.useState": ()=>Date.now() / 1000
    }["WorkerOrbsLayer.useState"]);
    const [inspectedId, setInspectedId] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])(null);
    // Show active/pending workers + recently completed workers (< 14s old) in orbit
    const orbitWorkers = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useMemo"])({
        "WorkerOrbsLayer.useMemo[orbitWorkers]": ()=>{
            return workers.filter({
                "WorkerOrbsLayer.useMemo[orbitWorkers]": (w)=>{
                    if (w.status === "in_progress" || w.status === "pending" || w.status === "needs_review") return true;
                    return nowSec - (w.updated_at || 0) < 14;
                }
            }["WorkerOrbsLayer.useMemo[orbitWorkers]"]).slice(0, 8);
        }
    }["WorkerOrbsLayer.useMemo[orbitWorkers]"], [
        workers,
        nowSec
    ]);
    (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useEffect"])({
        "WorkerOrbsLayer.useEffect": ()=>{
            if (orbitWorkers.length === 0) return;
            const id = setInterval({
                "WorkerOrbsLayer.useEffect.id": ()=>{
                    setAngleTick({
                        "WorkerOrbsLayer.useEffect.id": (t)=>(t + 0.018) % (Math.PI * 2)
                    }["WorkerOrbsLayer.useEffect.id"]);
                    setNowSec(Date.now() / 1000);
                }
            }["WorkerOrbsLayer.useEffect.id"], 50);
            return ({
                "WorkerOrbsLayer.useEffect": ()=>clearInterval(id)
            })["WorkerOrbsLayer.useEffect"];
        }
    }["WorkerOrbsLayer.useEffect"], [
        orbitWorkers.length
    ]);
    // Also refresh nowSec lightly so recently finished orbs age out cleanly
    (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useEffect"])({
        "WorkerOrbsLayer.useEffect": ()=>{
            const id = setInterval({
                "WorkerOrbsLayer.useEffect.id": ()=>setNowSec(Date.now() / 1000)
            }["WorkerOrbsLayer.useEffect.id"], 1500);
            return ({
                "WorkerOrbsLayer.useEffect": ()=>clearInterval(id)
            })["WorkerOrbsLayer.useEffect"];
        }
    }["WorkerOrbsLayer.useEffect"], []);
    if (orbitWorkers.length === 0) return null;
    const inspected = orbitWorkers.find((w)=>w.id === inspectedId) || null;
    return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
        "aria-label": "Active worker orbs",
        style: {
            position: "absolute",
            inset: 0,
            zIndex: 5,
            pointerEvents: "none"
        },
        children: [
            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("svg", {
                width: "100%",
                height: "100%",
                viewBox: "-500 -500 1000 1000",
                preserveAspectRatio: "xMidYMid meet",
                style: {
                    position: "absolute",
                    inset: 0,
                    overflow: "visible"
                },
                children: orbitWorkers.map((w, idx)=>{
                    const base = idx / Math.max(1, orbitWorkers.length) * Math.PI * 2;
                    const speed = w.status === "in_progress" ? 1 : 0.35;
                    const theta = base + angleTick * speed;
                    const rx = 265 + idx % 2 * 38;
                    const ry = 175 + idx % 2 * 26;
                    const x = Math.cos(theta) * rx;
                    const y = Math.sin(theta) * ry;
                    const color = w.status === "failed" || w.status === "cancelled" ? RED : w.status === "completed" ? GREEN : idx % 2 === 0 ? theme.primary : theme.secondary;
                    return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("line", {
                        x1: 0,
                        y1: 0,
                        x2: x,
                        y2: y,
                        stroke: color,
                        strokeOpacity: w.status === "in_progress" ? 0.38 : 0.18,
                        strokeWidth: w.status === "in_progress" ? 1.5 : 1,
                        strokeDasharray: w.status === "pending" ? "4 5" : undefined
                    }, w.id, false, {
                        fileName: "[project]/components/WorkerOrbsLayer.tsx",
                        lineNumber: 100,
                        columnNumber: 13
                    }, this);
                })
            }, void 0, false, {
                fileName: "[project]/components/WorkerOrbsLayer.tsx",
                lineNumber: 76,
                columnNumber: 7
            }, this),
            orbitWorkers.map((w, idx)=>{
                const base = idx / Math.max(1, orbitWorkers.length) * Math.PI * 2;
                const speed = w.status === "in_progress" ? 1 : 0.35;
                const theta = base + angleTick * speed;
                const rxPct = 25 + idx % 2 * 4;
                const ryPct = 24 + idx % 2 * 3.5;
                const leftPct = 50 + Math.cos(theta) * rxPct;
                const topPct = 50 + Math.sin(theta) * ryPct;
                const depthScale = 0.86 + (Math.sin(theta) + 1) * 0.14;
                const color = w.status === "failed" || w.status === "cancelled" ? RED : w.status === "completed" ? GREEN : idx % 2 === 0 ? theme.primary : theme.secondary;
                return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("button", {
                    type: "button",
                    onClick: ()=>setInspectedId(inspectedId === w.id ? null : w.id),
                    style: {
                        position: "absolute",
                        left: `${leftPct}%`,
                        top: `${topPct}%`,
                        transform: `translate(-50%, -50%) scale(${depthScale.toFixed(3)})`,
                        pointerEvents: "auto",
                        display: "flex",
                        alignItems: "center",
                        gap: 8,
                        padding: "6px 11px 6px 7px",
                        borderRadius: 999,
                        border: `1px solid ${color}77`,
                        background: "rgba(5, 11, 22, 0.84)",
                        backdropFilter: "blur(12px)",
                        boxShadow: `0 0 22px ${color}44`,
                        cursor: "pointer",
                        color: "#f0ede8"
                    },
                    children: [
                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("span", {
                            style: {
                                width: 16,
                                height: 16,
                                borderRadius: "50%",
                                background: `radial-gradient(circle at 32% 32%, #ffffff, ${color} 62%, rgba(0,0,0,0.85) 100%)`,
                                boxShadow: `0 0 14px ${color}`,
                                flexShrink: 0
                            }
                        }, void 0, false, {
                            fileName: "[project]/components/WorkerOrbsLayer.tsx",
                            lineNumber: 158,
                            columnNumber: 13
                        }, this),
                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("span", {
                            style: {
                                fontFamily: "var(--font-mono)",
                                fontSize: 9.5,
                                letterSpacing: "0.08em",
                                maxWidth: 150,
                                overflow: "hidden",
                                textOverflow: "ellipsis",
                                whiteSpace: "nowrap"
                            },
                            children: w.title
                        }, void 0, false, {
                            fileName: "[project]/components/WorkerOrbsLayer.tsx",
                            lineNumber: 168,
                            columnNumber: 13
                        }, this),
                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("span", {
                            style: {
                                fontFamily: "var(--font-mono)",
                                fontSize: 9,
                                color
                            },
                            children: liveElapsed(w, nowSec)
                        }, void 0, false, {
                            fileName: "[project]/components/WorkerOrbsLayer.tsx",
                            lineNumber: 181,
                            columnNumber: 13
                        }, this)
                    ]
                }, w.id, true, {
                    fileName: "[project]/components/WorkerOrbsLayer.tsx",
                    lineNumber: 135,
                    columnNumber: 11
                }, this);
            }),
            inspected && /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                style: {
                    position: "fixed",
                    left: "50%",
                    bottom: 86,
                    transform: "translateX(-50%)",
                    width: "min(430px, 92vw)",
                    pointerEvents: "auto",
                    padding: "13px 16px",
                    borderRadius: 14,
                    background: theme.drawerBg,
                    border: `1px solid ${theme.primary}55`,
                    backdropFilter: "blur(22px)",
                    boxShadow: "0 16px 48px rgba(0,0,0,0.7)"
                },
                children: [
                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                        style: {
                            display: "flex",
                            alignItems: "center",
                            gap: 8
                        },
                        children: [
                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("span", {
                                style: {
                                    fontFamily: "var(--font-mono)",
                                    fontSize: 10,
                                    letterSpacing: "0.14em",
                                    color: theme.primary,
                                    flex: 1
                                },
                                children: [
                                    "WORKER ORB · ",
                                    inspected.id.toUpperCase(),
                                    " (",
                                    inspected.status.toUpperCase(),
                                    ")"
                                ]
                            }, void 0, true, {
                                fileName: "[project]/components/WorkerOrbsLayer.tsx",
                                lineNumber: 213,
                                columnNumber: 13
                            }, this),
                            (inspected.status === "in_progress" || inspected.status === "pending" || inspected.status === "needs_review") && /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("button", {
                                type: "button",
                                onClick: ()=>cancelWorker(inspected.id),
                                style: {
                                    padding: "3px 9px",
                                    borderRadius: 999,
                                    border: `1px solid ${RED}66`,
                                    background: `${RED}1f`,
                                    color: RED,
                                    fontFamily: "var(--font-mono)",
                                    fontSize: 9,
                                    cursor: "pointer"
                                },
                                children: "CANCEL"
                            }, void 0, false, {
                                fileName: "[project]/components/WorkerOrbsLayer.tsx",
                                lineNumber: 225,
                                columnNumber: 15
                            }, this),
                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("button", {
                                type: "button",
                                onClick: ()=>setInspectedId(null),
                                style: {
                                    background: "none",
                                    border: "none",
                                    color: "rgba(255,255,255,0.5)",
                                    cursor: "pointer"
                                },
                                children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$x$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__X$3e$__["X"], {
                                    size: 14
                                }, void 0, false, {
                                    fileName: "[project]/components/WorkerOrbsLayer.tsx",
                                    lineNumber: 252,
                                    columnNumber: 15
                                }, this)
                            }, void 0, false, {
                                fileName: "[project]/components/WorkerOrbsLayer.tsx",
                                lineNumber: 242,
                                columnNumber: 13
                            }, this)
                        ]
                    }, void 0, true, {
                        fileName: "[project]/components/WorkerOrbsLayer.tsx",
                        lineNumber: 212,
                        columnNumber: 11
                    }, this),
                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                        style: {
                            fontSize: 12,
                            color: "#f0ede8",
                            marginTop: 6
                        },
                        children: inspected.goal
                    }, void 0, false, {
                        fileName: "[project]/components/WorkerOrbsLayer.tsx",
                        lineNumber: 255,
                        columnNumber: 11
                    }, this),
                    inspected.steps.length > 0 && /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                        style: {
                            marginTop: 8,
                            paddingTop: 8,
                            borderTop: "1px solid rgba(255,255,255,0.08)",
                            maxHeight: 110,
                            overflowY: "auto",
                            display: "flex",
                            flexDirection: "column",
                            gap: 4
                        },
                        children: inspected.steps.map((s)=>/*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                style: {
                                    fontFamily: "var(--font-mono)",
                                    fontSize: 10,
                                    color: "rgba(240,237,232,0.72)"
                                },
                                children: [
                                    "#",
                                    s.step,
                                    " ",
                                    s.action,
                                    " → ",
                                    s.result
                                ]
                            }, s.step, true, {
                                fileName: "[project]/components/WorkerOrbsLayer.tsx",
                                lineNumber: 272,
                                columnNumber: 17
                            }, this))
                    }, void 0, false, {
                        fileName: "[project]/components/WorkerOrbsLayer.tsx",
                        lineNumber: 259,
                        columnNumber: 13
                    }, this)
                ]
            }, void 0, true, {
                fileName: "[project]/components/WorkerOrbsLayer.tsx",
                lineNumber: 196,
                columnNumber: 9
            }, this)
        ]
    }, void 0, true, {
        fileName: "[project]/components/WorkerOrbsLayer.tsx",
        lineNumber: 66,
        columnNumber: 5
    }, this);
}
_s(WorkerOrbsLayer, "b0UKOmocPf6ZZR7AOSCjulSyQPU=", false, function() {
    return [
        __TURBOPACK__imported__module__$5b$project$5d2f$components$2f$JarvisBridge$2e$tsx__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useJarvis"]
    ];
});
_c = WorkerOrbsLayer;
function ActivityTimelineHud() {
    _s1();
    const { workers, activePersona, theme, activityOpen, setActivityOpen, spawnWorker, cancelWorker, clearCompletedWorkers } = (0, __TURBOPACK__imported__module__$5b$project$5d2f$components$2f$JarvisBridge$2e$tsx__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useJarvis"])();
    const [filter, setFilter] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])("all");
    const [goalInput, setGoalInput] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])("");
    const [expandedId, setExpandedId] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])(null);
    const [nowSec, setNowSec] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])({
        "ActivityTimelineHud.useState": ()=>Date.now() / 1000
    }["ActivityTimelineHud.useState"]);
    const runningCount = workers.filter((w)=>w.status === "in_progress" || w.status === "needs_review").length;
    const queuedCount = workers.filter((w)=>w.status === "pending").length;
    const doneCount = workers.filter((w)=>w.status === "completed" || w.status === "failed" || w.status === "cancelled" || w.status === "expired").length;
    (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useEffect"])({
        "ActivityTimelineHud.useEffect": ()=>{
            if (!activityOpen && runningCount === 0) return;
            const id = setInterval({
                "ActivityTimelineHud.useEffect.id": ()=>setNowSec(Date.now() / 1000)
            }["ActivityTimelineHud.useEffect.id"], 250);
            return ({
                "ActivityTimelineHud.useEffect": ()=>clearInterval(id)
            })["ActivityTimelineHud.useEffect"];
        }
    }["ActivityTimelineHud.useEffect"], [
        activityOpen,
        runningCount
    ]);
    const filtered = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useMemo"])({
        "ActivityTimelineHud.useMemo[filtered]": ()=>{
            return workers.filter({
                "ActivityTimelineHud.useMemo[filtered]": (w)=>{
                    if (filter === "running") return w.status === "in_progress" || w.status === "needs_review";
                    if (filter === "queued") return w.status === "pending";
                    if (filter === "done") {
                        return w.status === "completed" || w.status === "failed" || w.status === "cancelled" || w.status === "expired";
                    }
                    return true;
                }
            }["ActivityTimelineHud.useMemo[filtered]"]);
        }
    }["ActivityTimelineHud.useMemo[filtered]"], [
        workers,
        filter
    ]);
    const PRIMARY = theme.primary;
    const SECONDARY = theme.secondary;
    const onSpawn = async (e)=>{
        e.preventDefault();
        if (!goalInput.trim()) return;
        const g = goalInput.trim();
        setGoalInput("");
        await spawnWorker(g);
    };
    const showFloatingActivityPill = runningCount > 0 || queuedCount > 0 || activityOpen;
    return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["Fragment"], {
        children: [
            showFloatingActivityPill && /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("button", {
                type: "button",
                onClick: ()=>setActivityOpen((o)=>!o),
                style: {
                    position: "fixed",
                    top: 124,
                    left: 26,
                    zIndex: 42,
                    display: "inline-flex",
                    alignItems: "center",
                    gap: 7,
                    padding: "5px 11px",
                    borderRadius: 999,
                    border: `1px solid ${runningCount > 0 ? `${PRIMARY}77` : "rgba(255,255,255,0.14)"}`,
                    background: activityOpen ? `${PRIMARY}22` : theme.barBg,
                    backdropFilter: "blur(14px)",
                    color: runningCount > 0 || activityOpen ? PRIMARY : "rgba(240,237,232,0.8)",
                    fontFamily: "var(--font-mono)",
                    fontSize: 9.5,
                    letterSpacing: "0.14em",
                    cursor: "pointer"
                },
                children: [
                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$activity$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__Activity$3e$__["Activity"], {
                        size: 12
                    }, void 0, false, {
                        fileName: "[project]/components/WorkerOrbsLayer.tsx",
                        lineNumber: 377,
                        columnNumber: 11
                    }, this),
                    "ACTIVITY",
                    runningCount > 0 ? /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("span", {
                        style: {
                            color: GREEN
                        },
                        children: [
                            "· ",
                            runningCount,
                            " RUNNING"
                        ]
                    }, void 0, true, {
                        fileName: "[project]/components/WorkerOrbsLayer.tsx",
                        lineNumber: 380,
                        columnNumber: 13
                    }, this) : workers.length > 0 ? /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("span", {
                        style: {
                            opacity: 0.72
                        },
                        children: [
                            "· ",
                            workers.length
                        ]
                    }, void 0, true, {
                        fileName: "[project]/components/WorkerOrbsLayer.tsx",
                        lineNumber: 382,
                        columnNumber: 13
                    }, this) : null
                ]
            }, void 0, true, {
                fileName: "[project]/components/WorkerOrbsLayer.tsx",
                lineNumber: 352,
                columnNumber: 9
            }, this),
            activityOpen && /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("aside", {
                "aria-label": "Live worker activity timeline",
                style: {
                    position: "fixed",
                    top: showFloatingActivityPill ? 160 : 62,
                    left: 24,
                    width: "min(380px, 92vw)",
                    maxHeight: "calc(100vh - 230px)",
                    zIndex: 49,
                    background: theme.drawerBg,
                    border: `1px solid ${PRIMARY}38`,
                    borderRadius: 16,
                    backdropFilter: "blur(24px)",
                    boxShadow: "0 14px 48px rgba(0,0,0,0.68)",
                    display: "flex",
                    flexDirection: "column",
                    overflow: "hidden"
                },
                children: [
                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                        style: {
                            display: "flex",
                            alignItems: "center",
                            gap: 8,
                            padding: "11px 14px",
                            borderBottom: `1px solid ${PRIMARY}22`
                        },
                        children: [
                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$activity$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__Activity$3e$__["Activity"], {
                                size: 13,
                                color: PRIMARY
                            }, void 0, false, {
                                fileName: "[project]/components/WorkerOrbsLayer.tsx",
                                lineNumber: 416,
                                columnNumber: 13
                            }, this),
                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("span", {
                                style: {
                                    fontFamily: "var(--font-mono)",
                                    fontSize: 10,
                                    letterSpacing: "0.2em",
                                    color: PRIMARY,
                                    flex: 1
                                },
                                children: "PARALLEL WORKERS"
                            }, void 0, false, {
                                fileName: "[project]/components/WorkerOrbsLayer.tsx",
                                lineNumber: 417,
                                columnNumber: 13
                            }, this),
                            doneCount > 0 && /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("button", {
                                type: "button",
                                onClick: clearCompletedWorkers,
                                title: "Clear completed workers",
                                style: {
                                    display: "inline-flex",
                                    alignItems: "center",
                                    gap: 4,
                                    padding: "3px 8px",
                                    borderRadius: 999,
                                    border: "1px solid rgba(255,255,255,0.14)",
                                    background: "transparent",
                                    color: "rgba(240,237,232,0.62)",
                                    fontFamily: "var(--font-mono)",
                                    fontSize: 8.5,
                                    cursor: "pointer"
                                },
                                children: [
                                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$trash$2d$2$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__Trash2$3e$__["Trash2"], {
                                        size: 10
                                    }, void 0, false, {
                                        fileName: "[project]/components/WorkerOrbsLayer.tsx",
                                        lineNumber: 447,
                                        columnNumber: 17
                                    }, this),
                                    "CLEAR DONE"
                                ]
                            }, void 0, true, {
                                fileName: "[project]/components/WorkerOrbsLayer.tsx",
                                lineNumber: 429,
                                columnNumber: 15
                            }, this),
                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("button", {
                                type: "button",
                                onClick: ()=>setActivityOpen(false),
                                style: {
                                    background: "none",
                                    border: "none",
                                    color: "rgba(255,255,255,0.48)",
                                    cursor: "pointer"
                                },
                                children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$x$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__X$3e$__["X"], {
                                    size: 15
                                }, void 0, false, {
                                    fileName: "[project]/components/WorkerOrbsLayer.tsx",
                                    lineNumber: 461,
                                    columnNumber: 15
                                }, this)
                            }, void 0, false, {
                                fileName: "[project]/components/WorkerOrbsLayer.tsx",
                                lineNumber: 451,
                                columnNumber: 13
                            }, this)
                        ]
                    }, void 0, true, {
                        fileName: "[project]/components/WorkerOrbsLayer.tsx",
                        lineNumber: 407,
                        columnNumber: 11
                    }, this),
                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                        style: {
                            display: "flex",
                            gap: 5,
                            padding: "8px 12px",
                            borderBottom: "1px solid rgba(255,255,255,0.06)"
                        },
                        children: [
                            {
                                id: "all",
                                label: `ALL (${workers.length})`
                            },
                            {
                                id: "running",
                                label: `RUN (${runningCount})`
                            },
                            {
                                id: "queued",
                                label: `QUEUE (${queuedCount})`
                            },
                            {
                                id: "done",
                                label: `DONE (${doneCount})`
                            }
                        ].map((f)=>/*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("button", {
                                type: "button",
                                onClick: ()=>setFilter(f.id),
                                style: {
                                    flex: 1,
                                    padding: "4px 6px",
                                    borderRadius: 999,
                                    border: `1px solid ${filter === f.id ? `${PRIMARY}66` : "rgba(255,255,255,0.1)"}`,
                                    background: filter === f.id ? `${PRIMARY}1f` : "transparent",
                                    color: filter === f.id ? PRIMARY : "rgba(240,237,232,0.6)",
                                    fontFamily: "var(--font-mono)",
                                    fontSize: 8.5,
                                    letterSpacing: "0.08em",
                                    cursor: "pointer"
                                },
                                children: f.label
                            }, f.id, false, {
                                fileName: "[project]/components/WorkerOrbsLayer.tsx",
                                lineNumber: 482,
                                columnNumber: 15
                            }, this))
                    }, void 0, false, {
                        fileName: "[project]/components/WorkerOrbsLayer.tsx",
                        lineNumber: 466,
                        columnNumber: 11
                    }, this),
                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("form", {
                        onSubmit: onSpawn,
                        style: {
                            display: "flex",
                            gap: 6,
                            padding: "8px 12px",
                            borderBottom: "1px solid rgba(255,255,255,0.06)"
                        },
                        children: [
                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("input", {
                                type: "text",
                                value: goalInput,
                                onChange: (e)=>setGoalInput(e.target.value),
                                placeholder: "Spawn parallel worker goal…",
                                style: {
                                    flex: 1,
                                    padding: "6px 10px",
                                    borderRadius: 8,
                                    border: "1px solid rgba(255,255,255,0.14)",
                                    background: "rgba(0,0,0,0.35)",
                                    color: "#f0ede8",
                                    fontSize: 11.5,
                                    outline: "none"
                                }
                            }, void 0, false, {
                                fileName: "[project]/components/WorkerOrbsLayer.tsx",
                                lineNumber: 516,
                                columnNumber: 13
                            }, this),
                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("button", {
                                type: "submit",
                                style: {
                                    display: "inline-flex",
                                    alignItems: "center",
                                    gap: 4,
                                    padding: "6px 10px",
                                    borderRadius: 8,
                                    border: `1px solid ${SECONDARY}66`,
                                    background: `${SECONDARY}22`,
                                    color: SECONDARY,
                                    fontFamily: "var(--font-mono)",
                                    fontSize: 9.5,
                                    cursor: "pointer"
                                },
                                children: [
                                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$plus$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__Plus$3e$__["Plus"], {
                                        size: 11
                                    }, void 0, false, {
                                        fileName: "[project]/components/WorkerOrbsLayer.tsx",
                                        lineNumber: 548,
                                        columnNumber: 15
                                    }, this),
                                    "SPAWN"
                                ]
                            }, void 0, true, {
                                fileName: "[project]/components/WorkerOrbsLayer.tsx",
                                lineNumber: 532,
                                columnNumber: 13
                            }, this)
                        ]
                    }, void 0, true, {
                        fileName: "[project]/components/WorkerOrbsLayer.tsx",
                        lineNumber: 507,
                        columnNumber: 11
                    }, this),
                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                        style: {
                            flex: 1,
                            overflowY: "auto",
                            padding: "10px 12px",
                            display: "flex",
                            flexDirection: "column",
                            gap: 8
                        },
                        children: filtered.length === 0 ? /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                            style: {
                                fontSize: 11.5,
                                color: "rgba(240,237,232,0.42)",
                                textAlign: "center",
                                padding: "22px 10px"
                            },
                            children: "No workers in this view. Parallel tools and subagents fan out here and orbit the core in real time."
                        }, void 0, false, {
                            fileName: "[project]/components/WorkerOrbsLayer.tsx",
                            lineNumber: 565,
                            columnNumber: 15
                        }, this) : filtered.map((w)=>{
                            const statusColor = w.status === "in_progress" ? PRIMARY : w.status === "pending" || w.status === "needs_review" ? SECONDARY : w.status === "completed" ? GREEN : RED;
                            const open = expandedId === w.id;
                            return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                style: {
                                    padding: "9px 11px",
                                    borderRadius: 11,
                                    background: "rgba(255,255,255,0.025)",
                                    border: `1px solid ${statusColor}38`
                                },
                                children: [
                                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                        style: {
                                            display: "flex",
                                            alignItems: "center",
                                            gap: 6
                                        },
                                        children: [
                                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("button", {
                                                type: "button",
                                                onClick: ()=>setExpandedId(open ? null : w.id),
                                                style: {
                                                    background: "none",
                                                    border: "none",
                                                    color: statusColor,
                                                    padding: 0,
                                                    cursor: "pointer",
                                                    display: "inline-flex"
                                                },
                                                children: open ? /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$chevron$2d$down$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__ChevronDown$3e$__["ChevronDown"], {
                                                    size: 13
                                                }, void 0, false, {
                                                    fileName: "[project]/components/WorkerOrbsLayer.tsx",
                                                    lineNumber: 610,
                                                    columnNumber: 33
                                                }, this) : /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$chevron$2d$right$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__ChevronRight$3e$__["ChevronRight"], {
                                                    size: 13
                                                }, void 0, false, {
                                                    fileName: "[project]/components/WorkerOrbsLayer.tsx",
                                                    lineNumber: 610,
                                                    columnNumber: 61
                                                }, this)
                                            }, void 0, false, {
                                                fileName: "[project]/components/WorkerOrbsLayer.tsx",
                                                lineNumber: 598,
                                                columnNumber: 23
                                            }, this),
                                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("span", {
                                                style: {
                                                    fontFamily: "var(--font-mono)",
                                                    fontSize: 9,
                                                    padding: "1px 6px",
                                                    borderRadius: 999,
                                                    background: `${statusColor}22`,
                                                    color: statusColor,
                                                    textTransform: "uppercase"
                                                },
                                                children: w.status.replace("_", " ")
                                            }, void 0, false, {
                                                fileName: "[project]/components/WorkerOrbsLayer.tsx",
                                                lineNumber: 612,
                                                columnNumber: 23
                                            }, this),
                                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("span", {
                                                style: {
                                                    fontSize: 11.5,
                                                    color: "#f0ede8",
                                                    flex: 1,
                                                    overflow: "hidden",
                                                    textOverflow: "ellipsis",
                                                    whiteSpace: "nowrap"
                                                },
                                                children: w.title
                                            }, void 0, false, {
                                                fileName: "[project]/components/WorkerOrbsLayer.tsx",
                                                lineNumber: 625,
                                                columnNumber: 23
                                            }, this),
                                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("span", {
                                                style: {
                                                    fontFamily: "var(--font-mono)",
                                                    fontSize: 9.5,
                                                    color: "rgba(240,237,232,0.58)"
                                                },
                                                children: liveElapsed(w, nowSec)
                                            }, void 0, false, {
                                                fileName: "[project]/components/WorkerOrbsLayer.tsx",
                                                lineNumber: 637,
                                                columnNumber: 23
                                            }, this),
                                            (w.status === "in_progress" || w.status === "pending" || w.status === "needs_review") && /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("button", {
                                                type: "button",
                                                onClick: ()=>cancelWorker(w.id),
                                                title: "Cancel worker",
                                                style: {
                                                    display: "inline-flex",
                                                    alignItems: "center",
                                                    justifyContent: "center",
                                                    width: 22,
                                                    height: 22,
                                                    borderRadius: 6,
                                                    border: `1px solid ${RED}55`,
                                                    background: `${RED}1a`,
                                                    color: RED,
                                                    cursor: "pointer"
                                                },
                                                children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$square$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__Square$3e$__["Square"], {
                                                    size: 9
                                                }, void 0, false, {
                                                    fileName: "[project]/components/WorkerOrbsLayer.tsx",
                                                    lineNumber: 664,
                                                    columnNumber: 27
                                                }, this)
                                            }, void 0, false, {
                                                fileName: "[project]/components/WorkerOrbsLayer.tsx",
                                                lineNumber: 647,
                                                columnNumber: 25
                                            }, this)
                                        ]
                                    }, void 0, true, {
                                        fileName: "[project]/components/WorkerOrbsLayer.tsx",
                                        lineNumber: 597,
                                        columnNumber: 21
                                    }, this),
                                    open && /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                        style: {
                                            marginTop: 7,
                                            paddingTop: 7,
                                            borderTop: "1px solid rgba(255,255,255,0.06)",
                                            fontSize: 11,
                                            color: "rgba(240,237,232,0.75)"
                                        },
                                        children: [
                                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                                children: w.goal
                                            }, void 0, false, {
                                                fileName: "[project]/components/WorkerOrbsLayer.tsx",
                                                lineNumber: 679,
                                                columnNumber: 25
                                            }, this),
                                            w.steps.map((s)=>/*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                                    style: {
                                                        fontFamily: "var(--font-mono)",
                                                        fontSize: 10,
                                                        color: "rgba(240,237,232,0.6)",
                                                        marginTop: 3
                                                    },
                                                    children: [
                                                        "#",
                                                        s.step,
                                                        " ",
                                                        s.action,
                                                        " → ",
                                                        s.result
                                                    ]
                                                }, s.step, true, {
                                                    fileName: "[project]/components/WorkerOrbsLayer.tsx",
                                                    lineNumber: 681,
                                                    columnNumber: 27
                                                }, this)),
                                            w.result && /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                                style: {
                                                    color: GREEN,
                                                    marginTop: 4,
                                                    fontSize: 10.5
                                                },
                                                children: [
                                                    "Result: ",
                                                    w.result
                                                ]
                                            }, void 0, true, {
                                                fileName: "[project]/components/WorkerOrbsLayer.tsx",
                                                lineNumber: 694,
                                                columnNumber: 27
                                            }, this),
                                            w.error && /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                                style: {
                                                    color: RED,
                                                    marginTop: 4,
                                                    fontSize: 10.5
                                                },
                                                children: [
                                                    "Error: ",
                                                    w.error
                                                ]
                                            }, void 0, true, {
                                                fileName: "[project]/components/WorkerOrbsLayer.tsx",
                                                lineNumber: 699,
                                                columnNumber: 27
                                            }, this)
                                        ]
                                    }, void 0, true, {
                                        fileName: "[project]/components/WorkerOrbsLayer.tsx",
                                        lineNumber: 670,
                                        columnNumber: 23
                                    }, this)
                                ]
                            }, w.id, true, {
                                fileName: "[project]/components/WorkerOrbsLayer.tsx",
                                lineNumber: 588,
                                columnNumber: 19
                            }, this);
                        })
                    }, void 0, false, {
                        fileName: "[project]/components/WorkerOrbsLayer.tsx",
                        lineNumber: 554,
                        columnNumber: 11
                    }, this)
                ]
            }, void 0, true, {
                fileName: "[project]/components/WorkerOrbsLayer.tsx",
                lineNumber: 388,
                columnNumber: 9
            }, this)
        ]
    }, void 0, true, {
        fileName: "[project]/components/WorkerOrbsLayer.tsx",
        lineNumber: 349,
        columnNumber: 5
    }, this);
}
_s1(ActivityTimelineHud, "TfDV7ZVPc7TI2n85OZFzqFvjKA0=", false, function() {
    return [
        __TURBOPACK__imported__module__$5b$project$5d2f$components$2f$JarvisBridge$2e$tsx__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useJarvis"]
    ];
});
_c1 = ActivityTimelineHud;
var _c, _c1;
__turbopack_context__.k.register(_c, "WorkerOrbsLayer");
__turbopack_context__.k.register(_c1, "ActivityTimelineHud");
if (typeof globalThis.$RefreshHelpers$ === 'object' && globalThis.$RefreshHelpers !== null) {
    __turbopack_context__.k.registerExports(__turbopack_context__.m, globalThis.$RefreshHelpers$);
}
}),
"[project]/components/theme.ts [app-client] (ecmascript)", ((__turbopack_context__) => {
"use strict";

__turbopack_context__.s([
    "PERSONA_THEMES",
    ()=>PERSONA_THEMES
]);
const PERSONA_THEMES = {
    male: {
        id: "male",
        label: "MALE EDITION",
        shortLabel: "MALE",
        badge: "CYAN · STARK GOLD",
        subtitle: "Electric cyan particle core, warm gold orbital rings & deep baritone voice.",
        defaultVoice: "Charon",
        voiceHint: "Charon · Deep & Calm",
        primary: "#00e5ff",
        primaryBright: "#c8f7ff",
        primarySoftBg: "rgba(0, 229, 255, 0.08)",
        primaryBorder: "rgba(0, 229, 255, 0.28)",
        filamentLine: "#a5f3fc",
        filamentDot: "#e0fbff",
        filamentTextRgb: "165, 243, 252",
        secondary: "#f5a623",
        secondaryBright: "#ffd080",
        secondarySoftBg: "rgba(245, 166, 35, 0.09)",
        toolNode: "#7f9bb3",
        ringLine: "#1b5f78",
        pcbDot: "#37d6ef",
        fieldMesh: "#143f4f",
        fieldDot: "#2bd0e6",
        mesh: "#1a5468",
        spoke: "#22566b",
        spokeHot: "#33eaff",
        mote: "#5fe0f2",
        moteHot: "#bff6ff",
        coLink: "#5eead4",
        worldBg: "radial-gradient(ellipse 95% 88% at 50% 42%, #122c43 0%, #0c1d30 38%, #07111f 72%, #050b14 100%)",
        pageBg: "#04080f",
        panelBg: "rgba(5, 11, 22, 0.96)",
        drawerBg: "rgba(4, 9, 18, 0.88)",
        barBg: "rgba(4, 10, 20, 0.74)",
        inputBg: "rgba(10, 20, 36, 0.92)",
        tileBg: "rgba(6, 14, 26, 0.78)",
        orbGlowRgb: "13, 210, 255",
        orbGlow2Rgb: "13, 170, 228",
        femaleMix: 0
    },
    female: {
        id: "female",
        label: "FEMALE EDITION",
        shortLabel: "FEMALE",
        badge: "ROSE · ORCHID AMETHYST",
        subtitle: "Luminous rose-magenta particle core, orchid-violet rings & natural female voice.",
        defaultVoice: "Aoede",
        voiceHint: "Aoede · Warm & Articulate",
        primary: "#ff4db8",
        primaryBright: "#ffd6f3",
        primarySoftBg: "rgba(255, 77, 184, 0.09)",
        primaryBorder: "rgba(255, 77, 184, 0.30)",
        filamentLine: "#fbcfe8",
        filamentDot: "#fff0f8",
        filamentTextRgb: "251, 207, 232",
        secondary: "#c084fc",
        secondaryBright: "#f3d4ff",
        secondarySoftBg: "rgba(192, 132, 252, 0.10)",
        toolNode: "#b39ddb",
        ringLine: "#69275c",
        pcbDot: "#ff73cb",
        fieldMesh: "#4a1d46",
        fieldDot: "#e879f9",
        mesh: "#5c2657",
        spoke: "#6b2c63",
        spokeHot: "#ff7ce5",
        mote: "#ff8ee3",
        moteHot: "#ffe0f7",
        coLink: "#e879f9",
        worldBg: "radial-gradient(ellipse 95% 88% at 50% 42%, #2d1236 0%, #1d0b28 38%, #11061a 72%, #07030d 100%)",
        pageBg: "#07030d",
        panelBg: "rgba(16, 6, 24, 0.96)",
        drawerBg: "rgba(14, 5, 22, 0.88)",
        barBg: "rgba(15, 6, 24, 0.76)",
        inputBg: "rgba(26, 10, 38, 0.92)",
        tileBg: "rgba(20, 8, 30, 0.78)",
        orbGlowRgb: "255, 77, 184",
        orbGlow2Rgb: "192, 132, 252",
        femaleMix: 1
    }
};
if (typeof globalThis.$RefreshHelpers$ === 'object' && globalThis.$RefreshHelpers !== null) {
    __turbopack_context__.k.registerExports(__turbopack_context__.m, globalThis.$RefreshHelpers$);
}
}),
]);})()

//# sourceMappingURL=components_1n08vhqtzfrfm._.js.map