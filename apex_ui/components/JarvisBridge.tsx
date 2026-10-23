"use client";

import React, {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useRef,
  useState,
} from "react";
import type { OrbState } from "./ApexHeroOrb";

export type LogEntry = {
  id: number;
  line: string;
  role: "user" | "jarvis" | "sys" | "tool";
  ts: string;
};

export type TraceEvent = {
  n: number;
  trace: { helper: string }[];
  tool?: string;
};

export type ConfirmBanner = {
  title: string;
  detail: string;
};

export type ContentCard = {
  title: string;
  text: string;
};

export type JarvisContextValue = {
  connected: boolean;
  ready: boolean;
  assistantName: string;
  orbState: OrbState;
  rawState: string;
  muted: boolean;
  paused: boolean;
  offline: boolean;
  offlineReason: string;
  voice: string;
  voices: string[];
  bargeEnabled: boolean;
  gracePeriod: number;
  inputs: string[];
  outputs: string[];
  currentInput: string;
  currentOutput: string;
  logs: LogEntry[];
  lastSubtitle: { role: string; text: string } | null;
  trace: TraceEvent | null;
  confirm: ConfirmBanner | null;
  content: ContentCard | null;
  consoleOpen: boolean;
  settingsOpen: boolean;
  setupOpen: boolean;
  setConsoleOpen: React.Dispatch<React.SetStateAction<boolean>>;
  setSettingsOpen: React.Dispatch<React.SetStateAction<boolean>>;
  setSetupOpen: React.Dispatch<React.SetStateAction<boolean>>;
  clearContent: () => void;
  sendText: (text: string, traceNode?: string) => void;
  tapOrb: () => void;
  fireLocalTrace: (nodes: string[]) => void;
  toggleMute: () => void;
  togglePause: () => void;
  interrupt: () => void;
  stopAll: () => void;
  captureRegion: () => void;
  openRemoteQr: () => void;
  setVoice: (v: string) => void;
  setDevices: (inputName: string, outputName: string) => void;
  setBarge: (enabled: boolean) => void;
  setGrace: (seconds: number) => void;
  resolveConfirm: (approved: boolean) => void;
  saveApiKey: (key: string) => Promise<boolean>;
};

const JarvisContext = createContext<JarvisContextValue | null>(null);
const JarvisAudioLevelContext = createContext<number>(0);

export function useJarvisAudioLevel(): number {
  return useContext(JarvisAudioLevelContext);
}

function mapRawToOrb(raw: string, muted: boolean, paused: boolean): OrbState {
  const s = (raw || "").toUpperCase();
  if (muted || paused || s === "MUTED" || s === "PAUSED" || s === "SLEEPING") {
    return "idle";
  }
  if (s === "SPEAKING") return "speaking";
  if (s === "THINKING" || s === "PROCESSING") return "thinking";
  if (s === "LISTENING") return "listening";
  return "idle";
}

function classifyLog(line: string): { role: LogEntry["role"]; clean: string } {
  const trimmed = (line || "").trim();
  if (/^(you|user)\s*:/i.test(trimmed)) {
    return { role: "user", clean: trimmed.replace(/^(you|user)\s*:\s*/i, "") };
  }
  if (/^(sys|net|err)\s*:/i.test(trimmed)) {
    return { role: "sys", clean: trimmed };
  }
  if (/^(tool|action)\s*:/i.test(trimmed)) {
    return { role: "tool", clean: trimmed };
  }
  if (/^[a-z0-9_ -]{2,18}:\s/i.test(trimmed)) {
    return { role: "jarvis", clean: trimmed.replace(/^[a-z0-9_ -]{2,18}:\s*/i, "") };
  }
  return { role: "sys", clean: trimmed };
}

export function JarvisProvider({ children }: { children: React.ReactNode }) {
  const [connected, setConnected] = useState(false);
  const [ready, setReady] = useState(true);
  const [assistantName, setAssistantName] = useState("JARVIS");
  const [rawState, setRawState] = useState("STANDBY");
  const [demoState, setDemoState] = useState<OrbState>("idle");
  const [audioLevel, setAudioLevel] = useState(0);
  const [muted, setMuted] = useState(false);
  const [paused, setPaused] = useState(false);
  const [offline, setOffline] = useState(false);
  const [offlineReason, setOfflineReason] = useState("");
  const [voice, setVoiceState] = useState("Charon");
  const [voices, setVoices] = useState<string[]>([
    "Charon",
    "Puck",
    "Kore",
    "Fenrir",
    "Aoede",
  ]);
  const [bargeEnabled, setBargeEnabled] = useState(true);
  const [gracePeriod, setGracePeriod] = useState(8);
  const [inputs, setInputs] = useState<string[]>(["System default"]);
  const [outputs, setOutputs] = useState<string[]>(["System default"]);
  const [currentInput, setCurrentInput] = useState("");
  const [currentOutput, setCurrentOutput] = useState("");
  const [logs, setLogs] = useState<LogEntry[]>([]);
  const [lastSubtitle, setLastSubtitle] = useState<{ role: string; text: string } | null>(null);
  const [trace, setTrace] = useState<TraceEvent | null>(null);
  const [confirm, setConfirm] = useState<ConfirmBanner | null>(null);
  const [content, setContent] = useState<ContentCard | null>(null);
  const [consoleOpen, setConsoleOpen] = useState(false);
  const [settingsOpen, setSettingsOpen] = useState(false);
  const [setupOpen, setSetupOpen] = useState(false);

  const wsRef = useRef<WebSocket | null>(null);
  const seqRef = useRef(1);
  const logIdRef = useRef(1);
  const demoTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const subtitleTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const targetLevelRef = useRef(0);

  const pushLogLine = useCallback((line: string, ts?: string) => {
    if (!line || !line.trim()) return;
    const { role, clean } = classifyLog(line);
    const stamp =
      ts ||
      new Date().toLocaleTimeString("en-GB", {
        hour: "2-digit",
        minute: "2-digit",
        second: "2-digit",
      });
    const id = logIdRef.current++;
    setLogs((prev) => {
      const next = [...prev, { id, line: line.trim(), role, ts: stamp }];
      return next.length > 140 ? next.slice(next.length - 140) : next;
    });
    if (role === "jarvis" || role === "user") {
      setLastSubtitle({ role, text: clean });
      if (subtitleTimerRef.current) clearTimeout(subtitleTimerRef.current);
      subtitleTimerRef.current = setTimeout(() => {
        setLastSubtitle(null);
      }, 9000);
    }
  }, []);

  const fireLocalTrace = useCallback((nodes: string[]) => {
    if (!nodes || nodes.length === 0) return;
    const n = seqRef.current++;
    setTrace({
      n,
      trace: nodes.map((helper) => ({ helper })),
    });
  }, []);

  const sendAction = useCallback((payload: Record<string, unknown>) => {
    const ws = wsRef.current;
    if (ws && ws.readyState === WebSocket.OPEN) {
      ws.send(JSON.stringify(payload));
      return true;
    }
    fetch("/api/hud/action", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    }).catch(() => {});
    return false;
  }, []);

  // Smooth audio envelope decay isolated in JarvisAudioLevelContext; skips state
  // updates completely when silent so 0 React re-renders occur at rest.
  useEffect(() => {
    const id = setInterval(() => {
      const tgt = targetLevelRef.current;
      targetLevelRef.current = tgt < 0.004 ? 0 : tgt * 0.84;
      setAudioLevel((cur) => {
        if (cur === 0 && tgt === 0) return 0;
        const next = cur + (tgt - cur) * 0.45;
        const clamped = next < 0.005 ? 0 : Math.min(1, next);
        return Math.abs(clamped - cur) < 0.004 ? cur : clamped;
      });
    }, 40);
    return () => clearInterval(id);
  }, []);

  const applyBootstrap = useCallback(
    (d: Record<string, unknown>) => {
      if (!d || typeof d !== "object") return;
      const isReady = d.ready !== false;
      setReady(isReady);
      if (!isReady) setSetupOpen(true);
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
        setVoices(d.voices as string[]);
      }
      if (typeof d.barge_enabled === "boolean") setBargeEnabled(d.barge_enabled);
      if (typeof d.grace_period === "number") setGracePeriod(d.grace_period);
      if (Array.isArray(d.inputs) && d.inputs.length > 0) {
        setInputs(d.inputs as string[]);
      }
      if (Array.isArray(d.outputs) && d.outputs.length > 0) {
        setOutputs(d.outputs as string[]);
      }
      if (typeof d.current_input === "string") setCurrentInput(d.current_input);
      if (typeof d.current_output === "string") setCurrentOutput(d.current_output);
      if (Array.isArray(d.logs)) {
        const mapped: LogEntry[] = (d.logs as string[]).map((ln) => {
          const { role } = classifyLog(String(ln));
          return {
            id: logIdRef.current++,
            line: String(ln),
            role,
            ts: "",
          };
        });
        setLogs(mapped.slice(-120));
      }
      if (d.confirm && typeof d.confirm === "object") {
        setConfirm(d.confirm as ConfirmBanner);
      } else {
        setConfirm(null);
      }
      if (d.content && typeof d.content === "object") {
        setContent(d.content as ContentCard);
      }
    },
    []
  );

  // Connect WebSocket `/ws/hud` with automatic reconnect
  useEffect(() => {
    let alive = true;
    let retryTimer: ReturnType<typeof setTimeout> | null = null;

    fetch("/api/hud/bootstrap")
      .then((r) => (r.ok ? r.json() : null))
      .then((d) => {
        if (alive && d) {
          setConnected(true);
          applyBootstrap(d);
        }
      })
      .catch(() => {});

    const connectWs = () => {
      if (!alive || typeof window === "undefined") return;
      const proto = window.location.protocol === "https:" ? "wss:" : "ws:";
      const url = `${proto}//${window.location.host}/ws/hud`;
      let ws: WebSocket;
      try {
        ws = new WebSocket(url);
      } catch {
        retryTimer = setTimeout(connectWs, 2500);
        return;
      }
      wsRef.current = ws;

      ws.onopen = () => {
        if (!alive) return;
        setConnected(true);
      };

      ws.onmessage = (ev) => {
        if (!alive) return;
        try {
          const msg = JSON.parse(ev.data);
          switch (msg.type) {
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
              targetLevelRef.current = Math.max(
                0,
                Math.min(1, Number(msg.level) || 0)
              );
              break;
            case "log":
              pushLogLine(String(msg.line || ""), msg.ts);
              break;
            case "trace": {
              const nodes: string[] = Array.isArray(msg.nodes) ? msg.nodes : [];
              if (nodes.length > 0) {
                const n = seqRef.current++;
                setTrace({
                  n,
                  tool: msg.tool,
                  trace: nodes.map((helper) => ({ helper })),
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
            case "reconfig":
              setReady(false);
              setSetupOpen(true);
              break;
            case "config":
              applyBootstrap(msg);
              break;
            default:
              break;
          }
        } catch {
          // ignore malformed packets
        }
      };

      ws.onclose = () => {
        if (!alive) return;
        wsRef.current = null;
        setConnected(false);
        retryTimer = setTimeout(connectWs, 1800);
      };

      ws.onerror = () => {
        try {
          ws.close();
        } catch {}
      };
    };

    connectWs();

    return () => {
      alive = false;
      if (retryTimer) clearTimeout(retryTimer);
      if (demoTimerRef.current) clearTimeout(demoTimerRef.current);
      if (subtitleTimerRef.current) clearTimeout(subtitleTimerRef.current);
      try {
        wsRef.current?.close();
      } catch {}
    };
  }, [applyBootstrap, pushLogLine]);

  const orbState: OrbState = connected
    ? mapRawToOrb(rawState, muted, paused)
    : demoState;

  const tapOrb = useCallback(() => {
    if (!connected) {
      const next: OrbState =
        demoState === "idle"
          ? "listening"
          : demoState === "listening"
          ? "thinking"
          : demoState === "thinking"
          ? "speaking"
          : "idle";
      setDemoState(next);
      if (next === "thinking") {
        fireLocalTrace(["chief_of_staff", "researcher", "memory"]);
      } else if (next === "speaking") {
        targetLevelRef.current = 0.72;
      }
      if (demoTimerRef.current) clearTimeout(demoTimerRef.current);
      demoTimerRef.current = setTimeout(() => setDemoState("idle"), 8000);
      return;
    }
    fireLocalTrace(["chief_of_staff"]);
    sendAction({ action: "orb_tap" });
  }, [connected, demoState, fireLocalTrace, sendAction]);

  const sendText = useCallback(
    (text: string, traceNode?: string) => {
      const clean = text.trim();
      if (!clean) return;
      fireLocalTrace(
        traceNode ? [traceNode, "chief_of_staff"] : ["chief_of_staff"]
      );
      if (!connected) {
        pushLogLine(`You: ${clean}`);
        setDemoState("thinking");
        if (demoTimerRef.current) clearTimeout(demoTimerRef.current);
        demoTimerRef.current = setTimeout(() => {
          setDemoState("idle");
        }, 3500);
        return;
      }
      setRawState("THINKING");
      sendAction({ action: "text_command", text: clean });
    },
    [connected, fireLocalTrace, pushLogLine, sendAction]
  );

  const toggleMute = useCallback(() => {
    if (!connected) {
      setMuted((m) => !m);
      return;
    }
    sendAction({ action: "toggle_mute" });
  }, [connected, sendAction]);

  const togglePause = useCallback(() => {
    if (!connected) {
      setPaused((p) => !p);
      return;
    }
    sendAction({ action: "toggle_pause" });
  }, [connected, sendAction]);

  const interrupt = useCallback(() => {
    if (!connected) {
      setDemoState("idle");
      return;
    }
    sendAction({ action: "interrupt" });
  }, [connected, sendAction]);

  const stopAll = useCallback(() => {
    sendAction({ action: "stop_all" });
  }, [sendAction]);

  const captureRegion = useCallback(() => {
    fireLocalTrace(["design"]);
    sendAction({ action: "region_capture" });
  }, [fireLocalTrace, sendAction]);

  const openRemoteQr = useCallback(() => {
    sendAction({ action: "remote_qr" });
  }, [sendAction]);

  const setVoice = useCallback(
    (v: string) => {
      setVoiceState(v);
      sendAction({ action: "set_voice", voice: v });
    },
    [sendAction]
  );

  const setDevices = useCallback(
    (inputName: string, outputName: string) => {
      setCurrentInput(inputName);
      setCurrentOutput(outputName);
      sendAction({
        action: "set_audio_devices",
        input_device: inputName,
        output_device: outputName,
      });
    },
    [sendAction]
  );

  const setBarge = useCallback(
    (enabled: boolean) => {
      setBargeEnabled(enabled);
      sendAction({ action: "set_barge", enabled });
    },
    [sendAction]
  );

  const setGrace = useCallback(
    (seconds: number) => {
      setGracePeriod(seconds);
      sendAction({ action: "set_grace", seconds });
    },
    [sendAction]
  );

  const resolveConfirm = useCallback(
    (approved: boolean) => {
      setConfirm(null);
      sendAction({ action: "confirm_decision", approved });
    },
    [sendAction]
  );

  const saveApiKey = useCallback(async (key: string): Promise<boolean> => {
    const trimmed = key.trim();
    if (!trimmed) return false;
    try {
      const r = await fetch("/api/hud/action", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ action: "save_api_key", key: trimmed }),
      });
      if (r.ok) {
        setReady(true);
        setSetupOpen(false);
        return true;
      }
    } catch {}
    return false;
  }, []);

  const clearContent = useCallback(() => setContent(null), []);

  const value = useMemo<JarvisContextValue>(
    () => ({
      connected,
      ready,
      assistantName,
      orbState,
      rawState: connected ? rawState : demoState.toUpperCase(),
      muted,
      paused,
      offline,
      offlineReason,
      voice,
      voices,
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
      consoleOpen,
      settingsOpen,
      setupOpen,
      setConsoleOpen,
      setSettingsOpen,
      setSetupOpen,
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
    }),
    [
      connected,
      ready,
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
      consoleOpen,
      settingsOpen,
      setupOpen,
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
    ]
  );

  return (
    <JarvisContext.Provider value={value}>
      <JarvisAudioLevelContext.Provider value={audioLevel}>
        {children}
      </JarvisAudioLevelContext.Provider>
    </JarvisContext.Provider>
  );
}

export function useJarvis(): JarvisContextValue {
  const ctx = useContext(JarvisContext);
  if (!ctx) {
    throw new Error("useJarvis must be used inside <JarvisProvider>");
  }
  return ctx;
}
