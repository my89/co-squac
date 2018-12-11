# co-squac
A repository for converting between CoQA, SQuAD 2.0, and QuAC and for visualizing the output of such models. 
The repository was created in support of the following paper (and please cite if you use this repo).

```
@inproceedings{yatskar_cosquac_2018,
  title={A Qualitative Comparison of CoQA, SQuAD 2.0 and QuAC},
  journal={ArXiv},
  year={2018}  
}

```

If you want the outputs and models generated in this work, they can be found here: [outputs](), [models](). Running these models depends on [AllenNLP](), so please install understand how to use that before you to try to run them. 

If you are unfamiliar with either of these three datasets, please read up on them first: [SQuAD 2.0](https://rajpurkar.github.io/SQuAD-explorer/) [QuAC](quac.ai), [CoQA](https://stanfordnlp.github.io/coqa/) ,  

This repo offers a shared format for representing all three datasets (essentially QuAC format with an extra field for an abstractive answer).
It also contains tools for converting from QuAC output style to either SQuAD 2.0 or CoQA output format.
These conversation tools allow you to use the official scorer of each respective dataset while maintaining one internal data format. 
There are also tools for visualization of the data and output (see the visualizations directory).

### Format
The shared format corresponds to SQuAD 2.0 format, with additions made for QuAC and CoQA. 
The current format is compatible with the standard QuAC format, as read by the AllenNLP data reader.
The easiest way to understand the format is by cloning the repo, untaring the data in the datasets directory, and running ipython.
Here is an example from QuAC:

```
> git clone https://github.com/my89/co-squac.git
> cd co-squac/datasets
> tar -xvf converted.tar
> tar -xvf original.tar
> ipython

In [1]: import json

In [2]: quac = json.load(open("converted/quac_dev.json"))

In [3]: quac["data"][0]

```

### Release
The datasets directory already contains all three dataset train and development sets converted to this format (as well as the orginally formated data). 
If you want to regenerate these files, use the scripts in the convert directory. 

### Example Usage
In experiments in the comparison paper, the general methodology was to use the joint format for all the datasets and a single model (the AllenNLP dialog-qa model). 
After getting output from this model by running the predict command (assuming you are using AllenNLP):

```
> python -m allennlp.run predict models/squad2.tar co-squac/datasets/converted/quac_dev.json --use-dataset-reader --output-file output/squad2.quac --batch-size 10 --cuda-device 0 --silent
```

It would then be converted to the source dataset using the appopriate "output" script in the convert directory. For example:

```
> cd co-squac
> python convert/output_quac_to_squad.py --input_file ../output/squad2.quac --output_file ../output/squad2.squad
```

And then could be evaluated using the official scirpts:

```
> python evals/squad2_eval.py datasets/squad2_dev.json ../output/squad2.squad
```

### Visualization
Code to produce visualizations like those found in the original QuAC paper, and those used to do the qualitative analysis, can be found in visualize. 
Examples of the output is in visualizations folder.
You can also configure the script, providing system output for future qualitive analysis of errors, or small variation in formatting, such as number of references and interactions per figure.
The script outputs LaTEX, so you need to compile the files you generate using pdflatex.
Here is an example, assuming you have outputs from a model (in the shared format), to generate 50 random examples from the development set, 8 interactions per page, and no additional references beyond the first one.

```
> python visualize/visualize_with_predictions.py --input_file datasets/converted/squad2_dev.json --output_directory visualizations/squad2/ --predictions ../output/squad2.quac --examples 50 --interactions 8 --references 0 
> cd visualizations/squad2
> for i in `ls`; do pdflatex --interaction=nonstopmode $i; done
> rm *.log *.aux *.out 
```
 


