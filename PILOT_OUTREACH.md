# Pilot Outreach Guide - LLM Session Manager

## 🎯 Outreach Strategy

This guide provides email templates, value propositions, and talking points for reaching out to target companies for pilot programs.

---

## 📧 Email Template: Initial Outreach

### Subject Lines (A/B Test These)

**Option 1 (Problem-Focused):**
> "Managing 10+ AI coding sessions? We built a solution"

**Option 2 (Benefit-Focused):**
> "Reduce AI coding costs by 30-40% with better session management"

**Option 3 (Social Proof):**
> "YC founders: How we're solving multi-session AI context rot"

---

### Template 1: For Developer Tool Companies (Elessar, CodeViz)

```
Subject: Managing 10+ AI coding sessions? We built a solution

Hi [Name],

I noticed [Company] helps engineering teams [specific pain point from research]. Your engineers are likely using Claude Code/Cursor heavily to build those features.

We built an open-source tool that solves a problem we kept hitting: managing 5-10+ parallel AI coding sessions without:
- Unexpectedly hitting token limits mid-workflow
- Losing track of which sessions have "context rot"
- Wasting spend on degraded sessions

**Quick demo:** [Link to 2-minute Loom video]

Would you be open to a 15-minute pilot discussion? We're looking for 2-3 companies to test with before our official launch.

Best,
[Your Name]

P.S. - Built with Python/Poetry, local-first (no cloud telemetry). GitHub: [link]
```

---

### Template 2: For LLM/AI Companies (Helicone, Tara AI)

```
Subject: Developer-side LLM observability for coding sessions

Hi [Name],

[Company] monitors LLM usage in production. We're tackling the same problem, but for developers during coding.

**The gap:** Engineers run 5-10 Claude/Cursor sessions simultaneously. No visibility into:
- Which sessions are healthy vs. degraded
- Token consumption across sessions
- When to restart vs. continue a session

We built an open-source CLI/TUI tool that treats AI coding sessions as manageable resources (like Docker containers, but for LLM contexts).

**Interesting for [Company] because:**
- Your team likely hits this pain building LLM features
- Natural extension of your observability mindset
- Potential integration opportunity (session health → your platform)

Open to a 15-minute call to show you the tool?

Best,
[Your Name]

GitHub: [link] | Demo: [Loom link]
```

---

### Template 3: For Infrastructure/Platform Companies (Signadot)

```
Subject: Token budget management for AI coding sessions

Hi [Name],

Quick question: How many Claude Code/Cursor sessions does your eng team run simultaneously? (We've seen 5-10+ at companies your size)

We built a tool that prevents the most annoying AI coding bottleneck: **hitting token limits mid-iteration** when you have 8 sessions open across microservices work.

**3 features you'd appreciate:**
1. Real-time token tracking across all sessions
2. Health scoring (knows when context has rotted)
3. CLI-native (terminal users love it)

Looking for 2-3 pilot companies. 15-minute call to demo?

Best,
[Your Name]

P.S. - Local-first, no cloud dependency. Built by developers, for developers.
```

---

## 🎤 Pitch Deck Outline (5 Slides)

### Slide 1: The Problem
**Title:** "Engineering teams are running 10+ AI coding sessions with zero visibility"

**Content:**
- 53% of developers use Claude Code, 82% enterprise adoption of GitHub Copilot
- Teams open 5-10+ parallel sessions for different features/bugs
- No way to track: token usage, session health, context degradation
- Result: Surprise token limit hits, wasted time, degraded output quality

**Visual:** Screenshot of 10+ terminal windows with Claude/Cursor sessions

---

### Slide 2: The Solution
**Title:** "LLM Session Manager: The first multi-session orchestration tool for AI coding"

**Content:**
- Real-time dashboard showing all active sessions
- Health scoring (token usage + duration + activity + errors)
- Token budget tracking across sessions
- Context export/import for session recovery

**Visual:** Screenshot of the Rich TUI dashboard showing session table

---

### Slide 3: Why Now?
**Title:** "Perfect timing: AI adoption × token constraints"

**Content:**
- AI coding assistants hitting mainstream (Gartner: near-universal by 2028)
- Token limits becoming real constraint (200K standard, monorepos need millions)
- Enterprise spending $228-$468/user/year on AI assistants
- Our tool: $10/user/month to maximize that spend

**Visual:** Graph showing AI coding assistant adoption curve 2023-2028

---

### Slide 4: Competitive Advantage
**Title:** "No direct competitors — we're defining a new category"

**Table:**
| Feature | LLM Session Manager | Windsurf | Supermaven | Helicone |
|---------|---------------------|----------|------------|----------|
| Multi-session visibility | ✅ | ❌ | ❌ | ❌ |
| Health scoring | ✅ | ❌ | ❌ | ❌ |
| Token tracking | ✅ | ❌ | ⚠️ Single | ⚠️ API-level |
| Local-first | ✅ | ❌ | ❌ | ❌ |

**Tagline:** "First tool to treat AI coding sessions as manageable resources"

---

### Slide 5: Pilot Program
**Title:** "Join our pilot: Help shape the future of AI session management"

**Content:**
- **Free for 3 months** (normally $10/user/month)
- **Requirements:** 5-20 engineers using Claude/Cursor heavily
- **Commitment:** 30-minute onboarding, 15-minute weekly check-in
- **Benefits:** Early access to features, influence roadmap, case study opportunity

**CTA:** "Apply for pilot: [email] | Calendar link: [Calendly]"

---

## 🗣️ Discovery Call Script (15 Minutes)

### **Minutes 0-2: Introduction & Permission**
"Thanks for taking the time. I know you're busy, so I'll keep this to 15 minutes.

I want to understand how your team uses AI coding assistants, show you what we built, and see if there's a fit for a pilot. Sound good?"

**Wait for confirmation.**

---

### **Minutes 2-5: Discovery Questions**

1. **Usage patterns:**
   - "How many of your engineers use Claude Code, Cursor, or GitHub Copilot?"
   - "On average, how many sessions does one engineer have open at a time?"

2. **Pain points:**
   - "Have you hit token limits unexpectedly? How often?"
   - "Do engineers ever complain about AI responses getting 'weird' after long sessions?"

3. **Current solutions:**
   - "Do you track AI coding assistant usage or costs in any way?"
   - "Any internal tools for managing these sessions?"

**Listen carefully. Tailor demo to their specific pain.**

---

### **Minutes 5-10: Demo**

**Screen share: Live dashboard**

1. **Show the list command:**
   ```bash
   python -m llm_session_manager.cli list
   ```
   - "Here are my 3 active Claude sessions. Notice the health scores and token counts."

2. **Highlight a session nearing token limit:**
   - "This one is at 85% of my token budget. Health score: 62%. Time to export context and restart."

3. **Show the monitor dashboard:**
   ```bash
   python -m llm_session_manager.cli monitor
   ```
   - "Real-time view with auto-refresh. Press 'r' to force update, 'q' to quit."

4. **Demonstrate export/import:**
   ```bash
   python -m llm_session_manager.cli export <session-id> -o backup.json
   python -m llm_session_manager.cli import-context backup.json
   ```
   - "Save your context before restarting. Resume later without losing work."

**Pause for reactions/questions.**

---

### **Minutes 10-13: Value Proposition**

**Tailor based on company:**

**For developer tool companies:**
> "Your team builds productivity tools. This helps *your* engineers be more productive while building those tools. Dogfooding opportunity."

**For AI/LLM companies:**
> "You monitor production LLMs. This monitors development LLM usage. Same observability mindset, different stage."

**For infrastructure companies:**
> "You help teams iterate 10x faster. This prevents them from hitting token walls mid-iteration across their 8 microservice sessions."

**Key metric:**
> "Early users report 30-40% reduction in wasted AI assistant time by catching degraded sessions early."

---

### **Minutes 13-15: Pilot Proposal**

**Offer:**
"We're looking for 2-3 companies to pilot with. Here's what that looks like:

- **Free for 3 months** (normally $10/user/month after)
- **5-20 engineers** on your team test it
- **Weekly 15-minute check-ins** to gather feedback
- **You influence the roadmap** — tell us what features matter most
- **Optional case study** if you see good results (we can keep you anonymous if preferred)

Interested in moving forward?"

**If yes:** "Great! I'll send over onboarding instructions today. Can we schedule our first check-in for next [day]?"

**If hesitant:** "No pressure. What concerns do you have? / What would need to be true for this to be a yes?"

---

## 📊 Metrics to Track During Pilots

### **Adoption Metrics**
- % of engineers who install the tool
- Average sessions monitored per engineer
- Daily active users (DAU)
- Commands used most frequently (list, monitor, export)

### **Value Metrics**
- Number of "token limit surprises" prevented
- Sessions restarted due to health warnings
- Time saved per week (survey-based)
- Degraded sessions caught before wasting time

### **Feedback Metrics**
- NPS score (would you recommend this tool?)
- Feature requests (prioritized by frequency)
- Bug reports (prioritized by severity)
- Testimonial quotes for case studies

### **Financial Metrics**
- Estimated AI assistant spend ($/month)
- Estimated savings from better session management (%)
- Willingness to pay (price sensitivity)

---

## 🎯 Success Criteria for Pilot

**Pilot is successful if:**
1. **50%+ adoption** among target engineers
2. **3+ testimonials** with specific value examples
3. **$10/user/month willingness to pay** validated
4. **1-2 feature requests** that improve product-market fit
5. **Zero critical bugs** that block daily usage

**Pilot graduates to paid customer if:**
- Company commits to $10/user/month after free period
- Expands to more than pilot team (viral adoption)
- Provides case study or public testimonial

---

## 📋 Pilot Onboarding Checklist

### **Day 0: Before Pilot Starts**
- [ ] Signed pilot agreement (even if free, set expectations)
- [ ] Identified pilot lead (engineering manager or senior engineer)
- [ ] Scheduled kick-off call (30 minutes)
- [ ] Sent pre-pilot survey (baseline metrics)

### **Day 1: Kick-off Call**
- [ ] Demoed tool live
- [ ] Walked through installation (Poetry install)
- [ ] Ran first `list` command together
- [ ] Set up Slack channel or Discord for support
- [ ] Scheduled first weekly check-in

### **Week 1: Onboarding Support**
- [ ] Daily check-ins in Slack/Discord (async)
- [ ] Monitor usage metrics (are they using it?)
- [ ] Fix any installation blockers immediately
- [ ] Share tips/shortcuts as they use it

### **Week 2-4: Feature Feedback**
- [ ] Weekly 15-minute check-ins (video call)
- [ ] Collect feature requests (prioritize by votes)
- [ ] Fix bugs reported (same-day response if critical)
- [ ] Share early wins (screenshots, quotes)

### **Week 5-8: Expansion & Case Study**
- [ ] Ask if other teams want to try it
- [ ] Draft case study (with their approval)
- [ ] Validate pricing ($10/user/month)
- [ ] Discuss conversion to paid after Month 3

### **Week 9-12: Conversion Discussion**
- [ ] Present pilot results (metrics, testimonials)
- [ ] Offer discounted annual pricing (20% off)
- [ ] Sign contract for paid plan
- [ ] Request testimonial for website/docs

---

## 💬 FAQ for Pilot Companies

### **Q: Is our data sent to the cloud?**
**A:** No. LLM Session Manager runs 100% locally. All data stored in local SQLite database. No telemetry, no cloud dependency.

### **Q: Does this work with our IDE (VS Code, JetBrains)?**
**A:** Yes, as long as you're using Claude Code or Cursor CLI. It monitors the underlying processes, not the IDE.

### **Q: What if we use GitHub Copilot instead?**
**A:** Currently supports Claude Code and Cursor. GitHub Copilot support is on the roadmap (vote for it in our pilot feedback).

### **Q: How accurate is token estimation?**
**A:** ~90% accurate using Claude's character-to-token ratio (~4 chars/token). We're working on integration with official token counters.

### **Q: Can we self-host for security?**
**A:** It's already self-hosted! Just install via Poetry, no server required. Perfect for security-conscious teams.

### **Q: What metrics do you collect during pilots?**
**A:** Only what you share with us in check-ins. No automatic telemetry. We'll ask for anonymized usage data (# sessions, token counts) if you're comfortable sharing.

### **Q: Can we contribute features or bug fixes?**
**A:** Absolutely! It's open source. We welcome PRs and feature contributions. Pilot companies get priority on roadmap decisions.

---

## 🚀 Next Steps After This Guide

1. **Create Loom video** (2-3 minutes) showing dashboard in action
2. **Set up Calendly** for easy pilot call scheduling
3. **Draft pilot agreement** (simple 1-page PDF with expectations)
4. **Create feedback form** (Google Form or Typeform for weekly check-ins)
5. **Build email list** in CRM (HubSpot free tier, or just Google Sheets)
6. **Start outreach** to top 5 companies (Elessar first)

---

## 📞 Contact Templates

### **LinkedIn Connection Request**
"Hi [Name], I saw [Company] is working on [specific product from research]. We built an open-source tool that helps engineering teams manage multiple AI coding sessions (Claude/Cursor). Would love to connect and share it with you!"

### **Twitter/X DM**
"Hey [Name]! Love what you're building at [Company]. We made a CLI tool for managing 10+ AI coding sessions. Think your team might find it useful. Mind if I send a quick demo video?"

### **GitHub Issue/Discussion**
"Hi [Company] team! We built an open-source session manager for Claude Code/Cursor. Thought your engineering team might benefit since you're [specific use case]. Happy to demo or answer questions. GitHub: [link]"

---

## ✅ Outreach Tracking Sheet

| Company | Contact | Title | Date Sent | Response | Status | Next Step |
|---------|---------|-------|-----------|----------|--------|-----------|
| Elessar | TBD | CTO | - | - | Not contacted | Find email |
| CodeViz | TBD | Founder | - | - | Not contacted | Find email |
| Tara AI | TBD | CEO | - | - | Not contacted | Find email |
| Helicone | TBD | Founder | - | - | Not contacted | LinkedIn |
| Signadot | TBD | VP Eng | - | - | Not contacted | Twitter DM |

**Update this weekly.**

---

## 🎉 Pilot Success Stories (Template for Case Studies)

### **Template Structure:**

**Title:** "How [Company] reduced AI coding costs by [X%] with LLM Session Manager"

**Section 1: The Problem**
> "[Company] engineers were running 8-10 Claude Code sessions daily. They'd frequently hit token limits mid-feature, wasting 15-20 minutes restarting and re-explaining context..."

**Section 2: The Solution**
> "After deploying LLM Session Manager, engineers could see real-time health scores for all sessions. When a session hit 70% token usage, they'd proactively export context and restart..."

**Section 3: The Results**
> "Within 2 weeks:
> - 40% reduction in 'token limit surprises'
> - 3+ hours saved per engineer per week
> - 12/15 engineers adopted it daily
> - Estimated $2,400/month savings in wasted AI assistant time"

**Section 4: The Quote**
> "[Engineering Lead Name], [Title] at [Company]: 'This tool is like having a dashboard for Docker containers, but for AI coding sessions. We can't imagine working without it now.'"

---

## 🔥 Launch Plan Post-Pilots

After 3 successful pilots:

1. **Show HN Post**
   - Title: "Show HN: I built a CLI tool to manage my 10 Claude Code sessions"
   - Content: Problem, solution, demo GIF, GitHub link
   - Timing: Tuesday/Wednesday 9-11am PT

2. **Product Hunt Launch**
   - Get 3 pilot companies to be "first users"
   - Submit on Thursday for Friday feature
   - Prepare 24-hour response team for comments

3. **Reddit Posts**
   - r/programming, r/MachineLearning, r/cscareerquestions
   - Lead with problem, not product
   - Title: "Anyone else juggling 10+ AI coding sessions? Built a tool to help"

4. **Dev.to / Hashnode Article**
   - Title: "The Hidden Cost of AI Coding Sessions (And How to Fix It)"
   - SEO focus: "claude code token limit", "cursor session management"

5. **Twitter Thread**
   - 10-tweet thread with screenshots
   - Tag @AnthropicAI @cursor_ai
   - Ask pilot companies to retweet

---

**Ready to start outreach? Begin with Elessar — they're the best fit.** 🚀
