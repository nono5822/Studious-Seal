import os
from google import genai
from google.genai import types
from pydantic import BaseModel, Field

client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

class Assessment(BaseModel):
    name: str = Field(description="Name of the exam or assignment (e.g., Midterm 1, Final)")
    date: str = Field(description="Date in YYYY-MM-DD format. Infer current year if missing.")
    weight: float = Field(description="Percentage weight of the grade.")
    topics_covered: list[str] = Field(description="List of specific concepts covered.")

class SyllabusData(BaseModel):
    course_code: str
    assessments: list[Assessment]

class QuizQuestion(BaseModel):
    question: str = Field(description="A challenging short-answer question based on the material.")
    expected_answer_keywords: list[str] = Field(description="Keywords required for the answer to be considered correct.")

def extract_syllabus_data(file_path: str) -> SyllabusData:
    with open(file_path, 'rb') as f:
        pdf_bytes = f.read()
        
    pdf_part = types.Part.from_bytes(
        data=pdf_bytes,
        mime_type='application/pdf',
    )
    
    prompt = """
    Read this syllabus. Extract the course code and every graded assessment. 
    If an exam lists specific chapters, lectures, or topics, include them. If not, return an empty list for topics_covered.
    
    You MUST return your answer as a valid JSON object matching exactly this schema:
    {
      "course_code": "STRING",
      "assessments": [
        {
          "name": "STRING",
          "date": "YYYY-MM-DD",
          "weight": FLOAT,
          "topics_covered": ["STRING", "STRING"]
        }
      ]
    }
    """
    
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=[pdf_part, prompt],
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            temperature=0.1,
        ),
    )
    
    return SyllabusData.model_validate_json(response.text)

def generate_quiz(course_code: str, topics: list[str], notes_path: str = None) -> QuizQuestion:
    contents = []
    
    prompt = f"""
    The user is a university student studying for {course_code}. 
    The specific topics for this upcoming exam are: {', '.join(topics)}.
    """

    # If the user uploaded notes for this class, feed them to Gemini
    if notes_path and os.path.exists(notes_path):
        with open(notes_path, 'rb') as f:
            pdf_bytes = f.read()
        pdf_part = types.Part.from_bytes(data=pdf_bytes, mime_type='application/pdf')
        contents.append(pdf_part)
        
        prompt += "\nI have attached the official class notes/slides. You MUST base your question directly on the content of these notes that relates to the exam topics.\n"
    else:
        prompt += "\nAsk a fundamental, standard university-level question generally associated with these topics.\n"

    prompt += """
    CRITICAL INSTRUCTIONS: 
    1. Generate exactly ONE short-answer flashcard question.
    2. Keep the question under 3 sentences. Do NOT invent complex enterprise roleplay scenarios. Keep it strictly academic.
    3. Be aggressive and demanding in your tone. Make them sweat.

    You MUST return your answer as a valid JSON object matching exactly this schema:
    {
      "question": "STRING",
      "expected_answer_keywords": ["STRING", "STRING"]
    }
    """
    contents.append(prompt)

    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=contents,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            temperature=0.2, # Extremely low temperature so it sticks to your notes
        ),
    )
    return QuizQuestion.model_validate_json(response.text)

def grade_answer(question: str, user_answer: str, expected_keywords: list[str]) -> tuple[bool, str]:
    prompt = f"Question: {question}\nExpected concepts: {', '.join(expected_keywords)}\nUser's Answer: {user_answer}\n\nIs the user's answer fundamentally correct? Reply with ONLY 'YES' or 'NO', followed by a vertical bar '|', followed by a short, roasting explanation of why they are right or wrong."
    response = client.models.generate_content(model='gemini-2.5-flash', contents=prompt)
    parts = response.text.split('|')
    is_correct = "YES"
