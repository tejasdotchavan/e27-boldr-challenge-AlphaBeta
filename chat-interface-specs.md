# Chat Interface — Specs
### GitHub Pages · Competition Demo Build

---

## 1. Purpose & Context

A lightweight, single-page interface hosted on GitHub Pages. Intended for competition judges to experience BOLDR's AI-powered customer support flow firsthand. The page shows **two side-by-side chat windows**: a **Customer Chat** (what the customer sees) and an **Agent View** (what the human agent sees in Telegram, routed by n8n). The interface connects to an n8n workflow via webhook and demonstrates two key behaviours: an AI **draft-approval** flow where a knowledge-base answer is reviewed by a human agent before it reaches the customer, and an asynchronous **CS escalation** flow where the answer arrives after a human agent updates a record.

---

## 2. Functional Requirements

### 2.1 Core chat

- User types a message and submits (Enter key or Send button).
- Message is POSTed to a configurable n8n webhook URL.
- Response is displayed as a bot reply in the chat window.
- Chat history persists in-memory for the duration of the session (no localStorage).

### 2.2 KB hit — draft approval flow

- n8n finds an answer in the knowledge base and generates a **draft reply**.
- The HTTP response returns a `draft` payload (`ticket_id`, `customer`, `question`, `draft_reply`) — **not** a customer-facing answer.
- The Customer Chat shows a "waiting for an agent to approve the reply" indicator and the input bar is disabled.
- The draft is mirrored into the **Agent View** panel as a "Draft ready for approval" message with `/approve` and `/reject` commands.
- On **approve** — the agent panel calls the approve endpoint; the draft reply is delivered to the Customer Chat as a bot message, an acknowledgement appears in the Agent View, and the input bar re-enables (the session continues).
- On **reject** — the agent panel calls the reject endpoint; the draft is logged to the CS queue, the customer is told a CS agent will follow up, an "Unresolved ticket" appears in the Agent View, and the flow falls through to the async CS escalation polling (section 2.3).

### 2.3 KB miss — async CS escalation (two-message flow)

**Step 1 — Instant acknowledgement**
- n8n does not find an answer in the KB.
- HTTP response returns: an `escalation` reply (e.g. "Great question — a customer success agent will follow up shortly."), a unique `session_id`, and ticket fields (`ticket_id`, `customer`, `question`).
- Customer Chat displays the reply and stores the `session_id`.
- An "Unresolved ticket" notification is mirrored into the **Agent View** panel.
- UI enters a **polling state**: a subtle "waiting for CS..." indicator appears under the last bot message.

**Step 2 — CS updates Google Sheets**
- CS agent opens Google Sheets, locates the row by `session_id`, fills in the answer, and sets status to `resolved`.

**Step 3 — Answer delivered**
- Chat UI polls a second n8n endpoint every 5 seconds with the `session_id`.
- When the polling endpoint returns a resolved answer, the UI stops polling and displays the answer as a new bot message (visually distinct — labelled "CS Agent" above the bubble).
- The "waiting for CS..." indicator disappears.

**Step 4 — Session concluded**
- Immediately after the CS reply is rendered, a **session-end notice** appears below it — a centred, muted text block reading something like: "This session is now complete. This demo covers a limited scope of functionality — refresh to start a new conversation."
- A **"Start New Session" button** appears below the notice. Clicking it reloads the page (`window.location.reload()`).
- The input bar and send button are **disabled and visually dimmed** — no further messages can be sent in this session.
- The input placeholder text changes to: "Session ended — refresh to continue."

### 2.4 Error handling

- If the webhook returns a non-200 status, show a non-blocking error message: "Something went wrong — please try again."
- If polling does not return an answer within 5 minutes, the waiting indicator is replaced with: "Our team has your question and will be in touch via email."
- Network timeout on initial send: 15 seconds before showing error.

---

## 3. UI / UX Design

### 3.1 Layout

- Full-height single page, three columns inside a centred shell (max-width ~1560px).
- **Left panel** — BOLDR wordmark + tagline, competition/team info, resource links, demo note.
- **Customer Chat column** — the conversation the customer drives; input bar pinned to the bottom.
- **Agent View column** — read-only mirror of what the human agent sees in Telegram (drafts to approve/reject, unresolved tickets, acknowledgements). No input bar.
- Below 900px the three columns stack vertically.

### 3.1a Agent View panel

- Messages render as structured cards (not chat bubbles), mirroring the Telegram bot messages.
- **Draft card** — "✅ Draft ready for approval" header, `ID` / `Customer` / `Question` fields, a boxed draft reply, and `/approve{id}` `/reject{id}` command links, followed by an "Sent automatically with n8n" footer. Commands dim once actioned.
- **Unresolved ticket card** — "🚨 Unresolved ticket" header, `ID` / `Customer` / `Question` fields, and a note to fill `cs_answer` in the Google Sheet.
- **Acknowledgement card** — confirmation text after an approve/reject, with the n8n footer.
- `/approve` and `/reject` are command-styled links that trigger a background `fetch` to the n8n approve/reject endpoints and update both panels in place — no page navigation.

### 3.2 Visual style

**Palette — strict black and white**
- Background: `#ffffff`
- Primary text: `#0a0a0a`
- Muted text / labels: `#888888`
- Borders: `#e5e5e5`
- User bubble background: `#0a0a0a` (black), text: `#ffffff`
- Bot bubble background: `#f5f5f5`, text: `#0a0a0a`
- CS agent bubble background: `#efefef` with a left-side `2px` black border to visually distinguish it
- Input bar background: `#ffffff`, border: `1px solid #e5e5e5`
- Send button: black background, white label — inverts to white background + black border on hover
- Session-end button ("Start New Session"): outlined style — white background, `1px solid #0a0a0a`, black text; subtle fill on hover

**Typography — recommended font: Geist**
- Use [Geist](https://vercel.com/font) (by Vercel) via `@import` from `https://fonts.googleapis.com/css2?family=Geist:wght@400;500;600&display=swap` or self-host.
- Geist is purpose-built for interfaces: clean, geometric, excellent legibility at small sizes, and projects a modern/tech credibility well-suited to a product demo.
- Fallback stack: `'Geist', 'Inter', system-ui, sans-serif`
- Type scale: body `15px`, bubble sender label `11px` uppercase tracking, timestamps `12px`, session-end notice `13px`, button `14px medium`

**Rounding and borders**
- Chat bubbles: `border-radius: 18px` with the corner closest to the sender flattened (user = bottom-right `4px`, bot = bottom-left `4px`) — standard chat convention.
- CS agent bubble: same rounding but with a `2px solid #0a0a0a` left border instead of a colour-fill distinction.
- Input field: `border-radius: 12px`, `1px solid #e5e5e5`, focus state `1px solid #0a0a0a`.
- Send button: `border-radius: 10px`.
- Session-end "Start New Session" button: `border-radius: 10px`, full-width or auto-width centred.
- Outer chat container: `border-radius: 16px` with a `1px solid #e5e5e5` border (on desktop — borderless on mobile).

**Spacing**
- Bubble max-width: 75% of chat column.
- Gap between consecutive same-sender bubbles: `4px`. Gap on sender change: `16px`.
- Padding inside bubbles: `12px 16px`.

### 3.3 Chat bubbles

| Element | Style |
|---|---|
| User messages | Right-aligned, black background (`#0a0a0a`), white text |
| Bot messages | Left-aligned, `#f5f5f5` background, dark text |
| CS agent reply | Left-aligned, `#efefef` background + `2px` black left border + small "CS Agent" label above in `11px` uppercase muted text |
| Timestamps | `12px`, `#888888`, below each bubble |
| Typing indicator | Three-dot animation, black dots, shown while awaiting response |

### 3.4 Waiting / polling state

- A small pulsing dot (black, `8px`) appears inline below the first escalation reply.
- Text beside it: "Waiting for your CS agent..." in `#888888`, `13px`.
- Entire indicator disappears when the CS reply arrives.

### 3.5 Input bar

- Single-line text input (expands to 3 lines max before scrolling).
- `1px solid #e5e5e5` border, `border-radius: 12px`.
- Send button to the right, black, `border-radius: 10px`.
- Both disabled and visually dimmed (`opacity: 0.4`, `cursor: not-allowed`) when session is concluded or while a response is pending.
- Placeholder changes to "Session ended — refresh to continue." once session concludes.

### 3.6 Session-end state

- After the CS reply renders, a horizontal divider (`1px solid #e5e5e5`) appears below the final bubble.
- Below the divider: centred muted text — "This session is complete. This demo covers a limited scope of BOLDR's functionality."
- Below that: a centred **"Start New Session"** button (outlined, black border, white fill, `border-radius: 10px`).
- Input bar dims to indicate it is no longer active.

### 3.7 General style rules

- No colours other than black, white, and greys.
- No shadows — borders only for depth.
- No animations beyond: typing dots, the pulsing waiting dot, and a simple fade-in for new messages (`opacity 0 → 1` over `200ms`).
- Mobile-responsive: on screens below `640px`, remove the container border and border-radius, let it go full-bleed.

---

## 4. Technical / Integration Specs

### 4.1 Hosting

- Pure static HTML/CSS/JS — no build step, no framework dependencies.
- Hosted on GitHub Pages (single `index.html` file).
- Webhook, polling, approve and reject URLs stored as constants at the top of the JS file for easy swap-out (`N8N_WEBHOOK_URL`, `N8N_POLL_URL`, `N8N_APPROVE_URL`, `N8N_REJECT_URL`).

### 4.2 n8n Webhook — initial message

```
POST {N8N_WEBHOOK_URL}
Content-Type: application/json

{
  "message": "string",
  "session_id": "string"   // generated client-side: timestamp + 4-char random suffix
}
```

**Response — KB hit (draft for approval):**
```json
{
  "type": "draft",
  "ticket_id": "string",     // short ID shown to the agent, e.g. "47OFJN"
  "customer": "string",      // customer name/handle
  "question": "string",      // the customer's question
  "draft_reply": "string",   // AI-generated reply pending agent approval
  "session_id": "string"     // used by the approve/reject endpoints
}
```

> A `{ "type": "answer", "reply": "string" }` response is still accepted as a direct
> reply with no approval gate (backwards-compatible / optional fast path).

**Response — KB miss (escalation):**
```json
{
  "type": "escalation",
  "reply": "string",        // the "CS will get back to you" message
  "session_id": "string",   // echoed back or reassigned by n8n
  "ticket_id": "string",    // ID shown in the Agent View (ISO timestamp is fine)
  "customer": "string",
  "question": "string"
}
```

### 4.3 n8n Approve / Reject Endpoints

Triggered when the agent clicks `/approve{id}` or `/reject{id}` in the Agent View.

```
GET {N8N_APPROVE_URL}?id={ticket_id}&session_id={session_id}
GET {N8N_REJECT_URL}?id={ticket_id}&session_id={session_id}
```

- **Approve** — n8n marks the ticket sent. The response may optionally return
  `{ "reply": "string" }` to override the delivered text; otherwise the `draft_reply`
  already held by the UI is used.
- **Reject** — n8n logs the ticket to the CS queue keyed by `session_id`, so the
  customer's subsequent poll (section 4.4) resolves once CS answers.

### 4.4 n8n Polling Endpoint

```
GET {N8N_POLL_URL}?session_id={session_id}
```

**Response — still pending:**
```json
{ "status": "pending" }
```

**Response — resolved:**
```json
{
  "status": "resolved",
  "reply": "string"
}
```

### 4.5 Google Sheets schema

| Column | Value |
|---|---|
| `session_id` | Unique ID from the chat session |
| `timestamp` | ISO timestamp of the question |
| `question` | The user's original message |
| `answer` | Filled in by CS agent |
| `status` | `pending` / `resolved` |

### 4.6 Polling behaviour

- Polling interval: 5 seconds.
- Max polling duration: 5 minutes (60 attempts), then show fallback message and stop.
- Polling stops immediately on receiving `status: "resolved"`.

---

## 5. Competition / Judge Constraints

- **No login required** — judges access the page directly via URL, no account creation.
- **No data persistence** — chat history lives only in-memory for the session; refreshing resets the conversation. This is intentional to keep the demo clean.
- **Guided demo flow** — consider adding a subtle placeholder in the input field suggesting a sample question (e.g. "Ask me about BOLDR's features…") to guide judges toward a relevant question.
- **Fallback for offline n8n** — if the webhook is unreachable, display a clear but polite message rather than a broken experience.
- **Performance** — page must load fast on a cold visit; no heavy assets, no third-party JS beyond a font.
- **Mobile-ready** — judges at the event may view on a phone.
- **Demo mode toggle (optional)** — a hidden URL param `?demo=true` could auto-fill a scripted conversation to show the full two-message CS flow without needing a live n8n connection.

---

## 6. Out of Scope (for this build)

- Multi-session or conversation history persistence.
- Authentication or rate limiting.
- File/image uploads.
- Voice input.
- Full Telegram integration in the UI (handled separately in n8n).
