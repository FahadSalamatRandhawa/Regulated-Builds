import streamlit as st
from sentence_transformers import SentenceTransformer
from supabase import create_client
import google.generativeai as genai
import os
from datetime import datetime
import json

# Suggested test questions
demo_questions = [
    {
        "question": "An HVAC technician is working on a low-slope roof where roofers are using a 6-ft warning line. Can the HVAC worker enter the warning line zone without a harness?",
        "why_llm_fails": "General models may assume the 6-ft warning line applies to all workers, missing that this exemption is only valid for roofing work.",
        "correct_answer": "No. The 6-ft warning line under §1926.501(b)(10) applies only to roofing workers. HVAC or other trades need fall protection or must work 15 ft from the edge. (LOI 20021115)"
    },
    {
        "question": "A crew is erecting precast concrete wall panels, but says guardrails or PFAS would interfere with panel alignment. Can they skip conventional fall protection?",
        "why_llm_fails": "A general LLM might incorrectly claim that fall protection is always required above 6 feet, without considering infeasibility exceptions or the precast erection context.",
        "correct_answer": "Yes, but only if the employer creates a site-specific fall protection plan per §1926.502(k). This is allowed only as a last resort and OSHA will closely scrutinize feasibility claims. (LOI 20030926)"
    },
    {
        "question": "A rebar cage is assembled on the ground and lifted vertically. Workers connect it while it's suspended. Is fall protection needed?",
        "why_llm_fails": "An LLM may confuse this with in-place rebar exceptions or misclassify it as scaffold work, failing to address suspended assembly rules.",
        "correct_answer": "Yes. Once suspended, any worker exposed to a fall of 6 feet or more must have fall protection per §1926.501(b)(5). Exceptions apply only to rebar built in place. (LOI 19950620)"
    },
    {
        "question": "A worker crosses a concrete slab with a 70-ft by 7-ft depression that is 33 inches deep. Does this count as a hole requiring protection?",
        "why_llm_fails": "LLMs might say no fall protection is needed because the depression is less than 6 feet deep, ignoring OSHA's hole classification logic.",
        "correct_answer": "Yes. Due to its large area and depth, OSHA considers it a hole requiring protection (cover or guardrails) under §1926.501(b)(4)(ii). (LOI 20040930)"
    },
    {
    "question": "During leading edge work, there’s no wall to tie off a control line near the edge. Can a controlled access zone still be used?",
    "why_llm_fails": "Most LLMs might think you must tie control lines directly to the edge or abandon the CAZ altogether.",
    "correct_answer": "Yes. According to LOI 20091008, control lines for a CAZ may be tied to temporary stanchions located up to 10 feet from the edge, as long as they restrict access and meet other criteria under §1926.501(b)(2)(i)."
    }
]


# === Setup your API keys via Streamlit secrets or environment variables ===
SUPABASE_URL = st.secrets['SUPABASE_URL']
SUPABASE_KEY = st.secrets['SUPABASE_KEY']
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

model = SentenceTransformer("intfloat/e5-base-v2")
gemini = genai.GenerativeModel("gemini-2.5-pro")

st.set_page_config(
    page_title="Regulated Builds – AI Compliance for Construction",
    layout="centered"
)


st.title("🏗️ Regulated Builds")
st.markdown("**AI-powered regulatory compliance for the construction industry.**")
st.markdown("Instantly analyze OSHA, fire codes, permits, and violations for your projects.")
st.markdown("---")
st.markdown("📍 *We're building the regulatory OS for construction.*")


with st.sidebar:
    st.title("🏗️ Regulated Builds")
    st.markdown("**AI-powered compliance for the built world.**")
    st.markdown("*We're building the regulatory operating system for construction.*")
    st.markdown("---")

    st.title("🛠️ Product Roadmap")

    st.markdown("### 🚧 Phase 1: Core Compliance Engine (Now)")
    st.markdown("""
- ✅ Top 10 OSHA Citations + LLM Analysis (2/10 Covered + LOIs)
- 🔄 Match Regulations ↔ Letters of Interpretation
- 📤 Upload Docs for Permit + Violation Detection
- 🧪 Clause Filtering (e.g., fall hazards, PPE)
    """)

    st.markdown("### 🔥 Phase 2: Smart Analysis & Expansion")
    st.markdown("""
- 🔥 Fire Code Parsing & Search
- 📚 Full OSHA Subparts Coverage
- 🧠 Predict Common Violations for Projects
- 📝 Auto-generate Fall Protection Plans (502(k))
    """)

    st.markdown("### 🧰 Phase 3: Workflow Automation")
    st.markdown("""
- 🛂 Permit Requirements Based on Docs
- ✍️ Auto-Apply via E-permit APIs
- 🧾 Track Permit Status by Jurisdiction
    """)

    st.markdown("### 🏗️ Phase 4: Industry Platform Vision")
    st.markdown("""
- 🏛️ Map Agencies by Region + Regulation
- 📋 Auto-Generated Pre-Inspection Checklists
- 📊 Compliance Dashboards for Firms
- 🤖 AI Superintendent Agent (Full Site Scan)
    """)

    st.markdown("---")
    st.markdown("💬 *We're building the regulatory OS for construction.*")


query = st.text_input("🔍 Ask an OSHA-related question:", placeholder="e.g. Are there exceptions to the requirement for safety nets?")
answer_mode = st.radio(
    "🤖 Choose answer source:",
    options=["Regulated Builds", "Raw Gemini"],
    horizontal=True
)

with st.expander("📋 Suggested Test Questions (LLM Challenge Set)", expanded=False):
    for idx, q in enumerate(demo_questions, 1):
        st.markdown(f"### ❓ Q{idx}: {q['question']}")
        st.markdown(f"🔸 **Why LLMs Fail:** {q['why_llm_fails']}")
        st.markdown(f"✅ **Correct Answer:** {q['correct_answer']}")
        st.markdown("---")


if st.button("Search"):
    if not query:
        st.warning("❗ Please enter a question before searching.")
        st.stop()  # ⛔ Stops the app right here

    st.write(f"🔎 Searching for: **{query}**")

    if answer_mode == "Regulated Builds":
        with st.spinner("🔍 Searching regulations..."):
            embedding = model.encode([query], normalize_embeddings=True)[0]
            embedding_array = list(map(float, embedding))
            response = supabase.rpc("match_supporting_docs_grouped", {
                "query_embedding": embedding_array,
                "match_count": 5
            }).execute()
            clauses = response.data or []

        st.subheader("📘 Relevant OSHA Clauses")
        context_blocks = []
        for clause in clauses:
            with st.expander(f"🔹 {clause['clause_section_id']}: {clause['clause_title']}"):
                st.markdown(f"**Summary:** {clause['clause_summary']}")
                st.markdown(f"**Violations (FY2024):** {clause.get('violations_fy2024', 'N/A')}")
                st.markdown(f"**Hazard Type:** {clause.get('hazard_type', 'N/A')}")
                st.markdown(f"**Applies To:** {', '.join(clause.get('applies_to', []) or [])}")
                st.markdown(f"**Protective Equipment:** {clause.get('protective_equipment', 'N/A')}")
                clause_block = f"""
🔹 {clause['clause_section_id']}: {clause['clause_title']}
Summary: {clause['clause_summary']}
Violations (FY2024): {clause.get('violations_fy2024', 'N/A')}
Hazard Type: {clause.get('hazard_type', 'N/A')}
Applies To: {', '.join(clause.get('applies_to', []) or [])}
Protective Equipment: {clause.get('protective_equipment', 'N/A')}
""".strip()

                doc_blocks = []
                for doc in clause.get("support_docs", []):
                    with st.expander(f"📄 {doc.get('support_title', 'N/A')} | {doc.get('support_publication_date', 'N/A')}"):
                        st.markdown("---")
                        st.markdown(f"✅ **Supporting Document: {doc['support_title']}**")
                        st.markdown(f"• **Summary:** {doc['support_summary']}")
                        st.markdown(f"• **Compliance Guidance:** {doc.get('support_compliance_guidance', '')}")
                        st.markdown(f"• **Enforcement Notes:** {doc.get('support_enforcement_notes', '')}")
                        st.markdown(f"• **Revised Date:** {doc.get('support_revised_date', 'N/A')}")
                        st.markdown(f"• **Publication Type:** {doc.get('support_publication_type', 'N/A')}")
                        st.markdown(f"• **URL:** {doc['support_url']}")
                        doc_blocks.append(f"""
            ✅ Support Doc: {doc['support_title']}
            - Summary: {doc['support_summary']}
            - Guidance: {doc.get('support_compliance_guidance', '')}
            - Notes: {doc.get('support_enforcement_notes', '')}
            - URL: {doc['support_url']}
            - Related Sections: {doc.get('support_related_sections', 'N/A')}
            - Type: {doc.get('support_publication_type', 'N/A')}
            - Published: {doc.get('support_publication_date', 'N/A')}
            """.strip())

            full_block = f"{clause_block}\n\n" + "\n\n".join(doc_blocks)
            context_blocks.append(full_block)

    # Set a prompt based on Type
    if answer_mode == "Regulated Builds":
        prompt = f"""
You are a top-tier OSHA compliance advisor assisting field professionals, safety officers, and legal teams.

Your task is to answer the user’s question with clarity, precision, and regulatory grounding — using only the information provided in the **clause summaries**, **supporting documents**, and **enforcement notes**.

**Your response must:**
1. Be written in **clear, practical English** suitable for field decision-makers.
2. Explicitly cite the applicable **OSHA section ID(s)** (e.g., `1926.501(b)(11)`).
3. State whether the rule is **mandatory**, **conditional**, or **guidance only**.
4. Identify **who it applies to** and **where** (if applicable).
5. Include any **exceptions**, **scope limitations**, or **state plan differences**.
6. Indicate the **likelihood of citation or violation**, based on past enforcement patterns or violation frequency.
7. Highlight **common compliance pitfalls**, enforcement notes, or case-by-case considerations.
8. Never assume or invent interpretations — if unclear, write: `"Not clear from provided context."`

---

❓ **User Question**:
{query.strip()}

---

📘 **Regulatory Context**:
{'\n'.join(context_blocks)}

---

💬 **Answer**:
"""
    else:
        prompt = f"""
You are a top-tier OSHA compliance advisor assisting field professionals, safety officers, and legal teams.

Your task is to answer the user’s question with clarity, precision, and regulatory grounding — using only the information provided in the **clause summaries**, **supporting documents**, and **enforcement notes**.

**Your response must:**
1. Be written in **clear, practical English** suitable for field decision-makers.
2. Explicitly cite the applicable **OSHA section ID(s)** (e.g., `1926.501(b)(11)`).
3. State whether the rule is **mandatory**, **conditional**, or **guidance only**.
4. Identify **who it applies to** and **where** (if applicable).
5. Include any **exceptions**, **scope limitations**, or **state plan differences**.
6. Indicate the **likelihood of citation or violation**, based on past enforcement patterns or violation frequency.
7. Highlight **common compliance pitfalls**, enforcement notes, or case-by-case considerations.
8. Never assume or invent interpretations — if unclear, write: `"Not clear from provided context."`

---
Question:
{query}

---
Answer:
"""    
    
    with st.spinner("Generating a response..."):
        try:
            if answer_mode == "Regulated Builds":
                genai.configure(api_key=st.secrets['GEMINI_KEY_1'])
            else:
                genai.configure(api_key=st.secrets['GEMINI_KEY_2'])
            gemini_response = gemini.generate_content(prompt)
            answer = gemini_response.text.strip()
            st.subheader("💬 Answer")
            st.markdown(answer)

            if "helpful_count" not in st.session_state:
                st.session_state.helpful_count = 0

            if st.button("👍 Was this helpful?"):
                st.session_state.helpful_count += 1
            st.markdown(f"**Helpful Votes:** {st.session_state.helpful_count}")

            st.download_button(
                "📥 Export Answer",
                data=answer,
                file_name=f"OSHA_Answer_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                mime="text/plain"
            )

        except Exception as e:
            st.error("❌ Gemini failed to generate a response. Please try again or check back later.")
            st.code(str(e), language="python")
st.markdown("---")
st.markdown("📌 **Regulated Builds** is building the first AI-powered compliance layer for the construction industry — from OSHA to permits to inspections.")

