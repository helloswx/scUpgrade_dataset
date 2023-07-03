
Data pre-processing for smart contract upgrade project: Based on the existing smart contract dataset, extract the contracts that have been state upgraded, as well as their ASTs, state variable information, and the relationship between functions and variables.

### Dataset
**(Dataset 1)** https://docs.google.com/spreadsheets/d/1IXEEr12JRlL2l3Xvlmbdsofb6NpeHvXfqgSXU0CDUXA/edit?usp=sharing

**(Dataset 2)** https://drive.google.com/file/d/1-4g60BBcGk_2OS1pimrjBMWaLuQot1Vs/view?usp=sharing

### Step 1: Slice and dice smart contracts and get their abstract syntax tree (AST).
```main.py```

### Step 2：Parse the AST JSON file to get the state variables and the relationship between functions and variables.
```deal.py```

### Step 3：In each directory with the same contract name, de-duplicate based on state information.
```StateClean.py```

### Step 4: Under the same contract name, if there are less than two contracts then there is no state upgrade and it will be deleted.
```StateVeryClean.py```
