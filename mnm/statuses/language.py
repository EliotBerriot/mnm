import langdetect.detector


def guess(string):
    if len(string) < 25:
        # we cannot guess accurately on short strings
        return 'UNKNOWN'

    try:
        r = langdetect.detect_langs(string)[0]
    except langdetect.detector.LangDetectException:
        return 'UNKNOWN'
    return r.lang if r.prob >= 0.75 else 'UNKNOWN'
