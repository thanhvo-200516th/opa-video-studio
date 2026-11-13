import React, { useState, useRef, useEffect } from "react";
import { COLORS, RADIUS, TYPOGRAPHY, MascotState } from "./tokens";
import { MascotAvatar } from "./MascotAvatar";

export interface Message {
  id: string;
  sender: "user" | "agent";
  text: string;
  timestamp: string;
}

export interface ChatWidgetProps {
  apiEndpoint?: string;
  agentName?: string;
  initialMessage?: string;
  onSend?: (message: string) => Promise<string> | void;
}

export const ChatWidget: React.FC<ChatWidgetProps> = ({
  apiEndpoint = "/api/chat",
  agentName = "Trợ lý OPA",
  initialMessage = "Chào anh/chị! OPA có thể hỗ trợ gì cho đội ngũ bán hàng và marketing của mình hôm nay?",
  onSend,
}) => {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState<Message[]>([
    {
      id: "init",
      sender: "agent",
      text: initialMessage,
      timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
    },
  ]);
  const [input, setInput] = useState("");
  const [mascotState, setMascotState] = useState<MascotState>("idle");
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, mascotState]);

  const handleSend = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    const text = input.trim();
    if (!text || mascotState === "thinking") return;

    const userMsg: Message = {
      id: String(Date.now()),
      sender: "user",
      text,
      timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
    };

    setMessages((prev) => [...prev, userMsg]);
    setInput("");
    setMascotState("thinking");

    try {
      let replyText = "";
      if (onSend) {
        const res = await onSend(text);
        if (typeof res === "string") replyText = res;
      } else {
        // Mock fallback response if no backend attached
        await new Promise((r) => setTimeout(r, 1200));
        replyText = "Dạ OPA đã ghi nhận yêu cầu. Đội ngũ kỹ thuật sẽ kết nối hỗ trợ anh/chị ngay.";
      }

      if (replyText) {
        setMascotState("responding");
        const agentMsg: Message = {
          id: String(Date.now() + 1),
          sender: "agent",
          text: replyText,
          timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
        };
        setMessages((prev) => [...prev, agentMsg]);
        setMascotState("success");
        setTimeout(() => setMascotState("idle"), 1500);
      }
    } catch (err) {
      setMascotState("alert");
      setTimeout(() => setMascotState("idle"), 2000);
    }
  };

  return (
    <div
      style={{
        position: "fixed",
        bottom: "24px",
        right: "24px",
        zIndex: 9999,
        fontFamily: TYPOGRAPHY.fontFamily,
      }}
    >
      {/* Floating Trigger Button */}
      {!isOpen && (
        <button
          onClick={() => setIsOpen(true)}
          style={{
            width: "60px",
            height: "60px",
            borderRadius: RADIUS.full,
            backgroundColor: COLORS.primary,
            border: "none",
            boxShadow: "0 8px 24px rgba(0, 104, 255, 0.35)",
            cursor: "pointer",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            transition: "transform 0.2s cubic-bezier(0.34, 1.56, 0.64, 1)",
          }}
          onMouseEnter={(e) => (e.currentTarget.style.transform = "scale(1.08)")}
          onMouseLeave={(e) => (e.currentTarget.style.transform = "scale(1)")}
        >
          <MascotAvatar state="idle" size={38} color="#FFFFFF" />
        </button>
      )}

      {/* Chat Window */}
      {isOpen && (
        <div
          style={{
            width: "380px",
            maxWidth: "calc(100vw - 32px)",
            height: "560px",
            maxHeight: "calc(100vh - 48px)",
            backgroundColor: COLORS.bgLight,
            borderRadius: RADIUS.lg,
            boxShadow: "0 12px 40px rgba(0, 0, 0, 0.16)",
            display: "flex",
            flexDirection: "column",
            overflow: "hidden",
            border: `1px solid ${COLORS.borderLight}`,
          }}
        >
          {/* Header */}
          <div
            style={{
              padding: "14px 18px",
              backgroundColor: COLORS.primary,
              color: "#FFFFFF",
              display: "flex",
              alignItems: "center",
              justifyContent: "space-between",
            }}
          >
            <div style={{ display: "flex", alignItems: "center", gap: "12px" }}>
              <div
                style={{
                  width: "40px",
                  height: "40px",
                  borderRadius: RADIUS.full,
                  backgroundColor: "rgba(255, 255, 255, 0.15)",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                }}
              >
                <MascotAvatar state={mascotState} size={28} color="#FFFFFF" />
              </div>
              <div>
                <div style={{ fontWeight: 700, fontSize: "15px", lineHeight: 1.2 }}>
                  {agentName}
                </div>
                <div
                  style={{
                    fontSize: "12px",
                    opacity: 0.85,
                    display: "flex",
                    alignItems: "center",
                    gap: "5px",
                    marginTop: "2px",
                  }}
                >
                  <span
                    style={{
                      width: "7px",
                      height: "7px",
                      borderRadius: "50%",
                      backgroundColor: "#4ADE80",
                      display: "inline-block",
                    }}
                  />
                  {mascotState === "thinking"
                    ? "Đang suy nghĩ..."
                    : mascotState === "responding"
                    ? "Đang trả lời..."
                    : "Sẵn sàng hỗ trợ"}
                </div>
              </div>
            </div>
            <button
              onClick={() => setIsOpen(false)}
              style={{
                background: "transparent",
                border: "none",
                color: "#FFFFFF",
                fontSize: "20px",
                cursor: "pointer",
                padding: "4px",
                lineHeight: 1,
              }}
            >
              ✕
            </button>
          </div>

          {/* Messages Body */}
          <div
            style={{
              flex: 1,
              padding: "16px",
              overflowY: "auto",
              backgroundColor: COLORS.surfaceLight,
              display: "flex",
              flexDirection: "column",
              gap: "12px",
            }}
          >
            {messages.map((m) => (
              <div
                key={m.id}
                style={{
                  alignSelf: m.sender === "user" ? "flex-end" : "flex-start",
                  maxWidth: "82%",
                }}
              >
                <div
                  style={{
                    padding: "10px 14px",
                    borderRadius: RADIUS.lg,
                    borderBottomRightRadius: m.sender === "user" ? "4px" : RADIUS.lg,
                    borderBottomLeftRadius: m.sender === "agent" ? "4px" : RADIUS.lg,
                    backgroundColor: m.sender === "user" ? COLORS.primary : COLORS.bgLight,
                    color: m.sender === "user" ? "#FFFFFF" : COLORS.textOnLight,
                    fontSize: TYPOGRAPHY.body.fontSize,
                    lineHeight: TYPOGRAPHY.body.lineHeight,
                    boxShadow: m.sender === "agent" ? "0 2px 8px rgba(0,0,0,0.04)" : "none",
                    border: m.sender === "agent" ? `1px solid ${COLORS.borderLight}` : "none",
                    whiteSpace: "pre-wrap",
                  }}
                >
                  {m.text}
                </div>
                <div
                  style={{
                    fontSize: "10px",
                    color: "#94A3B8",
                    marginTop: "4px",
                    textAlign: m.sender === "user" ? "right" : "left",
                    padding: "0 4px",
                  }}
                >
                  {m.timestamp}
                </div>
              </div>
            ))}
            {mascotState === "thinking" && (
              <div
                style={{
                  alignSelf: "flex-start",
                  padding: "8px 14px",
                  borderRadius: RADIUS.lg,
                  backgroundColor: COLORS.primaryLight,
                  color: COLORS.primaryDark,
                  fontSize: "12px",
                  display: "flex",
                  alignItems: "center",
                  gap: "6px",
                }}
              >
                <MascotAvatar state="thinking" size={18} color={COLORS.primary} />
                <span>OPA đang soạn câu trả lời...</span>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          {/* Input Bar */}
          <form
            onSubmit={handleSend}
            style={{
              padding: "12px 14px",
              backgroundColor: COLORS.bgLight,
              borderTop: `1px solid ${COLORS.borderLight}`,
              display: "flex",
              alignItems: "center",
              gap: "8px",
            }}
          >
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Nhắn tin với OPA..."
              style={{
                flex: 1,
                padding: "10px 14px",
                borderRadius: RADIUS.md,
                border: `1px solid ${COLORS.borderLight}`,
                outline: "none",
                fontSize: "14px",
                fontFamily: TYPOGRAPHY.fontFamily,
              }}
              onFocus={(e) => (e.target.style.borderColor = COLORS.primary)}
              onBlur={(e) => (e.target.style.borderColor = COLORS.borderLight)}
            />
            <button
              type="submit"
              disabled={!input.trim() || mascotState === "thinking"}
              style={{
                backgroundColor: input.trim() && mascotState !== "thinking" ? COLORS.primary : "#CBD5E1",
                color: "#FFFFFF",
                border: "none",
                borderRadius: RADIUS.md,
                padding: "10px 16px",
                fontWeight: 600,
                fontSize: "14px",
                cursor: input.trim() && mascotState !== "thinking" ? "pointer" : "not-allowed",
                transition: "background-color 0.2s",
              }}
            >
              Gửi
            </button>
          </form>
        </div>
      )}
    </div>
  );
};

export default ChatWidget;
