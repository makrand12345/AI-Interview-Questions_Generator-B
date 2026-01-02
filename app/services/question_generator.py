from app.core.inference_client import inference_client
from typing import Optional
import re

class QuestionGenerator:
    """
    NLP Service that orchestrates prompt engineering for interview question generation.
    Performs implicit semantic decomposition and enforces strict output constraints.
    """

    @staticmethod
    async def create_questions(
        job_role: str, 
        seniority_level: str, 
        job_description: Optional[str] = None, 
        resume_text: Optional[str] = None
    ) -> str:
        
        # Construct the high-density system prompt
        system_prompt = (
            "SYSTEM ROLE: You are an elite NLP researcher and technical interviewer. "
            "TASK: Generate EXACTLY 10 interview questions based on the provided context. "
            "\nINTERNAL LOGIC STEPS:"
            "\n1. Perform semantic decomposition of the Job Role and Seniority to identify core competencies, "
            "technical stack, and leadership expectations relevant to the specific domain."
            "\n2. Infer specific responsibilities from the Job Description and Resume if provided."
            "\n3. AVOID ASSUMPTIONS: If the input is noisy, vague, or insufficient to generate high-quality "
            "technical or behavioral questions, you MUST instead generate 10 clarification questions designed "
            "to extract missing information from the candidate."
            "\n4. ANY DOMAIN: Support any professional field (e.g., Engineering, Medicine, Arts, Trade)."
            "\n\nSTRICT OUTPUT RULES:"
            "\n- Output EXACTLY 10 questions."
            "\n- Use a numbered list from 1 to 10."
            "\n- NO introductory text or pleasantries."
            "\n- NO concluding remarks."
            "\n- NO category headers, difficulty labels, or meta-explanations."
            "\n- Output ONLY the raw list of questions."
        )

        context_block = (
            f"PRIMARY INPUTS:\n"
            f"- Job Role: {job_role}\n"
            f"- Seniority Level: {seniority_level}\n\n"
            f"OPTIONAL CONTEXT:\n"
            f"- Job Description: {job_description if job_description else 'N/A'}\n"
            f"- Resume Text: {resume_text if resume_text else 'N/A'}\n"
        )

        full_prompt = f"{system_prompt}\n\n{context_block}"

        # Call the inference client
        raw_output = await inference_client.generate_text(full_prompt)
        
        return raw_output

def enforce_exactly_10(raw_text: str) -> list[str]:
    """
    Extracts numbered questions and enforces EXACTLY 10.
    """
    questions = re.findall(r'^\s*\d+\.\s*(.+)', raw_text, re.MULTILINE)

    if len(questions) != 10:
        raise ValueError(
            f"Model returned {len(questions)} questions instead of exactly 10."
        )

    return questions


question_service = QuestionGenerator()