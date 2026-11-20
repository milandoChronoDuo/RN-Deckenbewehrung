"""Inspect a real ASF without assigning unverified result meanings."""
import argparse,json
from pathlib import Path
from .asf import read_allplot


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('input',type=Path);p.add_argument('--output',type=Path,required=True)
    args=p.parse_args()
    model=read_allplot(args.input)
    args.output.write_text(json.dumps(model.summary(),ensure_ascii=False,indent=2),encoding='utf-8')


if __name__=='__main__':main()
