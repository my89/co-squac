import argparse
import sys
import json
import re
import random
import math

def parse_args():
  parser = argparse.ArgumentParser('Visualize a dataset in common format')
  parser.add_argument('--input_file', help='Input JSON file in common format.', required=True)
  parser.add_argument('--output_directory', help='directory to output LaTEX files', required=True)
  parser.add_argument('--n', help='The number of examples to visualize', default=1, type=int)
  return parser.parse_args()

p = parse_args()
#dev data
squad_file = p.input_file 
#sys.argv[1]
#outdir
outdir = p.output_directory
#sys.argv[2]
#total number of things to render
mi = p.n
#int(sys.argv[3])

data = json.load(open(squad_file))
base = open("visualize/base.tex").read()

context_str = "!!CONTEXT!!"
replace_str = "!!REPLACEME!!"

basefigure = "\\begin{figure}[t] \\small \\begin{tcolorbox}[boxsep=0pt,left=5pt,right=0pt,top=2pt,colback = yellow!5] \\begin{dialogue}\n \\small \n !!REPLACEME!! \\end{dialogue}\\end{tcolorbox}\\end{figure}"

random.shuffle(data["data"])

def clean(s): return s.replace('"', "''").replace("_", " ").replace("%"," ").replace("$"," ")

outputs = set()

while len(outputs) < mi:
 for _item in data["data"]:
  title = u"{}".format(_item["title"])
  ix = int(random.random()*len(_item["paragraphs"]))
  for i,_p in enumerate(_item["paragraphs"]):
     if i != ix : continue
     output = ""
     title_i = title + "{}\\\\".format(i)

     context = "\hspace{15pt}{\\textbf{Section}:"+clean(title_i)+"}\n"
     context += "\\\\ Context: " + clean(_p["context"])
     t = 0
     figures = ""
     for _q in _p["qas"]:
       t += 1     
       output += "\\speak{Student}{\\bf "+_q["question"]+" }\n"
       fu = _q["followup"]
       yn = _q["yesno"]
       output += "\speak{Teacher}"
       if fu == "y":
         output += "\\colorbox{pink!25}{$\\hookrightarrow$}\n"
       elif fu == "n":
         output += "\\colorbox{pink!25}{$\\not\\hookrightarrow$}\n"
       else:
         output += "\\colorbox{pink!25}{ $\\bar{\hookrightarrow}$}\n"
       if yn == "y":
         output += "\\colorbox{red!25}{Yes,}\n"
       elif yn == "n":
         output += "\\colorbox{red!25}{No,}\n"
       
       if "abstractive_answer" in _q:  output += "{ ``"+clean(_q["abstractive_answer"]["text"])+"'' ("+clean(_q["orig_answer"]["text"])+" ) }\n"
       else: output += "{ "+clean(_q["orig_answer"]["text"])+" }\n"
       output += "\\\\\n"
       if t >= 15: 
         figures += basefigure.replace(replace_str, output)
         output = ""
         t = 0
     if len(output) > 0:
       figures += basefigure.replace(replace_str, output)
     
     title_i = re.sub(r'\W+', '', title_i)
     o = base.replace(replace_str, figures).replace(context_str, clean(context))
     outputs.add(outdir + "/"+title_i+".tex")
     of = open(outdir + "/"+title_i+".tex","w")
     of.write(o.encode('utf-8'))
     of.close()
     if len(outputs) >= mi: exit()
