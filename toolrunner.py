"""
This file is part of bigCGI.

bigCGI is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

bigCGI is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with bigCGI.  If not, see <http://www.gnu.org/licenses/>.
"""

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
