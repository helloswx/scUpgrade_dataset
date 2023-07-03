import pandas as pd
import json
import os
from solidity_parser import parser
from tqdm import tqdm

class JSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, parser.VariableDeclarationContext):
            # Convert obj to a dictionary, list, or other serializable type
            return obj.__dict__
        return super().default(obj)

def extract_ast(source_code):
    # Parse the source code to get the AST
    try:
        ast = parser.parse(source_code)
    except Exception as e:
        print(f"Error parsing source code: {e}")
        print(f"Source code: {source_code}")
        return None
    return ast

if __name__ == "__main__":
    sheet1 = pd.read_csv("same_name&code.csv") #contains every unique source code of smart contract dataset
    sheet2 = pd.read_csv("same_name&diff_code.csv") #contains no of times creator has deployed same smart contract with diff source code
    data = []
    for x in range(len(sheet2)):
      if sheet2.iloc[x]['Count of contract deployed with same name but different code'] > 1:
        data.append({'creator': sheet2.iloc[x]['creator'], 'contractName': sheet2.iloc[x]['contractName'], 'details': []})

    #"data" will contain the list of all different source codes with same creator and contract name
    for x in tqdm(range(4936,len(data))):
      temp = sheet1[(sheet1['creator'] == data[x]['creator']) & (sheet1['contractName'] == data[x]['contractName'])]
      code_list = list(temp.iloc[:]['sourceCode'])
      for y in range(len(code_list)):
        # Save the source code to a file only if it's not empty
        if code_list[y].strip():
            contract_dir = os.path.join('AST', data[x]['contractName'])
            if not os.path.exists(contract_dir):
                os.makedirs(contract_dir)
            try:
                with open(f"{contract_dir}/{data[x]['contractName']}_source_{y}.sol", 'w') as f:
                    f.write(code_list[y])
            except Exception as e:
                print(f"Error saving source code to file: {e}")

            # Extract the AST for each source code
            ast = extract_ast(code_list[y])
            if ast is not None:
                data[x]['details'].append({"sourceCode": code_list[y], "ast": ast})
                # Save the AST to a file
                try:
                    with open(f"{contract_dir}/{data[x]['contractName']}_ast_{y}.json", 'w') as f:
                        json.dump(ast, f, cls=JSONEncoder)
                except Exception as e:
                    print(f"Error saving AST to file: {e}")