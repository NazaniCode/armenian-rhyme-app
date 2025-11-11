# clean_jsonl.py
import sys, json

def main():
    if len(sys.argv) < 3:
        print("usage: python clean_jsonl.py IN.jsonl OUT.jsonl", file=sys.stderr)
        sys.exit(1)
    inf, outf = sys.argv[1], sys.argv[2]

    removed_f = removed_fipa = removed_i = removed_ipa = lines = 0

    with open(inf, "r", encoding="utf-8") as fin, open(outf, "w", encoding="utf-8") as fout:
        for line in fin:
            line = line.strip()
            if not line:
                continue
            lines += 1
            obj = json.loads(line)

            # drop "i" and "ipa"
            if "i" in obj:
                removed_i += 1
                obj.pop("i", None)
            if "ipa" in obj:
                removed_ipa += 1
                obj.pop("ipa", None)

            # remove first element from f (if list & non-empty)
            f = obj.get("f")
            if isinstance(f, list) and f:
                f.pop(0)
                removed_f += 1

            # remove first element from f_ipa (if list & non-empty)
            fipa = obj.get("f_ipa")
            if isinstance(fipa, list) and fipa:
                fipa.pop(0)
                removed_fipa += 1

            fout.write(json.dumps(obj, ensure_ascii=False) + "\n")

    print(f"Processed {lines} lines", file=sys.stderr)
    print(f"Modified: f({removed_f}), f_ipa({removed_fipa}), removed keys: i({removed_i}), ipa({removed_ipa})", file=sys.stderr)

if __name__ == "__main__":
    main()
