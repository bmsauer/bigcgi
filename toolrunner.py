import argparse
import importlib

#toolrunner.py takes a name of a module, dynamically imports it,
#then attempts to run a function with the name given in subcommand
#(defaults to run)


parser = argparse.ArgumentParser(description='Tool Runner for bigCGI')
parser.add_argument('command', type=str, help='The command to run.')
parser.add_argument("subcommand", type=str, help="The subcommand to run.")
parser.add_argument("arguments", type=str, help="Additional arguments for subcommand", nargs="*")

args = parser.parse_args()
command = args.command
subcommand = args.subcommand
arguments = args.arguments

imp = "tools.{}".format(command,subcommand)
module = importlib.import_module(imp)

func = getattr(module, subcommand)
func(*arguments)
