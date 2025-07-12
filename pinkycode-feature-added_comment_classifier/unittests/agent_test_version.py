import os
import json

def evaluate(jsonfeedback):
    feedback = json.loads(f'{jsonfeedback}'.replace('\'', '"'))

    density = 0.0
    methods_pct = 0.0
    readability = 0.0
    
    try:
        missing_comments = [x['LINE'] for x in feedback['MISSING_COMMENTS']]
        incorrect_comments = [x['LINE'] for x in feedback['BAD_COMMENTS'] if x['TYPE'] == 'INCORRECT']
        useless_comments = [x['LINE'] for x in feedback['BAD_COMMENTS'] if x['TYPE'] == 'USELESS']
        vague_comments = [x['LINE'] for x in feedback['BAD_COMMENTS'] if x['TYPE'] == 'VAGUE']
        jargon_comments = [x['LINE'] for x in feedback['BAD_COMMENTS'] if x['TYPE'] == 'JARGON']
        garbage_comments = [x['LINE'] for x in feedback['BAD_COMMENTS'] if x['TYPE'] == 'GARBAGE']
    
        result = {
            "filename": "filename.ext",
            "density": density,
            "methods_pct": methods_pct,
            "readability": readability,
            "meaningless_pct": feedback['MEANINGLESS_COMMENTS_PERCENTAGE'],
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
        raise json.JSONDecodeError(exc.args[0], "doc", 0) from None
    return result