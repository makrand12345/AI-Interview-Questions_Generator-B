from app.core.inference_client import inference_client
from typing import Optional
import re

class QuestionGenerator:
    """
    NLP Service that bifurcates resume text and JD requirements to generate 
    targeted interview questions with strict seniority guardrails.
    """

    def _bifurcate_resume(self, text: Optional[str]) -> dict:
        """
        Extracts specific sections from raw text to focus the AI.
        """
        if not text:
            return {"skills": "N/A", "experience": "N/A"}
        
        # Normalize text
        clean_text = re.sub(r'\s+', ' ', text)
        text_lower = clean_text.lower()
        
        parts = {"skills": "", "experience": ""}
        
        # Regex to find Skills and Experience sections
        skills_match = re.search(r'(skills|technologies|tools)(.*?)(experience|work|employment|education|$)', text_lower, re.DOTALL)
        exp_match = re.search(r'(experience|work history|employment|projects)(.*)', text_lower, re.DOTALL)
        
        if skills_match:
            parts["skills"] = clean_text[skills_match.start(2):skills_match.end(2)].strip()
        
        if exp_match:
            parts["experience"] = clean_text[exp_match.start(2):].strip()[:2000] # Buffer limit
            
        return parts

    async def create_questions(
        self, 
        job_role: str, 
        seniority_level: str, 
        job_description: Optional[str] = None, 
        resume_text: Optional[str] = None
    ) -> str:
        
        # 1. BIFURCATE text into Experience and Skills
        data = self._bifurcate_resume(resume_text)

        # 2. Define Seniority Guardrails
        # This mapping prevents a 'Fresher' from getting 'Senior' questions even if the JD is for a Lead role.
        seniority_logic = {
            "Fresher": "Focus on syntax, fundamentals, academic projects, and bug-fixing. Do NOT ask about leadership or system architecture.",
            "Experienced": "Focus on mid-level execution, independent feature delivery, and optimization of existing codebases.",
            "Mid-level": "Focus on design patterns, API integration, and code quality standards.",
            "Senior": "Focus on system design, scalability, mentoring, and technical trade-offs (The 'Why' behind the 'How')."
        }
        
        level_instruction = seniority_logic.get(seniority_level, "Focus on general technical competencies.")
        
        # 3. Triangulated Prompt Logic with Conflict Resolution
        system_prompt = (
            "SYSTEM ROLE: You are an expert Technical Recruiter."
            f"\nREQUIRED CANDIDATE LEVEL: {seniority_level}"
            f"\nLEVEL-SPECIFIC STRATEGY: {level_instruction}"
            "\n\nSTRICT INTERVIEW LOGIC:"
            "\n1. SENIORITY GUARDRAIL (CRITICAL): The 'REQUIRED CANDIDATE LEVEL' is the absolute truth. "
            "If the Job Description asks for more seniority (e.g., 'Founding' or 'Lead') than the candidate's level, "
            "you MUST downgrade the question complexity to match the candidate's level."
            "\n2. RESUME ANALYSIS: Create 4 questions about specific projects in 'RESUME EXPERIENCE'. Use company names."
            "\n3. JD GAP ANALYSIS: Find 3 requirements in the 'JOB DESCRIPTION' not mentioned in the resume. "
            "Ask how they would learn or apply their skills to these new tools."
            "\n4. ROLE FUNDAMENTALS: Create 3 questions testing core competencies for the Job Role at the specified seniority."
            "\n\nSTRICT OUTPUT RULES:"
            "\n- Output EXACTLY 10 questions numbered 1-10."
            "\n- NO intro text, NO labels, NO category headers."
        )

        context_block = (
            f"--- INPUTS ---\n"
            f"JOB TITLE: {job_role}\n"
            f"SENIORITY: {seniority_level}\n\n"
            f"--- JOB DESCRIPTION ---\n"
            f"{job_description if job_description else 'Standard industry requirements apply.'}\n\n"
            f"--- RESUME DATA ---\n"
            f"SKILLS: {data['skills']}\n"
            f"EXPERIENCE: {data['experience']}"
        )

        full_prompt = f"{system_prompt}\n\n{context_block}"

        # 4. Generate using Qwen 2.5 Coder 32B
        try:
            return await inference_client.generate_text(full_prompt)
        except Exception as e:
            return f"Error during generation: {str(e)}."

question_service = QuestionGenerator()