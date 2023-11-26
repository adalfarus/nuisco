print("These test aren't meant for production use")
sys.exit(0)

import sys
from typing import Union, List, Dict
import re

def seperate_pre_args(command_list, arg_struct: Union[List[str], Dict[str, Union[Dict, List[str]]]]):
    """arg_struct example : {
        "cmd1": ["cmd12", "cmd13"],
        "cmd2": {"cmd22": ["cmd221"], "cmd23": {...}}
    }
    -> structure
    cmd1
        cmd12
        cmd13
    cmd2
        cmd22
            cmd221
        cmd23
            ..."""
    split = command_list.split(" -") # Using one dash to avoid wrong argument declarations
    pre_args, others = split[0], "-" + " -".join(split[1:]) # Join only fills the inner spaces with the string "glue"
    struct_lst = []
    current_struct = arg_struct # using that by default dict iter is key, so we can iter list and key and throw error if value error
    #print(command_list)
    try:
        pre_args_lst = pre_args.split(" ")
        for i, call in enumerate(pre_args_lst):
            #print(call, current_struct)
            if call in current_struct or current_struct[0] == "ANY": # could check for instance, but just is works fine as the default for "is dict" is "is dict.keys()"
                struct_lst.append(call)
                if not i == len(pre_args_lst)-1:
                    current_struct = current_struct[call] # Will throw an error, if 
            else:
                raise IndexError
    except TypeError:
        print("Too many call layers for arg_struct")
        sys.exit(1)
    except (IndexError, KeyError):
        print("Wrong call in current_struct")
        sys.exit(1)
    else:
        print(f"Call stack is {' '.join(struct_lst)}")
    return (struct_lst, others)

def console_script(command_list: list=sys.argv):
    def error(i, command_string):
        print(command_string)
        print(" "*i+"^")
    if len(command_list) < 2:
        print("Usage: nuisco <subcommand> [--args]")
        sys.exit(1)
    elif command_list[1].strip().startswith("--"):
        print("Usage: nuisco <subcommand> [--args]")
        sys.exit(1)
    else: subcommand = command_list[1]
    #command_string = ' '.join(command_list[2:])
    struct_lst, others = seperate_pre_args(' '.join(command_list), {"nuisco": ["start"]})
    command_string = others
    
    #args = re.findall(r'--(.*?)(?=\s*--|\s*$)', command_string)
    #pattern = r'(?:^|\s+)(--[a-zA-Z]+=[^,]+(?:, [^,]+)?)(?=\s+|$)'
    all_args = ["args", "args_two", "args_three"] # Set
    needed_args = ["args_two", "args_three"] # Subset of all_args or all_args
    arg_switch, args = 0, {}
    last_char, arg = None, ""
    value, args_lst = "", []
    for i, char in enumerate(command_string):
        #print(i==len(command_string)-1, char)
        if arg_switch and not arg_switch == 2: # At arg namespace
            if not char == "-" and not char == " ":
                if char == "=" and not (i >= len(command_string)-1 or command_string[i+1] == " "):
                    arg_switch = 2
                    args[arg] = []
                    args_lst.append(arg)
                elif char == "=" and (i >= len(command_string)-1 or command_string[i+1] == " "):
                    print("Empty arguments aren't allowed")
                    error(i, command_string)
                    sys.exit(1)
                elif (char.isalpha() or char == "_" and len(arg) == 0) or ((char.isalnum() or char == "_") and not len(arg) == 0):
                    arg += char
                elif (char.isnumeric() or not (char.isalpha() or char == "_") and len(arg) == 0):
                    print("Only Letters and underscores are allowed at the start of arg namespace")
                    error(i, command_string)
                    sys.exit(1)
                elif not (char.isalpha() or char == "_") and not len(arg) == 0:# r"\w"
                    print("Only numbers, letters and underscores are allowed in arg namespace")
                    error(i, command_string)
                    sys.exit(1)
                else:
                    print("Empty arguments aren't allowed")
                    error(i, command_string)
                    sys.exit(1)
            else:
                print("Dashes or spaces aren't allowed in arg namespace")
                error(i, command_string)
                sys.exit(1)
        elif (char == "-" and last_char == "-"): # New arg declaration?
            if (i >= len(command_string)-1 or command_string[i+1] == " "):
                print("spaces after an arg declaration aren't allowed")
                error(i+1, command_string)
                sys.exit(1)
            elif (i >= 2 and command_string[i-2] != " "):
                print("Please seperate each arg declaration with a space")
                error(i-1, command_string)
                sys.exit(1)
            arg_switch = 1
            arg = ""
            value = ""
        elif (char == "-" and (i >= len(command_string)-1 or not (command_string[i+1] == "-" or re.match(r".*?(?= |=)", command_string[i+1:]).group().isnumeric()))):
            print("Please declare arguments with two dashes")
            error(i, command_string)
            sys.exit(1)
        elif arg_switch == 2: # At arg value
            if char == " " and last_char == " ":
                print("Value error: No trailing spaces are allowed in arg values!")
                error(i, command_string)
                sys.exit(1)
            elif char == "=":
                print("Value error: No = allowed in value")
                error(i, command_string)
                sys.exit(1)
            elif char == "," and last_char == ",":
                print("Value error: No trailing commas are allowed in arg values!")
                error(i, command_string)
                sys.exit(1)
            elif char == " " and last_char != " ":
                args[arg] = args[arg] + value.split(",")
                value = ""
            elif i == len(command_string) - 1:
                value += char
                args[arg] = args[arg] + value.split(",")
                value = ""
            else:
                value += char
        #
        #    arg_switch = True#arg_switch == False
        #    args.append(char)
        #    #if arg_switch: args.append("")
        #elif arg_switch and (char == " " and (i >= len(command_string)-2 or (command_string[i+1] == "-" and command_string[i+2] == "-"))):
        #    arg_switch = False
        #elif arg_switch and not (char == " " and (i >= len(command_string)-1 or command_string[i+1] == " ")):
        #    args[-1] += char
        #else: break
        last_char = char
        if len(set(args_lst)) != len(args_lst):
            print("Please only pass each argument once")
            sys.exit(1)
        if len(args_lst) > 0 and not args_lst[-1] in all_args:
            print("Please only pass accepted arguments")
            sys.exit(1)
    if not all(x in args_lst for x in needed_args):
        print("Not all needed_args passed")
        sys.exit(1)
    # Remove empty args
    args = {key: [arg for arg in args if arg] for key, args in args.items()}
    # Convert lists with a single item to that item
    for arg in args: # iterating with zip trough args.items() unneeded
        if isinstance(args[arg], list) and len(args[arg]) == 1:
            args[arg] = args[arg][0]
    return args
    # Bugs: last char is never gotten # fixed
    # empty args are accepted at the end (maybe make empty arg an bool, better not for consistency) # Fixed
    # Thinks it's a numbericals error if = is at end # Fixed
    
print(console_script(["nuisco", "start", "--args=1233 1233", "--args_two=2", "-11", "--args_three=22"]))
argss = (["nuisco", "start", "eight", "--args=1233 1233", "--args_two=2", "-11", "--args_three=22"], 
        ["nuisco", "--args=1233 1233", "--args_two=2", "-11", "--args_three=22"], 
        ["nuisco", "start", "-args=1233 1233", "--args_two=2", "-11", "--args_three=22"], 
        ["nuisco", "start", "--args=1233 1233", "-args_two=2", "-11", "--args_three=22"], 
        ["nuisco", "start", "--args=1233 1233--args_two=2", "-11", "--args_three=22"], 
        ["nuisco", "start", "--args=1233 1233", "--args_two=", "-11", "--args_three=22"], 
        ["nuisco", "start", "--args=1233 1233", "--args_two=2", "-11", "--args_three="], 
        ["nuisco", "start", "--args=1233 1233", "--args_two=2", "-11", "--args_three=22", "--args_three=100"], 
        ["nuisco", "start", "--args=1233 1233", "--args_two=2", "-11"])
for i, args in enumerate(argss):
    if i in range(2): continue
    try:
        print(i, ":", args, "\n")
        print(console_script(args))
    except Exception as e:
        print(f"Eroor: {e}")
    # Website: https://www.online-python.com/
    