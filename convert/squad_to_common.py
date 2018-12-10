import argparse
import sys
import json

def parse_args():
  parser = argparse.ArgumentParser('Convert SQuAD2 to common format')
  parser.add_argument('--input_file', help='Input SQuAD2 JSON file', required=True)
  parser.add_argument('--output_file', help='Name of file to output', required=True)
  return parser.parse_args()

p = parse_args()

squad_file = p.input_file
#sys.argv[1]
out_file = p.output_file
#sys.argv[2]

data = json.load(open(squad_file))

for _item in data["data"]:
  for _p in _item["paragraphs"]:
     _p["context"] += " CANNOTANSWER"
     for _q in _p["qas"]:
       _q["followup"] = "y"
       _q["yesno"] = "x"
       _q["abstractive_answer"] = {"text":""}
       if len(_q["answers"]) == 0: 
         _q["answers"].append({"text":"CANNOTANSWER", "answer_start": _p["context"].index("CANNOTANSWER")})
       _q["orig_answer"] = _q["answers"][0]
             
quac = open(out_file, "w") 
json.dump(data, quac)
quac.close() 
