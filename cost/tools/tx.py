"""English -> Japanese text for this estimate.

Every project string is written once, as a pair, where it is used:

    desc = t("Spend guard core ...", "スペンドガードの中核 ...")

t() records the pair in JA and returns the English text, so model.py and md.py
work in English, and the template's snapshot.Translator (holding JA) gives the
Japanese for the Japanese workbook and markdown. make.py fails if a string
reaches the Japanese output without a pair.

Generic labels of sections 1-6 are translated by the template's snapshot.py.
"""
JA = {}


def t(en, ja):
    if en in JA and JA[en] != ja:
        raise ValueError(f"two Japanese texts for {en!r}")
    JA[en] = ja
    return en
