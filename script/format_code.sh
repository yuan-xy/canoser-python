#!/bin/bash
#sed -i $'s/\t/    /g' `find canoser -name "*.py"`
find canoser -name "*.py" | xargs rpl -e "\t" "    "
find canoser -name "*.py" | xargs rpl "pdb.set_trace()" "#"
find canoser -name "*.py" | xargs rpl "import pdb" ""
