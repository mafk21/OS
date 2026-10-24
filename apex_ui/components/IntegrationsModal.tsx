"use client";

import React, { useEffect, useState } from "react";
import {
  Check,
  ExternalLink,
  EyeOff,
  Link2,
  Mail,
  Sparkles,
  Trash2,
  X,
} from "lucide-react";
import { useJarvis } from "./JarvisBridge";
import { PERSONA_THEMES, type PersonaMode } from "./theme";

const GREEN = "#34d399";
const RED = "#ff5b79";

export default function IntegrationsModal() {
  const {
    assistantName,
    activePersona,
    theme,
    personaChosen,
    integrationsReady,
    integrations,
    integrationsModalOpen,
    setIntegrationsModalOpen,
    setPreviewPersona,
    choosePersona,
    saveIntegrations,
    skipIntegrations,
    disconnectIntegration,
    startGoogleOAuth,
  } = useJarvis();

  const PRIMARY = theme.primary;
  const SECONDARY = theme.secondary;
  const isFirstRunStep = !integrationsReady || !personaChosen;

  // Per-service ignore flags + form values
  const [ignoredMap, setIgnoredMap] = useState<Record<string, boolean>>({});
  const [emailAddr, setEmailAddr] = useState("");
  const [emailAppPw, setEmailAppPw] = useState("");
  const [imapHost, setImapHost] = useState("");
  const [smtpHost, setSmtpHost] = useState("");

  const [googleClientId, setGoogleClientId] = useState("");
  const [googleClientSecret, setGoogleClientSecret] = useState("");
  const [googleToken, setGoogleToken] = useState("");
  const [googleRefreshToken, setGoogleRefreshToken] = useState("");
  const [oauthMsg, setOauthMsg] = useState("");

  const [githubToken, setGithubToken] = useState("");
  const [notionToken, setNotionToken] = useState("");
  const [notionPageId, setNotionPageId] = useState("");
  const [slackToken, setSlackToken] = useState("");
  const [slackWebhook, setSlackWebhook] = useState("");
  const [slackChannel, setSlackChannel] = useState("");
  const [discordWebhook, setDiscordWebhook] = useState("");
  const [discordToken, setDiscordToken] = useState("");
  const [discordChannelId, setDiscordChannelId] = useState("");
  const [telegramToken, setTelegramToken] = useState("");
  const [spotifyId, setSpotifyId] = useState("");
  const [spotifySecret, setSpotifySecret] = useState("");
  const [trelloKey, setTrelloKey] = useState("");
  const [trelloToken, setTrelloToken] = useState("");

  const [saving, setSaving] = useState(false);

  useEffect(() => {
    if (!integrationsModalOpen) return;
    const svcs = integrations.services || {};
    setIgnoredMap({
      email: Boolean(svcs.email?.ignored),
      google: Boolean(
        svcs.google_drive?.ignored &&
          svcs.gmail?.ignored &&
          svcs.google_calendar?.ignored
      ),
      github: Boolean(svcs.github?.ignored),
      notion: Boolean(svcs.notion?.ignored),
      slack: Boolean(svcs.slack?.ignored),
      discord: Boolean(svcs.discord?.ignored),
      telegram: Boolean(svcs.telegram?.ignored),
      spotify: Boolean(svcs.spotify?.ignored),
      trello: Boolean(svcs.trello?.ignored),
    });
    if (svcs.email?.email && !emailAddr) {
      setEmailAddr(svcs.email.email);
    }
    if (svcs.discord?.channel_id && !discordChannelId) {
      setDiscordChannelId(svcs.discord.channel_id);
    }
  }, [integrationsModalOpen, integrations, emailAddr, discordChannelId]);

  if (!integrationsModalOpen) return null;

  const svcs = integrations.services || {};
  const isGoogleConnected = Boolean(
    svcs.google_drive?.connected ||
      svcs.gmail?.connected ||
      svcs.google_calendar?.connected
  );

  const toggleIgnore = (key: string) => {
    setIgnoredMap((prev) => ({ ...prev, [key]: !prev[key] }));
  };

  const onSave = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    await saveIntegrations({
      email: {
        ignore: Boolean(ignoredMap.email),
        email: emailAddr,
        app_password: emailAppPw,
        imap_host: imapHost,
        smtp_host: smtpHost,
      },
      google: {
        ignore: Boolean(ignoredMap.google),
        client_id: googleClientId,
        client_secret: googleClientSecret,
        token: googleToken,
        refresh_token: googleRefreshToken,
        email: emailAddr,
      },
      github: {
        ignore: Boolean(ignoredMap.github),
        token: githubToken,
      },
      notion: {
        ignore: Boolean(ignoredMap.notion),
        token: notionToken,
        parent_page_id: notionPageId,
      },
      slack: {
        ignore: Boolean(ignoredMap.slack),
        token: slackToken,
        webhook_url: slackWebhook,
        default_channel: slackChannel,
      },
      discord: {
        ignore: Boolean(ignoredMap.discord),
        webhook_url: discordWebhook,
        token: discordToken,
        channel_id: discordChannelId,
      },
      telegram: {
        ignore: Boolean(ignoredMap.telegram),
        token: telegramToken,
      },
      spotify: {
        ignore: Boolean(ignoredMap.spotify),
        client_id: spotifyId,
        client_secret: spotifySecret,
      },
      trello: {
        ignore: Boolean(ignoredMap.trello),
        api_key: trelloKey,
        token: trelloToken,
      },
    });
    setSaving(false);
  };

  const onOAuthClick = async () => {
    setOauthMsg("");
    const res = await startGoogleOAuth(googleClientId, googleClientSecret);
    if (!res.ok) {
      setOauthMsg(res.error || "Enter Client ID & Client Secret first.");
    } else {
      setOauthMsg(
        "Opened Google sign-in in your browser — complete consent and this status updates automatically."
      );
    }
  };

  const inputStyle: React.CSSProperties = {
    width: "100%",
    background: theme.inputBg,
    color: "#f0ede8",
    border: `1px solid ${theme.primaryBorder}`,
    borderRadius: 8,
    padding: "8px 10px",
    fontSize: 12,
    outline: "none",
    fontFamily: "var(--font-mono)",
  };

  const cardWrap = (ignored: boolean, connected: boolean): React.CSSProperties => ({
    borderRadius: 14,
    padding: "13px 15px",
    background: ignored
      ? "rgba(255,255,255,0.015)"
      : connected
      ? `${GREEN}0d`
      : "rgba(255,255,255,0.03)",
    border: `1px solid ${
      ignored
        ? "rgba(255,255,255,0.07)"
        : connected
        ? `${GREEN}55`
        : `${PRIMARY}2a`
    }`,
    opacity: ignored ? 0.62 : 1,
    display: "flex",
    flexDirection: "column",
    gap: 9,
    transition: "all 0.2s ease",
  });

  const renderCardHeader = (
    key: string,
    title: string,
    subtitle: string,
    connected: boolean,
    disconnectKey?: string
  ) => {
    const ignored = Boolean(ignoredMap[key]);
    return (
      <div
        style={{
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          gap: 10,
          flexWrap: "wrap",
        }}
      >
        <div>
          <div
            style={{
              display: "flex",
              alignItems: "center",
              gap: 8,
              fontFamily: "var(--font-mono)",
              fontSize: 11,
              letterSpacing: "0.14em",
              color: connected ? GREEN : ignored ? "rgba(240,237,232,0.5)" : PRIMARY,
              fontWeight: 600,
            }}
          >
            {title}
            {connected && (
              <span
                style={{
                  display: "inline-flex",
                  alignItems: "center",
                  gap: 4,
                  fontSize: 9,
                  padding: "2px 7px",
                  borderRadius: 999,
                  background: `${GREEN}22`,
                  border: `1px solid ${GREEN}66`,
                  color: GREEN,
                }}
              >
                <Check size={10} /> CONNECTED
              </span>
            )}
            {ignored && !connected && (
              <span
                style={{
                  fontSize: 9,
                  padding: "2px 7px",
                  borderRadius: 999,
                  background: "rgba(255,255,255,0.06)",
                  color: "rgba(240,237,232,0.5)",
                }}
              >
                IGNORED
              </span>
            )}
          </div>
          <div
            style={{
              fontSize: 11,
              color: "rgba(240,237,232,0.58)",
              marginTop: 2,
            }}
          >
            {subtitle}
          </div>
        </div>

        <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
          {connected && (
            <button
              type="button"
              onClick={() => disconnectIntegration(disconnectKey || key)}
              style={{
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
                cursor: "pointer",
              }}
            >
              <Trash2 size={10} /> DISCONNECT
            </button>
          )}
          <button
            type="button"
            onClick={() => toggleIgnore(key)}
            style={{
              display: "inline-flex",
              alignItems: "center",
              gap: 5,
              fontFamily: "var(--font-mono)",
              fontSize: 9.5,
              letterSpacing: "0.12em",
              padding: "4px 10px",
              borderRadius: 999,
              border: `1px solid ${
                ignored ? `${SECONDARY}66` : "rgba(255,255,255,0.18)"
              }`,
              background: ignored ? `${SECONDARY}1e` : "transparent",
              color: ignored ? SECONDARY : "rgba(240,237,232,0.72)",
              cursor: "pointer",
            }}
          >
            <EyeOff size={10} />
            {ignored ? "UN-IGNORE" : "IGNORE"}
          </button>
        </div>
      </div>
    );
  };

  return (
    <div
      role="dialog"
      aria-modal="true"
      aria-label="Configure Optional Integrations"
      onClick={() => {
        if (!isFirstRunStep) setIntegrationsModalOpen(false);
      }}
      style={{
        position: "fixed",
        inset: 0,
        zIndex: 89,
        background: "rgba(2, 6, 14, 0.76)",
        backdropFilter: "blur(12px)",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        padding: 14,
      }}
    >
      <form
        onSubmit={onSave}
        onClick={(e) => e.stopPropagation()}
        style={{
          width: "min(760px, 96vw)",
          maxHeight: "88vh",
          background: theme.panelBg,
          border: `1px solid ${PRIMARY}55`,
          borderRadius: 22,
          padding: "20px 22px 18px",
          boxShadow: `0 0 60px ${PRIMARY}26, 0 22px 64px rgba(0,0,0,0.88)`,
          display: "flex",
          flexDirection: "column",
          gap: 14,
        }}
      >
        {/* Header + Live Male / Female Switcher */}
        <div
          style={{
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
            gap: 10,
            flexWrap: "wrap",
          }}
        >
          <div style={{ display: "flex", alignItems: "center", gap: 9 }}>
            <Link2 size={17} style={{ color: PRIMARY }} />
            <span
              style={{
                fontFamily: "var(--font-mono)",
                fontSize: 11,
                letterSpacing: "0.22em",
                color: PRIMARY,
              }}
            >
              {isFirstRunStep
                ? `STEP 2 OF 3 · OPTIONAL INTEGRATIONS`
                : `${assistantName.toUpperCase()} · INTEGRATIONS & ACCOUNTS`}
            </span>
          </div>

          <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
            {(["male", "female"] as PersonaMode[]).map((pKey) => {
              const pTheme = PERSONA_THEMES[pKey];
              const isAct = activePersona === pKey;
              return (
                <button
                  key={pKey}
                  type="button"
                  onClick={() =>
                    personaChosen ? choosePersona(pKey) : setPreviewPersona(pKey)
                  }
                  title={`Switch theme to ${pTheme.label}`}
                  style={{
                    display: "inline-flex",
                    alignItems: "center",
                    gap: 5,
                    fontFamily: "var(--font-mono)",
                    fontSize: 9.5,
                    letterSpacing: "0.14em",
                    padding: "4px 9px",
                    borderRadius: 999,
                    border: `1px solid ${
                      isAct ? pTheme.primary : "rgba(255,255,255,0.14)"
                    }`,
                    background: isAct ? `${pTheme.primary}22` : "transparent",
                    color: isAct ? pTheme.primary : "rgba(240,237,232,0.62)",
                    cursor: "pointer",
                  }}
                >
                  <Sparkles size={10} />
                  {pKey === "female" ? "♀ FEMALE" : "♂ MALE"}
                </button>
              );
            })}

            {!isFirstRunStep && (
              <button
                type="button"
                onClick={() => setIntegrationsModalOpen(false)}
                aria-label="Close integrations modal"
                style={{
                  background: "none",
                  border: "none",
                  color: "rgba(255,255,255,0.5)",
                  cursor: "pointer",
                  marginLeft: 4,
                }}
              >
                <X size={18} />
              </button>
            )}
          </div>
        </div>

        <div
          style={{
            fontSize: 12,
            lineHeight: 1.5,
            color: "rgba(240,237,232,0.74)",
          }}
        >
          Set up only the accounts you want {assistantName} to use in both{" "}
          <strong>Male</strong> and <strong>Female</strong> editions. Click{" "}
          <strong>IGNORE</strong> on anything you don&apos;t use, or leave it blank
          — nothing here is forced.
        </div>

        {/* Scrollable Service Cards */}
        <div
          style={{
            overflowY: "auto",
            display: "flex",
            flexDirection: "column",
            gap: 11,
            paddingRight: 4,
          }}
        >
          {/* 1. Direct Email (Gmail / Outlook / iCloud App Password) */}
          <div
            style={cardWrap(
              Boolean(ignoredMap.email),
              Boolean(svcs.email?.connected)
            )}
          >
            {renderCardHeader(
              "email",
              "EMAIL · DIRECT IMAP / SMTP",
              "Read & send real emails instantly with a Gmail 16-char App Password, Outlook, iCloud, or custom mail.",
              Boolean(svcs.email?.connected)
            )}
            {!ignoredMap.email && (
              <div
                style={{
                  display: "grid",
                  gridTemplateColumns: "repeat(auto-fit, minmax(210px, 1fr))",
                  gap: 8,
                }}
              >
                <input
                  type="email"
                  value={emailAddr}
                  onChange={(e) => setEmailAddr(e.target.value)}
                  placeholder="Email address (e.g. you@gmail.com)"
                  style={inputStyle}
                />
                <input
                  type="password"
                  value={emailAppPw}
                  onChange={(e) => setEmailAppPw(e.target.value)}
                  placeholder="App Password (16-char Gmail/iCloud)"
                  style={inputStyle}
                />
                <input
                  type="text"
                  value={imapHost}
                  onChange={(e) => setImapHost(e.target.value)}
                  placeholder="IMAP host (auto-detected if blank)"
                  style={inputStyle}
                />
                <input
                  type="text"
                  value={smtpHost}
                  onChange={(e) => setSmtpHost(e.target.value)}
                  placeholder="SMTP host (auto-detected if blank)"
                  style={inputStyle}
                />
              </div>
            )}
          </div>

          {/* 2. Google Workspace (Gmail + Google Drive + Google Calendar) */}
          <div style={cardWrap(Boolean(ignoredMap.google), isGoogleConnected)}>
            {renderCardHeader(
              "google",
              "GOOGLE WORKSPACE · DRIVE, GMAIL & CALENDAR",
              "Direct Google Drive upload/search/download, Calendar events, and Gmail API via OAuth.",
              isGoogleConnected,
              "google"
            )}
            {!ignoredMap.google && (
              <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
                <div
                  style={{
                    display: "grid",
                    gridTemplateColumns: "repeat(auto-fit, minmax(210px, 1fr))",
                    gap: 8,
                  }}
                >
                  <input
                    type="text"
                    value={googleClientId}
                    onChange={(e) => setGoogleClientId(e.target.value)}
                    placeholder="Google OAuth Client ID (optional)"
                    style={inputStyle}
                  />
                  <input
                    type="password"
                    value={googleClientSecret}
                    onChange={(e) => setGoogleClientSecret(e.target.value)}
                    placeholder="Google OAuth Client Secret (optional)"
                    style={inputStyle}
                  />
                  <input
                    type="password"
                    value={googleToken}
                    onChange={(e) => setGoogleToken(e.target.value)}
                    placeholder="Or paste OAuth Access Token (ya29...)"
                    style={inputStyle}
                  />
                  <input
                    type="password"
                    value={googleRefreshToken}
                    onChange={(e) => setGoogleRefreshToken(e.target.value)}
                    placeholder="Optional Refresh Token (1//...)"
                    style={inputStyle}
                  />
                </div>
                <div style={{ display: "flex", alignItems: "center", gap: 10, flexWrap: "wrap" }}>
                  <button
                    type="button"
                    onClick={onOAuthClick}
                    style={{
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
                      cursor: "pointer",
                    }}
                  >
                    <ExternalLink size={11} />
                    AUTHORIZE GOOGLE IN BROWSER
                  </button>
                  {oauthMsg && (
                    <span style={{ fontSize: 11, color: SECONDARY }}>
                      {oauthMsg}
                    </span>
                  )}
                </div>
              </div>
            )}
          </div>

          {/* 3. GitHub */}
          <div
            style={cardWrap(
              Boolean(ignoredMap.github),
              Boolean(svcs.github?.connected)
            )}
          >
            {renderCardHeader(
              "github",
              "GITHUB",
              "Manage repos, issues, pull requests & CI runs.",
              Boolean(svcs.github?.connected)
            )}
            {!ignoredMap.github && (
              <input
                type="password"
                value={githubToken}
                onChange={(e) => setGithubToken(e.target.value)}
                placeholder="GitHub Personal Access Token (ghp_... / github_pat_...)"
                style={inputStyle}
              />
            )}
          </div>

          {/* 4. Notion */}
          <div
            style={cardWrap(
              Boolean(ignoredMap.notion),
              Boolean(svcs.notion?.connected)
            )}
          >
            {renderCardHeader(
              "notion",
              "NOTION",
              "Search, read, create, and append pages & databases.",
              Boolean(svcs.notion?.connected)
            )}
            {!ignoredMap.notion && (
              <div
                style={{
                  display: "grid",
                  gridTemplateColumns: "repeat(auto-fit, minmax(210px, 1fr))",
                  gap: 8,
                }}
              >
                <input
                  type="password"
                  value={notionToken}
                  onChange={(e) => setNotionToken(e.target.value)}
                  placeholder="Notion Integration Secret (ntn_... / secret_...)"
                  style={inputStyle}
                />
                <input
                  type="text"
                  value={notionPageId}
                  onChange={(e) => setNotionPageId(e.target.value)}
                  placeholder="Default Parent Page ID (optional)"
                  style={inputStyle}
                />
              </div>
            )}
          </div>

          {/* 5. Slack */}
          <div
            style={cardWrap(
              Boolean(ignoredMap.slack),
              Boolean(svcs.slack?.connected)
            )}
          >
            {renderCardHeader(
              "slack",
              "SLACK",
              "Send messages, list channels, and read recent Slack threads.",
              Boolean(svcs.slack?.connected)
            )}
            {!ignoredMap.slack && (
              <div
                style={{
                  display: "grid",
                  gridTemplateColumns: "repeat(auto-fit, minmax(180px, 1fr))",
                  gap: 8,
                }}
              >
                <input
                  type="password"
                  value={slackToken}
                  onChange={(e) => setSlackToken(e.target.value)}
                  placeholder="Bot/User Token (xoxb-...)"
                  style={inputStyle}
                />
                <input
                  type="password"
                  value={slackWebhook}
                  onChange={(e) => setSlackWebhook(e.target.value)}
                  placeholder="Or Webhook URL (https://hooks.slack.com/...)"
                  style={inputStyle}
                />
                <input
                  type="text"
                  value={slackChannel}
                  onChange={(e) => setSlackChannel(e.target.value)}
                  placeholder="Default #channel (optional)"
                  style={inputStyle}
                />
              </div>
            )}
          </div>

          {/* 6. Discord */}
          <div
            style={cardWrap(
              Boolean(ignoredMap.discord),
              Boolean(svcs.discord?.connected)
            )}
          >
            {renderCardHeader(
              "discord",
              "DISCORD",
              "Post updates via Webhook or read/send channels via Discord Bot Token.",
              Boolean(svcs.discord?.connected)
            )}
            {!ignoredMap.discord && (
              <div
                style={{
                  display: "grid",
                  gridTemplateColumns: "repeat(auto-fit, minmax(180px, 1fr))",
                  gap: 8,
                }}
              >
                <input
                  type="password"
                  value={discordWebhook}
                  onChange={(e) => setDiscordWebhook(e.target.value)}
                  placeholder="Webhook URL (https://discord.com/api/webhooks/...)"
                  style={inputStyle}
                />
                <input
                  type="password"
                  value={discordToken}
                  onChange={(e) => setDiscordToken(e.target.value)}
                  placeholder="Or Discord Bot Token"
                  style={inputStyle}
                />
                <input
                  type="text"
                  value={discordChannelId}
                  onChange={(e) => setDiscordChannelId(e.target.value)}
                  placeholder="Default Channel ID (optional)"
                  style={inputStyle}
                />
              </div>
            )}
          </div>

          {/* 7. Telegram + Spotify + Trello */}
          <div
            style={cardWrap(
              Boolean(ignoredMap.telegram),
              Boolean(svcs.telegram?.connected)
            )}
          >
            {renderCardHeader(
              "telegram",
              "TELEGRAM REMOTE BOT",
              "Control JARVIS remotely from your phone via @BotFather token.",
              Boolean(svcs.telegram?.connected)
            )}
            {!ignoredMap.telegram && (
              <input
                type="password"
                value={telegramToken}
                onChange={(e) => setTelegramToken(e.target.value)}
                placeholder="Telegram Bot Token (123456789:ABC...)"
                style={inputStyle}
              />
            )}
          </div>

          <div
            style={cardWrap(
              Boolean(ignoredMap.spotify),
              Boolean(svcs.spotify?.connected)
            )}
          >
            {renderCardHeader(
              "spotify",
              "SPOTIFY",
              "Direct Spotify playback & track search.",
              Boolean(svcs.spotify?.connected)
            )}
            {!ignoredMap.spotify && (
              <div
                style={{
                  display: "grid",
                  gridTemplateColumns: "repeat(auto-fit, minmax(210px, 1fr))",
                  gap: 8,
                }}
              >
                <input
                  type="text"
                  value={spotifyId}
                  onChange={(e) => setSpotifyId(e.target.value)}
                  placeholder="Spotify Client ID"
                  style={inputStyle}
                />
                <input
                  type="password"
                  value={spotifySecret}
                  onChange={(e) => setSpotifySecret(e.target.value)}
                  placeholder="Spotify Client Secret"
                  style={inputStyle}
                />
              </div>
            )}
          </div>

          <div
            style={cardWrap(
              Boolean(ignoredMap.trello),
              Boolean(svcs.trello?.connected)
            )}
          >
            {renderCardHeader(
              "trello",
              "TRELLO",
              "Read boards and create Trello task cards.",
              Boolean(svcs.trello?.connected)
            )}
            {!ignoredMap.trello && (
              <div
                style={{
                  display: "grid",
                  gridTemplateColumns: "repeat(auto-fit, minmax(210px, 1fr))",
                  gap: 8,
                }}
              >
                <input
                  type="text"
                  value={trelloKey}
                  onChange={(e) => setTrelloKey(e.target.value)}
                  placeholder="Trello API Key"
                  style={inputStyle}
                />
                <input
                  type="password"
                  value={trelloToken}
                  onChange={(e) => setTrelloToken(e.target.value)}
                  placeholder="Trello Token"
                  style={inputStyle}
                />
              </div>
            )}
          </div>
        </div>

        {/* Sticky Footer */}
        <div
          style={{
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
            gap: 10,
            paddingTop: 8,
            borderTop: "1px solid rgba(255,255,255,0.09)",
            flexWrap: "wrap",
          }}
        >
          <button
            type="button"
            onClick={() => skipIntegrations()}
            style={{
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
              cursor: "pointer",
            }}
          >
            {isFirstRunStep ? "IGNORE ALL / SKIP FOR NOW" : "CLOSE"}
          </button>

          <button
            type="submit"
            disabled={saving}
            style={{
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
              cursor: "pointer",
            }}
          >
            <Mail size={13} />
            {saving
              ? "SAVING..."
              : isFirstRunStep
              ? "SAVE SELECTED & CHOOSE EDITION →"
              : "SAVE INTEGRATIONS"}
          </button>
        </div>
      </form>
    </div>
  );
}
