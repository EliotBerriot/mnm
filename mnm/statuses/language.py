import langdetect


def guess(string):
    if len(string) < 25:
        # we cannot guess accurately on short strings
        return 'UNKNOWN'

    r = langdetect.detect_langs(string)[0]
    return r.lang if r.prob >= 0.75 else 'UNKNWOWN'
