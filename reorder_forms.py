# reorder_forms.py
# usage: python reorder_forms.py IN.jsonl OUT.jsonl
import sys, json

def main():
    if len(sys.argv) < 3:
        print("usage: python reorder_forms.py IN.jsonl OUT.jsonl", file=sys.stderr)
        sys.exit(1)
    inf, outf = sys.argv[1], sys.argv[2]

    lines = moved = not_found = skipped_len_mismatch = 0

    with open(inf, "r", encoding="utf-8") as fin, open(outf, "w", encoding="utf-8") as fout:
        for raw in fin:
            raw = raw.strip()
            if not raw:
                continue
            lines += 1
            obj = json.loads(raw)

            lemma = obj.get("", "")
            f = obj.get("f")
            f_ipa = obj.get("f_ipa")

            # Only proceed if f is a list and lemma is non-empty
            if isinstance(f, list) and lemma:
                try:
                    idx = f.index(lemma)  # first occurrence
                except ValueError:
                    not_found += 1
                else:
                    if idx != 0:
                        # Move lemma in f
                        form = f.pop(idx)
                        f.insert(0, form)

                        # Move aligned ipa if present & long enough
                        if isinstance(f_ipa, list) and idx < len(f_ipa):
                            ipa_form = f_ipa.pop(idx)
                            f_ipa.insert(0, ipa_form)
                        else:
                            # Keep count when we can’t move f_ipa in sync
                            if isinstance(f_ipa, list):
                                skipped_len_mismatch += 1
                            # If f_ipa missing or too short, we just leave it as-is

                        moved += 1

            # Write back the (possibly) updated object
            obj["f"] = f if isinstance(f, list) else obj.get("f")
            if isinstance(f_ipa, list):
                obj["f_ipa"] = f_ipa
            fout.write(json.dumps(obj, ensure_ascii=False) + "\n")

    # Summary to stderr
    print(f"Processed lines: {lines}", file=sys.stderr)
    print(f"Moved lemma to front: {moved}", file=sys.stderr)
    print(f"Lemma not found in f: {not_found}", file=sys.stderr)
    print(f"Couldn’t realign f_ipa due to length/index: {skipped_len_mismatch}", file=sys.stderr)

if __name__ == "__main__":
    main()
