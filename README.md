# ai-kill-switch-survival
A high-stakes, 60-second survival game for RSA 2026. Spot AI hallucinations and rogue code before they hit production.


# 🚨 The AI Kill-Switch Challenge (RSA 2026)

### "Speed vs. Security: Can you stop a rogue AI pipeline?"

## 🚀 The Vision
As AI agents accelerate the software development lifecycle (SDLC), the risk of "confidently wrong" code increases. **The AI Kill-Switch** is a high-pressure survival game designed for the Endor Labs RSA W Lounge. It demonstrates that without **Reachability Analysis**, security becomes a series of costly "fire drills" and false alarms.



## 🎯 The Core Logic: Signal vs. Noise
Most security tools flag every vulnerability (Noise). Endor Labs finds the ones that can actually be executed (Signal). This game proves that distinction:

1. **The Signal:** Attendees must kill the pipeline when they see Typosquats or Logic Bombs.
2. **The Noise:** If an attendee kills the pipeline for an **unreachable** vulnerability, they are penalized. 
   - *Lesson:* Halting production for unreachable code is a business failure.

## 🛠 Tech Stack & Logistics
- **Frontend:** Streamlit (Python)
- **Deployment:** GitHub Codespaces (One-Click Setup)
- **Hardware Interface:** Compatible with any USB HID "Big Red Button" (mapped to Spacebar).
- **Vibe:** "Hacker House" Dark Mode with real-time code streaming.

## 🏁 How to Run
1. Open this repo in **GitHub Codespaces**.
2. Run `pip install -r requirements.txt`.
3. Run `streamlit run app.py`.
