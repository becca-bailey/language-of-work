#!/usr/bin/env python
"""Step 4a: generate candidate axis sentences for hand-curation (manual step M5).

For each pole of each axis YAML, asks the judge-class LLM for 15-20 candidate
sentences in careers-page voice. Output goes to axes/candidates/<axis>.md for
review — curate down to 6-10 per pole and update axes/<axis>.yaml.
"""

from __future__ import annotations

import argparse

from anthropic import Anthropic

from lowork.axes import AxisDef
from lowork.config import AXES_DIR, JUDGE_MODEL

PROMPT = """Write 18 distinct sentences that a tech company careers page might \
plausibly use, each expressing this value/stance: {concept}

Rules:
- First-person corporate careers-page voice ("we", "our", "join us")
- Vary sentence structure and vocabulary across the set; no two sentences should \
share a distinctive phrase
- Each sentence expresses ONLY this concept — do not drift into adjacent values
- Do not imitate any specific real company's known slogans or copy
- One sentence per line, no numbering, no commentary"""


def main(axis_names: list[str]) -> None:
    client = Anthropic()
    out_dir = AXES_DIR / "candidates"
    out_dir.mkdir(exist_ok=True)

    for name in axis_names:
        axis = AxisDef.from_yaml(AXES_DIR / f"{name}.yaml")
        lines = [f"# Candidate sentences: {axis.name}", "",
                 "Curate 6-10 per pole into the axis YAML (manual step M5).",
                 "Check: on-concept, varied form, careers-page voice, no corpus lifts.", ""]
        for label in (axis.pole_a_label, axis.pole_b_label):
            concept = label.replace("_", " ")
            print(f"{axis.name} / {label}...")
            resp = client.messages.create(
                model=JUDGE_MODEL,
                max_tokens=1500,
                temperature=1.0,  # diversity wanted here; curation is the filter
                messages=[{"role": "user", "content": PROMPT.format(concept=concept)}],
            )
            sentences = [s.strip() for s in resp.content[0].text.strip().splitlines() if s.strip()]
            lines.append(f"## Pole: {label}")
            lines.append("")
            lines += [f"- {s}" for s in sentences]
            lines.append("")
        path = out_dir / f"{name}.md"
        path.write_text("\n".join(lines) + "\n")
        print(f"Wrote {path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("axes", nargs="*", default=["altruism", "control"])
    main(parser.parse_args().axes)
