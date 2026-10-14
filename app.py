import streamlit as st
from llm import ask_ai
from pypdf import PdfReader
import os
import json
from dotenv import load_dotenv
from google import genai
from coach import analyze_profile, generate_questions, evaluate_answers, final_report

#next application title
st.title("AI Interview Coach")

#to define pdf - reading function
#extract from all the pages 
def read_pdf(file):
    reader=PdfReader(file)
    text=""

    for page in reader.pages:
        text += page.extract_text() or ""
    return text

#to allow users to upload a resume
resume_file=st.file_uploader("Upload your Resume (PDF)!!",type="pdf")

#to allow user to paste the job description
job_description=st.text_area("Paste the job description",height=200)

#to process the resume 
if resume_file:
    resume_text=read_pdf(resume_file)
    if resume_text.strip()=="":
        st.error("Is empty or could not be read" 
                 "Try another file"
                )
    else:
        st.success("Uploaded!!")
        with st.expander("See extracted text"):
            st.text(resume_text)

# Step 4.3 - 2: analyze profile
if resume_file and resume_text.strip():
    if st.button("Analyze my profile"):
        if job_description.strip() == "":
            st.warning("Please paste a job description first.")
        else:
            with st.spinner("Analyzing your profile..."):
                st.session_state.pop("questions", None)
                st.session_state.resume_text = resume_text
                st.session_state.job_description = job_description
                st.session_state.analysis = analyze_profile(
                    resume_text,
                    job_description
                )

# Step 4.3 - 3: show analysis
if "analysis" in st.session_state:
    a = st.session_state.analysis
    st.header(f"Profile analysis: {a.get('role', 'Role')}")
    st.metric("Match score", f"{a.get('match_score', 0)}%")
    st.write(a.get("summary", ""))

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Matching skills")
        for skill in a.get("matching_skills", []):
            st.write("-", skill)
    with col2:
        st.subheader("Missing skills")
        for skill in a.get("missing_skills", []):
            st.write("-", skill)

    with st.expander("See raw JSON from the AI"):
        st.json(a)

#to analyze resume with both inputs
if resume_file and job_description:
    #to display a button 
    if st.button("Analyze Resume"):
        # prompt for detailed interview coach feedback

        prompt=f"""
        You are an expert interview coach 
        Analyze the candidate's resume against the job description.

        RESUME:
        {resume_text}

        JOB_DESCRIPTION:
        {job_description}

        Provide:
        1. A short summary of the candidate.
        2. Key skills found in the resume.
        3. Skills required by the job description.
        4. Matching skills.
        5. Missing skills.
        6. Overall suitability for the role.
        7. Areas the candidate should prepare for the interview.
        """
        
        #to send prompt to gemini
        Analysis=ask_ai(prompt)

        #to display analysis
        st.subheader("Resume Analysis")
        st.write(Analysis)


#loading the api key
load_dotenv()

#connect to gemini
client=genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

#choose the model
MODEL="gemini-3.5-flash-lite"


# Step 5 Part 4: question-generation section
# (Part 3's line "st.session_state.interview_started = False" is included here)
if "analysis" in st.session_state:
    st.divider()
    st.header("Interview questions")
    num = st.slider("How many questions?", 3, 10, 5)

    if st.button("Generate questions"):
        st.session_state.interview_started = False
        with st.spinner("Writing questions for you..."):
            result = generate_questions(
                st.session_state.analysis,
                st.session_state.resume_text,
                st.session_state.job_description,
                num,
            )
            st.session_state.questions = result.get("questions", [])

if "questions" in st.session_state:
    for i, q in enumerate(st.session_state.questions, start=1):
        st.markdown(f"**Q{i}.** {q.get('question')}")
        st.caption(f"Type: {q.get('type')} | Skill: {q.get('skill')}")

# Step 6 Part 1 (+ Step 7 Part 4: clear previous evaluations)
if "questions" in st.session_state and st.session_state.questions:
    if st.button("Start interview"):
        st.session_state.pop("evaluations", None)
        st.session_state.pop("report", None)
        first_q = st.session_state.questions[0]["question"]
        st.session_state.interview_started = True
        st.session_state.current_q = 0
        st.session_state.messages = [{
            "role": "assistant",
            "content": f"**Q1.** {first_q}"
        }]
        st.session_state.answers = []
        st.rerun()

# Step 6 Part 2: interview flow
if "questions" in st.session_state and st.session_state.get("interview_started"):
    st.divider()
    st.header("Interview")
    questions = st.session_state.questions
    current = st.session_state.current_q
    total = len(questions)

    st.progress(current / total, text=f"Answered {current} of {total}")

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if current < total:
        answer = st.chat_input("Type your answer...")
        if answer:
            q = questions[current]
            st.session_state.messages.append({"role": "user", "content": answer})
            st.session_state.answers.append({
                "question": q.get("question"),
                "type": q.get("type"),
                "skill": q.get("skill"),
                "answer": answer,
            })
            st.session_state.current_q += 1
            nxt = st.session_state.current_q
            if nxt < total:
                next_text = f"**Q{nxt + 1}.** {questions[nxt]['question']}"
            else:
                next_text = "That's the end of the interview. Thank you!"
            st.session_state.messages.append({"role": "assistant", "content": next_text})
            st.rerun()
    else:
        st.success("Interview complete! Your answers are saved.")

# Step 7 Part 5: evaluation button and results
if (
    st.session_state.get("interview_started")
    and st.session_state.get("answers")
    and st.session_state.current_q >= len(st.session_state.questions)
):
    if st.button("Evaluate my answers"):
        with st.spinner("Evaluating your answers..."):
            result = evaluate_answers(
                st.session_state.answers,
                st.session_state.analysis.get("role", "this role")
            )
            st.session_state.evaluations = result.get("evaluations", [])

if "evaluations" in st.session_state:
    st.divider()
    st.header("Interview feedback")
    for i, item in enumerate(st.session_state.evaluations, start=1):
        st.subheader(f"Question {i}")
        st.write(f"Relevance: {item.get('relevance', 0)}/10")
        st.write(f"Depth: {item.get('depth', 0)}/10")
        st.write(f"Clarity: {item.get('clarity', 0)}/10")
        st.write(f"Examples: {item.get('examples', 0)}/10")
        st.write(item.get("feedback", ""))
        st.info(item.get("better_answer_tip", ""))

# Step 7 Part 6: final scorecard and improvement plan
if st.session_state.get("interview_started") and "evaluations" in st.session_state:
    st.divider()
    st.header("Final scorecard")

    evals = st.session_state.evaluations
    # Only change from the doc: the doc used e["score"], which does not exist
    # in the evaluations and raises a KeyError. This averages the 4 rubric scores.
    overall = round(
        sum(
            (e.get("relevance", 0) + e.get("depth", 0)
             + e.get("clarity", 0) + e.get("examples", 0)) / 4
            for e in evals
        ) / len(evals),
        1,
    )

    if overall >= 7.5:
        readiness = "Ready for interviews"
    elif overall >= 5:
        readiness = "Almost ready; more practice recommended"
    else:
        readiness = "More practice needed"

    col1, col2 = st.columns(2)
    col1.metric("Interview score", f"{overall}/10")
    col2.metric(
        "Resume match",
        f"{st.session_state.analysis.get('match_score', 0)}%"
    )
    st.subheader(readiness)

    st.markdown("#### Score by rubric area")
    for area in ["relevance", "depth", "clarity", "examples"]:
        avg = sum(e.get(area, 0) for e in evals) / len(evals)
        st.write(f"{area.title()}: {avg:.1f}/10")
        st.progress(min(avg / 10, 1.0))

    if st.button("Get my improvement plan"):
        with st.spinner("Preparing your personal feedback..."):
            st.session_state.report = final_report(
                st.session_state.analysis,
                st.session_state.answers,
                evals,
            )

    if "report" in st.session_state:
        report = st.session_state.report
        st.markdown("#### Strengths")
        for item in report.get("strengths", []):
            st.write("-", item)
        st.markdown("#### Areas to improve")
        for item in report.get("improvements", []):
            st.write("-", item)
        st.markdown("#### Study plan")
        for item in report.get("study_plan", []):
            st.write("-", item)
        st.success(report.get("message", ""))

        lines = [
            "AI INTERVIEW COACH - SCORECARD",
            f"Role: {st.session_state.analysis.get('role', '')}",
            f"Interview score: {overall}/10",
            f"Resume match: {st.session_state.analysis.get('match_score', 0)}%",
            f"Readiness: {readiness}",
            "", "STRENGTHS:",
            *[f"- {x}" for x in report.get("strengths", [])],
            "", "AREAS TO IMPROVE:",
            *[f"- {x}" for x in report.get("improvements", [])],
            "", "STUDY PLAN:",
            *[f"- {x}" for x in report.get("study_plan", [])],
        ]
        st.download_button(
            "Download scorecard",
            "\n".join(lines),
            file_name="interview_scorecard.txt",
        )