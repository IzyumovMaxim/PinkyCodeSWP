import re
from readability_grading_functions import flesch_reading_ease, gunning_fog_index, coleman_liau_index, dale_chall_readability_score

def get_density(code):
    lines = code.splitlines()
    code_lines = 0
    comment_lines = 0
    in_block = False
    for line in lines:
        stripped = line.strip()

        if not stripped:
            continue

        if '/*' in stripped:
            in_block = True

        if in_block:
            comment_lines += 1
            if '*/' in stripped:
                in_block = False
            continue

        if "//" in stripped:
            comment_lines += 1

            if not stripped.startswith("//"):
                code_lines += 1

        else:
            code_lines += 1

    return (comment_lines / max(code_lines, 1)) * 100.0

def get_comments(code):
    pattern = (r"(\n\s*(?:(public|private|protected)\s+)?(?:(static|final|synchronized|abstract|strictfp|default)\s+)*(?:(short\s*)|"
              r"((?:(short|long)\s+)?\w+(<[\w<>\[\],\s]+>)?))(\[\])?\s+\w+\s*\(((((\s*(?:(short\s*)|"
              r"((?:(short|long)\s+)?[\w\.]+(<[\w<>\[\],\s]+>)?))(\[\])?\s+\w+\s*),)*"
              r"(\s*(?:(short\s*)|((?:(short|long)\s+)?[\w\.]+(<[\w<>\[\],\s]+>)?))(\[\])?\s+\w+\s*))|\s*)\)\s*(?:throws[\w\s,]+)?\s*\{)|"

              r"(\n\s*((auto|register|static|extern|const)\s+)?(?:(short\s*)|((?:(short|long|long long)\s+)?\w+))\*?"
              r"\s+[\w*]+\s*\(((((\s*(?:const\s+)?(?:(short\s*)|((?:(short|long|long long)\s+)?\w+))\*?\s+[\w*]+(\[\d+\])?\s*),)*"
              r"(\s*(?:const\s+)?(?:(short\s*)|((?:(short|long|long long)\s+)?\w+))\*?\s+[\w*]+(\[\d+\])?\s*))|\s*)\)\s*\{)|"

              r"(\n\s*(?:(public|private|protected|internal|protected internal)\s+)?(?:(static|async|partial)\s+)?(?:(short\s*)|((?:(short|long|long long)\s+)?[\w:]+(<[\w*<>\[\]:,\s]+>)?))(\[\])?\*?"
              r"\s+[\w*]+\s*\(((((\s*((ref|out|params|const)\s+)*(?:(short\s*)|((?:(short|long|long long)\s+)?[\w:]+(<[\w*<>\[\]:,\s]+>)?))(\[\])?\*?\s+[\w*]+\s*),)*"
              r"(\s*((ref|out|params|const)\s+)*(?:(short\s*)|((?:(short|long|long long)\s+)?[\w:]+(<[\w*<>\[\]:,\s]+>)?))(\[\])?\*?\s+[\w*]+\s*))|\s*)\)\s*\{)|"

              r"(\n\s*(?:(auto|static|inline|constexpr|noexcept|extern|virtual|final|const)\s+)*(?:(short\s*)|((?:(short|long|long long)\s+)?[\w:]+(<[\w*&<>\[\]:,\s]+>)?))(?:&|\*+)?"
              r"\s+[\w*]+\s*\(((((\s*(?:const\s+)?(?:(short\s*)|((?:(short|long|long long)\s+)?[\w:]+(<[\w*&<>\[\]:,\s]+>)?))?(?:&|\*+)?\s+[\w*]+(\[\d+\])?\s*),)*"
              r"(\s*(?:const\s+)?(?:(short\s*)|((?:(short|long|long long)\s+)?[\w:]+(<[\w*&<>\[\]:,\s]+>)?))(?:&|\*+)?\s+[\w*]+(\[\d+\])?\s*))|\s*)\)\s*(?:(const|override|noexcept)\s*)*\s*\{)")

    constructor_pattern = re.compile(r"(?:public|private|protected|internal|protected internal|explicit)\s+[A-Z]\w+")

    methods = [m for m in re.finditer(pattern, code) if not(re.fullmatch(constructor_pattern, m.group().strip()[:m.group().strip().find("(")]))]

    total = len(methods)
    if total == 0:
        return 0.0
        
    lines = code.splitlines()
    commented = 0
    for m in methods:
        method_line_idx = code[:m.start()].count('\n')
        found_comment = False
        for i in range(1, 4):
            idx = method_line_idx - i
            if idx < 0:
                break
            prev = lines[idx].strip()
            if not prev:
                continue
            if prev.startswith('//') or prev.startswith('/*') or prev.endswith('*/'):
                found_comment = True
                break
        if found_comment:
            commented += 1
            
    return (commented / total) * 100.0


def get_readability(code):
    comments_union = ""

    for comment in re.finditer(r"(((?<=/\*)|(?<=/\*\*))((?:(?!\*/)(.|\n))*?)(?=\*/))|"
                               r"((?<=//)[^\n]*(?=\n))", code):

        comments_union += f"{comment.group().strip()}."

    if not comments_union:
        return 0.0

    fre_score = flesch_reading_ease(comments_union)
    gfi_score = gunning_fog_index(comments_union)
    cli_score = coleman_liau_index(comments_union)
    dcr_score = dale_chall_readability_score(comments_union)

    # Projection of FRE score onto 100 scale
    if get_readability.FRE_MIN_GOOD_SCORE <= fre_score:
        fre_score_projection = 100

    elif get_readability.FRE_MIN_ACCEPTABLE_SCORE <= fre_score < get_readability.FRE_MIN_GOOD_SCORE:
        fre_score_projection = (75 + 25 * (fre_score - get_readability.FRE_MIN_ACCEPTABLE_SCORE) /
                               (get_readability.FRE_MIN_GOOD_SCORE - get_readability.FRE_MIN_ACCEPTABLE_SCORE))

    elif get_readability.FRE_MIN_MEDIUM_SCORE <= fre_score < get_readability.FRE_MIN_ACCEPTABLE_SCORE:
        fre_score_projection = (50 + 25 * (fre_score - get_readability.FRE_MIN_MEDIUM_SCORE) /
                               (get_readability.FRE_MIN_ACCEPTABLE_SCORE - get_readability.FRE_MIN_MEDIUM_SCORE))

    else:
        fre_score_projection = (50 * (max(0, fre_score - get_readability.FRE_MIN_BAD_SCORE)) /
                               (get_readability.FRE_MIN_MEDIUM_SCORE - get_readability.FRE_MIN_BAD_SCORE))

    # Projection of GFI score onto 100 scale
    if gfi_score <= get_readability.GFI_MAX_GOOD_SCORE:
        gfi_score_projection = 100

    elif get_readability.GFI_MAX_GOOD_SCORE < gfi_score <= get_readability.GFI_MAX_ACCEPTABLE_SCORE:
        gfi_score_projection = (75 + 25 * (get_readability.GFI_MAX_ACCEPTABLE_SCORE - gfi_score) /
                               (get_readability.GFI_MAX_ACCEPTABLE_SCORE - get_readability.GFI_MAX_GOOD_SCORE))

    elif get_readability.GFI_MAX_ACCEPTABLE_SCORE < gfi_score <= get_readability.GFI_MAX_MEDIUM_SCORE:
        gfi_score_projection = (50 + 25 * (get_readability.GFI_MAX_MEDIUM_SCORE - gfi_score) /
                               (get_readability.GFI_MAX_MEDIUM_SCORE - get_readability.GFI_MAX_ACCEPTABLE_SCORE))

    else:
        gfi_score_projection = (50 * (max(0, get_readability.GFI_MAX_BAD_SCORE - gfi_score)) /
                               (get_readability.GFI_MAX_BAD_SCORE - get_readability.GFI_MAX_MEDIUM_SCORE))

    # Projection of CLI score onto 100 scale
    if get_readability.CLI_MIN_GOOD_SCORE <= cli_score:
        cli_score_projection = 100

    elif get_readability.CLI_MIN_ACCEPTABLE_SCORE <= cli_score < get_readability.CLI_MIN_GOOD_SCORE:
        cli_score_projection = (75 + 25 * (cli_score - get_readability.CLI_MIN_ACCEPTABLE_SCORE) /
                               (get_readability.CLI_MIN_GOOD_SCORE - get_readability.CLI_MIN_ACCEPTABLE_SCORE))

    elif get_readability.CLI_MIN_MEDIUM_SCORE <= cli_score < get_readability.CLI_MIN_ACCEPTABLE_SCORE:
        cli_score_projection = (50 + 25 * (cli_score - get_readability.CLI_MIN_MEDIUM_SCORE) /
                               (get_readability.CLI_MIN_ACCEPTABLE_SCORE - get_readability.CLI_MIN_MEDIUM_SCORE))

    else:
        cli_score_projection = (50 * (max(0, cli_score - get_readability.CLI_MIN_BAD_SCORE)) /
                               (get_readability.CLI_MIN_MEDIUM_SCORE - get_readability.CLI_MIN_BAD_SCORE))

    # Projection of DCR score onto 100 scale
    if dcr_score <= get_readability.DCR_MAX_GOOD_SCORE:
        dcr_score_projection = 100

    elif get_readability.DCR_MAX_GOOD_SCORE < dcr_score <= get_readability.DCR_MAX_ACCEPTABLE_SCORE:
        dcr_score_projection = (75 + 25 * (get_readability.DCR_MAX_ACCEPTABLE_SCORE - dcr_score) /
                               (get_readability.DCR_MAX_ACCEPTABLE_SCORE - get_readability.DCR_MAX_GOOD_SCORE))

    elif get_readability.DCR_MAX_ACCEPTABLE_SCORE < dcr_score <= get_readability.DCR_MAX_MEDIUM_SCORE:
        dcr_score_projection = (50 + 25 * (get_readability.DCR_MAX_MEDIUM_SCORE - dcr_score) /
                               (get_readability.DCR_MAX_MEDIUM_SCORE - get_readability.DCR_MAX_ACCEPTABLE_SCORE))

    else:
        dcr_score_projection = (50 * (max(0, get_readability.DCR_MAX_BAD_SCORE - dcr_score)) /
                               (get_readability.DCR_MAX_BAD_SCORE - get_readability.DCR_MAX_MEDIUM_SCORE))

    # Return the average score
    return (fre_score_projection + gfi_score_projection + cli_score_projection + dcr_score_projection) / 4


get_readability.FRE_MIN_GOOD_SCORE = 7.07
get_readability.FRE_MIN_ACCEPTABLE_SCORE = -16.61
get_readability.FRE_MIN_MEDIUM_SCORE = -476.80
get_readability.FRE_MIN_BAD_SCORE = -1314.99

get_readability.GFI_MAX_GOOD_SCORE = 51.00
get_readability.GFI_MAX_ACCEPTABLE_SCORE = 59.53
get_readability.GFI_MAX_MEDIUM_SCORE = 224.47
get_readability.GFI_MAX_BAD_SCORE = 550.24

get_readability.CLI_MIN_GOOD_SCORE = 8.44
get_readability.CLI_MIN_ACCEPTABLE_SCORE = 3.10
get_readability.CLI_MIN_MEDIUM_SCORE = -101.89
get_readability.CLI_MIN_BAD_SCORE = -344.69

get_readability.DCR_MAX_GOOD_SCORE = 13.83
get_readability.DCR_MAX_ACCEPTABLE_SCORE = 14.63
get_readability.DCR_MAX_MEDIUM_SCORE = 37.21
get_readability.DCR_MAX_BAD_SCORE = 77.56