# Boldr Intelligence Engine — System Architecture

## Full System Flow

```mermaid
flowchart TD
    Customer([Customer on Telegram]) -->|sends message| TG_TRIGGER[Telegram Trigger]

    subgraph WF1["WF1 — Intelligence Engine"]
        TG_TRIGGER --> CMD_CHECK{Is it an\napproval command?}
        CMD_CHECK -->|"/approve or /reject"| PARSE_CMD[Parse Command]
        CMD_CHECK -->|normal message| LLM[LLM — FPT AI Factory / Qwen\nClassify + KB match + Draft reply\nPersona + Marketing signal]
        LLM --> PARSE[Parse Response JSON]
        PARSE --> CONF_CHECK{KB match\n+ confidence?}
    end

    subgraph WF1_HIGH["High Confidence Branch"]
        CONF_CHECK -->|yes| GEN_ID[Generate Approval ID]
        GEN_ID --> APPEND_QUEUE[Append to cs_queue\nstatus: pending_approval]
        APPEND_QUEUE --> NOTIFY_CS[Telegram → CS Agent\nDraft + /approve_ID + /reject_ID]
    end

    subgraph WF1_LOW["Low Confidence Branch"]
        CONF_CHECK -->|no| FLAG[Flag Knowledge Gap]
        FLAG --> NOTIFY_CS2[Telegram → CS Agent\nUnresolved ticket alert]
        NOTIFY_CS2 --> APPEND_CS[Append to cs_queue\nstatus: pending]
    end

    subgraph WF1_APPROVAL["Approval Handler (inside WF1)"]
        PARSE_CMD --> GET_ROW[Google Sheets\nGet row by approval_id]
        GET_ROW --> APPROVE_CHECK{approve\nor reject?}
        APPROVE_CHECK -->|approve| SEND_CUSTOMER[Telegram → Customer\nsend draft_reply]
        SEND_CUSTOMER --> UPDATE_ANSWERED[Update cs_queue\nstatus: answered]
        APPROVE_CHECK -->|reject| UPDATE_PENDING[Update cs_queue\nstatus: pending]
        UPDATE_PENDING --> CS_FILLS[CS fills in cs_answer\nin Google Sheet]
    end

    subgraph WF2["WF2 — CS Reply Processor (every 5 min)"]
        POLL[Read cs_queue\nwhere status = pending] --> HAS_ANSWER{Has cs_answer?}
        HAS_ANSWER -->|yes| REDRAFT[LLM — Redraft reply\nin brand voice]
        REDRAFT --> SEND_CUSTOMER2[Telegram → Customer]
        SEND_CUSTOMER2 --> UPDATE_ANSWERED2[Update cs_queue\nstatus: answered]
        UPDATE_ANSWERED2 --> LOG_KB[Append to kb_log]
        HAS_ANSWER -->|no| WAIT[Skip — wait for next poll]
    end

    subgraph WF3["WF3 — Weekly Theme Clustering (Sunday 11pm)"]
        READ_WEEK[Read cs_queue\nlast 7 days] --> FORMAT[Format questions\nby persona + classification]
        FORMAT --> CLUSTER[LLM — Identify\ntop 5 themes + pain points\n+ marketing signals + KB gaps]
        CLUSTER --> PARSE_THEMES[Parse JSON output]
        PARSE_THEMES --> SAVE_THEMES[Append to weekly_themes]
    end

    subgraph WF4["WF4 — Monthly Marketing Brief (1st of month)"]
        READ_MONTH[Read weekly_themes\nlast 4 weeks] --> FORMAT2[Format weekly summaries]
        FORMAT2 --> BRIEF[LLM — Generate\nmarketing brief]
        BRIEF --> SAVE_BRIEF[Append to marketing_briefs]
        SAVE_BRIEF --> SEND_BRIEF[Telegram → Team\nmonthly brief]
    end

    subgraph SHEETS["Google Sheets — Data Layer"]
        CS_QUEUE[(cs_queue)]
        KB_LOG[(kb_log)]
        WEEKLY[(weekly_themes)]
        BRIEFS[(marketing_briefs)]
    end

    APPEND_CS --> CS_QUEUE
    APPEND_QUEUE --> CS_QUEUE
    CS_FILLS --> CS_QUEUE
    UPDATE_ANSWERED --> CS_QUEUE
    UPDATE_PENDING --> CS_QUEUE
    CS_QUEUE --> POLL
    UPDATE_ANSWERED2 --> CS_QUEUE
    LOG_KB --> KB_LOG
    CS_QUEUE --> READ_WEEK
    SAVE_THEMES --> WEEKLY
    WEEKLY --> READ_MONTH
    SAVE_BRIEF --> BRIEFS
```

---

## Data Flow per Ticket

```mermaid
sequenceDiagram
    participant C as Customer
    participant TG as Telegram Bot
    participant WF1 as Intelligence Engine
    participant LLM as LLM (FPT/Qwen)
    participant CS as CS Agent
    participant SH as Google Sheets

    C->>TG: Sends question
    TG->>WF1: Trigger
    WF1->>LLM: Full KB + question
    LLM-->>WF1: JSON (classification, persona, kb_match, draft_reply, marketing_signal)

    alt High confidence
        WF1->>SH: Append cs_queue (pending_approval)
        WF1->>CS: Telegram — draft + /approve_ID
        CS->>TG: /approve_ID
        TG->>WF1: Approval command
        WF1->>SH: Update status = answered
        WF1->>C: Send draft reply
    else Low confidence
        WF1->>SH: Append cs_queue (pending)
        WF1->>CS: Telegram — unresolved ticket alert
        CS->>SH: Fill in cs_answer manually
        Note over SH,CS: WF2 polls every 5 min
        WF1->>LLM: Redraft cs_answer in brand voice
        LLM-->>WF1: Polished reply
        WF1->>C: Send redrafted reply
        WF1->>SH: Log to kb_log
    end
```

---

## LLM Output Schema

Every customer message produces a single structured JSON object:

```json
{
  "classification": "engraving | servicing | product | orders | cs_operations | out_of_scope",
  "buyer_persona": "Gift Buyer | Health-Conscious Buyer | Enthusiast | Active Buyer | Sustainability Advocate | General",
  "kb_match": "yes | no",
  "confidence_score": 0.0,
  "draft_reply": "Brand-voiced reply to the customer",
  "summary": "One-line internal summary of the question",
  "marketing_signal": "Potential marketing insight from this question",
  "marketing_flag": "yes | no"
}
```

---

## Google Sheet Structure

| Tab | Columns |
|---|---|
| `cs_queue` | `id, chat_id, customer_name, question, persona, draft_reply, cs_answer, status, timestamp` |
| `kb_log` | `id, question, cs_answer, drafted_reply, timestamp` |
| `weekly_themes` | `week, theme_1–5, top_pain_point, kb_gaps, marketing_signals, total_tickets` |
| `marketing_briefs` | `month, brief_text, generated_at` |
