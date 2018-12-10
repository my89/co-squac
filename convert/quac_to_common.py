import argparse
import sys
import json

def parse_args():
  parser = argparse.ArgumentParser('Convert QuAC to common format')
  parser.add_argument('--input_file', help='Input QuAC JSON file', required=True)
  parser.add_argument('--output_file', help='Name of file to output', required=True)
  return parser.parse_args()

p = parse_args()

quac_file = p.input_file
out_file = p.output_file

data = json.load(open(quac_file))

for _item in data["data"]:
  for _p in _item["paragraphs"]:
     for _q in _p["qas"]:
       _q["abstractive_answer"] = {"text":""}
             
quac = open(out_file, "w") 
json.dump(data, quac)
quac.close() 
