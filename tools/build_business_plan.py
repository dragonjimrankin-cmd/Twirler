#!/usr/bin/env python3
"""
Twirler Pictures — business plan PDF generator.

Pure ReportLab, no system dependencies. A4 portrait, editorial layout:
ink ground, cream type, gold rules, oxblood accents.

    pip install reportlab
    python tools/build_business_plan.py

Writes: business-plan/twirler-business_plan1.pdf
"""

import os

from reportlab.lib.colors import HexColor
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.pdfgen import canvas

# ----------------------------------------------------------------------------
# palette + geometry
# ----------------------------------------------------------------------------
INK       = HexColor("#0A0A0C")
PANEL     = HexColor("#15151A")
PANEL_2   = HexColor("#1B1B21")
CREAM     = HexColor("#F5EFE6")
CREAM_DIM = HexColor("#CFC6B8")
MUTED     = HexColor("#8F887E")
GOLD      = HexColor("#C8A35A")
GOLD_DARK = HexColor("#8A6E33")
OXBLOOD   = HexColor("#8E1C2B")
ROSE      = HexColor("#D98B93")
SLATE     = HexColor("#3A3A44")
LINE      = HexColor("#2A2A31")

W, H = A4
M = 54.0
CW = W - 2 * M            # 487.3
TOP = H - M               # 787.9
BOT = 46.0

F, FB, FI, FBI = "Helvetica", "Helvetica-Bold", "Helvetica-Oblique", "Helvetica-BoldOblique"

OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                   "business-plan", "twirler-business_plan1.pdf")

PAGE_LABEL = "TWIRLER PICTURES · BUSINESS PLAN 2027–2029"


# ----------------------------------------------------------------------------
# primitives
# ----------------------------------------------------------------------------
def tracked(c, x, y, text, font=F, size=7.0, color=GOLD, tracking=1.9):
    c.setFont(font, size)
    c.setFillColor(color)
    for ch in text:
        c.drawString(x, y, ch)
        x += stringWidth(ch, font, size) + tracking
    return x


def wrap(text, font, size, maxw):
    lines = []
    for block in text.split("\n"):
        words, cur = block.split(), ""
        if not words:
            lines.append("")
            continue
        for w_ in words:
            t = (cur + " " + w_).strip()
            if stringWidth(t, font, size) <= maxw or not cur:
                cur = t
            else:
                lines.append(cur)
                cur = w_
        if cur:
            lines.append(cur)
    return lines


def para(c, x, y, maxw, text, font=F, size=9.4, leading=14.0,
         color=CREAM_DIM, align="left"):
    for block in text.split("\n"):
        if block.strip() == "":
            y -= leading * 0.55
            continue
        c.setFont(font, size)
        c.setFillColor(color)
        for ln in wrap(block, font, size, maxw):
            if align == "center":
                c.drawString(x + (maxw - stringWidth(ln, font, size)) / 2, y, ln)
            elif align == "right":
                c.drawString(x + maxw - stringWidth(ln, font, size), y, ln)
            else:
                c.drawString(x, y, ln)
            y -= leading
    return y


def h1(c, x, y, text, size=30, color=CREAM, maxw=None, leading=None):
    leading = leading or size * 1.12
    c.setFont(FB, size)
    c.setFillColor(color)
    for ln in wrap(text, FB, size, maxw or CW):
        c.drawString(x, y, ln)
        y -= leading
    return y


def rule(c, x, y, w, color=GOLD, thick=0.8, alpha=1.0):
    c.saveState()
    if alpha < 1:
        c.setStrokeAlpha(alpha)
    c.setStrokeColor(color)
    c.setLineWidth(thick)
    c.line(x, y, x + w, y)
    c.restoreState()


def panel(c, x, y, w, h, fill=PANEL, stroke=None, r=3):
    c.saveState()
    c.setFillColor(fill)
    if stroke is not None:
        c.setStrokeColor(stroke)
        c.setLineWidth(0.7)
        c.roundRect(x, y, w, h, r, stroke=1, fill=1)
    else:
        c.roundRect(x, y, w, h, r, stroke=0, fill=1)
    c.restoreState()


def bg(c, tone=INK):
    c.setFillColor(tone)
    c.rect(0, 0, W, H, stroke=0, fill=1)


def page_furniture(c, num):
    c.saveState()
    rule(c, M, BOT + 12, CW, LINE, 0.6)
    tracked(c, M, BOT, PAGE_LABEL, F, 6.2, MUTED, 1.5)
    c.setFont(F, 7.4)
    c.setFillColor(MUTED)
    c.drawRightString(W - M, BOT, "%02d" % num)
    c.restoreState()


def new_page(c, num):
    c.showPage()
    bg(c)
    page_furniture(c, num)


def section_head(c, kicker, title, blurb=None, blurb_w=None):
    y = TOP
    tracked(c, M, y, kicker, F, 7.2, GOLD, 2.0)
    y -= 14
    rule(c, M, y, 26, GOLD, 1.2)
    y -= 32
    y = h1(c, M, y, title, 27, leading=31)
    if blurb:
        y -= 6
        y = para(c, M, y, blurb_w or CW * 0.74, blurb, F, 9.8, 15.0, CREAM_DIM)
    return y


def takeaway(c, text, label="THE TAKEAWAY", y=112, h=None, accent=GOLD):
    lines = wrap(text, F, 8.8, CW - 44)
    h = h or (54 + len(lines) * 12.4)
    panel(c, M, y, CW, h, PANEL_2, LINE)
    c.saveState()
    c.setFillColor(accent)
    c.rect(M, y, 2.4, h, stroke=0, fill=1)
    c.restoreState()
    tracked(c, M + 22, y + h - 22, label, F, 6.6, accent, 1.9)
    para(c, M + 22, y + h - 40, CW - 44, text, F, 8.8, 12.4, CREAM_DIM)
    return y


def table(c, x, y, col_w, rows, aligns=None, row_h=24, size=8.6, header=True,
          head_size=6.9, pad=7, strong_last=False):
    """Ruled table. aligns per column: 'l' or 'r'."""
    n = len(col_w)
    aligns = aligns or (["l"] + ["r"] * (n - 1))
    total = sum(col_w)
    for i, row in enumerate(rows):
        is_head = (i == 0 and header)
        if is_head:
            c.setFillColor(PANEL_2)
            c.rect(x, y - row_h + 8, total, row_h, stroke=0, fill=1)
        cx = x
        for j in range(n):
            cell = row[j] if j < len(row) else ""
            if is_head:
                c.setFont(FB, head_size)
                c.setFillColor(GOLD)
            else:
                last = strong_last and i == len(rows) - 1
                c.setFont(FB if last else F, size if not last else size)
                c.setFillColor(CREAM if (j == 0 or last) else CREAM_DIM)
            if aligns[j] == "r":
                c.drawRightString(cx + col_w[j] - pad, y, cell)
            else:
                c.drawString(cx + pad, y, cell)
            cx += col_w[j]
        rule(c, x, y - row_h + 12, total, LINE, 0.5)
        y -= row_h
    return y


def stat_row(c, y, items, x=M, w=CW, h=64, accent=GOLD):
    """Horizontal metric strip with hairline dividers."""
    n = len(items)
    cw = w / n
    for i, (big, label) in enumerate(items):
        px = x + i * cw
        c.setFont(FB, 19)
        c.setFillColor(accent)
        c.drawString(px, y, big)
        tracked(c, px, y - 14, label.upper(), F, 6.2, MUTED, 1.3)
        if i:
            rule(c, px - 14, y - 6, 0.6, LINE, 0.6)
            c.saveState()
            c.setStrokeColor(LINE)
            c.setLineWidth(0.6)
            c.line(px - 14, y - 20, px - 14, y + 18)
            c.restoreState()
    return y - h


# ----------------------------------------------------------------------------
# 01 — cover
# ----------------------------------------------------------------------------
def p_cover(c):
    bg(c)

    # atmosphere, clipped to page by construction
    c.saveState()
    for i in range(44):
        t = i / 43.0
        c.setFillColor(GOLD)
        c.setFillAlpha(0.010 + 0.012 * (1 - t))
        c.circle(W * 0.14, H * 0.87, 230 * (1 - t) + 36, stroke=0, fill=1)
    for i in range(36):
        t = i / 35.0
        c.setFillColor(OXBLOOD)
        c.setFillAlpha(0.012 + 0.018 * (1 - t))
        c.circle(W * 0.94, H * 0.14, 200 * (1 - t) + 30, stroke=0, fill=1)
    c.restoreState()

    # hairline grid
    c.saveState()
    c.setStrokeColor(CREAM)
    c.setStrokeAlpha(0.03)
    c.setLineWidth(0.5)
    x = M
    while x < W - M:
        c.line(x, 0, x, H)
        x += 44
    c.restoreState()

    # masthead
    c.setStrokeColor(GOLD)
    c.setLineWidth(1.0)
    c.circle(M + 15, H - 66, 15, stroke=1, fill=0)
    c.setFont(FB, 13)
    c.setFillColor(GOLD)
    c.drawCentredString(M + 15, H - 70.5, "T")
    tracked(c, M + 44, H - 62, "INDEPENDENT ADULT STUDIO", F, 7.2, CREAM_DIM, 2.6)
    tracked(c, M + 44, H - 74, "ESSEX · UNITED KINGDOM", F, 6.4, MUTED, 2.2)
    c.setFont(F, 6.8)
    c.setFillColor(MUTED)
    c.drawRightString(W - M, H - 62, "CONFIDENTIAL · NOVEMBER 2026")

    # title
    y = H * 0.505
    tracked(c, M, y + 104, "BUSINESS PLAN 2027 – 2029", F, 8.4, GOLD, 3.4)
    c.setFont(FB, 60)
    c.setFillColor(CREAM)
    c.drawString(M - 3, y + 30, "TWIRLER")
    c.drawString(M - 3, y - 26, "PICTURES")
    rule(c, M, y - 52, 96, GOLD, 2.0)

    c.setFont(FI, 20)
    c.setFillColor(GOLD)
    c.drawString(M, y - 92, "Building one name the audience")
    c.drawString(M, y - 118, "can follow three times a week.")

    para(c, M, y - 152, 320,
         "A growth plan for a single-performer studio: concentrate the audience on "
         "Lady Carey, industrialise a three-shoots-a-week production rhythm, and turn "
         "predictability into subscription revenue.",
         F, 9.6, 15.0, CREAM_DIM)

    # metric strip
    top = 100
    rule(c, M, top + 46, CW, LINE, 0.6)
    items = [("3+", "SHOOTS / WEEK", "Mon · Wed · Fri"),
             ("156", "SCENES / YEAR", "at full rhythm"),
             ("£508k", "REVENUE Y3", "plan case"),
             ("48%", "EBITDA MARGIN", "Y3 plan case")]
    cw = CW / 4
    for i, (big, label, note) in enumerate(items):
        x = M + i * cw
        c.setFont(FB, 22)
        c.setFillColor(CREAM)
        c.drawString(x, top + 10, big)
        tracked(c, x, top - 4, label, F, 6.4, GOLD, 1.4)
        c.setFont(F, 7.2)
        c.setFillColor(MUTED)
        c.drawString(x, top - 16, note)

    c.setFont(F, 6.6)
    c.setFillColor(MUTED)
    c.drawString(M, 26, "Prepared for Twirler Pictures · Adult content business · 18+ only")
    c.drawRightString(W - M, 26, "Page 01")


# ----------------------------------------------------------------------------
# 02 — thesis
# ----------------------------------------------------------------------------
def p_thesis(c):
    bg(c)
    tracked(c, M, TOP, "00 · THE ONE-PAGE VERSION", F, 7.2, GOLD, 2.0)
    rule(c, M, TOP - 14, 26, GOLD, 1.2)
    y = h1(c, M, TOP - 46, "The thesis", 30)

    colw = CW * 0.555
    y = para(c, M, y - 6, colw,
             "Twirler Pictures does not need to be a big studio to be a profitable one. It needs "
             "to be the studio a specific audience cannot stop checking — and that only works if "
             "there is one recognisable performer releasing on a schedule nobody has to guess at.",
             F, 10.6, 16.4, CREAM_DIM)

    items = [
        ("Concentrate, don't diversify",
         "One anchor performer outperforms a rotating cast at this scale. Every scene, cutdown and "
         "post points at the same name: Lady Carey."),
        ("Rhythm is the product",
         "Three shoots a week, released every Saturday. Predictability is what converts a curious "
         "viewer into a renewing member — and what keeps churn measurable."),
        ("Shoot once, publish five times",
         "Each shoot day yields one long-form scene, three vertical cutdowns and a photo set. The "
         "marginal cost of the extra outputs is close to zero."),
        ("Stay small, stay compliant",
         "Closed sets, verified records, real age assurance. Compliance is the moat that keeps the "
         "studio its payment processor and its distribution."),
    ]
    yy = y - 14
    for i, (t, b) in enumerate(items):
        c.setFont(FB, 7.6)
        c.setFillColor(GOLD_DARK)
        c.drawString(M, yy, "%02d" % (i + 1))
        c.setFont(FB, 10.2)
        c.setFillColor(CREAM)
        c.drawString(M + 26, yy, t)
        yy = para(c, M + 26, yy - 15, colw - 26, b, F, 8.8, 13.0, MUTED) - 15

    # contents rail
    px = M + colw + 30
    pw = W - M - px
    ptop = TOP - 30
    ph = 548
    panel(c, px, ptop - ph, pw, ph, PANEL, LINE)
    tracked(c, px + 20, ptop - 26, "CONTENTS", F, 6.9, GOLD, 2.0)
    rule(c, px + 20, ptop - 36, pw - 40, LINE, 0.6)

    contents = [("01", "The thesis", "02"), ("02", "The market", "03"),
                ("03", "Positioning", "04"), ("04", "Lady Carey, the anchor", "05"),
                ("05", "The three-a-week engine", "06"), ("06", "Unit economics", "07"),
                ("07", "Financial plan", "08"), ("08", "Revenue mix", "09"),
                ("09", "Audience & distribution", "10"), ("10", "Compliance & risk", "11"),
                ("11", "Roadmap & KPIs", "12")]
    cy = ptop - 60
    for num, label, page in contents:
        c.setFont(F, 6.8)
        c.setFillColor(GOLD_DARK)
        c.drawString(px + 20, cy, num)
        c.setFont(F, 8.8)
        c.setFillColor(CREAM_DIM)
        c.drawString(px + 42, cy, label)
        c.setFont(F, 7.4)
        c.setFillColor(MUTED)
        c.drawRightString(px + pw - 20, cy, page)
        cy -= 30

    tracked(c, px + 20, cy - 4, "PREPARED BY", F, 6.2, MUTED, 1.6)
    para(c, px + 20, cy - 20, pw - 40,
         "Studio management, with Lady Carey as creative lead. Draft for review — "
         "figures are planning estimates, not audited accounts.",
         F, 7.6, 10.8, MUTED)

    # closing bet
    by = 112
    ph2 = 84
    panel(c, M, by, CW, ph2, PANEL_2, LINE)
    c.saveState()
    c.setFillColor(GOLD)
    c.rect(M, by, 2.4, ph2, stroke=0, fill=1)
    c.restoreState()
    tracked(c, M + 22, by + ph2 - 22, "THE BET, IN ONE SENTENCE", F, 6.6, GOLD, 1.9)
    para(c, M + 22, by + ph2 - 42, CW - 44,
         "£25k of founder capital, twelve months of disciplined weekly output and a single performer "
         "promoted harder than any competitor promotes a roster — for a business running at ~45% "
         "EBITDA and £0.5m of revenue by year three.",
         FI, 9.6, 14.0, CREAM)
    page_furniture(c, 2)


# ----------------------------------------------------------------------------
# 03 — market
# ----------------------------------------------------------------------------
def p_market(c):
    bg(c)
    sy = section_head(c, "01 · THE MARKET",
                 "A saturated market with an\nunderserved middle",
                 "Free tube sites have flattened the price of a single clip to zero. What they "
                 "cannot copy is a performer with a personality, a release schedule and a reason "
                 "to pay.", CW * 0.80)

    cards = [
        ("FREE CONTENT", "Unlimited clips at zero price",
         "Tube aggregators own discovery and pay creators a pittance. Competing on volume of free "
         "clips is a losing game for a studio of any size."),
        ("SUBSCRIPTION FATIGUE", "Too many platforms,\ntoo little signal",
         "Buyers will pay for one or two memberships at most. They pick the studio whose next "
         "release they can actually anticipate."),
        ("COMPLIANCE SQUEEZE", "Processors are\ntightening",
         "Age assurance and performer verification now gate access to card processing and "
         "distribution. Small operators fall out; prepared ones inherit the demand."),
    ]
    gap = 14
    cwx = (CW - 2 * gap) / 3
    cy_top = sy - 26
    ch = 158
    for i, (tag, t, b) in enumerate(cards):
        x = M + i * (cwx + gap)
        panel(c, x, cy_top - ch, cwx, ch, PANEL, LINE)
        tracked(c, x + 16, cy_top - 24, tag, F, 6.3, GOLD, 1.6)
        h1(c, x + 16, cy_top - 46, t, 11.0, leading=14.5, maxw=cwx - 32)
        para(c, x + 16, cy_top - 84, cwx - 32, b, F, 8.0, 12.0, MUTED)

    # money table
    ty = cy_top - ch - 44
    tracked(c, M, ty, "WHERE THE MONEY ACTUALLY SITS", F, 6.9, GOLD, 2.0)
    ty -= 18
    rows = [
        ["Segment", "Share of spend", "Twirler's play"],
        ["Subscription memberships", "~55%", "Core product: £12.99 / £19.99 tiers"],
        ["Pay-per-view & bundles", "~22%", "Back catalogue, £6.99 per scene"],
        ["Custom & commissions", "~14%", "£600–£1,500 per commission"],
        ["Licensing & affiliate", "~9%", "Clip licensing rev-share"],
    ]
    tw = CW * 0.655
    ty = table(c, M, ty, [tw * 0.40, tw * 0.22, tw * 0.38], rows,
               aligns=["l", "r", "l"], row_h=29)
    para(c, M, ty - 8, tw,
         "Shares reflect typical independent-studio mixes. Twirler weights memberships more "
         "heavily because a single-performer catalogue sells better as a subscription than as a "
         "series of one-off purchases.", F, 7.6, 11.0, MUTED)

    # why now rail
    rx = M + tw + 30
    rw = W - M - rx
    panel(c, rx, ty + 26, rw, 148, PANEL_2, LINE)
    tracked(c, rx + 16, ty + 152, "WHY NOW", F, 6.4, GOLD, 1.8)
    para(c, rx + 16, ty + 134, rw - 32,
         "Search demand for performer-led content is stable. Supply of well-produced, compliant "
         "UK content is not. The gap is credibility plus cadence — and a one-performer studio can "
         "occupy it faster than a network can.",
         F, 7.6, 11.2, CREAM_DIM)

    takeaway(c, "Twirler is not competing with free sites for attention. It is competing with "
                "every other paid membership for a renewal — and renewals are won by the studio "
                "whose next release the buyer already expects.", "POSITION IN ONE LINE")
    page_furniture(c, 3)


# ----------------------------------------------------------------------------
# 04 — positioning
# ----------------------------------------------------------------------------
def p_positioning(c):
    bg(c)
    sy = section_head(c, "02 · POSITIONING",
                 "One performer, promoted like\na label promotes a band",
                 "Breadth is how studios compete when they have no name worth remembering. "
                 "Twirler's entire strategy is the opposite bet.", CW * 0.80)

    top = sy - 24
    hgt = 240
    w1 = CW * 0.465
    x1, x2 = M, M + CW * 0.535
    w2 = CW * 0.465

    panel(c, x1, top - hgt, w1, hgt, PANEL_2, LINE)
    tracked(c, x1 + 20, top - 26, "THE USUAL SMALL STUDIO", F, 6.4, MUTED, 1.8)
    usual = ["Rotating cast of ten to twenty performers",
             "Releases whenever footage happens to be ready",
             "Audience cannot name the brand",
             "Marketing spread across every platform at once",
             "No reason to renew in a quiet month"]
    yy = top - 58
    for item in usual:
        c.setFont(FB, 9)
        c.setFillColor(SLATE)
        c.drawString(x1 + 20, yy, "—")
        para(c, x1 + 36, yy, w1 - 56, item, F, 8.6, 12.0, MUTED)
        yy -= 34

    panel(c, x2, top - hgt, w2, hgt, PANEL, GOLD_DARK)
    tracked(c, x2 + 20, top - 26, "THE TWIRLER POSITION", F, 6.4, GOLD, 1.8)
    ours = ["One anchor: Lady Carey, front and centre",
            "Releases every Saturday, without fail",
            "The name is the brand",
            "Marketing compounds on a single search term",
            "A new scene every week is the renewal pitch"]
    yy = top - 58
    for item in ours:
        c.setFont(FB, 8.4)
        c.setFillColor(GOLD)
        c.drawString(x2 + 20, yy - 1, "◆")
        para(c, x2 + 38, yy, w2 - 58, item, F, 8.6, 12.0, CREAM)
        yy -= 34

    # three moves
    my = top - hgt - 46
    tracked(c, M, my, "THE THREE MOVES", F, 6.9, GOLD, 2.0)
    my -= 24
    moves = [
        ("Make her the interface",
         "Lady Carey is not a category inside the site — she is the site. Navigation, hero, covers "
         "and email subject lines all resolve to one name."),
        ("Sell the calendar",
         "Publish the release schedule. Members buy the certainty of a Saturday drop as much as "
         "they buy the scene itself."),
        ("Publish the standard",
         "Show how the studio runs: verified records, closed sets, real releases. It reassures "
         "buyers, processors and collaborators at once."),
    ]
    bw = (CW - 2 * 16) / 3
    for i, (t, b) in enumerate(moves):
        x = M + i * (bw + 16)
        rule(c, x, my + 10, bw, GOLD, 0.9)
        c.setFont(FB, 10.4)
        c.setFillColor(CREAM)
        c.drawString(x, my - 10, t)
        para(c, x, my - 30, bw, b, F, 8.4, 12.6, MUTED)

    takeaway(c, "The measurable version of this: by month twelve, more search traffic should "
                "resolve to the performer's name than to the studio's. That single ratio is the "
                "cleanest proof the positioning is working.", "HOW YOU KNOW IT IS WORKING")
    page_furniture(c, 4)


# ----------------------------------------------------------------------------
# 05 — the anchor
# ----------------------------------------------------------------------------
def p_anchor(c):
    bg(c)

    pw_, ph_ = CW * 0.355, 612
    px, py = M, TOP - ph_

    # clipped portrait block
    c.saveState()
    p = c.beginPath()
    p.roundRect(px, py, pw_, ph_, 3)
    c.clipPath(p, stroke=0, fill=0)
    c.setFillColor(PANEL)
    c.rect(px, py, pw_, ph_, stroke=0, fill=1)
    for i in range(30):
        t = i / 29.0
        c.setFillColor(GOLD)
        c.setFillAlpha(0.014 + 0.018 * (1 - t))
        c.circle(px + pw_ * 0.42, py + ph_ * 0.74, 140 * (1 - t) + 24, stroke=0, fill=1)
    for i in range(26):
        t = i / 25.0
        c.setFillColor(OXBLOOD)
        c.setFillAlpha(0.016 + 0.022 * (1 - t))
        c.circle(px + pw_ * 0.78, py + ph_ * 0.22, 120 * (1 - t) + 20, stroke=0, fill=1)
    c.setFillColor(CREAM)
    c.setFillAlpha(0.20)
    c.setFont(FB, 54)
    c.drawCentredString(px + pw_ / 2, py + ph_ * 0.50, "LC")
    c.restoreState()

    c.saveState()
    c.setStrokeColor(CREAM)
    c.setStrokeAlpha(0.12)
    c.setLineWidth(0.7)
    c.rect(px + 11, py + 11, pw_ - 22, ph_ - 22, stroke=1, fill=0)
    c.restoreState()

    tracked(c, px + 22, py + 34, "ANCHOR PERFORMER", F, 6.4, GOLD, 1.8)
    c.setFont(F, 7.4)
    c.setFillColor(MUTED)
    c.drawString(px + 22, py + 21, "Essex · UK · 18+ verified")

    # right column
    rx = px + pw_ + 30
    rw = W - M - rx
    y = TOP
    tracked(c, rx, y, "03 · THE ANCHOR", F, 7.0, GOLD, 2.0)
    y -= 26
    c.setFont(FB, 26)
    c.setFillColor(CREAM)
    c.drawString(rx, y, "Lady Carey")
    y -= 20
    c.setFont(FI, 11.6)
    c.setFillColor(GOLD)
    c.drawString(rx, y, "the asset the plan is built around")
    y -= 26

    y = para(c, rx, y, rw,
             "Every studio has one performer the audience arrives for. Most spread that attention "
             "thin, then wonder why nobody remembers the brand. Twirler makes the anchor explicit: "
             "Lady Carey is the creative lead, the cover, the search term and the reason to renew.",
             F, 9.0, 13.6, CREAM_DIM)

    y -= 8
    tracked(c, rx, y, "WHAT SHE BRINGS", F, 6.5, GOLD, 1.8)
    y -= 18
    points = [
        ("Recognisable", "A consistent look and voice that survives a fifteen-second vertical cut."),
        ("Productive", "Comfortable on a three-day shooting week, with a scene bank as buffer."),
        ("Editorial", "Leads concept, styling and casting — the taste that differentiates the catalogue."),
        ("Commercial", "Fronts commissions, customs and partner shoots at a premium rate."),
    ]
    for t, b in points:
        c.setFont(FB, 8.8)
        c.setFillColor(CREAM)
        c.drawString(rx, y, t)
        y = para(c, rx, y - 12, rw, b, F, 8.2, 11.8, MUTED) - 9

    # protection terms
    sy = py + 96
    panel(c, rx, sy, rw, 96, PANEL_2, LINE)
    tracked(c, rx + 16, sy + 74, "ASSET PROTECTION", F, 6.4, GOLD, 1.8)
    para(c, rx + 16, sy + 56, rw - 32,
         "The plan depends on one person. Terms: profit share on memberships, first refusal on "
         "commissions, a hard maximum of four shoot days a week, and a written exit clause "
         "covering the back catalogue.", F, 7.6, 11.0, CREAM_DIM)

    # caption under the portrait
    tracked(c, px, py - 24, "ANCHOR OUTPUT AT PLAN CADENCE", F, 5.9, MUTED, 1.5)
    c.setFont(F, 7.2)
    c.setFillColor(CREAM_DIM)
    c.drawString(px, py - 38, "156 scenes a year · 4K master · 48h early access")
    c.drawString(px, py - 49, "3 shoot days a week · Mon / Wed / Fri")

    page_furniture(c, 5)


# ----------------------------------------------------------------------------
# 06 — the engine
# ----------------------------------------------------------------------------
def p_engine(c):
    bg(c)
    section_head(c, "04 · THE ENGINE",
                 "Three shoots a week, every week",
                 "The model rests on cadence. Not three scenes a week when inspiration strikes — "
                 "three shoot days on the calendar, with a scene bank absorbing the bad weeks.",
                 CW * 0.80)

    days = ["MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN"]
    modes = ["SHOOT", "EDIT", "SHOOT", "EDIT", "SHOOT", "RELEASE", "REST"]
    gap = 7
    dw = (CW - 6 * gap) / 7
    cy = 648
    dh = 78
    for i, (d, m_) in enumerate(zip(days, modes)):
        x = M + i * (dw + gap)
        c.saveState()
        if m_ == "SHOOT":
            c.setFillColor(GOLD); c.setFillAlpha(0.17)
            c.roundRect(x, cy - dh, dw, dh, 3, stroke=0, fill=1)
        elif m_ == "RELEASE":
            c.setFillColor(OXBLOOD); c.setFillAlpha(0.34)
            c.roundRect(x, cy - dh, dw, dh, 3, stroke=0, fill=1)
        else:
            c.setFillColor(PANEL)
            c.roundRect(x, cy - dh, dw, dh, 3, stroke=0, fill=1)
        c.setStrokeColor(GOLD if m_ == "SHOOT" else (OXBLOOD if m_ == "RELEASE" else LINE))
        c.setLineWidth(0.9)
        c.roundRect(x, cy - dh, dw, dh, 3, stroke=1, fill=0)
        c.restoreState()
        c.setFont(FB, 11.5)
        c.setFillColor(CREAM if m_ != "REST" else MUTED)
        c.drawCentredString(x + dw / 2, cy - 28, d)
        c.setFont(F, 5.9)
        c.setFillColor(GOLD if m_ == "SHOOT" else (ROSE if m_ == "RELEASE" else MUTED))
        c.drawCentredString(x + dw / 2, cy - 44, m_)

    my = cy - dh - 32
    tracked(c, M, my, "WHAT ONE SHOOT DAY PRODUCES", F, 6.9, GOLD, 2.0)
    my -= 22
    outs = [("1", "long-form scene", "18–26 min, 4K master"),
            ("3", "vertical cutdowns", "15–45 sec, discovery channels"),
            ("1", "photo set", "20–40 frames, press & socials"),
            ("1", "archive master", "4K + proxies, 7-year retention")]
    ow = (CW - 3 * 12) / 4
    for i, (n, t, s) in enumerate(outs):
        x = M + i * (ow + 12)
        panel(c, x, my - 74, ow, 74, PANEL, LINE)
        c.setFont(FB, 19)
        c.setFillColor(GOLD)
        c.drawString(x + 14, my - 30, n)
        c.setFont(F, 8.4)
        c.setFillColor(CREAM)
        c.drawString(x + 14, my - 46, t)
        c.setFont(F, 7.0)
        c.setFillColor(MUTED)
        c.drawString(x + 14, my - 59, s)

    ty = my - 108
    tracked(c, M, ty, "ANNUAL CAPACITY AT THREE SHOOTS A WEEK", F, 6.9, GOLD, 2.0)
    ty -= 20
    rows = [
        ["Output", "Per week", "Per year", "Note"],
        ["Shoot days", "3", "156", "A fourth day is held as flex capacity"],
        ["Long-form scenes", "3", "156", "13 released each month, rest banked"],
        ["Vertical cutdowns", "9", "468", "Two to three posted per day"],
        ["Photo sets", "3", "156", "Newsletter, press and affiliate use"],
    ]
    ty = table(c, M, ty, [CW * 0.26, CW * 0.13, CW * 0.13, CW * 0.48], rows,
               aligns=["l", "r", "r", "l"], row_h=27)

    takeaway(c, "Never release from a bank of fewer than six finished scenes. It costs about one "
                "week of editing to hold, and it is the only thing keeping the Saturday drop "
                "credible when illness, holidays or a reshoot eat a shooting day.", "THE BUFFER RULE")
    page_furniture(c, 6)


# ----------------------------------------------------------------------------
# 07 — unit economics
# ----------------------------------------------------------------------------
def p_unit(c):
    bg(c)
    section_head(c, "05 · UNIT ECONOMICS",
                 "What a shoot day costs,\nand what it earns",
                 "Costs are modelled per shoot day, not per year, so the studio can flex cadence up "
                 "or down and see the margin move immediately.", CW * 0.78)

    lw = CW * 0.44
    ty = 640
    tracked(c, M, ty, "COST PER SHOOT DAY", F, 6.8, GOLD, 1.8)
    ty -= 20
    rows = [["Line", "£", "%"],
            ["Performer fee", "250", "44.6%"],
            ["Camera & crew", "110", "19.6%"],
            ["Studio, lighting & kit", "60", "10.7%"],
            ["Edit, grade & audio", "90", "16.1%"],
            ["Make-up, styling, M&O", "50", "8.9%"],
            ["Total", "560", "100%"]]
    ty = table(c, M, ty, [lw * 0.54, lw * 0.23, lw * 0.23], rows, row_h=25, strong_last=True)
    c.saveState()
    c.setStrokeColor(GOLD_DARK)
    c.setLineWidth(0.8)
    c.line(M, ty + 25 - 13, M + lw, ty + 25 - 13)
    c.restoreState()

    # headline cost
    rx = M + lw + 32
    rw = W - M - rx
    c.setFont(FB, 26)
    c.setFillColor(GOLD)
    c.drawString(rx, 634, "£560")
    tracked(c, rx + 84, 630, "FULLY-LOADED COST PER SHOOT DAY", F, 6.2, MUTED, 1.3)

    tracked(c, rx, 600, "REVENUE ATTRIBUTABLE PER SCENE · YEAR 2", F, 6.6, GOLD, 1.8)
    rev = [["Source", "Per scene", "Basis"],
           ["Membership", "£1,110", "900 members × £16 ARPU ÷ 13"],
           ["PPV / back catalogue", "£335", "≈ £0.35 per member per scene"],
           ["Commissions", "£225", "3 per month at £975 average"],
           ["Licensing", "£140", "Partner clip licensing rev-share"],
           ["Total", "£1,810", "against £560 of cost"]]
    y2 = table(c, rx, 580, [rw * 0.36, rw * 0.20, rw * 0.44], rev,
               aligns=["l", "r", "l"], row_h=25, strong_last=True)

    # margin bar
    bar_y = y2 - 46
    tracked(c, rx, bar_y + 40, "CONTRIBUTION MARGIN PER SCENE", F, 6.6, GOLD, 1.8)
    frac = 560 / 1810.0
    c.setFillColor(OXBLOOD)
    c.rect(rx, bar_y, rw * frac, 20, stroke=0, fill=1)
    c.setFillColor(GOLD)
    c.rect(rx + rw * frac, bar_y, rw * (1 - frac), 20, stroke=0, fill=1)
    c.setFont(F, 6.8)
    c.setFillColor(CREAM)
    c.drawString(rx + 7, bar_y + 7, "cost £560")
    c.setFillColor(INK)
    c.drawString(rx + rw * frac + 7, bar_y + 7, "contribution £1,250")
    c.setFont(F, 7.0)
    c.setFillColor(MUTED)
    c.drawString(rx, bar_y - 14, "69% contribution margin at plan volume")

    # sensitivity
    sy = 372
    tracked(c, M, sy, "WHAT HAPPENS IF CADENCE SLIPS", F, 6.8, GOLD, 1.8)
    sens = [["Shoots / week", "Scenes / yr", "Production cost", "Breakeven members*"],
            ["2", "104", "£58,240", "390"],
            ["3", "156", "£87,360", "585"],
            ["4", "208", "£116,480", "780"]]
    sy = table(c, M, sy - 18, [CW * 0.24, CW * 0.20, CW * 0.28, CW * 0.28], sens,
               aligns=["l", "r", "r", "r"], row_h=26)
    para(c, M, sy - 12, CW * 0.64,
         "*Members required at £16 blended monthly ARPU to cover production cost alone, before "
         "platform, marketing and admin. The plan targets 900 members by the end of year two — "
         "roughly 1.5× the three-a-week breakeven.", F, 7.4, 10.8, MUTED)

    takeaway(c, "Every extra shoot day costs £560 and returns roughly £1,810 at plan volume. The "
                "constraint is not demand — it is the anchor performer's sustainable working week, "
                "which is why four days is treated as the ceiling.", "THE OPERATING RULE")
    page_furniture(c, 7)


# ----------------------------------------------------------------------------
# 08 — financials
# ----------------------------------------------------------------------------
def p_financials(c):
    bg(c)
    sy = section_head(c, "06 · FINANCIAL PLAN",
                 "Three years to £0.5m",
                 "Base case: soft launch in December 2026, full three-a-week cadence from Q2 2027, "
                 "prices held flat through 2027 with a small uplift at each anniversary.",
                 CW * 0.78)

    ch_x = M
    ch_w, ch_h = CW * 0.56, 182
    ch_base = sy - 44 - ch_h
    tracked(c, ch_x, ch_base + ch_h + 26, "REVENUE VS. OPERATING COST · £000", F, 6.6, GOLD, 1.8)

    rev = [93, 247, 508]
    cost = [98, 158, 263]
    ebitda = [r - c_ for r, c_ in zip(rev, cost)]
    vmax = 540.0
    c.saveState()
    c.setStrokeColor(LINE)
    c.setLineWidth(0.5)
    for g in range(6):
        gy = ch_base + ch_h * g / 5.0
        c.line(ch_x, gy, ch_x + ch_w, gy)
        c.setFont(F, 6.2)
        c.setFillColor(MUTED)
        c.drawRightString(ch_x - 6, gy - 2, "%d" % int(vmax * g / 5))
    c.restoreState()

    gw = ch_w / 3.0
    bw = 30
    for i in range(3):
        mid = ch_x + i * gw + gw / 2
        for j, (val, colr) in enumerate(((rev[i], GOLD), (cost[i], SLATE))):
            hgt = ch_h * val / vmax
            xpos = mid - bw - 5 + j * (bw + 10)
            c.setFillColor(colr)
            c.rect(xpos, ch_base, bw, hgt, stroke=0, fill=1)
            c.setFont(FB, 7.2)
            c.setFillColor(CREAM if j == 0 else MUTED)
            c.drawCentredString(xpos + bw / 2, ch_base + hgt + 7, "%d" % val)
        c.setFont(FB, 8.6)
        c.setFillColor(CREAM_DIM)
        c.drawCentredString(mid, ch_base - 17, ["2027", "2028", "2029"][i])
        c.setFont(F, 6.8)
        c.setFillColor(GOLD if ebitda[i] > 0 else ROSE)
        c.drawCentredString(mid, ch_base - 29,
                            ("EBITDA £%dk" % ebitda[i]) if ebitda[i] >= 0 else ("EBITDA £%dk" % ebitda[i]))

    c.setFillColor(GOLD); c.rect(ch_x, ch_base - 52, 8, 8, stroke=0, fill=1)
    c.setFont(F, 6.8); c.setFillColor(MUTED)
    c.drawString(ch_x + 13, ch_base - 50, "Revenue")
    c.setFillColor(SLATE); c.rect(ch_x + 72, ch_base - 52, 8, 8, stroke=0, fill=1)
    c.setFont(F, 6.8); c.setFillColor(MUTED)
    c.drawString(ch_x + 85, ch_base - 50, "Operating cost")

    # membership ramp
    mx = M + ch_w + 40
    mw = W - M - mx
    tracked(c, mx, ch_base + ch_h + 26, "PAYING MEMBERS", F, 6.6, GOLD, 1.8)
    members = [40, 120, 260, 340, 420, 480, 560, 660, 760, 840, 900, 1000]
    lb = ch_base
    lh = ch_h - 26
    pts = [(mx + mw * i / 11.0, lb + lh * v / 1050.0) for i, v in enumerate(members)]
    c.saveState()
    p = c.beginPath()
    p.moveTo(pts[0][0], lb)
    for pt in pts:
        p.lineTo(*pt)
    p.lineTo(pts[-1][0], lb)
    p.close()
    c.setFillColor(GOLD)
    c.setFillAlpha(0.13)
    c.drawPath(p, stroke=0, fill=1)
    c.restoreState()
    c.setStrokeColor(GOLD)
    c.setLineWidth(1.4)
    p = c.beginPath()
    p.moveTo(*pts[0])
    for pt in pts[1:]:
        p.lineTo(*pt)
    c.drawPath(p, stroke=1, fill=0)
    c.setFillColor(GOLD)
    c.circle(pts[-1][0], pts[-1][1], 3, stroke=0, fill=1)
    c.setFont(FB, 8.0)
    c.setFillColor(CREAM)
    c.drawRightString(pts[-1][0] - 3, pts[-1][1] + 11, "1,000")
    for lab, idx in (("Dec 27", 5), ("Dec 28", 11)):
        c.setFont(F, 6.4)
        c.setFillColor(MUTED)
        c.drawCentredString(pts[idx][0], lb - 13, lab)

    # P&L
    ty = ch_base - 86
    tracked(c, M, ty, "PROFIT & LOSS SUMMARY · £000", F, 6.9, GOLD, 2.0)
    ty -= 20
    rows = [["", "2026 (soft)", "2027", "2028", "2029"],
            ["Memberships", "4", "48", "173", "357"],
            ["PPV, customs & commissions", "3", "37", "52", "86"],
            ["Licensing & partnerships", "1", "8", "22", "65"],
            ["Total revenue", "8", "93", "247", "508"],
            ["Production", "6", "74", "87", "112"],
            ["Platform, hosting & payments", "1", "6", "12", "18"],
            ["Marketing", "2", "12", "26", "45"],
            ["Team, legal, insurance, admin", "2", "6", "33", "88"],
            ["Total operating cost", "11", "98", "158", "263"],
            ["EBITDA", "(3)", "(5)", "89", "245"]]
    ty = table(c, M, ty, [CW * 0.40, CW * 0.15, CW * 0.15, CW * 0.15, CW * 0.15], rows,
               aligns=["l", "r", "r", "r", "r"], row_h=20, size=7.9, strong_last=True)

    para(c, M, ty - 6, CW,
         "Founder capital of £25k covers the 2026 soft launch and the first half of 2027, including "
         "a six-scene buffer. No debt assumed and no outside investment before year two.",
         F, 7.6, 11.0, MUTED)

    page_furniture(c, 8)


# ----------------------------------------------------------------------------
# 09 — revenue mix
# ----------------------------------------------------------------------------
def p_revenue(c):
    bg(c)
    sy = section_head(c, "07 · REVENUE MIX",
                      "Five ways one shoot day pays",
                      "Membership is the spine, but a single-performer catalogue is unusually good at "
                      "selling the same footage repeatedly: to subscribers, to one-off buyers, to "
                      "commissioners and to partners.", CW * 0.80)

    bar_top = sy - 40
    bar_h = 172
    bar_base = bar_top - bar_h
    tracked(c, M, bar_top + 16, "REVENUE MIX BY YEAR · £000", F, 6.6, GOLD, 1.8)

    mix = [("Memberships", GOLD, [48, 173, 357]),
           ("PPV & bundles", HexColor("#B8894A"), [16, 26, 42]),
           ("Commissions & customs", OXBLOOD, [21, 26, 44]),
           ("Licensing", HexColor("#6E4B5A"), [8, 22, 45]),
           ("Partnerships & other", HexColor("#3E3E48"), [0, 0, 20])]
    totals = [sum(s_[2][i] for s_ in mix) for i in range(3)]
    vmax = 540.0
    bw = 84
    xs = [M + 18 + i * 100 for i in range(3)]
    for i in range(3):
        acc = 0.0
        for _, colr, vals in mix:
            hgt = bar_h * vals[i] / vmax
            c.setFillColor(colr)
            c.rect(xs[i], bar_base + acc, bw, hgt, stroke=0, fill=1)
            acc += hgt
        c.setFont(FB, 9.4)
        c.setFillColor(CREAM)
        c.drawCentredString(xs[i] + bw / 2, bar_base + acc + 10, "£%dk" % totals[i])
        c.setFont(F, 6.9)
        c.setFillColor(MUTED)
        c.drawCentredString(xs[i] + bw / 2, bar_base - 15, ["2027", "2028", "2029"][i])

    # legend column
    lx = M + 326
    yy = bar_top - 4
    for name, colr, vals in mix:
        c.setFillColor(colr)
        c.rect(lx, yy - 2, 9, 9, stroke=0, fill=1)
        c.setFont(F, 7.8)
        c.setFillColor(CREAM_DIM)
        c.drawString(lx + 15, yy, name)
        c.setFont(FB, 7.2)
        c.setFillColor(MUTED)
        c.drawRightString(W - M, yy, "%d%%" % round(vals[2] / float(totals[2]) * 100))
        yy -= 21
    c.setFont(F, 6.6)
    c.setFillColor(MUTED)
    c.drawString(lx, yy - 2, "shares shown for 2029")

    # pricing ladder
    ty = bar_base - 54
    tracked(c, M, ty, "PRICING LADDER", F, 6.9, GOLD, 2.0)
    ty -= 20
    rows = [["Tier", "Price", "Includes", "Target mix"],
            ["Standard", "£12.99 / mo", "Full catalogue, 48h early access", "55% of members"],
            ["Premium", "£19.99 / mo", "4K downloads, requests, photo sets", "30% of members"],
            ["Annual", "£119 / yr", "Standard, two months free", "15% of members"],
            ["PPV scene", "£6.99", "Single scene, non-members", "—"]]
    ty = table(c, M, ty, [CW * 0.17, CW * 0.18, CW * 0.45, CW * 0.20], rows,
               aligns=["l", "r", "l", "l"], row_h=25)

    # detail cards
    cy = ty - 12
    cards = [("Commissions", "£600–£1,500",
              "Custom scenes for verified buyers. Three to four a month; the highest-margin line "
              "and the fastest cash."),
             ("Licensing", "rev-share",
              "Non-exclusive clip licensing to partner platforms and affiliate networks. Pure "
              "margin on footage already shot."),
             ("Back catalogue", "compounding",
              "156 scenes a year means 500+ sellable assets by year four. Repackaged monthly as "
              "bundles and themed collections.")]
    cw_ = (CW - 2 * 14) / 3
    for i, (t, price, b) in enumerate(cards):
        x = M + i * (cw_ + 14)
        panel(c, x, cy - 108, cw_, 108, PANEL, LINE)
        c.setFont(FB, 9.4)
        c.setFillColor(CREAM)
        c.drawString(x + 15, cy - 24, t)
        c.setFont(FB, 8.2)
        c.setFillColor(GOLD)
        c.drawString(x + 15, cy - 38, price)
        para(c, x + 15, cy - 54, cw_ - 30, b, F, 7.4, 10.4, MUTED)

    takeaway(c, "The pricing ladder is deliberately simple: one price for the catalogue, one for "
                "the collector, and a pay-per-scene door for people who will never subscribe. "
                "No tier exists that cannibalises another.", "PRICING DISCIPLINE")
    page_furniture(c, 9)


# ----------------------------------------------------------------------------
# 10 — audience
# ----------------------------------------------------------------------------
def p_marketing(c):
    bg(c)
    sy = section_head(c, "08 · AUDIENCE",
                      "Discovery is rented; audience is owned",
                      "Adult platforms will always control reach. The plan treats every social channel "
                      "as a funnel into the one asset the studio actually owns: the email list and the "
                      "membership base.", CW * 0.80)

    fy = sy - 20
    stages = [("Cutdowns", "468 clips a year across three channels", 1.00),
              ("Site visit", "target 18% click-through to site", 0.74),
              ("Age gate passed", "target 84% proceed", 0.54),
              ("Membership", "target 2.4% of visitors", 0.36),
              ("Renewal", "target 78% month-two retention", 0.22)]
    maxw = CW * 0.34
    for i, (label, sub, frac) in enumerate(stages):
        w_ = maxw * frac + 96
        yy = fy - i * 48
        c.saveState()
        c.setFillColor(GOLD)
        c.setFillAlpha(0.05 + 0.032 * (4 - i))
        c.roundRect(M, yy - 34, w_, 42, 2, stroke=0, fill=1)
        c.setStrokeColor(GOLD_DARK if i < 3 else OXBLOOD)
        c.setLineWidth(0.6)
        c.roundRect(M, yy - 34, w_, 42, 2, stroke=1, fill=0)
        c.restoreState()
        c.setFont(FB, 9.2)
        c.setFillColor(CREAM)
        c.drawString(M + 14, yy - 12, label)
        c.setFont(F, 7.0)
        c.setFillColor(MUTED)
        c.drawString(M + 14, yy - 25, sub)

    rx = M + CW * 0.60
    rw = W - M - rx
    tracked(c, rx, fy + 4, "CHANNEL PLAN", F, 6.6, GOLD, 1.8)
    rows = [["Channel", "Role", "Cadence"],
            ["Vertical cutdowns", "Discovery", "3 / day"],
            ["Email list", "Conversion", "2 / week"],
            ["Partner networks", "Licensing", "Monthly"],
            ["Press & interviews", "Credibility", "Monthly"]]
    table(c, rx, fy - 14, [rw * 0.42, rw * 0.33, rw * 0.25], rows,
          aligns=["l", "l", "r"], row_h=24, size=7.5)

    # owned audience note
    oy = 360
    tracked(c, M, oy, "THE ONE ASSET THAT COMPOUNDS", F, 6.8, GOLD, 1.8)
    para(c, M, oy - 18, CW * 0.64,
         "Every cutdown exists to move someone onto the list. A subscriber who has given an email "
         "address is worth roughly four times one who has not: they can be re-engaged after a "
         "lapse, sold a commission, and counted when a partner asks for reach.",
         F, 8.6, 12.8, CREAM_DIM)

    metrics = [("2.4%", "VISIT → MEMBER"), ("78%", "MONTH-2 RETENTION"),
               ("£16", "BLENDED ARPU"), ("4.1", "SCENES / MEMBER / YR")]
    rule(c, M, 292, CW, LINE, 0.6)
    cw4 = CW / 4
    for i, (big, lab) in enumerate(metrics):
        x = M + i * cw4
        c.setFont(FB, 20)
        c.setFillColor(GOLD)
        c.drawString(x, 258, big)
        tracked(c, x, 244, lab, F, 6.2, MUTED, 1.3)

    takeaway(c, "Marketing spend stays under 9% of revenue because the release rhythm does most of "
                "the work: 468 cutdowns a year is a content engine, not an advertising budget.",
             "WHY THE NUMBERS HOLD")
    page_furniture(c, 10)


# ----------------------------------------------------------------------------
# 11 — risk
# ----------------------------------------------------------------------------
def p_risk(c):
    bg(c)
    section_head(c, "09 · COMPLIANCE & RISK",
                 "The constraints are the moat",
                 "Most of the risk in this plan is not commercial — it is regulatory. Handling it "
                 "early is what keeps card processing, hosting and distribution available.",
                 CW * 0.78)

    cy = 660
    tracked(c, M, cy, "NON-NEGOTIABLES", F, 6.9, GOLD, 2.0)
    cy -= 24
    items = [
        ("Age assurance", "UK OSA-aligned measure at entry — verified card, digital ID or age estimation. Logged and reviewed quarterly."),
        ("Performer records", "Photo ID, signed release and scene log for every shoot, retained for seven years."),
        ("Consent & limits", "Agreed in writing. Stop-any-time policy. Footage withheld if consent is withdrawn."),
        ("Payment processing", "Adult-friendly processor approved before public launch, with a published chargeback policy."),
        ("Data protection", "UK GDPR basis for contact data. No ID documents by email. Encrypted storage."),
        ("Content standards", "All performers 18+. No prohibited content. Territory restrictions documented."),
    ]
    for i, (t, b) in enumerate(items):
        yy = cy - i * 56
        c.setFillColor(GOLD)
        c.circle(M + 3, yy + 3, 2.2, stroke=0, fill=1)
        c.setFont(FB, 9.2)
        c.setFillColor(CREAM)
        c.drawString(M + 16, yy, t)
        para(c, M + 16, yy - 13, CW * 0.52 - 16, b, F, 7.7, 10.8, MUTED)

    rx = M + CW * 0.55
    rw = W - M - rx
    tracked(c, rx, 660, "RISK REGISTER", F, 6.9, GOLD, 2.0)
    rows = [["Risk", "Impact", "Mitigation"],
            ["Single-performer dependency", "High", "Profit share, written exit"],
            ["Cadence failure", "High", "Six-scene buffer, flex day"],
            ["Processor withdrawal", "High", "Two processors, clean records"],
            ["Platform reach cut", "Medium", "Owned email list from day one"],
            ["Copycat pricing", "Medium", "Brand, not price, competition"],
            ["Burnout", "Medium", "Four shoot days a week max"]]
    table(c, rx, 638, [rw * 0.46, rw * 0.16, rw * 0.38], rows,
          aligns=["l", "r", "l"], row_h=29, size=7.5)

    # launch gate
    gy = 112
    panel(c, M, gy, CW, 86, PANEL_2, LINE)
    c.saveState()
    c.setFillColor(OXBLOOD)
    c.rect(M, gy, 2.4, 86, stroke=0, fill=1)
    c.restoreState()
    tracked(c, M + 22, gy + 64, "LAUNCH GATE", F, 6.6, ROSE, 1.9)
    para(c, M + 22, gy + 46, CW - 44,
         "The site does not go public, and paid membership does not open, until four things are "
         "true: age assurance is live, the performer record folder is complete, a processor has "
         "approved the account, and a solicitor has reviewed the terms.",
         F, 8.6, 12.2, CREAM_DIM)

    page_furniture(c, 11)


# ----------------------------------------------------------------------------
# 12 — roadmap
# ----------------------------------------------------------------------------
def p_roadmap(c):
    bg(c)
    section_head(c, "10 · ROADMAP & KPIS",
                 "Twelve months, four gates",
                 "Sequenced so nothing is sold before it can be delivered, and nothing is public "
                 "before it is compliant.", CW * 0.80)

    gy = 654
    months = ["J", "F", "M", "A", "M", "J", "J", "A", "S", "O", "N", "D"]
    gx = M + 140
    gw = W - M - gx
    colw = gw / 12.0
    tracked(c, M, gy + 6, "PHASE 2027", F, 6.2, MUTED, 1.6)
    for i, m_ in enumerate(months):
        c.setFont(F, 6.4)
        c.setFillColor(MUTED)
        c.drawCentredString(gx + colw * (i + 0.5), gy + 6, m_)
    rule(c, M, gy - 4, CW, LINE, 0.6)

    phases = [("Soft launch & buffer", 0, 2, GOLD, "Site live, gate on, six scenes banked"),
              ("Three-a-week cadence", 2, 6, GOLD, "Mon / Wed / Fri locked, Saturday drops"),
              ("Membership & PPV", 3, 4, OXBLOOD, "Processor approved, tiers live"),
              ("Commissions & licensing", 7, 5, HexColor("#6E4B5A"), "Partner deals, customs open")]
    for i, (name, start, span, colr, note) in enumerate(phases):
        yy = gy - 30 - i * 46
        c.setFont(FB, 8.8)
        c.setFillColor(CREAM)
        c.drawString(M, yy + 2, name)
        c.setFont(F, 6.6)
        c.setFillColor(MUTED)
        c.drawString(M, yy - 10, note)
        c.saveState()
        c.setFillColor(colr)
        c.setFillAlpha(0.85)
        c.roundRect(gx + colw * start + 2, yy - 4, colw * span - 4, 13, 2, stroke=0, fill=1)
        c.restoreState()

    # KPI grid
    ky = 448
    tracked(c, M, ky, "WHAT TO WATCH MONTHLY", F, 6.9, GOLD, 2.0)
    ky -= 22
    kpis = [("Scenes released", "≥ 13 / month", "The only non-negotiable"),
            ("Buffer depth", "≥ 6 scenes", "Protects the Saturday drop"),
            ("New members", "≥ 55 / month", "From month six"),
            ("Month-2 retention", "≥ 78%", "The real health metric"),
            ("Blended ARPU", "≥ £15", "Price discipline"),
            ("Cost per scene", "≤ £600", "Efficiency guardrail")]
    cw_ = (CW - 2 * 12) / 3
    for i, (t, target, note) in enumerate(kpis):
        col, row = i % 3, i // 3
        x = M + col * (cw_ + 12)
        yy = ky - row * 68
        panel(c, x, yy - 56, cw_, 56, PANEL, LINE)
        c.setFont(F, 8.0)
        c.setFillColor(CREAM)
        c.drawString(x + 15, yy - 18, t)
        c.setFont(FB, 10.4)
        c.setFillColor(GOLD)
        c.drawString(x + 15, yy - 34, target)
        c.setFont(F, 6.6)
        c.setFillColor(MUTED)
        c.drawString(x + 15, yy - 47, note)

    # closing
    cy = 190
    rule(c, M, cy + 62, CW, LINE, 0.6)
    c.setFont(FI, 13.0)
    c.setFillColor(CREAM)
    c.drawString(M, cy + 36, "Three shoots a week is not a slogan. It is the whole plan —")
    c.drawString(M, cy + 16, "and everything else in this document is downstream of hitting it.")
    tracked(c, M, cy - 12, "TWIRLER PICTURES · ESSEX · 2027", F, 6.4, GOLD, 2.0)

    page_furniture(c, 12)


# ----------------------------------------------------------------------------
# build
# ----------------------------------------------------------------------------
def build():
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    c = canvas.Canvas(OUT, pagesize=A4)
    c.setTitle("Twirler Pictures — Business Plan 2027–2029")
    c.setAuthor("Twirler Pictures")
    c.setSubject("Growth plan for a single-performer adult studio")
    c.setKeywords("Twirler Pictures, Lady Carey, business plan, adult studio, 18+")

    bg(c)
    p_cover(c)
    new_page(c, 2);  p_thesis(c)
    new_page(c, 3);  p_market(c)
    new_page(c, 4);  p_positioning(c)
    new_page(c, 5);  p_anchor(c)
    new_page(c, 6);  p_engine(c)
    new_page(c, 7);  p_unit(c)
    new_page(c, 8);  p_financials(c)
    new_page(c, 9);  p_revenue(c)
    new_page(c, 10); p_marketing(c)
    new_page(c, 11); p_risk(c)
    new_page(c, 12); p_roadmap(c)

    c.showPage()
    c.save()
    print("wrote", OUT)


if __name__ == "__main__":
    build()
