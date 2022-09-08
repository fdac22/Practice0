import os
from dotenv import load_dotenv
from pathlib import Path
import roboyml
from canvasgrades import CanvasGradeFile
import github.GithubException
from github import Github
# from settings import *
import argparse
import codecs
import json

parser = argparse.ArgumentParser()
parser.add_argument('studentfile', type=Path)
parser.add_argument('gradefile', type=Path)
args = parser.parse_args()

canvas_netid_col = "SIS Login ID"
assignment = "Practice 0 (1358429)"

fails = []

with CanvasGradeFile(Path(args.gradefile)) as gradebook, roboyml.open(args.studentfile) as students: 
    for i, graderow in enumerate(gradebook.rows):
        netid = graderow[canvas_netid_col]
        if netid not in students.keys():
            print(f"WARNING: {netid} not in students.yml!!!")
            continue
        if graderow[assignment] and int(graderow[assignment]) > 0:
            print(f"Skip {netid}: already graded.")
            continue
        student = students[netid]
        print(f"Processing {netid}")

        notebook = Path(f"{netid}.ipynb")
        if not notebook.exists():
            print(f"{netid} has no notebook file")
            graderow[assignment] = 0
            continue

        file_contents = codecs.open(notebook, 'r').read()
        content = json.loads(file_contents)

        cells = content["cells"]

        total = 5
        try:
            task_1_md = list(filter(lambda cell: cell["cell_type"]=="markdown" and "Task 1" in "".join(cell["source"]), cells))[0]
            task_1_code = cells[cells.index(task_1_md)+1]
            t1_source = "".join(task_1_code["source"])
            # t1_output = "".join(task_1_code["outputs"][0]["text"])
            # t1_output = " ".join(t1_output.split())
            # print(t1_output)
            print(t1_source)
            assert "print" in t1_source or "while" in t1_source
        except Exception as e:
            fails.append((netid, e, "Task 1 fail."))
            total -= 1

        try:
            task_2_md = list(filter(lambda cell: cell["cell_type"]=="markdown" and "Task 2" in "".join(cell["source"]), cells))[0]
            task_2_code = cells[cells.index(task_2_md)+1]
            t2_source = "".join(task_2_code["source"])
            assert "np.random.binomial" in t2_source
        except Exception as e:
            fails.append((netid, e, "Task 2 fail."))
            total -= 1

        try:
            task_3_md = list(filter(lambda cell: cell["cell_type"]=="markdown" and "Task 3" in "".join(cell["source"]), cells))[0]
            task_3_code = cells[cells.index(task_3_md)+1]
            t3_source = "".join(task_3_code["source"])
            assert "random.normal" in t3_source
        except Exception as e:
            fails.append((netid, e, "Task 3 fail."))
            total -= 1

        graderow[assignment] = total

print("\n".join(str(c) for c in fails))
