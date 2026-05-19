"""
utils/ai_client.py
------------------
Thin wrapper around the OpenAI Python SDK.
Provides two high-level functions:
  - generate_business_summary()
  - generate_email_reply()

Both accept a plain API key string so the caller (Streamlit) can pass
st.secrets["OPENAI_API_KEY"] or a user-supplied key from the sidebar.
"""

from openai import OpenAI


def _get_client(api_key: str) -> OpenAI:
    """Instantiate an OpenAI client with the given key."""
    return OpenAI(api_key=api_key)


def generate_business_summary(data_summary: str, api_key: str) -> str:
    """
    Ask GPT to write a professional business analysis based on a text
    summary of the uploaded dataset.

    Parameters
    ----------
    data_summary : str
        Plain-text description of the dataset (built by build_data_summary_text).
    api_key : str
        OpenAI API key.

    Returns
    -------
    str
        Markdown-formatted business summary from GPT.
    """
    client = _get_client(api_key)

    system_prompt = (
        "You are a senior business analyst. "
        "You receive a statistical summary of a company's sales dataset "
        "and produce a concise professional report in Markdown. "
        "Structure your report with these sections: "
        "**Executive Summary**, **Key Trends**, **Potential Issues**, **Recommendations**. "
        "Be specific, cite numbers from the data, keep it under 350 words."
    )

    user_prompt = (
        f"Here is the dataset summary:\n\n{data_summary}\n\n"
        "Please write a professional business analysis report."
    )

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        max_tokens=600,
        temperature=0.5,
    )

    return response.choices[0].message.content


def generate_email_reply(situation: str, api_key: str, tone: str = "professional") -> str:
    """
    Generate a professional business email based on a short situation description.

    Parameters
    ----------
    situation : str
        A short description, e.g. "Customer complaint about delayed shipment".
    api_key : str
        OpenAI API key.
    tone : str
        One of: 'professional', 'friendly', 'formal'.

    Returns
    -------
    str
        A ready-to-send email (subject line + body).
    """
    client = _get_client(api_key)

    system_prompt = (
        "You are an expert business communication specialist. "
        "Write clear, empathetic, and action-oriented business emails. "
        f"Tone: {tone}. "
        "Always include: Subject line, greeting, body (2-3 paragraphs), closing. "
        "Keep the email under 200 words."
    )

    user_prompt = (
        f"Write a business email for this situation:\n\n{situation}\n\n"
        "Return ONLY the email text, starting with 'Subject:'."
    )

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        max_tokens=400,
        temperature=0.6,
    )

    return response.choices[0].message.content
