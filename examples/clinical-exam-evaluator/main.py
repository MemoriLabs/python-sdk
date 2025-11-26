"""
Clinical Exam Evaluator - MRCPCH Preparation Simulator

This example demonstrates using Memori to evaluate medical candidates against
a clinical competency rubric without building rule engines.

Key Features:
- Automatic extraction of skills, facts, and clinical reasoning from responses
- Rubric-based evaluation using structured memory
- Session-based examination tracking
- Detailed feedback generation

Requirements:
- Environment variables:
  - OPENAI_API_KEY
"""

import os

from dotenv import load_dotenv
from openai import OpenAI
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from memori import Memori

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise RuntimeError("OPENAI_API_KEY is not set")

# SQLite for simplicity (can use any database)
db_path = "./clinical_exam.db"
database_url = f"sqlite:///{db_path}"

client = OpenAI(api_key=api_key)

engine = create_engine(
    database_url,
    pool_pre_ping=True,
    connect_args={"check_same_thread": False},
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

with engine.connect() as conn:
    result = conn.execute(text("SELECT 1")).scalar_one()
    print(f"Database connection OK: {result}")


# Clinical competency rubric
RUBRIC = """
MRCPCH Clinical Competency Rubric:

1. Clinical Knowledge (0-5 points)
   - Demonstrates accurate medical facts and information
   - References appropriate guidelines and evidence
   - Shows depth of understanding

2. Clinical Skills (0-5 points)
   - Describes proper examination techniques
   - Identifies appropriate procedures
   - Demonstrates practical competency

3. Communication (0-5 points)
   - Clear explanation to patient/family
   - Active listening and empathy
   - Appropriate language for audience

4. Clinical Reasoning (0-5 points)
   - Logical diagnostic approach
   - Considers differential diagnoses
   - Evidence-based decision making

5. Professionalism (0-5 points)
   - Patient-centered care
   - Ethical considerations
   - Safety awareness
"""


def conduct_examination(mem, candidate_id, scenario):
    """Conduct a clinical examination scenario"""
    print("\n" + "=" * 80)
    print("CLINICAL SCENARIO")
    print("=" * 80)
    print(f"\n{scenario}\n")
    print("=" * 80)

    # Examiner asks the scenario question
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": "You are a clinical examiner conducting an MRCPCH examination. "
                "Present the scenario and ask the candidate to explain their approach.",
            },
            {"role": "user", "content": scenario},
        ],
    )

    examiner_question = response.choices[0].message.content
    print(f"\nEXAMINER: {examiner_question}\n")

    # Simulate candidate response (in real app, this would be voice input)
    print("CANDIDATE: ", end="", flush=True)
    candidate_input = input()

    # Store the exchange - Memori automatically extracts skills, facts, reasoning
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "assistant", "content": examiner_question},
            {"role": "user", "content": candidate_input},
        ],
    )

    # Memori has now extracted and stored:
    # - Clinical skills mentioned
    # - Medical facts stated
    # - Clinical reasoning demonstrated
    # - Communication style
    mem.config.storage.adapter.commit()

    return candidate_input


def evaluate_candidate(mem, candidate_id):
    """Evaluate candidate using rubric + structured memories from Memori"""
    print("\n" + "=" * 80)
    print("EVALUATION")
    print("=" * 80)

    # This prompt will be augmented by Memori with relevant extracted memories
    evaluation_prompt = f"""
You are evaluating a medical candidate's performance in a clinical examination.

{RUBRIC}

Based on the candidate's responses and demonstrated competencies, provide:
1. Score for each rubric category (0-5)
2. Specific observations from their responses
3. Strengths identified
4. Areas for improvement
5. Overall feedback

Be specific and reference actual things the candidate said or demonstrated.
"""

    # Memori retrieves relevant structured memories (skills, facts, reasoning)
    # and includes them in the context automatically
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": "You are a clinical examiner providing detailed evaluation and feedback.",
            },
            {"role": "user", "content": evaluation_prompt},
        ],
    )

    evaluation = response.choices[0].message.content
    print(f"\n{evaluation}\n")
    print("=" * 80)

    mem.config.storage.adapter.commit()


if __name__ == "__main__":
    # Register OpenAI client with Memori
    mem = Memori(conn=SessionLocal).openai.register(client)

    # Attribution: candidate is the entity, clinical-exam is the process
    candidate_id = "candidate_001"
    mem.attribution(entity_id=candidate_id, process_id="mrcpch-clinical-exam")

    # Build database schema
    mem.config.storage.build()

    print("\n" + "=" * 80)
    print("MRCPCH CLINICAL EXAM PREPARATION SIMULATOR")
    print("=" * 80)
    print(f"\nCandidate ID: {candidate_id}")
    print("Session started - All responses will be evaluated against the rubric\n")

    # Clinical scenario
    scenario = """
A 3-year-old child presents to the emergency department with a 2-day history of fever (39°C),
refusing to eat, and drooling. The child is sitting upright and leaning forward.
Parents report the child is making a muffled voice and having difficulty breathing.

What is your immediate assessment and management approach?
"""

    try:
        # Conduct examination
        candidate_input = conduct_examination(mem, candidate_id, scenario)

        # Evaluate using rubric + Memori's structured memories
        print(
            "\nEvaluating candidate... Memori will retrieve extracted skills, facts, and reasoning.\n"
        )
        evaluate_candidate(mem, candidate_id)

        print(f"\n✓ Examination session saved to: {db_path}")
        print(
            "  Memori has stored structured memories that can be used for future evaluations.\n"
        )

    except KeyboardInterrupt:
        print("\n\nExamination interrupted.")
    except Exception as e:
        print(f"\nError: {e}")
    finally:
        if mem.config.storage.adapter:
            mem.config.storage.adapter.close()
