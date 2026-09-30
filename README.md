<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/header-dark.svg">
  <source media="(prefers-color-scheme: light)" srcset="assets/header-light.svg">
  <img src="assets/header.svg" width="100%" alt="I break AI agents.">
</picture>

**Praneesh R V.** Offensive security and AI red teaming. Final year of B.Tech Cybersecurity at Amrita Vishwa Vidyapeetham, graduating 2027.

I look for the ways multi-agent LLM systems can be talked into doing things they shouldn't: prompt injection, memory poisoning, tool misuse, forged identities passed between agents over MCP and A2A. What I find usually ends up as a CTF challenge or a tool, so other people can practise it too.

### Selected work

**[Agent red-teaming CTF challenges](https://github.com/PraneeshRV/Agent-Redteaming-CTF-challs)**<br>
Two multi-agent challenges: a JSON injection that rides an A2A pipeline into a command-running agent, and poisoned shared memory that gets a task router to hand out privileges. Plus a scanner that fires attack payloads and has an LLM grade the result.<br>
<sub>Python · A2A · sole author</sub>

**[Granzion Labs](https://github.com/SecurinResearch/granzion-labs)**, contributor<br>
Securin's open-source testbed for attacking multi-agent systems. My [two merged PRs](https://github.com/SecurinResearch/granzion-labs/pulls?q=is%3Apr+is%3Amerged+author%3APraneeshRV) add four attack scenarios: token forgery, agent-card forgery, orchestrator task-queue poisoning and delegation loops.<br>
<sub>Python · MCP · A2A · from my research internship at Securin</sub>

**[RedCalibur 2.0](https://github.com/PraneeshRV/Redcalibur2.0)**<br>
Local-first exposure workbench for developer machines. It inventories MCP configs, AI-tool configs and secrets (stored redacted), ranks vulnerable dependencies by CISA KEV and EPSS, and gates every scan on scope and risk tier, with an append-only audit log.<br>
<sub>Python · FastAPI · Next.js</sub>

**[Crucible](https://github.com/PraneeshRV/crucible)**<br>
A falsification gate for AI agents. Before an agent commits to a conclusion that is expensive to get wrong, it has to build a rival explanation, say up front what each result would mean, and land on an explicit verdict instead of a confident guess.<br>
<sub>Agent skill · Python</sub>

Outside security: [Nabhasa](https://praneeshrv.github.io/nabhasa/), my portfolio as a neutron-star system you fly through, and [axec-cli](https://github.com/PraneeshRV/axec-cli), an AppImage launcher for Arch written in Rust.

### CTF

I co-founded [Team Hunter](https://ctftime.org/team/375677), 8th in India on CTFtime for 2026, across 50+ CTFs. Best finishes: CREST 3rd and CryptoNite 5th. I mostly play OSINT, forensics and web.

I led L3m0nCTF 2025 and ran its infrastructure: a 24-hour onsite CTF for 200+ players on Google Cloud, CTFd and Docker. I also wrote its AI-security challenges and its [CTFd theme](https://github.com/PraneeshRV/CTFd-stargaze-theme).

### Background

- **Securin**, research intern in AI red teaming. Sep 2025 to May 2026.
- **Joy IT Solutions**, AI developer intern on an Azure recruitment-agent platform. Apr to Jun 2026.
- **PJPT**, Practical Junior Penetration Tester, TCM Security. 2026.
- **Amrita Vishwa Vidyapeetham**, B.Tech CSE (Cybersecurity). 2023 to 2027.

<sub>Python, Go, Rust, TypeScript · Burp Suite, Ghidra, BloodHound, nmap · Docker, Google Cloud, Azure</sub>

### Elsewhere

[praneeshrv.me](https://praneeshrv.me) · [LinkedIn](https://www.linkedin.com/in/praneesh-r-v-3a81b221a/) · [praneeshrv404@gmail.com](mailto:praneeshrv404@gmail.com)
