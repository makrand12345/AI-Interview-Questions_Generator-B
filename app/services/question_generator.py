from app.core.inference_client import inference_client
from typing import Optional
import re

class QuestionGenerator:
    """
    NLP Service that orchestrates prompt engineering for interview question generation.
    Uses Resume Bifurcation to generate experience-linked technical questions.
    """

    def _bifurcate_context(self, text: Optional[str]) -> dict:
        """
        Internal logic to split resume text into logical buckets for the LLM.
        """
        if not text:
            return {"skills": "N/A", "experience": "N/A"}
        
        # Simple extraction logic using common keywords
        text_lower = text.lower()
        parts = {"skills": "", "experience": ""}
        
        # Look for markers to separate skills from the rest
        skills_idx = text_lower.find("skills")
        exp_idx = text_lower.find("experience")
        
        if skills_idx != -1:
            # Take a chunk starting from 'skills'
            end_idx = exp_idx if exp_idx > skills_idx else len(text)
            parts["skills"] = text[skills_idx:end_idx].strip()
        
        if exp_idx != -1:
            parts["experience"] = text[exp_idx:].strip()
        else:
            # If no experience header found, provide the full text as fallback
            parts["experience"] = text
            
        return parts

    async def create_questions(
        self, 
        job_role: str, 
        seniority_level: str, 
        job_description: Optional[str] = None, 
        resume_text: Optional[str] = None
    ) -> str:
        
        # 1. BIFURCATE the resume text for high-precision targeting
        bifurcated = self._bifurcate_context(resume_text)
        
        # 2. Construct the high-density system prompt
        system_prompt = (
            "SYSTEM ROLE: You are an elite Technical Hiring Manager at a Tier-1 Tech Company. "
            f"TASK: Generate 10 highly specific interview questions for a {seniority_level} {job_role}. "
            "\nINTERVIEW STRATEGY:"
            "\n1. Analyze 'RESUME SKILLS' to identify the candidate's core stack."
            "\n2. Analyze 'RESUME EXPERIENCE' to find specific projects or roles."
            "\n3. GRILLING LOGIC: 5 questions must be deep-dive technical scenarios based on their listed experience. "
            "(Example: 'In your project [X], why did you choose [Y] over [Z]?')"
            "\n4. 5 questions must validate core fundamentals required for the Job Role."
            "\n5. If the input is insufficient, generate 10 clarification questions about their background."
            "\n\nSTRICT OUTPUT RULES:"
            "\n- Output EXACTLY 10 questions."
            "\n- Use a numbered list (1. to 10.)."
            "\n- NO introductory text, NO category headers, NO bold labels like 'Scenario:'. "
            "\n- Output ONLY the raw list of questions."
        )

        context_block = (
            f"--- TARGET ROLE ---\n"
            f"Role: {job_role}\n"
            f"Seniority: {seniority_level}\n\n"
            f"--- BIFURCATED RESUME DATA ---\n"
            f"RESUME SKILLS: {bifurcated['skills'] if bifurcated['skills'] else 'N/A'}\n"
            f"RESUME EXPERIENCE: {bifurcated['experience'] if bifurcated['experience'] else 'N/A'}\n\n"
            f"--- JOB DESCRIPTION ---\n"
            f"{job_description if job_description else 'N/A'}"
        )

        full_prompt = f"{system_prompt}\n\n{context_block}"

        # 3. Call the inference client (Qwen 2.5 Coder 32B)
        raw_output = await inference_client.generate_text(full_prompt)
        
        return raw_output

# Helper functions for post-processing
def enforce_exactly_10(raw_text: str) -> list[str]:
    questions = re.findall(r'^\s*\d+\.\s*(.+)', raw_text, re.MULTILINE)
    if len(questions) != 10:
        # Fallback: simple split if regex fails
        questions = [q.strip() for q in raw_text.split('\n') if q.strip() and q[0].isdigit()]
    return questions[:10]

question_service = QuestionGenerator()