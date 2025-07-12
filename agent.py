import os
import json
import openai
from groq import Groq

from metrics import get_density, get_comments, get_readability
from comment_analyzer import CommentAnalyzer 

# client = openai.OpenAI(
#     api_key=os.environ.get('API_KEY'))
client = Groq(api_key=os.environ["GROQ_API_KEY"])
comment_analyzer = CommentAnalyzer()

def make_prompt(filename, code):
    splitlines = code.splitlines()
    lines = []
    for n in range(len(splitlines)):
        lines.append(f"{n + 1}: {splitlines[n].strip()}")
    code = '\n'.join(lines)

    return f"""
Act as a senior software engineer proficient in various programming languages.
Your task is to evaluate comments in the programming code given below.
You must repeat evaluation several times until you are confident in your evaluation by getting same result per 3 last iterations.
You must fill the form with metrics and output only the exact JSON according to this template
(no extra text, no formatting, no explanations and no other lyrics):
{{
"MISSING_COMMENTS":
  [
    {{"LINE": #}},
    ... 
  ],
"BAD_COMMENTS":
  [
    {{
      "LINE": #,
      "TYPE": "$",
    }},
    ... 
  ]


}}

Evaluation criteria:

For MISSING_COMMENTS, identify places that need commenting, i.e. for complex logic or public methods
BAD_COMMENTS: Grade all comments in range A-best to D-worst, for comments graded D, output strictly:
- INCORRECT - for comments that don't match the code
- USELESS - for redundant comments that just repeat the code
- VAGUE - for comments that don't explain the code
- JARGON - for using jargon without explanation
- GARBAGE - for comments that are just nonsense

---
{filename}: 
{code}
"""


def evaluate(path):
    with open(path, 'r') as file:
        content = file.read()

    filename = os.path.basename(path)

    prompt = make_prompt(filename, content)

    meaningless_pct = comment_analyzer.analyze_file(path)

    # response = client.chat.completions.create(
    #     model="gpt-4.1",
    #     messages=[{"role": "user", "content": prompt}],
    #     seed=1337,
    #     temperature=1e-21,
    #     top_p=1.0,  # Controls diversity by limiting token selection to a probability mass
    #     frequency_penalty=0.0,  # Penalizes frequently used tokens (range -2.0 to 2.0)
    #     presence_penalty=0.0,
    #     # Penalizes new tokens based on whether they appear in the text so far (range -2.0 to 2.0)
    #     max_tokens=1024
    # )


    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=1e-21,
        max_tokens=1024,
        top_p=1.0,
        frequency_penalty=0.0,
        presence_penalty=0.0,
        seed=1337
    )
    feedback = json.loads(response.choices[0].message.content.strip())

    density = get_density(content)
    methods_pct = get_comments(content)
    readability = get_readability(content)

    try:

      missing_comments = [x['LINE'] for x in feedback['MISSING_COMMENTS']]
      incorrect_comments = [x['LINE'] for x in feedback['BAD_COMMENTS'] if x['TYPE'] == 'INCORRECT']
      useless_comments = [x['LINE'] for x in feedback['BAD_COMMENTS'] if x['TYPE'] == 'USELESS']
      vague_comments = [x['LINE'] for x in feedback['BAD_COMMENTS'] if x['TYPE'] == 'VAGUE']
      jargon_comments = [x['LINE'] for x in feedback['BAD_COMMENTS'] if x['TYPE'] == 'JARGON']
      garbage_comments = [x['LINE'] for x in feedback['BAD_COMMENTS'] if x['TYPE'] == 'GARBAGE']

      result = {
          "filename": filename,
          "density": density,
          "methods_pct": methods_pct,
          "readability": readability,
          "meaningless_pct": meaningless_pct,
          "issues": {
                      "missing": {"info": "<b>Missing comments for complex code snippets:</b><br>Lines: ", "lines": missing_comments},
                      "incorrect": {"info": "<b>Comments that do not match the code:</b><br>Lines: ", "lines": incorrect_comments},
                      "useless": {"info": "<b>Redundant comments that just repeat the code:</b><br>Lines: ", "lines": useless_comments},
                      "vague": {"info": "<b>Comments that do not explain the code:<\b><br>Lines: ", "lines": vague_comments},
                      "jargon": {"info": "<b>Comments that use specific jargon w/o explanation:</b><br>Lines: ", "lines": jargon_comments},
                      "garbage": {"info": "<b>Completely nonsensical comments:</b><br>Lines: ", "lines": garbage_comments}
          }
      }
    
    except Exception as exc:
      raise json.JSONDecodeError(exc.args[0]) from None 

    else:
      return result
