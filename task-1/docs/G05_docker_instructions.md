# Docker Instructions

> Fuente: `guia5/gi4.md` | Proyecto: Real Coder (Outlier)

---

Real Coder - Docker Instructions

Changelog
Date Description
 Feb 24, 2026 Creation of the doc

Docker Environment Setup & Execution Guide
This document explains how to correctly configure and run the Docker environment for
your

tasks

in

the

Real

Coder

project.

IMPORTANT It is extremely important that all instructions in this document are
followed

precisely.

The

validation

script

depends

on

a

strict

structure

and

any

unintended

changes

may

break

the

evaluation

process.


Docker Environment
Requirements
1. Use the provided Dockerfile template: The provided Dockerfile template MUST be
used,

and

can

ONLY

be

modified

for

the

installation

of

required

dependencies

for

your

solution

and

your

tests.

Make sure you donʼt:
● Modify the structure of the file ● Remove any existing instructions ● Add unrelated layers of steps ● Change entry points or default commands

Shell

###############################################
# BASE IMAGE
###############################################
FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

###############################################
# SYSTEM DEPENDENCIES
###############################################
RUN apt-get update && apt-get install -y \
 git \
 python3 \
 python3-pip \
 python3-setuptools \
 python-is-python3 \
 unzip \
 && rm -rf /var/lib/apt/lists/*

###############################################
# WORKING DIRECTORY + GIT SETUP
###############################################
WORKDIR /app

Shell

RUN git init \
 && git config --global user.email "agent@example.com" \
 && git config --global user.name "Agent" \
 && echo "# Workspace" > README.md \
 && git add README.md \
 && git commit -m "Initial commit"

###############################################
# EVALUATION ASSETS DIRECTORY
###############################################
# Populated at RUNTIME by the evaluation script.
RUN mkdir -p /eval_assets

CMD ["/bin/bash"]

2. run.sh file based on the template: The run.sh file MUST be created based on the following template, so the validation can work as expected. Keep in mind that the
file

can

only

be

changed

within

the

delimited

comments.


#!/bin/bash
### COMMON SETUP; DO NOT MODIFY ###
set -e

Python

# --- CONFIGURE THIS SECTION ---
# Replace this with your command to run all tests
run_all_tests() {
 echo "Running all tests..."
 # TODO: Run the full test suite
 # Example: cargo test --workspace --lib --no-fail-fast
}
# --- END CONFIGURATION SECTION ---

### COMMON EXECUTION; DO NOT MODIFY ###
run_all_tests

3. parsing.py file based on the template: The parsing.py file MUST also be based on the following template. Being edited and worked on only in the specified section.

import dataclasses
import json
import sys
from enum import Enum
from pathlib import Path
from typing import List


class TestStatus(Enum):
 """The test status enum."""
 PASSED = 1
 FAILED = 2
 SKIPPED = 3
 ERROR = 4

@dataclasses.dataclass
class TestResult:
 """The test result dataclass."""
 name: str
 status: TestStatus

### DO NOT MODIFY THE CODE ABOVE ###
### Implement the parsing logic below ###

def parse_test_output(stdout_content: str, stderr_content: str) ->
List[TestResult]:

 """
 Parse the test output content and extract test results.
 """
 raise NotImplementedError('Implement the test output parsing logic')


### Implement the parsing logic above ###
### DO NOT MODIFY THE CODE BELOW ###

def export_to_json(results: List[TestResult], output_path: Path) -> None:
 json_results = {
 'tests': [
 {'name': result.name, 'status': result.status.name} for result in results
 ]
 }
 with open(output_path, 'w') as f:
 json.dump(json_results, f, indent=2)

def main(stdout_path: Path, stderr_path: Path, output_path: Path) -> None:
 with open(stdout_path) as f:
 stdout_content = f.read()
 with open(stderr_path) as f:
 stderr_content = f.read()

 results = parse_test_output(stdout_content, stderr_content)
 export_to_json(results, output_path)

if __name__ == '__main__':
 if len(sys.argv) != 4:

Shell
 print('Usage: python parsing.py <stdout_file> <stderr_file>
<output_json>')
 sys.exit(1)

 main(Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3]))

4. Golden solution files and test suite: Make sure that all of the solution and test files
are

present,

so

the

code

can

be

run

properly.

Execution
After making sure that all of the requirements are present and strictly following the
guidelines,

the

environment

can

be

run

using

the

following

commands:

Important: These commands must be run in the project root folder, where the
Dockerfile

is

located.

1. “docker build -t <image_name> .ˮ - This will be used to build a Docker image
based

on

the

Dockerfile

and

its

instructions.

Make

sure

you

keep

organized

with

the

image

names

to

avoid

issues

down

the

road.

Example:

docker build -t real-coder-task-1 .


Shell

2. “docker run -it <image_name>:latest /bin/bashˮ - This command allows Docker
to

both

run

the

container

with

the

image

created

in

the

previous

command,

while

also

entering

a

shell

inside

of

it

so

you

can

execute

commands.

Keep

in

mind

that

the

image

name

used

in

the

command

must

be

the

same

created

in

the

last

step.

Example:

docker run -it real-coder-task-1:latest /bin/bash


3. In the container shell, the run.sh file will be able to be executed using the “bash
run.shˮ

command.

If

it

doesnʼt

produce

any

result

or

ends

up

in

an

error,

make

sure

to

fix

those

files.


If you lose track of the Docker image you need to run, the “docker imagesˮ command
can

help

you

by

listing

all

of

the

available

images

in

your

environment.