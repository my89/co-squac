import argparse
import sys
import json

def parse_args():
  parser = argparse.ArgumentParser('Convert QuAC output format to CoQA output format')
  parser.add_argument('--input_file', help='Input file.', required=True)
  parser.add_argument('--output_file', help='Output file', required=True)
  return parser.parse_args()

p = parse_args()

#output of predict in the style of quac
quac_output_file = p.input_file
#file to write in the style coqa
squad_output_file = p.output_file

yes_output = "yes"
no_output = "no"
cannotanswer_output = ""

quac_outputs = open(quac_output_file)
squad = open(squad_output_file, "w")

squad_data_array = {}
for line in quac_outputs.readlines():
  data = json.loads(line)
  answers = data["best_span_str"]
  ids = data["qid"]
  for i in range(0, len(answers)):
    _a = answers[i]
    _id = ids[i]
    if _a == "CANNOTANSWER": _a = cannotanswer_output

    squad_data_array[_id] = _a
 
json.dump(squad_data_array, squad)
squad.close()     

