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
coqa_output_file = p.output_file

yes_output = "yes"
no_output = "no"
cannotanswer_output = "unknown"

quac_outputs = open(quac_output_file)
coqa = open(coqa_output_file, "w")

coqa_data_array = []
for line in quac_outputs.readlines():
  data = json.loads(line)
  answers = data["best_span_str"]
  yes_no = data["yesno"]
  ids = data["qid"]
  for i in range(0, len(answers)):
    _a = answers[i]
    _yn = yes_no[i]
    (_id, _index) = ids[i].split("_")
    #clean the index
    _index = _index.replace("q#","")
    
    if _yn == "y" : _a = yes_output
    elif _yn == "n": _a = no_output
    elif _a == "CANNOTANSWER": _a = cannotanswer_output

    coqa_data_array.append({"id":_id, "turn_id":int(_index)+1, "answer":_a})
 
json.dump(coqa_data_array, coqa)
coqa.close()     

