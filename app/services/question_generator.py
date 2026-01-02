from app.core.inference_client import inference_client
from typing import Optional
import re

class QuestionGenerator:
    """
    NLP Service that bifurcates resume text to generate highly targeted 
    interview questions based on experience and skills.
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
            parts["experience"] = clean_text[exp_match.start(2):].strip()[:2000] # Limit to 2k chars to prevent timeout
            
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
        
        # 2. Triangulated Prompt Logic
        system_prompt = (
            "SYSTEM ROLE: You are a Lead Technical Architect conducting a high-stakes interview."
            f"\nTARGET ROLE: {seniority_level} {job_role}"
            "\n\nSTRICT INTERVIEW LOGIC:"
            "\n1. RESUME ANALYSIS: Extract specific projects from 'RESUME EXPERIENCE'. Create 4 questions "
            "that challenge the candidate on the 'Why' and 'How' of their past work."
            "\n2. JD GAP ANALYSIS: Look at the 'JOB DESCRIPTION'. Identify 3 core requirements (tools/architectures). "
            "Create 3 questions testing the candidate's proficiency in these JD-specific areas, "
            "especially if they aren't highlighted in the resume."
            "\n3. SENIORITY VALIDATION: Create 3 questions on high-level system design, scalability, or "
            "mentorship expectations consistent with a Senior-level role."
            "\n\nSTRICT OUTPUT RULES:"
            "\n- Output EXACTLY 10 questions numbered 1-10."
            "\n- NO introductory or concluding text."
            "\n- NO labels like 'JD Question' or 'Resume Question'. Just the questions."
        )

        context_block = (
            f"--- INPUT CONTEXT ---\n"
            f"JOB TITLE: {job_role}\n"
            f"EXPECTED SENIORITY: {seniority_level}\n\n"
            f"--- JOB DESCRIPTION (The Requirements) ---\n"
            f"{job_description if job_description else 'No JD provided - focus on general industry standards for this role.'}\n\n"
            f"--- RESUME SKILLS ---\n"
            f"{data['skills'] if data['skills'] else 'N/A'}\n\n"
            f"--- RESUME EXPERIENCE (The History) ---\n"
            f"{data['experience'] if data['experience'] else 'N/A'}"
        )

        full_prompt = f"{system_prompt}\n\n{context_block}"

        # 3. Generate using Qwen 2.5 Coder 32B
        try:
            return await inference_client.generate_text(full_prompt)
        except Exception as e:
            return f"Error during generation: {str(e)}."

question_service = QuestionGenerator()