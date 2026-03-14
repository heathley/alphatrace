# AlphaTrace AI 
**"Don't follow the hype, follow the commits."**

AlphaTrace AI is an autonomous **Market Intelligence Engine** designed to surface early-stage technical alpha by tracking developer velocity, academic research, and predictive market signals. 

Built for the **Nous Research Hackathon 2026** 🏆

---

### Multimodal Signal Intelligence
AlphaTrace aggregates and processes signals from four essential market layers:

1. **Developer Signals (GitHub)**  
   Tracks newly created repositories over the last 14 days across technology sectors such as AI agents, multi-agent systems, zkML, DePIN, and RWA.

2. **Ecosystem Signals (Market News)**  
   Monitors real-time industry developments through aggregated feeds from sources such as CoinDesk, The Block, and CryptoPanic.

3. **Research Signals (ArXiv)**  
   Observes newly published academic papers related to cryptography, distributed systems, and AI agents.

4. **Market Expectations (Prediction Markets)**  
   Tracks probability signals from prediction markets such as Polymarket to understand collective expectations around major ecosystem events.

---

### ## Signal Filtering
AlphaTrace applies a strict filtering pipeline to reduce noise:
- **Crypto-Native Verification:** Automatically disqualifies non-industry projects (e.g., generic tools, FPS tweaks, PDF utilities).
- **Narrative Isolation:** Prevents "AI Leakage" into other categories like DePIN or zkML using strict keyword-description validation.

---

### Alpha Score Model
AlphaTrace estimates developer momentum using a time-normalized scoring model.

`SCORE = BASE(30) + ( (STARS × 0.5) + (FORKS × 2) ) / (DAYS + 3)`

- **"A star signals interest; a fork signals intent."**
- **Forks are weighted 4x more than stars** to focus on genuine engineering activity.
- **Time Normalization:** The `DAYS + 3` factor stabilizes scores for extremely new repositories, filtering out short-term noise.

---

### Built with Hermes Agent
This project was developed using an **agent-assisted engineering workflow** powered by Hermes Agent. Architectural design, taxonomy construction, and filtering logic were iteratively developed through agent collaboration.
---

### Production & Automation

- **Automated Updates:** GitHub Actions runs the AlphaTrace signal pipeline on a scheduled basis.
- **Data Pipeline:** `alpha_tracker.py` collects signals and updates `data/data.js`.
- **Frontend:** Lightweight dashboard built with HTML, Tailwind CSS, and JavaScript.
- **Data Sync:** Updated data is committed automatically and served to the dashboard.
*Designed for the next generation of crypto and AI ecosystem analysts.*
