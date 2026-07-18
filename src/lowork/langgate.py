"""Conservative chunk-level English gate for extraction.

Careers pages sometimes serve non-English copy with no URL marker (amazon.jobs
root captured in German; Coinbase appends the same GDPR notice in a dozen
languages to one English page), so URL-level exclude_url patterns can't catch
everything. This gate drops a chunk only on strong evidence:

- non-Latin script dominates the letters (CJK, Cyrillic, Arabic, Thai...), or
- Latin script but a common-stopword vote across languages is won decisively
  by a language other than English.

Ties and low-signal text (job-title lists, terse English) stay IN — false
drops are worse than the odd straggler, which the M4 mission review catches.

NOTE: `text_filter.is_english` is a DIFFERENT, deliberate implementation
(ascii-ratio + langdetect) used at scoring time; this one gates extraction.
Same name, different tradeoffs — don't swap one for the other.
"""

from __future__ import annotations

import re

# Distinctive high-frequency function words. Deliberately excludes words shared
# with English or across these languages (e.g. "a", "die" is kept: rare in
# careers-page English; "on"/"in" excluded: English collision).
_STOPWORDS = {
    "en": {"the", "and", "of", "to", "we", "our", "you", "your", "for", "with",
           "are", "that", "this", "have", "will", "work", "at", "be", "from"},
    "de": {"und", "der", "die", "das", "wir", "sie", "mit", "für", "ist",
           "nicht", "eine", "auf", "als", "auch", "werden", "bei", "unsere"},
    "fr": {"et", "les", "des", "nous", "vous", "dans", "pour", "est", "une",
           "qui", "sur", "avec", "sont", "notre", "votre"},
    "es": {"los", "las", "para", "por", "una", "con", "del", "que", "nuestro",
           "más", "como", "está", "son", "trabajo"},
    "it": {"che", "per", "della", "nel", "una", "con", "sono", "più", "nostro",
           "anche", "come", "lavoro", "gli"},
    "pt": {"que", "para", "uma", "com", "não", "mais", "nosso", "você", "são",
           "como", "trabalho", "pela"},
    "nl": {"het", "een", "van", "voor", "met", "aan", "onze", "wij", "je",
           "niet", "zijn", "ook", "werk"},
    "pl": {"się", "nie", "jest", "oraz", "które", "aby", "przez", "jako",
           "praca", "firmy", "naszych"},
    "tr": {"bir", "için", "olarak", "ile", "bu", "olan", "gibi", "daha",
           "çalışma", "olur", "veya"},
    "vi": {"và", "của", "các", "cho", "bạn", "với", "được", "những", "công",
           "việc", "chúng"},
    "da": {"og", "det", "til", "der", "som", "på", "med", "vores", "ikke",
           "arbejde", "hos"},
}

_LATIN = re.compile(r"[a-zA-ZÀ-ɏ]")
_NONLATIN = re.compile(r"[Ѐ-ӿ֐-ۿऀ-෿฀-๿"
                       r"ᄀ-ᇿ぀-ヿ㐀-鿿가-힯]")

MIN_WORDS = 8            # below this, always keep (headings, title lists)
NONLATIN_MAX_RATIO = 0.3  # letters in non-Latin scripts vs all letters


def is_english(text: str) -> bool:
    """True unless the text is decisively non-English."""
    latin = len(_LATIN.findall(text))
    nonlatin = len(_NONLATIN.findall(text))
    if latin + nonlatin == 0:
        return True
    if nonlatin / (latin + nonlatin) > NONLATIN_MAX_RATIO:
        return False

    words = [w.strip(".,;:!?()\"'«»„“”") for w in text.lower().split()]
    if len(words) < MIN_WORDS:
        return True
    votes = {lang: sum(w in sw for w in words) for lang, sw in _STOPWORDS.items()}
    en = votes.pop("en")
    best_lang, best = max(votes.items(), key=lambda kv: kv[1])
    # Decisive: the foreign language clearly outvotes English and carries a
    # meaningful share of the text.
    return not (best >= 3 and best > 2 * en and best / len(words) > 0.08)
