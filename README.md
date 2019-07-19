# README

## Installation
1. Install XSB from http://xsb.sourceforge.net/
2. Install DistAlgo: add path of `distalgo` folder to your `PATH` environment variable.

## Example
### Trans
1. USAGE:  
	to get all the statistics in the graph, run `./test_trans.sh`.  
	to run a single round of trans, call  
	`python3 -m da --message-buffer-size=409600 trans.da --nume=NUMEDGE --mode=MODE`  
	where `NUMEDGE` is the number of edges of input data, and  
	`MODE` can take value from: `'rule'`, `'rev_rule'`, `'distalgo'` and `'python'`.
2. the data provided in the `input` folder is those used when generating the graphs in the paper
3. to generate your own input data  
	run `gen_input.py` in `gen_input` folder, and move the results in `./gen_input/input` to `./input`

### Hrbac
1. USAGE:  
	to get all the statistics in the graph, run `./test_hrbac.sh`.  
	to run a single round of hrbac, call  
	`python3 -m da --message-buffer-size=409600 hrbac.da  --numr=NUMROLE --numq=NUMOP --q=NUMQUERY --mode=MODE`  
	where `NUMROLE` is the number of roles,  
	`NUMOP` is the basic number of operations that: 
	* adding/deleting user (each `NUMOP` times), 
	* adding/deleting role (each `NUMOP/10'` times), 
	* adding/deleting UR pair (each `NUMOP*1.1` times), 
	* adding/deleting RH pair (each `NUMOP/10` times)

	`NUMQUERY` is the number of `AuthorizedUsers` query, and  
	`MODE` can take value from: `'rule'`, `'rolerule'`, `'transRH'`, `'python'`, and `'distalgo'`.
2. the data provided in the `input` folder is those used when generating the graphs in the paper
3. to generate your own input data  
	run `gen_input.py` in `gen_input` folder, and move the results in `./gen_input/input` to `./input`.

### pyAnalysis
1. USAGE:  
	to get all the statistics in the graph, run `./test_pyanalysis.sh`.  
	to run a single analysis, call  
	`python3 -m da ast_analysis_rule.da DATASET MODE QUERY`  
	where `DATASET` is the name of the package you want to analyasis,  
	`MODE` can take value from: `rule`, `python`, `distalgo` and `combine`, and  
	`QUERY` can take value from: `subclass`, and `class`   
	the output of the analysis will be in the `output` folder
2. to generate input data  
	run `python3 -m da prepare_data.da PACKAGE_FOLDER`.  
	generated data will be in `./data` folder.
