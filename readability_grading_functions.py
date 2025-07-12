import os
import re
import sqlite3

import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import cmudict
from pydantic.v1.error_wrappers import display_errors

# Downloading necessary resources of NLTK
nltk.download('punkt')
nltk.download('cmudict')
nltk.download('punkt_tab')

# Initialization of a dictionary for syllables count
d = cmudict.dict()

# For Dale-Chall: complex words percentage (which are not in this list of basic words)
basic_words = {
    "a", "about", "above", "after", "again", "all", "am", "an", "and", "any", "are", "as", "at", "be", "because",
    "been", "before", "being", "below", "between", "both", "but", "by", "can", "could", "did", "do", "does", "doing",
    "down", "during", "each", "few", "for", "from", "further", "had", "has", "have", "having", "he", "her", "here",
    "hers", "herself", "him", "himself", "his", "how", "i", "if", "in", "into", "is", "it", "its", "itself", "me",
    "more", "most", "my", "myself", "no", "nor", "not", "of", "off", "on", "once", "only", "or", "other", "our",
    "ours", "ourselves", "out", "over", "own", "same", "she", "should", "so", "some", "such", "than", "that", "the",
    "their", "theirs", "them", "themselves", "then", "there", "these", "they", "this", "those", "through", "to",
    "too", "under", "until", "up", "very", "was", "we", "were", "what", "when", "where", "which", "while", "who",
    "whom", "why", "will", "with", "you", "your", "yours", "yourself",
    "algorithm", "array", "argument", "assign", "attribute", "boolean", "break", "byte", "call", "case", "catch",
    "class", "comment", "condition", "constant", "constructor", "continue", "counter", "data", "debug", "default",
    "delete", "dictionary", "divide", "element", "else", "empty", "encode", "end", "error", "exception", "execute",
    "false", "field", "file", "filter", "flag", "float", "for", "function", "global", "handle", "hash", "heap", "if",
    "import", "index", "initialize", "input", "integer", "interface", "iterate", "key", "lambda", "length", "library",
    "list", "loop", "map", "match", "memory", "method", "module", "multiply", "null", "object", "operator", "option",
    "output", "parameter", "parse", "pointer", "print", "process", "property", "queue", "raise", "range", "read",
    "record", "recursion", "reference", "regex", "return", "script", "set", "slice", "sort", "stack", "start",
    "statement", "step", "string", "struct", "switch", "syntax", "template", "test", "throw", "token", "true", "try",
    "tuple", "type", "undefined", "update", "value", "variable", "vector", "void", "while", "write", "array", "binary",
    "bit", "block", "bubble", "bucket", "cache", "child", "circular", "cluster", "compare",
    "concat", "cycle", "depth", "edge", "encode", "encrypt", "extract", "fibonacci", "filter", "graph", "greedy",
    "hash", "heap", "insert", "iterate", "leaf", "linked", "list", "loop", "matrix", "merge", "node", "parent",
    "partition", "pivot", "queue", "quicksort", "recursive", "rotate", "search", "select", "sequence", "shuffle",
    "sort", "sparse", "split", "stack", "substring", "subtree", "swap", "traverse", "tree", "vertex", "action",
    "application", "behavior", "calculate", "check", "clean", "clear", "combine", "compare", "compute", "configure",
    "construct", "create", "define", "describe", "destroy", "determine", "document", "enable", "ensure", "evaluate",
    "example", "explain", "extend", "feature", "format", "generate", "group", "handle", "implement", "improve",
    "include", "indicate", "initialize", "instantiate", "interface", "invoke", "limit", "log", "maintain", "manage",
    "modify", "note", "optimize", "override", "perform", "prevent", "process", "provide", "reduce", "refresh",
    "register", "release", "remove", "replace", "reset", "resolve", "restrict", "reuse", "save", "secure", "separate",
    "share", "simplify", "simulate", "specify", "store", "support", "transform", "trigger", "validate", "verify",
    "wrap", "add", "adjust", "allow", "apply", "avoid", "base", "begin", "build", "call", "change", "check", "choose",
    "clear", "close", "complete", "connect", "convert", "copy", "create", "define", "delete", "demonstrate",
    "describe", "disable", "display", "divide", "enable", "ensure", "execute", "expand", "extract", "fetch", "filter",
    "find", "finish", "fix", "format", "generate", "get", "handle", "ignore", "implement", "improve", "include",
    "increment", "initialize", "insert", "load", "lock", "log", "manage", "merge", "move", "open", "parse", "pass",
    "perform", "populate", "prepare", "process", "produce", "push", "query", "read", "reduce", "refresh", "register",
    "release", "remove", "rename", "replace", "reset", "resolve", "restart", "restore", "return", "retry", "reverse",
    "run", "save", "scale", "search", "select", "send", "set", "show", "skip", "solve", "sort", "split", "start",
    "stop", "store", "strip", "submit", "subtract", "switch", "sync", "terminate", "test", "throw", "trace",
    "transform", "trigger", "unlock", "update", "use", "validate", "verify", "wait", "watch", "write", "arg", "attr",
    "bool", "def", "func", "int", "lib", "mod", "obj", "param", "proc", "prop", "ptr", "ref", "str", "var"
}

def count_syllables(word):
    """This function counts the number of syllables"""
    try:
        return max([len(list(y for y in x if y[-1].isdigit())) for x in d[word.lower()]])
    except KeyError:
        return 1  # If the word is not in dictionary, we consider it as having onr syllable


def analyze_text(text):
    """This function analyzes the text and returns characteristics for readability assessment formulas"""
    sentences = sent_tokenize(text)
    words = word_tokenize(text)
    letters = [sym for word in words if word.isalpha() for sym in word]

    # Basic metrics
    num_sentences = len(sentences)
    num_words = len(words)
    num_letters = len(letters)
    num_syllables = sum(count_syllables(word) for word in words if word.isalpha())
    avg_word_length = num_letters / num_words if num_words > 0 else 0
    avg_sentence_length = num_words / num_sentences if num_sentences > 0 else 0
    avg_syllables_per_word = num_syllables / num_words if num_words > 0 else 0

    complex_words = [word for word in words if word.lower() not in basic_words and word.isalpha()]
    percent_complex_words = (len(complex_words) / num_words) * 100 if num_words > 0 else 0

    return {
        "num_sentences": num_sentences,
        "num_words": num_words,
        "num_syllables": num_syllables,
        "avg_word_length": avg_word_length,
        "avg_sentence_length": avg_sentence_length,
        "avg_syllables_per_word": avg_syllables_per_word,
        "percent_complex_words": percent_complex_words
    }


def flesch_reading_ease(text):
    """This method computes readability score using Flesch Reading Ease"""
    stats = analyze_text(text)
    score = 206.835 - (1.015 * stats["avg_sentence_length"]) - (84.6 * stats["avg_syllables_per_word"])
    return round(score, 2)

def gunning_fog_index(text):
    """This method computes readability score using Gunning Fog Index"""
    stats = analyze_text(text)
    score = 0.4 * (stats["avg_sentence_length"] + stats["percent_complex_words"])
    return round(score, 2)

def coleman_liau_index(text):
    """This method computes readability score using Coleman-Liau Index"""
    stats = analyze_text(text)
    score = (5.89 * (stats["avg_word_length"])) - (0.3 * (stats["avg_sentence_length"]) - 15.8)
    return round(score, 2)

def dale_chall_readability_score(text):
    """This method computes readability score using Dale-Chall Readability Score"""
    stats = analyze_text(text)
    score = 0.1579 * stats["percent_complex_words"] + 0.0496 * stats["avg_sentence_length"]
    if stats["percent_complex_words"] > 5:
        score += 3.6365
    return round(score, 2)
