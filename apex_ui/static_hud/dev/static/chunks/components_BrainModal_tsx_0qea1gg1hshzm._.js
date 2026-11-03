(globalThis["TURBOPACK"] || (globalThis["TURBOPACK"] = [])).push([typeof document === "object" ? document.currentScript : undefined,
"[project]/components/BrainModal.tsx [app-client] (ecmascript)", ((__turbopack_context__) => {
"use strict";

__turbopack_context__.s([
    "default",
    ()=>BrainModal
]);
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/next/dist/compiled/react/jsx-dev-runtime.js [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/next/dist/compiled/react/index.js [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$brain$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__Brain$3e$__ = __turbopack_context__.i("[project]/node_modules/lucide-react/dist/esm/icons/brain.js [app-client] (ecmascript) <export default as Brain>");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$clock$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__Clock$3e$__ = __turbopack_context__.i("[project]/node_modules/lucide-react/dist/esm/icons/clock.js [app-client] (ecmascript) <export default as Clock>");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$download$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__Download$3e$__ = __turbopack_context__.i("[project]/node_modules/lucide-react/dist/esm/icons/download.js [app-client] (ecmascript) <export default as Download>");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$pen$2d$line$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__Edit3$3e$__ = __turbopack_context__.i("[project]/node_modules/lucide-react/dist/esm/icons/pen-line.js [app-client] (ecmascript) <export default as Edit3>");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$file$2d$text$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__FileText$3e$__ = __turbopack_context__.i("[project]/node_modules/lucide-react/dist/esm/icons/file-text.js [app-client] (ecmascript) <export default as FileText>");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$pin$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__Pin$3e$__ = __turbopack_context__.i("[project]/node_modules/lucide-react/dist/esm/icons/pin.js [app-client] (ecmascript) <export default as Pin>");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$plus$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__Plus$3e$__ = __turbopack_context__.i("[project]/node_modules/lucide-react/dist/esm/icons/plus.js [app-client] (ecmascript) <export default as Plus>");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$search$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__Search$3e$__ = __turbopack_context__.i("[project]/node_modules/lucide-react/dist/esm/icons/search.js [app-client] (ecmascript) <export default as Search>");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$shield$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__Shield$3e$__ = __turbopack_context__.i("[project]/node_modules/lucide-react/dist/esm/icons/shield.js [app-client] (ecmascript) <export default as Shield>");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$sparkles$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__Sparkles$3e$__ = __turbopack_context__.i("[project]/node_modules/lucide-react/dist/esm/icons/sparkles.js [app-client] (ecmascript) <export default as Sparkles>");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$trash$2d$2$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__Trash2$3e$__ = __turbopack_context__.i("[project]/node_modules/lucide-react/dist/esm/icons/trash-2.js [app-client] (ecmascript) <export default as Trash2>");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$upload$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__Upload$3e$__ = __turbopack_context__.i("[project]/node_modules/lucide-react/dist/esm/icons/upload.js [app-client] (ecmascript) <export default as Upload>");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$x$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__X$3e$__ = __turbopack_context__.i("[project]/node_modules/lucide-react/dist/esm/icons/x.js [app-client] (ecmascript) <export default as X>");
var __TURBOPACK__imported__module__$5b$project$5d2f$components$2f$JarvisBridge$2e$tsx__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/components/JarvisBridge.tsx [app-client] (ecmascript)");
;
var _s = __turbopack_context__.k.signature();
"use client";
;
;
;
const GREEN = "#34d399";
const RED = "#ff5b79";
const CATEGORIES = [
    "preferences",
    "identity",
    "projects",
    "relationships",
    "wishes",
    "notes"
];
function BrainModal() {
    _s();
    const { assistantName, theme, privacy, brainModalOpen, setBrainModalOpen, updatePrivacy, showContentCard, fireLocalTrace } = (0, __TURBOPACK__imported__module__$5b$project$5d2f$components$2f$JarvisBridge$2e$tsx__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useJarvis"])();
    const PRIMARY = theme.primary;
    const SECONDARY = theme.secondary;
    const [tab, setTab] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])("memories");
    const [query, setQuery] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])("");
    const [channelFilter, setChannelFilter] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])("");
    const [memories, setMemories] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])([]);
    const [timeline, setTimeline] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])([]);
    const [epochs, setEpochs] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])([]);
    const [files, setFiles] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])([]);
    const [outputs, setOutputs] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])([]);
    const [loading, setLoading] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])(false);
    // Add / edit memory states
    const [newCat, setNewCat] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])("preferences");
    const [newKey, setNewKey] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])("");
    const [newVal, setNewVal] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])("");
    const [editId, setEditId] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])(null);
    const [editVal, setEditVal] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])("");
    // Knowledge file upload / paste states
    const [dragging, setDragging] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])(false);
    const [noteTitle, setNoteTitle] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])("");
    const [noteBody, setNoteBody] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])("");
    const [expandedFile, setExpandedFile] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])(null);
    const [expandedOutId, setExpandedOutId] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])(null);
    const [statusMsg, setStatusMsg] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])("");
    const fileInputRef = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useRef"])(null);
    const importInputRef = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useRef"])(null);
    const applySnap = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useCallback"])({
        "BrainModal.useCallback[applySnap]": (b)=>{
            if (!b || typeof b !== "object") return;
            if (Array.isArray(b.memories)) setMemories(b.memories);
            if (Array.isArray(b.timeline)) {
                setTimeline([
                    ...b.timeline
                ].reverse());
            }
            if (Array.isArray(b.epochs)) setEpochs(b.epochs);
            if (Array.isArray(b.files)) setFiles(b.files);
            if (Array.isArray(b.outputs)) setOutputs(b.outputs);
        }
    }["BrainModal.useCallback[applySnap]"], []);
    const refreshBrain = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useCallback"])({
        "BrainModal.useCallback[refreshBrain]": async ()=>{
            setLoading(true);
            try {
                const r = await fetch("/api/hud/brain");
                if (r.ok) {
                    const d = await r.json();
                    applySnap(d.brain);
                }
            } catch  {}
            setLoading(false);
        }
    }["BrainModal.useCallback[refreshBrain]"], [
        applySnap
    ]);
    (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useEffect"])({
        "BrainModal.useEffect": ()=>{
            if (brainModalOpen) {
                fireLocalTrace([
                    "memory",
                    "editor"
                ]);
                refreshBrain();
            }
        }
    }["BrainModal.useEffect"], [
        brainModalOpen,
        fireLocalTrace,
        refreshBrain
    ]);
    (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useEffect"])({
        "BrainModal.useEffect": ()=>{
            if (!brainModalOpen) return;
            const t = setTimeout({
                "BrainModal.useEffect.t": async ()=>{
                    if (!query.trim() && !channelFilter) {
                        refreshBrain();
                        return;
                    }
                    try {
                        const r = await fetch("/api/hud/action", {
                            method: "POST",
                            headers: {
                                "Content-Type": "application/json"
                            },
                            body: JSON.stringify({
                                action: "brain_search",
                                query,
                                channel: channelFilter
                            })
                        });
                        if (r.ok) {
                            const d = await r.json();
                            if (Array.isArray(d.memories)) setMemories(d.memories);
                            if (Array.isArray(d.timeline)) setTimeline(d.timeline);
                            if (Array.isArray(d.files)) setFiles(d.files);
                            if (Array.isArray(d.outputs)) setOutputs(d.outputs);
                        }
                    } catch  {}
                }
            }["BrainModal.useEffect.t"], 180);
            return ({
                "BrainModal.useEffect": ()=>clearTimeout(t)
            })["BrainModal.useEffect"];
        }
    }["BrainModal.useEffect"], [
        query,
        channelFilter,
        brainModalOpen,
        refreshBrain
    ]);
    if (!brainModalOpen) return null;
    const postBrain = async (payload)=>{
        const r = await fetch("/api/hud/action", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(payload)
        });
        const d = await r.json();
        if (d.brain) applySnap(d.brain);
        return d;
    };
    const onAddMemory = async (e)=>{
        e.preventDefault();
        if (!newKey.trim() || !newVal.trim()) return;
        await postBrain({
            action: "brain_save_memory",
            category: newCat,
            key: newKey.trim(),
            value: newVal.trim()
        });
        setNewKey("");
        setNewVal("");
        setStatusMsg("Saved memory ✓");
        setTimeout(()=>setStatusMsg(""), 2000);
    };
    const onSaveEdit = async (m)=>{
        if (!editVal.trim()) return;
        await postBrain({
            action: "brain_save_memory",
            category: m.category,
            key: m.key,
            value: editVal.trim()
        });
        setEditId(null);
    };
    const onForget = async (m)=>{
        await postBrain({
            action: "brain_forget_memory",
            category: m.category,
            key: m.key
        });
    };
    const uploadBrowserFiles = async (fileList)=>{
        if (!fileList || fileList.length === 0) return;
        for (const f of Array.from(fileList)){
            const dataUrl = await new Promise((resolve)=>{
                const reader = new FileReader();
                reader.onload = ()=>resolve(String(reader.result || ""));
                reader.readAsDataURL(f);
            });
            await postBrain({
                action: "brain_upload_file",
                filename: f.name,
                content: dataUrl,
                is_base64: true
            });
        }
        setStatusMsg("Indexed knowledge file(s) into Brain ✓");
        setTimeout(()=>setStatusMsg(""), 2400);
    };
    const onSaveNote = async (e)=>{
        e.preventDefault();
        if (!noteBody.trim()) return;
        const fname = (noteTitle.trim() || "brain_note") + (noteTitle.includes(".") ? "" : ".md");
        await postBrain({
            action: "brain_upload_file",
            filename: fname,
            content: noteBody,
            is_base64: false
        });
        setNoteTitle("");
        setNoteBody("");
        setStatusMsg("Added note to Brain ✓");
        setTimeout(()=>setStatusMsg(""), 2000);
    };
    const onViewFile = async (f)=>{
        if (expandedFile?.id === f.id) {
            setExpandedFile(null);
            return;
        }
        const d = await postBrain({
            action: "brain_read_file",
            file_id: f.id
        });
        if (d.file) setExpandedFile(d.file);
    };
    const onExportJson = ()=>{
        window.open("/api/hud/brain/export", "_blank", "noopener,noreferrer");
    };
    const onImportJson = async (fileList)=>{
        if (!fileList || fileList.length === 0) return;
        try {
            const raw = await fileList[0].text();
            const parsed = JSON.parse(raw);
            await postBrain({
                action: "brain_import_json",
                payload: parsed
            });
            setStatusMsg("Imported Brain backup ✓");
            setTimeout(()=>setStatusMsg(""), 2500);
        } catch  {
            setStatusMsg("Invalid JSON export file.");
        }
    };
    const downloadOutputMd = (o)=>{
        const blob = new Blob([
            `# ${o.title}\n\n${o.content}`
        ], {
            type: "text/markdown;charset=utf-8"
        });
        const url = URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = `${o.title.toLowerCase().replace(/[^a-z0-9]+/g, "_") || "output"}.md`;
        a.click();
        URL.revokeObjectURL(url);
    };
    const inputStyle = {
        background: theme.inputBg,
        color: "#f0ede8",
        border: `1px solid ${theme.primaryBorder}`,
        borderRadius: 8,
        padding: "8px 10px",
        fontSize: 12,
        outline: "none",
        fontFamily: "var(--font-mono)"
    };
    const pillBtn = (active = false, accent = PRIMARY)=>({
            display: "inline-flex",
            alignItems: "center",
            gap: 6,
            fontFamily: "var(--font-mono)",
            fontSize: 10,
            letterSpacing: "0.14em",
            textTransform: "uppercase",
            padding: "6px 12px",
            borderRadius: 999,
            border: `1px solid ${active ? accent : "rgba(240,237,232,0.18)"}`,
            background: active ? `${accent}24` : "rgba(255,255,255,0.03)",
            color: active ? accent : "rgba(240,237,232,0.78)",
            cursor: "pointer"
        });
    return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
        role: "dialog",
        "aria-modal": "true",
        "aria-label": "JARVIS Brain and Forever Timeline",
        onClick: ()=>setBrainModalOpen(false),
        style: {
            position: "fixed",
            inset: 0,
            zIndex: 86,
            background: "rgba(2, 6, 14, 0.78)",
            backdropFilter: "blur(13px)",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            padding: 14
        },
        children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
            onClick: (e)=>e.stopPropagation(),
            style: {
                width: "min(880px, 96vw)",
                height: "min(86vh, 760px)",
                background: theme.panelBg,
                border: `1px solid ${PRIMARY}55`,
                borderRadius: 22,
                padding: "20px 22px 16px",
                boxShadow: `0 0 64px ${PRIMARY}26, 0 24px 68px rgba(0,0,0,0.88)`,
                display: "flex",
                flexDirection: "column",
                gap: 13
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
                                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$brain$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__Brain$3e$__["Brain"], {
                                    size: 18,
                                    style: {
                                        color: PRIMARY
                                    }
                                }, void 0, false, {
                                    fileName: "[project]/components/BrainModal.tsx",
                                    lineNumber: 370,
                                    columnNumber: 13
                                }, this),
                                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("span", {
                                    style: {
                                        fontFamily: "var(--font-mono)",
                                        fontSize: 11.5,
                                        letterSpacing: "0.22em",
                                        color: PRIMARY,
                                        fontWeight: 600
                                    },
                                    children: [
                                        assistantName.toUpperCase(),
                                        " · THE BRAIN & FOREVER TIMELINE"
                                    ]
                                }, void 0, true, {
                                    fileName: "[project]/components/BrainModal.tsx",
                                    lineNumber: 371,
                                    columnNumber: 13
                                }, this),
                                statusMsg && /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("span", {
                                    style: {
                                        fontSize: 11,
                                        color: GREEN,
                                        fontFamily: "var(--font-mono)"
                                    },
                                    children: statusMsg
                                }, void 0, false, {
                                    fileName: "[project]/components/BrainModal.tsx",
                                    lineNumber: 383,
                                    columnNumber: 15
                                }, this)
                            ]
                        }, void 0, true, {
                            fileName: "[project]/components/BrainModal.tsx",
                            lineNumber: 369,
                            columnNumber: 11
                        }, this),
                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                            style: {
                                display: "flex",
                                alignItems: "center",
                                gap: 7
                            },
                            children: [
                                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("button", {
                                    type: "button",
                                    onClick: onExportJson,
                                    style: pillBtn(),
                                    children: [
                                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$download$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__Download$3e$__["Download"], {
                                            size: 11
                                        }, void 0, false, {
                                            fileName: "[project]/components/BrainModal.tsx",
                                            lineNumber: 397,
                                            columnNumber: 15
                                        }, this),
                                        " EXPORT JSON"
                                    ]
                                }, void 0, true, {
                                    fileName: "[project]/components/BrainModal.tsx",
                                    lineNumber: 396,
                                    columnNumber: 13
                                }, this),
                                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("button", {
                                    type: "button",
                                    onClick: ()=>importInputRef.current?.click(),
                                    style: pillBtn(),
                                    children: [
                                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$upload$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__Upload$3e$__["Upload"], {
                                            size: 11
                                        }, void 0, false, {
                                            fileName: "[project]/components/BrainModal.tsx",
                                            lineNumber: 404,
                                            columnNumber: 15
                                        }, this),
                                        " IMPORT JSON"
                                    ]
                                }, void 0, true, {
                                    fileName: "[project]/components/BrainModal.tsx",
                                    lineNumber: 399,
                                    columnNumber: 13
                                }, this),
                                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("input", {
                                    ref: importInputRef,
                                    type: "file",
                                    accept: ".json,application/json",
                                    style: {
                                        display: "none"
                                    },
                                    onChange: (e)=>onImportJson(e.target.files)
                                }, void 0, false, {
                                    fileName: "[project]/components/BrainModal.tsx",
                                    lineNumber: 406,
                                    columnNumber: 13
                                }, this),
                                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("button", {
                                    type: "button",
                                    onClick: ()=>setBrainModalOpen(false),
                                    "aria-label": "Close Brain drawer",
                                    style: {
                                        background: "none",
                                        border: "none",
                                        color: "rgba(255,255,255,0.55)",
                                        cursor: "pointer",
                                        marginLeft: 4
                                    },
                                    children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$x$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__X$3e$__["X"], {
                                        size: 19
                                    }, void 0, false, {
                                        fileName: "[project]/components/BrainModal.tsx",
                                        lineNumber: 425,
                                        columnNumber: 15
                                    }, this)
                                }, void 0, false, {
                                    fileName: "[project]/components/BrainModal.tsx",
                                    lineNumber: 413,
                                    columnNumber: 13
                                }, this)
                            ]
                        }, void 0, true, {
                            fileName: "[project]/components/BrainModal.tsx",
                            lineNumber: 395,
                            columnNumber: 11
                        }, this)
                    ]
                }, void 0, true, {
                    fileName: "[project]/components/BrainModal.tsx",
                    lineNumber: 360,
                    columnNumber: 9
                }, this),
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
                                gap: 6,
                                flexWrap: "wrap"
                            },
                            children: [
                                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("button", {
                                    type: "button",
                                    onClick: ()=>setTab("memories"),
                                    style: pillBtn(tab === "memories"),
                                    children: [
                                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$sparkles$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__Sparkles$3e$__["Sparkles"], {
                                            size: 11
                                        }, void 0, false, {
                                            fileName: "[project]/components/BrainModal.tsx",
                                            lineNumber: 446,
                                            columnNumber: 15
                                        }, this),
                                        " MEMORIES (",
                                        memories.length,
                                        ")"
                                    ]
                                }, void 0, true, {
                                    fileName: "[project]/components/BrainModal.tsx",
                                    lineNumber: 441,
                                    columnNumber: 13
                                }, this),
                                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("button", {
                                    type: "button",
                                    onClick: ()=>setTab("timeline"),
                                    style: pillBtn(tab === "timeline"),
                                    children: [
                                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$clock$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__Clock$3e$__["Clock"], {
                                            size: 11
                                        }, void 0, false, {
                                            fileName: "[project]/components/BrainModal.tsx",
                                            lineNumber: 453,
                                            columnNumber: 15
                                        }, this),
                                        " TIMELINE (",
                                        timeline.length,
                                        ")"
                                    ]
                                }, void 0, true, {
                                    fileName: "[project]/components/BrainModal.tsx",
                                    lineNumber: 448,
                                    columnNumber: 13
                                }, this),
                                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("button", {
                                    type: "button",
                                    onClick: ()=>setTab("files"),
                                    style: pillBtn(tab === "files"),
                                    children: [
                                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$file$2d$text$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__FileText$3e$__["FileText"], {
                                            size: 11
                                        }, void 0, false, {
                                            fileName: "[project]/components/BrainModal.tsx",
                                            lineNumber: 460,
                                            columnNumber: 15
                                        }, this),
                                        " KNOWLEDGE FILES (",
                                        files.length,
                                        ")"
                                    ]
                                }, void 0, true, {
                                    fileName: "[project]/components/BrainModal.tsx",
                                    lineNumber: 455,
                                    columnNumber: 13
                                }, this),
                                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("button", {
                                    type: "button",
                                    onClick: ()=>setTab("outputs"),
                                    style: pillBtn(tab === "outputs"),
                                    children: [
                                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$pin$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__Pin$3e$__["Pin"], {
                                            size: 11
                                        }, void 0, false, {
                                            fileName: "[project]/components/BrainModal.tsx",
                                            lineNumber: 467,
                                            columnNumber: 15
                                        }, this),
                                        " OUTPUTS (",
                                        outputs.length,
                                        ")"
                                    ]
                                }, void 0, true, {
                                    fileName: "[project]/components/BrainModal.tsx",
                                    lineNumber: 462,
                                    columnNumber: 13
                                }, this)
                            ]
                        }, void 0, true, {
                            fileName: "[project]/components/BrainModal.tsx",
                            lineNumber: 440,
                            columnNumber: 11
                        }, this),
                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                            style: {
                                display: "flex",
                                alignItems: "center",
                                gap: 7,
                                background: theme.inputBg,
                                border: `1px solid ${theme.primaryBorder}`,
                                borderRadius: 999,
                                padding: "5px 12px",
                                minWidth: 230,
                                flex: "0 1 280px"
                            },
                            children: [
                                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$search$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__Search$3e$__["Search"], {
                                    size: 13,
                                    style: {
                                        color: PRIMARY
                                    }
                                }, void 0, false, {
                                    fileName: "[project]/components/BrainModal.tsx",
                                    lineNumber: 484,
                                    columnNumber: 13
                                }, this),
                                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("input", {
                                    type: "text",
                                    value: query,
                                    onChange: (e)=>setQuery(e.target.value),
                                    placeholder: "Search Brain & Timeline...",
                                    style: {
                                        background: "transparent",
                                        border: "none",
                                        color: "#f0ede8",
                                        fontSize: 12,
                                        outline: "none",
                                        width: "100%"
                                    }
                                }, void 0, false, {
                                    fileName: "[project]/components/BrainModal.tsx",
                                    lineNumber: 485,
                                    columnNumber: 13
                                }, this)
                            ]
                        }, void 0, true, {
                            fileName: "[project]/components/BrainModal.tsx",
                            lineNumber: 471,
                            columnNumber: 11
                        }, this)
                    ]
                }, void 0, true, {
                    fileName: "[project]/components/BrainModal.tsx",
                    lineNumber: 431,
                    columnNumber: 9
                }, this),
                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                    style: {
                        flex: 1,
                        overflowY: "auto",
                        display: "flex",
                        flexDirection: "column",
                        gap: 10,
                        paddingRight: 4
                    },
                    children: [
                        loading && /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                            style: {
                                fontSize: 12,
                                color: "rgba(240,237,232,0.5)"
                            },
                            children: "Syncing Brain..."
                        }, void 0, false, {
                            fileName: "[project]/components/BrainModal.tsx",
                            lineNumber: 514,
                            columnNumber: 13
                        }, this),
                        tab === "memories" && /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["Fragment"], {
                            children: [
                                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("form", {
                                    onSubmit: onAddMemory,
                                    style: {
                                        display: "grid",
                                        gridTemplateColumns: "130px 150px 1fr auto",
                                        gap: 7,
                                        alignItems: "center"
                                    },
                                    children: [
                                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("select", {
                                            value: newCat,
                                            onChange: (e)=>setNewCat(e.target.value),
                                            style: inputStyle,
                                            children: CATEGORIES.map((c)=>/*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("option", {
                                                    value: c,
                                                    children: c
                                                }, c, false, {
                                                    fileName: "[project]/components/BrainModal.tsx",
                                                    lineNumber: 537,
                                                    columnNumber: 21
                                                }, this))
                                        }, void 0, false, {
                                            fileName: "[project]/components/BrainModal.tsx",
                                            lineNumber: 531,
                                            columnNumber: 17
                                        }, this),
                                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("input", {
                                            type: "text",
                                            value: newKey,
                                            onChange: (e)=>setNewKey(e.target.value),
                                            placeholder: "Key (e.g. role, coffee)",
                                            style: inputStyle
                                        }, void 0, false, {
                                            fileName: "[project]/components/BrainModal.tsx",
                                            lineNumber: 542,
                                            columnNumber: 17
                                        }, this),
                                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("input", {
                                            type: "text",
                                            value: newVal,
                                            onChange: (e)=>setNewVal(e.target.value),
                                            placeholder: "What should JARVIS remember?",
                                            style: inputStyle
                                        }, void 0, false, {
                                            fileName: "[project]/components/BrainModal.tsx",
                                            lineNumber: 549,
                                            columnNumber: 17
                                        }, this),
                                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("button", {
                                            type: "submit",
                                            style: pillBtn(true),
                                            children: [
                                                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$plus$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__Plus$3e$__["Plus"], {
                                                    size: 12
                                                }, void 0, false, {
                                                    fileName: "[project]/components/BrainModal.tsx",
                                                    lineNumber: 557,
                                                    columnNumber: 19
                                                }, this),
                                                " SAVE"
                                            ]
                                        }, void 0, true, {
                                            fileName: "[project]/components/BrainModal.tsx",
                                            lineNumber: 556,
                                            columnNumber: 17
                                        }, this)
                                    ]
                                }, void 0, true, {
                                    fileName: "[project]/components/BrainModal.tsx",
                                    lineNumber: 522,
                                    columnNumber: 15
                                }, this),
                                memories.length > 0 && /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                    style: {
                                        display: "flex",
                                        justifyContent: "flex-end"
                                    },
                                    children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("button", {
                                        type: "button",
                                        onClick: ()=>postBrain({
                                                action: "brain_clear_memories"
                                            }),
                                        style: pillBtn(false, RED),
                                        children: [
                                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$trash$2d$2$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__Trash2$3e$__["Trash2"], {
                                                size: 11
                                            }, void 0, false, {
                                                fileName: "[project]/components/BrainModal.tsx",
                                                lineNumber: 568,
                                                columnNumber: 21
                                            }, this),
                                            " FORGET ALL MEMORIES"
                                        ]
                                    }, void 0, true, {
                                        fileName: "[project]/components/BrainModal.tsx",
                                        lineNumber: 563,
                                        columnNumber: 19
                                    }, this)
                                }, void 0, false, {
                                    fileName: "[project]/components/BrainModal.tsx",
                                    lineNumber: 562,
                                    columnNumber: 17
                                }, this),
                                memories.length === 0 ? /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                    style: {
                                        padding: 28,
                                        textAlign: "center",
                                        color: "rgba(240,237,232,0.5)",
                                        fontSize: 12.5
                                    },
                                    children: [
                                        "No personal memories stored yet. Talk naturally with ",
                                        assistantName,
                                        " or add facts above — you can edit or forget anything in one click."
                                    ]
                                }, void 0, true, {
                                    fileName: "[project]/components/BrainModal.tsx",
                                    lineNumber: 574,
                                    columnNumber: 17
                                }, this) : memories.map((m)=>{
                                    const idKey = `${m.category}/${m.key}`;
                                    const isEditing = editId === idKey;
                                    return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                        style: {
                                            borderRadius: 12,
                                            padding: "11px 14px",
                                            background: "rgba(255,255,255,0.03)",
                                            border: `1px solid ${PRIMARY}26`,
                                            display: "flex",
                                            alignItems: "center",
                                            justifyContent: "space-between",
                                            gap: 10
                                        },
                                        children: [
                                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                                style: {
                                                    flex: 1
                                                },
                                                children: [
                                                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                                        style: {
                                                            display: "flex",
                                                            alignItems: "center",
                                                            gap: 8,
                                                            marginBottom: 4
                                                        },
                                                        children: [
                                                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("span", {
                                                                style: {
                                                                    fontFamily: "var(--font-mono)",
                                                                    fontSize: 9.5,
                                                                    padding: "2px 7px",
                                                                    borderRadius: 999,
                                                                    background: `${SECONDARY}22`,
                                                                    color: SECONDARY,
                                                                    textTransform: "uppercase"
                                                                },
                                                                children: m.category
                                                            }, void 0, false, {
                                                                fileName: "[project]/components/BrainModal.tsx",
                                                                lineNumber: 612,
                                                                columnNumber: 27
                                                            }, this),
                                                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("span", {
                                                                style: {
                                                                    fontFamily: "var(--font-mono)",
                                                                    fontSize: 11,
                                                                    color: PRIMARY,
                                                                    fontWeight: 600
                                                                },
                                                                children: m.key.replace(/_/g, " ")
                                                            }, void 0, false, {
                                                                fileName: "[project]/components/BrainModal.tsx",
                                                                lineNumber: 625,
                                                                columnNumber: 27
                                                            }, this),
                                                            m.updated && /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("span", {
                                                                style: {
                                                                    fontSize: 10,
                                                                    color: "rgba(240,237,232,0.42)"
                                                                },
                                                                children: m.updated
                                                            }, void 0, false, {
                                                                fileName: "[project]/components/BrainModal.tsx",
                                                                lineNumber: 636,
                                                                columnNumber: 29
                                                            }, this)
                                                        ]
                                                    }, void 0, true, {
                                                        fileName: "[project]/components/BrainModal.tsx",
                                                        lineNumber: 604,
                                                        columnNumber: 25
                                                    }, this),
                                                    isEditing ? /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                                        style: {
                                                            display: "flex",
                                                            gap: 6
                                                        },
                                                        children: [
                                                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("input", {
                                                                type: "text",
                                                                value: editVal,
                                                                onChange: (e)=>setEditVal(e.target.value),
                                                                style: {
                                                                    ...inputStyle,
                                                                    flex: 1
                                                                }
                                                            }, void 0, false, {
                                                                fileName: "[project]/components/BrainModal.tsx",
                                                                lineNumber: 649,
                                                                columnNumber: 29
                                                            }, this),
                                                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("button", {
                                                                type: "button",
                                                                onClick: ()=>onSaveEdit(m),
                                                                style: pillBtn(true, GREEN),
                                                                children: "SAVE"
                                                            }, void 0, false, {
                                                                fileName: "[project]/components/BrainModal.tsx",
                                                                lineNumber: 655,
                                                                columnNumber: 29
                                                            }, this),
                                                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("button", {
                                                                type: "button",
                                                                onClick: ()=>setEditId(null),
                                                                style: pillBtn(),
                                                                children: "CANCEL"
                                                            }, void 0, false, {
                                                                fileName: "[project]/components/BrainModal.tsx",
                                                                lineNumber: 662,
                                                                columnNumber: 29
                                                            }, this)
                                                        ]
                                                    }, void 0, true, {
                                                        fileName: "[project]/components/BrainModal.tsx",
                                                        lineNumber: 648,
                                                        columnNumber: 27
                                                    }, this) : /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                                        style: {
                                                            fontSize: 12.5,
                                                            color: "rgba(240,237,232,0.88)",
                                                            lineHeight: 1.45
                                                        },
                                                        children: m.value
                                                    }, void 0, false, {
                                                        fileName: "[project]/components/BrainModal.tsx",
                                                        lineNumber: 671,
                                                        columnNumber: 27
                                                    }, this)
                                                ]
                                            }, void 0, true, {
                                                fileName: "[project]/components/BrainModal.tsx",
                                                lineNumber: 603,
                                                columnNumber: 23
                                            }, this),
                                            !isEditing && /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                                style: {
                                                    display: "flex",
                                                    gap: 6
                                                },
                                                children: [
                                                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("button", {
                                                        type: "button",
                                                        onClick: ()=>{
                                                            setEditId(idKey);
                                                            setEditVal(m.value);
                                                        },
                                                        style: pillBtn(),
                                                        title: "Correct memory",
                                                        children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$pen$2d$line$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__Edit3$3e$__["Edit3"], {
                                                            size: 11
                                                        }, void 0, false, {
                                                            fileName: "[project]/components/BrainModal.tsx",
                                                            lineNumber: 694,
                                                            columnNumber: 29
                                                        }, this)
                                                    }, void 0, false, {
                                                        fileName: "[project]/components/BrainModal.tsx",
                                                        lineNumber: 685,
                                                        columnNumber: 27
                                                    }, this),
                                                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("button", {
                                                        type: "button",
                                                        onClick: ()=>onForget(m),
                                                        style: {
                                                            ...pillBtn(),
                                                            borderColor: `${RED}55`,
                                                            color: RED
                                                        },
                                                        title: "Forget this memory",
                                                        children: [
                                                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$trash$2d$2$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__Trash2$3e$__["Trash2"], {
                                                                size: 11
                                                            }, void 0, false, {
                                                                fileName: "[project]/components/BrainModal.tsx",
                                                                lineNumber: 702,
                                                                columnNumber: 29
                                                            }, this),
                                                            " FORGET"
                                                        ]
                                                    }, void 0, true, {
                                                        fileName: "[project]/components/BrainModal.tsx",
                                                        lineNumber: 696,
                                                        columnNumber: 27
                                                    }, this)
                                                ]
                                            }, void 0, true, {
                                                fileName: "[project]/components/BrainModal.tsx",
                                                lineNumber: 684,
                                                columnNumber: 25
                                            }, this)
                                        ]
                                    }, idKey, true, {
                                        fileName: "[project]/components/BrainModal.tsx",
                                        lineNumber: 590,
                                        columnNumber: 21
                                    }, this);
                                })
                            ]
                        }, void 0, true, {
                            fileName: "[project]/components/BrainModal.tsx",
                            lineNumber: 521,
                            columnNumber: 13
                        }, this),
                        tab === "timeline" && /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["Fragment"], {
                            children: [
                                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                    style: {
                                        display: "flex",
                                        justifyContent: "space-between",
                                        alignItems: "center",
                                        gap: 8,
                                        flexWrap: "wrap"
                                    },
                                    children: [
                                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                            style: {
                                                display: "flex",
                                                gap: 6,
                                                flexWrap: "wrap"
                                            },
                                            children: [
                                                [
                                                    "",
                                                    "ALL CHANNELS"
                                                ],
                                                [
                                                    "voice",
                                                    "🎙 VOICE"
                                                ],
                                                [
                                                    "text",
                                                    "⌨ TEXT"
                                                ],
                                                [
                                                    "telegram",
                                                    "✈ TELEGRAM"
                                                ]
                                            ].map(([val, lbl])=>/*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("button", {
                                                    type: "button",
                                                    onClick: ()=>setChannelFilter(val),
                                                    style: pillBtn(channelFilter === val),
                                                    children: lbl
                                                }, val, false, {
                                                    fileName: "[project]/components/BrainModal.tsx",
                                                    lineNumber: 732,
                                                    columnNumber: 21
                                                }, this))
                                        }, void 0, false, {
                                            fileName: "[project]/components/BrainModal.tsx",
                                            lineNumber: 725,
                                            columnNumber: 17
                                        }, this),
                                        timeline.length > 0 && /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("button", {
                                            type: "button",
                                            onClick: ()=>postBrain({
                                                    action: "brain_clear_timeline"
                                                }),
                                            style: {
                                                ...pillBtn(),
                                                borderColor: `${RED}55`,
                                                color: RED
                                            },
                                            children: [
                                                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$trash$2d$2$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__Trash2$3e$__["Trash2"], {
                                                    size: 11
                                                }, void 0, false, {
                                                    fileName: "[project]/components/BrainModal.tsx",
                                                    lineNumber: 749,
                                                    columnNumber: 21
                                                }, this),
                                                " CLEAR TIMELINE"
                                            ]
                                        }, void 0, true, {
                                            fileName: "[project]/components/BrainModal.tsx",
                                            lineNumber: 744,
                                            columnNumber: 19
                                        }, this)
                                    ]
                                }, void 0, true, {
                                    fileName: "[project]/components/BrainModal.tsx",
                                    lineNumber: 716,
                                    columnNumber: 15
                                }, this),
                                epochs.length > 0 && /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                    style: {
                                        borderRadius: 12,
                                        padding: "10px 13px",
                                        background: `${SECONDARY}12`,
                                        border: `1px solid ${SECONDARY}44`,
                                        fontSize: 11.5,
                                        color: "rgba(240,237,232,0.82)"
                                    },
                                    children: [
                                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                            style: {
                                                fontFamily: "var(--font-mono)",
                                                fontSize: 9.5,
                                                letterSpacing: "0.14em",
                                                color: SECONDARY,
                                                marginBottom: 4
                                            },
                                            children: [
                                                "COMPRESSED EPOCH DIGESTS (",
                                                epochs.length,
                                                ")"
                                            ]
                                        }, void 0, true, {
                                            fileName: "[project]/components/BrainModal.tsx",
                                            lineNumber: 765,
                                            columnNumber: 19
                                        }, this),
                                        epochs.slice(0, 3).map((ep)=>/*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                                style: {
                                                    marginBottom: 3
                                                },
                                                children: [
                                                    "• ",
                                                    ep.summary
                                                ]
                                            }, ep.id, true, {
                                                fileName: "[project]/components/BrainModal.tsx",
                                                lineNumber: 777,
                                                columnNumber: 21
                                            }, this))
                                    ]
                                }, void 0, true, {
                                    fileName: "[project]/components/BrainModal.tsx",
                                    lineNumber: 755,
                                    columnNumber: 17
                                }, this),
                                timeline.length === 0 ? /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                    style: {
                                        padding: 28,
                                        textAlign: "center",
                                        color: "rgba(240,237,232,0.5)",
                                        fontSize: 12.5
                                    },
                                    children: "Your Forever Timeline is empty. Spoken, typed, and Telegram exchanges roll on continuously here across restarts."
                                }, void 0, false, {
                                    fileName: "[project]/components/BrainModal.tsx",
                                    lineNumber: 785,
                                    columnNumber: 17
                                }, this) : timeline.map((t)=>/*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                        style: {
                                            borderRadius: 12,
                                            padding: "10px 13px",
                                            background: t.role === "user" ? "rgba(255,255,255,0.04)" : `${PRIMARY}0d`,
                                            border: `1px solid ${t.role === "user" ? "rgba(255,255,255,0.1)" : `${PRIMARY}33`}`,
                                            display: "flex",
                                            justifyContent: "space-between",
                                            gap: 10
                                        },
                                        children: [
                                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                                style: {
                                                    flex: 1
                                                },
                                                children: [
                                                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                                        style: {
                                                            display: "flex",
                                                            alignItems: "center",
                                                            gap: 8,
                                                            fontSize: 10.5,
                                                            fontFamily: "var(--font-mono)",
                                                            color: t.role === "user" ? SECONDARY : PRIMARY,
                                                            marginBottom: 3
                                                        },
                                                        children: [
                                                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("span", {
                                                                children: t.speaker || t.role.toUpperCase()
                                                            }, void 0, false, {
                                                                fileName: "[project]/components/BrainModal.tsx",
                                                                lineNumber: 829,
                                                                columnNumber: 25
                                                            }, this),
                                                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("span", {
                                                                style: {
                                                                    padding: "1px 6px",
                                                                    borderRadius: 999,
                                                                    background: "rgba(255,255,255,0.07)",
                                                                    color: "rgba(240,237,232,0.65)",
                                                                    fontSize: 9
                                                                },
                                                                children: t.channel.toUpperCase()
                                                            }, void 0, false, {
                                                                fileName: "[project]/components/BrainModal.tsx",
                                                                lineNumber: 830,
                                                                columnNumber: 25
                                                            }, this),
                                                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("span", {
                                                                style: {
                                                                    color: "rgba(240,237,232,0.4)"
                                                                },
                                                                children: t.created_at
                                                            }, void 0, false, {
                                                                fileName: "[project]/components/BrainModal.tsx",
                                                                lineNumber: 841,
                                                                columnNumber: 25
                                                            }, this)
                                                        ]
                                                    }, void 0, true, {
                                                        fileName: "[project]/components/BrainModal.tsx",
                                                        lineNumber: 818,
                                                        columnNumber: 23
                                                    }, this),
                                                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                                        style: {
                                                            fontSize: 12.5,
                                                            color: "rgba(240,237,232,0.88)",
                                                            lineHeight: 1.48,
                                                            whiteSpace: "pre-wrap"
                                                        },
                                                        children: t.content
                                                    }, void 0, false, {
                                                        fileName: "[project]/components/BrainModal.tsx",
                                                        lineNumber: 845,
                                                        columnNumber: 23
                                                    }, this)
                                                ]
                                            }, void 0, true, {
                                                fileName: "[project]/components/BrainModal.tsx",
                                                lineNumber: 817,
                                                columnNumber: 21
                                            }, this),
                                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("button", {
                                                type: "button",
                                                onClick: ()=>postBrain({
                                                        action: "brain_delete_turn",
                                                        id: t.id
                                                    }),
                                                style: {
                                                    background: "none",
                                                    border: "none",
                                                    color: "rgba(255,91,121,0.7)",
                                                    cursor: "pointer",
                                                    alignSelf: "flex-start"
                                                },
                                                title: "Delete turn",
                                                children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$trash$2d$2$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__Trash2$3e$__["Trash2"], {
                                                    size: 13
                                                }, void 0, false, {
                                                    fileName: "[project]/components/BrainModal.tsx",
                                                    lineNumber: 871,
                                                    columnNumber: 23
                                                }, this)
                                            }, void 0, false, {
                                                fileName: "[project]/components/BrainModal.tsx",
                                                lineNumber: 857,
                                                columnNumber: 21
                                            }, this)
                                        ]
                                    }, t.id, true, {
                                        fileName: "[project]/components/BrainModal.tsx",
                                        lineNumber: 798,
                                        columnNumber: 19
                                    }, this))
                            ]
                        }, void 0, true, {
                            fileName: "[project]/components/BrainModal.tsx",
                            lineNumber: 715,
                            columnNumber: 13
                        }, this),
                        tab === "files" && /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["Fragment"], {
                            children: [
                                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                    onDragOver: (e)=>{
                                        e.preventDefault();
                                        setDragging(true);
                                    },
                                    onDragLeave: ()=>setDragging(false),
                                    onDrop: (e)=>{
                                        e.preventDefault();
                                        setDragging(false);
                                        uploadBrowserFiles(e.dataTransfer.files);
                                    },
                                    onClick: ()=>fileInputRef.current?.click(),
                                    style: {
                                        borderRadius: 14,
                                        padding: "18px 16px",
                                        border: `1.5px dashed ${dragging ? PRIMARY : "rgba(240,237,232,0.25)"}`,
                                        background: dragging ? `${PRIMARY}16` : "rgba(255,255,255,0.02)",
                                        textAlign: "center",
                                        cursor: "pointer"
                                    },
                                    children: [
                                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$upload$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__Upload$3e$__["Upload"], {
                                            size: 18,
                                            style: {
                                                color: PRIMARY,
                                                margin: "0 auto 6px"
                                            }
                                        }, void 0, false, {
                                            fileName: "[project]/components/BrainModal.tsx",
                                            lineNumber: 907,
                                            columnNumber: 17
                                        }, this),
                                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                            style: {
                                                fontSize: 12.5,
                                                color: "#f0ede8"
                                            },
                                            children: "Drop reference files here or click to upload (`.md`, `.txt`, `.pdf`, `.csv`, `.json`, `.py`)"
                                        }, void 0, false, {
                                            fileName: "[project]/components/BrainModal.tsx",
                                            lineNumber: 911,
                                            columnNumber: 17
                                        }, this),
                                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                            style: {
                                                fontSize: 11,
                                                color: "rgba(240,237,232,0.52)",
                                                marginTop: 2
                                            },
                                            children: "Automatically chunked & indexed for instant voice & text recall"
                                        }, void 0, false, {
                                            fileName: "[project]/components/BrainModal.tsx",
                                            lineNumber: 915,
                                            columnNumber: 17
                                        }, this),
                                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("input", {
                                            ref: fileInputRef,
                                            type: "file",
                                            multiple: true,
                                            style: {
                                                display: "none"
                                            },
                                            onChange: (e)=>uploadBrowserFiles(e.target.files)
                                        }, void 0, false, {
                                            fileName: "[project]/components/BrainModal.tsx",
                                            lineNumber: 924,
                                            columnNumber: 17
                                        }, this)
                                    ]
                                }, void 0, true, {
                                    fileName: "[project]/components/BrainModal.tsx",
                                    lineNumber: 882,
                                    columnNumber: 15
                                }, this),
                                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("form", {
                                    onSubmit: onSaveNote,
                                    style: {
                                        display: "grid",
                                        gridTemplateColumns: "180px 1fr auto",
                                        gap: 7
                                    },
                                    children: [
                                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("input", {
                                            type: "text",
                                            value: noteTitle,
                                            onChange: (e)=>setNoteTitle(e.target.value),
                                            placeholder: "Note title (optional)",
                                            style: inputStyle
                                        }, void 0, false, {
                                            fileName: "[project]/components/BrainModal.tsx",
                                            lineNumber: 941,
                                            columnNumber: 17
                                        }, this),
                                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("input", {
                                            type: "text",
                                            value: noteBody,
                                            onChange: (e)=>setNoteBody(e.target.value),
                                            placeholder: "Or paste knowledge / SOP / reference text directly...",
                                            style: inputStyle
                                        }, void 0, false, {
                                            fileName: "[project]/components/BrainModal.tsx",
                                            lineNumber: 948,
                                            columnNumber: 17
                                        }, this),
                                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("button", {
                                            type: "submit",
                                            style: pillBtn(true),
                                            children: [
                                                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$plus$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__Plus$3e$__["Plus"], {
                                                    size: 12
                                                }, void 0, false, {
                                                    fileName: "[project]/components/BrainModal.tsx",
                                                    lineNumber: 956,
                                                    columnNumber: 19
                                                }, this),
                                                " ADD NOTE"
                                            ]
                                        }, void 0, true, {
                                            fileName: "[project]/components/BrainModal.tsx",
                                            lineNumber: 955,
                                            columnNumber: 17
                                        }, this)
                                    ]
                                }, void 0, true, {
                                    fileName: "[project]/components/BrainModal.tsx",
                                    lineNumber: 933,
                                    columnNumber: 15
                                }, this),
                                files.map((f)=>/*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                        style: {
                                            borderRadius: 12,
                                            padding: "11px 14px",
                                            background: "rgba(255,255,255,0.03)",
                                            border: `1px solid ${PRIMARY}26`,
                                            display: "flex",
                                            flexDirection: "column",
                                            gap: 6
                                        },
                                        children: [
                                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                                style: {
                                                    display: "flex",
                                                    justifyContent: "space-between",
                                                    alignItems: "center",
                                                    gap: 8
                                                },
                                                children: [
                                                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                                        children: [
                                                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("span", {
                                                                style: {
                                                                    fontFamily: "var(--font-mono)",
                                                                    fontSize: 11.5,
                                                                    color: PRIMARY,
                                                                    fontWeight: 600
                                                                },
                                                                children: f.filename
                                                            }, void 0, false, {
                                                                fileName: "[project]/components/BrainModal.tsx",
                                                                lineNumber: 982,
                                                                columnNumber: 23
                                                            }, this),
                                                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("span", {
                                                                style: {
                                                                    fontSize: 10.5,
                                                                    color: "rgba(240,237,232,0.48)",
                                                                    marginLeft: 10
                                                                },
                                                                children: [
                                                                    f.chunk_count,
                                                                    " chunk(s) ·",
                                                                    " ",
                                                                    Math.max(1, Math.round(f.size_bytes / 1024)),
                                                                    " KB ·",
                                                                    " ",
                                                                    f.created_at
                                                                ]
                                                            }, void 0, true, {
                                                                fileName: "[project]/components/BrainModal.tsx",
                                                                lineNumber: 992,
                                                                columnNumber: 23
                                                            }, this)
                                                        ]
                                                    }, void 0, true, {
                                                        fileName: "[project]/components/BrainModal.tsx",
                                                        lineNumber: 981,
                                                        columnNumber: 21
                                                    }, this),
                                                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                                        style: {
                                                            display: "flex",
                                                            gap: 6
                                                        },
                                                        children: [
                                                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("button", {
                                                                type: "button",
                                                                onClick: ()=>onViewFile(f),
                                                                style: pillBtn(expandedFile?.id === f.id),
                                                                children: expandedFile?.id === f.id ? "HIDE" : "READ"
                                                            }, void 0, false, {
                                                                fileName: "[project]/components/BrainModal.tsx",
                                                                lineNumber: 1006,
                                                                columnNumber: 23
                                                            }, this),
                                                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("button", {
                                                                type: "button",
                                                                onClick: ()=>postBrain({
                                                                        action: "brain_delete_file",
                                                                        file_id: f.id
                                                                    }),
                                                                style: {
                                                                    ...pillBtn(),
                                                                    borderColor: `${RED}55`,
                                                                    color: RED
                                                                },
                                                                children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$trash$2d$2$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__Trash2$3e$__["Trash2"], {
                                                                    size: 11
                                                                }, void 0, false, {
                                                                    fileName: "[project]/components/BrainModal.tsx",
                                                                    lineNumber: 1020,
                                                                    columnNumber: 25
                                                                }, this)
                                                            }, void 0, false, {
                                                                fileName: "[project]/components/BrainModal.tsx",
                                                                lineNumber: 1013,
                                                                columnNumber: 23
                                                            }, this)
                                                        ]
                                                    }, void 0, true, {
                                                        fileName: "[project]/components/BrainModal.tsx",
                                                        lineNumber: 1005,
                                                        columnNumber: 21
                                                    }, this)
                                                ]
                                            }, void 0, true, {
                                                fileName: "[project]/components/BrainModal.tsx",
                                                lineNumber: 973,
                                                columnNumber: 19
                                            }, this),
                                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                                style: {
                                                    fontSize: 11.5,
                                                    color: "rgba(240,237,232,0.7)",
                                                    whiteSpace: "pre-wrap"
                                                },
                                                children: expandedFile?.id === f.id ? expandedFile.full_text || f.preview : f.preview
                                            }, void 0, false, {
                                                fileName: "[project]/components/BrainModal.tsx",
                                                lineNumber: 1024,
                                                columnNumber: 19
                                            }, this)
                                        ]
                                    }, f.id, true, {
                                        fileName: "[project]/components/BrainModal.tsx",
                                        lineNumber: 961,
                                        columnNumber: 17
                                    }, this))
                            ]
                        }, void 0, true, {
                            fileName: "[project]/components/BrainModal.tsx",
                            lineNumber: 881,
                            columnNumber: 13
                        }, this),
                        tab === "outputs" && /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["Fragment"], {
                            children: outputs.length === 0 ? /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                style: {
                                    padding: 28,
                                    textAlign: "center",
                                    color: "rgba(240,237,232,0.5)",
                                    fontSize: 12.5
                                },
                                children: [
                                    "Every research report, briefing, digest, and code review",
                                    " ",
                                    assistantName,
                                    " produces is automatically archived here."
                                ]
                            }, void 0, true, {
                                fileName: "[project]/components/BrainModal.tsx",
                                lineNumber: 1044,
                                columnNumber: 17
                            }, this) : outputs.map((o)=>{
                                const isExp = expandedOutId === o.id;
                                return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                    style: {
                                        borderRadius: 12,
                                        padding: "11px 14px",
                                        background: o.pinned ? `${SECONDARY}12` : "rgba(255,255,255,0.03)",
                                        border: `1px solid ${o.pinned ? `${SECONDARY}66` : `${PRIMARY}26`}`,
                                        display: "flex",
                                        flexDirection: "column",
                                        gap: 7
                                    },
                                    children: [
                                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                            style: {
                                                display: "flex",
                                                justifyContent: "space-between",
                                                alignItems: "center",
                                                gap: 8,
                                                flexWrap: "wrap"
                                            },
                                            children: [
                                                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                                    children: [
                                                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("span", {
                                                            style: {
                                                                fontFamily: "var(--font-mono)",
                                                                fontSize: 11.5,
                                                                color: o.pinned ? SECONDARY : PRIMARY,
                                                                fontWeight: 600
                                                            },
                                                            children: [
                                                                o.pinned ? "📌 " : "",
                                                                o.title
                                                            ]
                                                        }, void 0, true, {
                                                            fileName: "[project]/components/BrainModal.tsx",
                                                            lineNumber: 1085,
                                                            columnNumber: 27
                                                        }, this),
                                                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("span", {
                                                            style: {
                                                                fontSize: 10,
                                                                color: "rgba(240,237,232,0.45)",
                                                                marginLeft: 9
                                                            },
                                                            children: o.created_at
                                                        }, void 0, false, {
                                                            fileName: "[project]/components/BrainModal.tsx",
                                                            lineNumber: 1096,
                                                            columnNumber: 27
                                                        }, this)
                                                    ]
                                                }, void 0, true, {
                                                    fileName: "[project]/components/BrainModal.tsx",
                                                    lineNumber: 1084,
                                                    columnNumber: 25
                                                }, this),
                                                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                                    style: {
                                                        display: "flex",
                                                        gap: 6
                                                    },
                                                    children: [
                                                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("button", {
                                                            type: "button",
                                                            onClick: ()=>postBrain({
                                                                    action: "brain_pin_output",
                                                                    id: o.id
                                                                }),
                                                            style: pillBtn(Boolean(o.pinned), SECONDARY),
                                                            children: [
                                                                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$pin$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__Pin$3e$__["Pin"], {
                                                                    size: 10
                                                                }, void 0, false, {
                                                                    fileName: "[project]/components/BrainModal.tsx",
                                                                    lineNumber: 1115,
                                                                    columnNumber: 29
                                                                }, this),
                                                                " ",
                                                                o.pinned ? "PINNED" : "PIN"
                                                            ]
                                                        }, void 0, true, {
                                                            fileName: "[project]/components/BrainModal.tsx",
                                                            lineNumber: 1108,
                                                            columnNumber: 27
                                                        }, this),
                                                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("button", {
                                                            type: "button",
                                                            onClick: ()=>setExpandedOutId(isExp ? null : o.id),
                                                            style: pillBtn(isExp),
                                                            children: isExp ? "COLLAPSE" : "EXPAND"
                                                        }, void 0, false, {
                                                            fileName: "[project]/components/BrainModal.tsx",
                                                            lineNumber: 1117,
                                                            columnNumber: 27
                                                        }, this),
                                                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("button", {
                                                            type: "button",
                                                            onClick: ()=>{
                                                                showContentCard({
                                                                    title: o.title,
                                                                    text: o.content
                                                                });
                                                                setBrainModalOpen(false);
                                                            },
                                                            style: pillBtn(),
                                                            children: "OPEN IN HUD"
                                                        }, void 0, false, {
                                                            fileName: "[project]/components/BrainModal.tsx",
                                                            lineNumber: 1126,
                                                            columnNumber: 27
                                                        }, this),
                                                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("button", {
                                                            type: "button",
                                                            onClick: ()=>downloadOutputMd(o),
                                                            style: pillBtn(),
                                                            children: [
                                                                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$download$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__Download$3e$__["Download"], {
                                                                    size: 10
                                                                }, void 0, false, {
                                                                    fileName: "[project]/components/BrainModal.tsx",
                                                                    lineNumber: 1141,
                                                                    columnNumber: 29
                                                                }, this),
                                                                " .MD"
                                                            ]
                                                        }, void 0, true, {
                                                            fileName: "[project]/components/BrainModal.tsx",
                                                            lineNumber: 1136,
                                                            columnNumber: 27
                                                        }, this),
                                                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("button", {
                                                            type: "button",
                                                            onClick: ()=>postBrain({
                                                                    action: "brain_delete_output",
                                                                    id: o.id
                                                                }),
                                                            style: {
                                                                ...pillBtn(),
                                                                borderColor: `${RED}55`,
                                                                color: RED
                                                            },
                                                            children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$trash$2d$2$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__Trash2$3e$__["Trash2"], {
                                                                size: 10
                                                            }, void 0, false, {
                                                                fileName: "[project]/components/BrainModal.tsx",
                                                                lineNumber: 1150,
                                                                columnNumber: 29
                                                            }, this)
                                                        }, void 0, false, {
                                                            fileName: "[project]/components/BrainModal.tsx",
                                                            lineNumber: 1143,
                                                            columnNumber: 27
                                                        }, this)
                                                    ]
                                                }, void 0, true, {
                                                    fileName: "[project]/components/BrainModal.tsx",
                                                    lineNumber: 1107,
                                                    columnNumber: 25
                                                }, this)
                                            ]
                                        }, void 0, true, {
                                            fileName: "[project]/components/BrainModal.tsx",
                                            lineNumber: 1075,
                                            columnNumber: 23
                                        }, this),
                                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                            style: {
                                                fontSize: 12,
                                                color: "rgba(240,237,232,0.78)",
                                                whiteSpace: "pre-wrap",
                                                lineHeight: 1.5
                                            },
                                            children: isExp ? o.content : o.content.slice(0, 260) + (o.content.length > 260 ? "…" : "")
                                        }, void 0, false, {
                                            fileName: "[project]/components/BrainModal.tsx",
                                            lineNumber: 1155,
                                            columnNumber: 23
                                        }, this)
                                    ]
                                }, o.id, true, {
                                    fileName: "[project]/components/BrainModal.tsx",
                                    lineNumber: 1059,
                                    columnNumber: 21
                                }, this);
                            })
                        }, void 0, false, {
                            fileName: "[project]/components/BrainModal.tsx",
                            lineNumber: 1042,
                            columnNumber: 13
                        }, this)
                    ]
                }, void 0, true, {
                    fileName: "[project]/components/BrainModal.tsx",
                    lineNumber: 503,
                    columnNumber: 9
                }, this),
                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                    style: {
                        display: "flex",
                        alignItems: "center",
                        justifyContent: "space-between",
                        gap: 8,
                        paddingTop: 10,
                        borderTop: "1px solid rgba(255,255,255,0.09)",
                        flexWrap: "wrap"
                    },
                    children: [
                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                            style: {
                                display: "flex",
                                alignItems: "center",
                                gap: 6,
                                fontFamily: "var(--font-mono)",
                                fontSize: 10,
                                letterSpacing: "0.14em",
                                color: "rgba(240,237,232,0.58)"
                            },
                            children: [
                                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$lucide$2d$react$2f$dist$2f$esm$2f$icons$2f$shield$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__Shield$3e$__["Shield"], {
                                    size: 13,
                                    style: {
                                        color: PRIMARY
                                    }
                                }, void 0, false, {
                                    fileName: "[project]/components/BrainModal.tsx",
                                    lineNumber: 1196,
                                    columnNumber: 13
                                }, this),
                                "LOCAL DATA GOVERNANCE:"
                            ]
                        }, void 0, true, {
                            fileName: "[project]/components/BrainModal.tsx",
                            lineNumber: 1185,
                            columnNumber: 11
                        }, this),
                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                            style: {
                                display: "flex",
                                gap: 6,
                                flexWrap: "wrap"
                            },
                            children: [
                                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("button", {
                                    type: "button",
                                    onClick: ()=>updatePrivacy({
                                            personalization_enabled: !privacy.personalization_enabled
                                        }),
                                    style: pillBtn(privacy.personalization_enabled, GREEN),
                                    children: [
                                        "PERSONALIZATION: ",
                                        privacy.personalization_enabled ? "ON" : "PAUSED"
                                    ]
                                }, void 0, true, {
                                    fileName: "[project]/components/BrainModal.tsx",
                                    lineNumber: 1201,
                                    columnNumber: 13
                                }, this),
                                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("button", {
                                    type: "button",
                                    onClick: ()=>updatePrivacy({
                                            adaptive_learning_enabled: !privacy.adaptive_learning_enabled
                                        }),
                                    style: pillBtn(privacy.adaptive_learning_enabled, GREEN),
                                    children: [
                                        "ADAPTIVE LEARNING:",
                                        " ",
                                        privacy.adaptive_learning_enabled ? "ON" : "PAUSED"
                                    ]
                                }, void 0, true, {
                                    fileName: "[project]/components/BrainModal.tsx",
                                    lineNumber: 1212,
                                    columnNumber: 13
                                }, this),
                                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("button", {
                                    type: "button",
                                    onClick: ()=>updatePrivacy({
                                            timeline_persistence_enabled: !privacy.timeline_persistence_enabled
                                        }),
                                    style: pillBtn(privacy.timeline_persistence_enabled, GREEN),
                                    children: [
                                        "FOREVER TIMELINE:",
                                        " ",
                                        privacy.timeline_persistence_enabled ? "ON" : "PAUSED"
                                    ]
                                }, void 0, true, {
                                    fileName: "[project]/components/BrainModal.tsx",
                                    lineNumber: 1224,
                                    columnNumber: 13
                                }, this)
                            ]
                        }, void 0, true, {
                            fileName: "[project]/components/BrainModal.tsx",
                            lineNumber: 1200,
                            columnNumber: 11
                        }, this)
                    ]
                }, void 0, true, {
                    fileName: "[project]/components/BrainModal.tsx",
                    lineNumber: 1174,
                    columnNumber: 9
                }, this)
            ]
        }, void 0, true, {
            fileName: "[project]/components/BrainModal.tsx",
            lineNumber: 344,
            columnNumber: 7
        }, this)
    }, void 0, false, {
        fileName: "[project]/components/BrainModal.tsx",
        lineNumber: 327,
        columnNumber: 5
    }, this);
}
_s(BrainModal, "VU1sx8qh9zZQ1iSRcIZSwcWeRg0=", false, function() {
    return [
        __TURBOPACK__imported__module__$5b$project$5d2f$components$2f$JarvisBridge$2e$tsx__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useJarvis"]
    ];
});
_c = BrainModal;
var _c;
__turbopack_context__.k.register(_c, "BrainModal");
if (typeof globalThis.$RefreshHelpers$ === 'object' && globalThis.$RefreshHelpers !== null) {
    __turbopack_context__.k.registerExports(__turbopack_context__.m, globalThis.$RefreshHelpers$);
}
}),
]);

//# sourceMappingURL=components_BrainModal_tsx_0qea1gg1hshzm._.js.map