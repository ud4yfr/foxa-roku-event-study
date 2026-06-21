# Pre-Flight Results: FOXA/ROKU Event Study

**Run date:** 2026-06-19  
**Event:** Fox Corporation (FOXA) acquisition of Roku, Inc. (ROKU) announced June 14–15, 2026  
**Source:** SEC EDGAR submissions API + SGML filing headers (authoritative timestamps)

---

## Check 1: Exact Disclosure Timing and Day Zero Determination

### How EDGAR timestamps work
EDGAR records two timestamps for every filing:
- `filingDate`: calendar date only (no time), what most data vendors show
- `acceptanceDateTime` (in submissions JSON) / `<ACCEPTANCE-DATETIME>` (in SGML header): the exact second the filing was accepted by EDGAR's system, in Eastern Time. This is the authoritative timestamp used in securities litigation.

NYSE/Nasdaq trading hours are 9:30 AM – 4:00 PM ET. Any filing accepted before 9:30 AM ET is effectively pre-market. After 4:00 PM ET is after-hours (day zero shifts to the next trading day).

---

### FOXA — 8-K filings on June 15, 2026

Two separate 8-K filings landed the same date:

| Accession Number         | Items      | SGML `<ACCEPTANCE-DATETIME>` | acceptanceDateTime (JSON)       | Subject                              |
|--------------------------|------------|------------------------------|---------------------------------|--------------------------------------|
| 0001193125-26-270285     | 7.01, 9.01 | `20260615071308` = **7:13 AM ET** | 2026-06-15T11:13:08.000Z (UTC) | Joint press release + investor call  |
| 0001193125-26-271101     | 1.01, 9.01 | `20260615161516` = **4:15 PM ET** | 2026-06-15T20:15:16.000Z (UTC) | Entry into Material Definitive Agreement (merger agreement) |

**Note on UTC vs ET:** The JSON `acceptanceDateTime` field is UTC. Converting:
- 11:13 UTC = 7:13 AM ET (pre-market)
- 20:15 UTC = 4:15 PM ET (just after close)

**Primary acquisition filing for FOXA:**
- Accession: `0001193125-26-270285` (Item 7.01 = Regulation FD, the joint press release)
- SGML acceptance: `20260615071308` → **June 15, 2026 at 7:13 AM Eastern Time**
- This is PRE-MARKET (market opens at 9:30 AM ET)

The Item 1.01 filing (the formal merger agreement document) came at 4:15 PM ET — after the close — but the material information (deal terms, $22B price, cash-and-stock structure) was disclosed in the 7:13 AM press release. Market participants had the full deal details before the open on June 15.

**FOXA Day Zero = June 15, 2026**

---

### ROKU — 8-K filing on June 15, 2026

| Accession Number         | Items              | SGML `<ACCEPTANCE-DATETIME>` | Subject                              |
|--------------------------|--------------------|------------------------------|--------------------------------------|
| 0001140361-26-025115     | 1.01, 8.01, 9.01   | `20260615074746` = **7:47 AM ET** | Entry into Merger Agreement + Other Events |

- SGML acceptance: `20260615074746` → **June 15, 2026 at 7:47 AM Eastern Time**
- This is PRE-MARKET

The ROKU 8-K (Item 1.01 = Entry into a Material Definitive Agreement) confirms Roku entered the merger agreement on June 14, 2026. The filing was accepted by EDGAR at 7:47 AM ET on June 15, well before market open.

**ROKU Day Zero = June 15, 2026**

---

### Day Zero Conclusion

**Both tickers: Day Zero = June 15, 2026.**

Both the FOXA press-release 8-K (7:13 AM ET) and the ROKU merger-agreement 8-K (7:47 AM ET) were accepted by EDGAR pre-market on June 15. The market had full deal information before the 9:30 AM open. There is no ambiguity about which trading day is day zero.

---

## Check 2: Confound Check

### Methodology
Scanned all SEC filings for FOXA and ROKU from May 15 through June 22, 2026, flagging any filing that is NOT the acquisition announcement and that might independently move the stock price.

---

### FOXA — Confounding filings

#### FOXA 8-K filed June 11, 2026
- Accession: `0001628280-26-042499`
- Item **5.02**: Departure of Directors/Officers; Appointment; Compensatory Arrangements
- Accepted: `20260611160247` = 4:02 PM ET (after-hours June 11)
- **Content:** Compensation Committee extended CEO Lachlan Murdoch's employment through June 30, 2030, raised his target bonus to $9M/year and equity award target to $20M/year. Other executive comp adjustments approved.
- **Assessment:** This is a CONFOUND RISK. CEO contract extensions and compensation increases are firm-specific news unrelated to the Roku deal. Filed after-hours June 11, so it would show up in trading on June 12. This is 3 trading days before our event (June 15). It falls inside a [-5, +5] event window if we use that, but outside a [-1, +1] window. **Recommendation:** Use a narrow event window ([-1, +1] or [-2, +2]) to minimize the risk that the June 11 comp news bleeds into the measured CAR. If using a wide window ([-5, +5]), flag this filing explicitly as a potential confound and note it predates the deal announcement.

#### FOXA — 425 filings (June 15–16, 2026)
Multiple Form 425 filings ("written communications pursuant to Rule 425 under the Securities Act"). These are merger-related communications (press releases, investor presentations, analyst calls), all filed on June 15 simultaneously with the acquisition 8-Ks. They are part of the acquisition announcement, not independent confounds.

#### FOXA — SCHEDULE 13D/A filed June 16, 2026
- Accession: `0001193125-26-272917`
- This is a Schedule 13D/A amendment (beneficial ownership disclosure). Filed June 16, the day after the announcement. Likely a Murdoch family / News Corp entity amending their ownership position in connection with the merger. This is a downstream consequence of the deal, not an independent confound.

**FOXA confound verdict:** One pre-event firm-specific filing (June 11 CEO comp extension) that falls within a wide event window but NOT within a narrow [-1, +1] window. No earnings release, no guidance, no unrelated litigation or restructuring news in the window.

---

### ROKU — Confounding filings

#### ROKU 8-K filed June 17, 2026
- Accession: `0001628280-26-043866`
- Item **5.07**: Submission of Matters to a Vote of Security Holders
- Accepted: `20260617160240` = 4:02 PM ET (after-hours June 17)
- **Content:** Results of Roku's annual meeting of stockholders held June 11, 2026. Three proposals voted on (director elections, say-on-pay, auditor ratification — standard annual meeting items).
- **Assessment:** The annual meeting was held June 11 (pre-deal), results reported June 17. Routine corporate governance, not a price-moving event. Low confound risk. However, if the vote included anything unusual (e.g., a significant say-on-pay failure) it could color sentiment in the event window. The filing indicates it was three standard proposals. **Treat as immaterial.**

#### ROKU 8-K filed June 18, 2026
- Accession: `0001628280-26-044373`
- Item **8.01**: Other Events
- Accepted: `20260618164203` = 4:42 PM ET (after-hours June 18)
- **Content:** Roku filed an 8-K to re-present financial information from its 2025 10-K and Q1 2026 10-Q following a change in segment reporting structure. This is an accounting/presentation reclassification, not new business news.
- **Assessment:** Filed after-hours June 18. Falls inside a [+0, +3] window. Contains no new financial results — it re-states historical figures under a new segment structure. **Treat as immaterial** for the event study, but worth noting in the writeup.

#### ROKU — 425 filings (June 15–16)
Same as FOXA: merger-related communications, part of the acquisition announcement.

#### ROKU — Form 4 (insider transaction, June 16)
- One Form 4 filed June 16 (reporting date June 15). Insider transaction in connection with the deal (likely a stock award or option modification triggered by the merger agreement). Not an independent confound.

#### ROKU — Form 144 and Form 4 filings (June 12 and earlier)
Multiple routine Form 144 (intent to sell restricted stock) and Form 4 (insider transaction reports) filed in the weeks before the announcement. All pre-date the deal. Routine and not price-moving.

**ROKU confound verdict:** No material confounds. The June 17 annual meeting results and June 18 segment re-statement are both immaterial. No earnings release, no guidance update, no unrelated news.

---

## Summary

| Check | FOXA | ROKU |
|-------|------|------|
| Acquisition 8-K filed | June 15, 7:13 AM ET (pre-market) | June 15, 7:47 AM ET (pre-market) |
| Day Zero | **June 15, 2026** | **June 15, 2026** |
| Pre-event confounds | June 11 CEO comp extension (5.02) — material but pre-event and outside [-1,+1] window | Annual meeting held June 11, results filed June 17 — immaterial |
| Post-event confounds | 13D/A June 16 (deal-related) | Segment re-statement June 18 (accounting, immaterial) |
| **Proceed?** | **Yes — use narrow event window** | **Yes — clean** |

**Final day-zero determination: June 15, 2026 for both FOXA and ROKU.**  
The one flag worth carrying into the analysis is the FOXA June 11 CEO comp 8-K (items 5.02). It is specific to Fox, could affect FOXA's price on June 12, and falls inside a [-5, +5] window. This is the reason we prefer a narrow event window ([-1, +1]) for the main result, with [-3, +3] as a robustness check.

---

## Raw EDGAR Accession Numbers (for audit trail)

| Ticker | Filing Role | Accession Number | Filing Date | Acceptance (ET) | Items |
|--------|-------------|-----------------|-------------|-----------------|-------|
| FOXA | Acquisition press release (primary) | 0001193125-26-270285 | 2026-06-15 | 7:13 AM | 7.01, 9.01 |
| FOXA | Merger agreement (supplemental) | 0001193125-26-271101 | 2026-06-15 | 4:15 PM | 1.01, 9.01 |
| FOXA | CEO comp extension (confound) | 0001628280-26-042499 | 2026-06-11 | 4:02 PM | 5.02, 9.01 |
| ROKU | Merger agreement | 0001140361-26-025115 | 2026-06-15 | 7:47 AM | 1.01, 8.01, 9.01 |
| ROKU | Annual meeting results (immaterial) | 0001628280-26-043866 | 2026-06-17 | 4:02 PM | 5.07 |
| ROKU | Segment re-statement (immaterial) | 0001628280-26-044373 | 2026-06-18 | 4:42 PM | 8.01 |
