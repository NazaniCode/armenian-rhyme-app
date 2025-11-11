# add_ipa_fast.py
import json, sys, argparse, os
from pathlib import Path
from collections import OrderedDict
from phonemizer import phonemize
from phonemizer.separator import Separator
from math import ceil
from itertools import islice
import multiprocessing as mp

def batched_iterable(iterable, size):
    it = iter(iterable)
    while True:
        chunk = list(islice(it, size))
        if not chunk:
            return
        yield chunk

def enrich_chunk(lines, lang, sep, njobs):
    """
    lines: list[str] of JSONL lines
    returns: list[str] of enriched JSONL lines
    """
    # 1) collect unique tokens (lemma + forms) in order
    uniq = OrderedDict()
    parsed = []
    for line in lines:
        obj = json.loads(line)
        lemma = obj.get("", "")
        forms = obj.get("f", []) if isinstance(obj.get("f"), list) else []
        parsed.append((obj, lemma, forms))
        if lemma:
            uniq.setdefault(lemma, None)
        for f in forms:
            if f:
                uniq.setdefault(f, None)

    tokens = list(uniq.keys())

    # 2) phonemize in one go (multi-process inside phonemizer)
    if tokens:
        phones = phonemize(
            tokens,
            language=lang,
            backend="espeak",
            strip=True,
            preserve_punctuation=False,
            separator=sep,
            njobs=njobs
        )
        # phonemizer returns a single string for single input or a list for list input
        if isinstance(phones, str):
            phones = [phones]
        mapping = dict(zip(tokens, phones))
    else:
        mapping = {}

    # 3) write enriched objects
    out_lines = []
    for obj, lemma, forms in parsed:
        obj["ipa"] = mapping.get(lemma, "") if lemma else ""
        obj["f_ipa"] = [mapping.get(f, "") for f in forms] if forms else []
        out_lines.append(json.dumps(obj, ensure_ascii=False))
    return out_lines

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("infile")
    ap.add_argument("outfile")
    ap.add_argument("lang", nargs="?", default="hy", help='e.g. "hy" (Eastern) or "hyw" (Western)')
    ap.add_argument("--chunk", type=int, default=20000, help="lines per batch (memory/speed tradeoff)")
    ap.add_argument("--jobs", type=int, default=max(mp.cpu_count() - 1, 1), help="workers for phonemizer")
    args = ap.parse_args()

    # Separators: phones separated by spaces; keep words unsplit
    sep = Separator(phone=" ", syllable="", word="")

    in_path = Path(args.infile)
    out_path = Path(args.outfile)

    # Stream read → batch → enrich → write
    total = 0
    with in_path.open("r", encoding="utf-8") as fin, out_path.open("w", encoding="utf-8") as fout:
        for lines in batched_iterable(fin, args.chunk):
            # strip newlines
            lines = [ln.strip() for ln in lines if ln.strip()]
            if not lines:
                continue
            enriched = enrich_chunk(lines, args.lang, sep, args.jobs)
            for ln in enriched:
                fout.write(ln + "\n")
            total += len(lines)
            # optional: progress to stderr
            print(f"Processed {total} lines…", file=sys.stderr)

if __name__ == "__main__":
    main()
