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
        
        # 2. Advanced Technical Prompt
        system_prompt = (
            "SYSTEM ROLE: You are a Senior Technical Architect and Interviewer. "
            "TASK: Generate 10 deep-dive interview questions."
            "\n\nBIFURCATION STRATEGY:"
            "\n- Analyze the 'RESUME EXPERIENCE' section to find specific tools used."
            "\n- Cross-reference with the 'RESUME SKILLS' list."
            "\n- 6 Questions MUST be 'Behavioral-Technical': Ask how they solved specific problems "
            "in the projects listed in their experience."
            "\n- 4 Questions MUST be 'Architecture-Based': Ask for the 'Why' behind their technical choices."
            "\n\nSTRICT RULES:"
            "\n- NO conversational filler. Numbered list 1-10 only."
        )

        context_block = (
            f"TARGET: {seniority_level} {job_role}\n\n"
            f"RESUME SKILLS:\n{data['skills'] if data['skills'] else 'Not provided'}\n\n"
            f"RESUME EXPERIENCE & PROJECTS:\n{data['experience'] if data['experience'] else 'Not provided'}\n\n"
            f"JOB DESCRIPTION:\n{job_description if job_description else 'Not provided'}"
        )

        full_prompt = f"{system_prompt}\n\n{context_block}"

        # 3. Generate using Qwen 2.5 Coder
        try:
            return await inference_client.generate_text(full_prompt)
        except Exception as e:
            return f"Error during generation: {str(e)}. Try a smaller resume or check model status."

question_service = QuestionGenerator()