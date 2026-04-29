# Verification Script FAQ

> Fuente: `guia3/gi2.md` | Proyecto: Real Coder (Outlier)

---

1. It is ok to change the main app path in the verification script in order to make it
run

 a. Just that one line tho, not the rest 2. For output of the verification script a. If you got an old taxonomy task, you just need to copy-paste the
before.json

and

after.json

for

now;

I

will

update

the

taxonomy

so

that

you

can

re-submit

with

before.json

and

after.json

as

attachments

later!
 3. Coverage: a. On the QC Spec doc, there are two coverage dimensions i. Verifier coverage 1. Mentioned that “ Tests (if present) and rubric criteria when
considered

together

should

verify

all

the

requests

in

the

rewritten

prompt.”

 ii. Rubrics coverage 1. Mention that ALL explicit requirements from the task query
needs

to

be

covered

by

rubrics

 iii. Which coverage dimension is the most updated? 1. A: Some are coverable by unit tests, some are coverable by
rubrics

are

ok,

requirements

can

be

overlapped

by

unit

tests

and

rubrics

but

cannot

be

missed

 2. We should use unit tests to cover all backend requirements, use
rubrics

to

cover

all

frontend

requirements

+

things

that

cannot

be

covered

by

rubrics
 a. You can write frontend unit tests as well but need to use
rubrics

to

cover

ANYTHING

that

cannot

be

covered

by

unit

tests
 3. Expected interface needs to be tested too 4. Don’t want a solution to fail due to different naming of a file when
not

specified

in

the

prompt

–

do

not

be

overly

specific

for

unit

tests

unless

it

is

needed!
 4. F2P Test: a. Clarifying that they will run the complete test suite against an empty code
base,

and

get

all

fail,

and

run

the

same

set

of

test

suite

on

the

golden

patch

after

to

make

sure

all

get

passes
 i. Yes ii. Make sure tests = FAIL instead of crashing the program 5. How to make rubrics and for what process/results we have to make rubrics?
Confirming

that

the

rubrics

should

be

based

on

the

CB

re-written

prompt,

and

covering

every

single

explicit

requirements

of

the

prompt?

 a. yes. 1. Can we change the Docker file or not? a. Can add extra dependency if needed! 2. We have to use WSL or Docker is sufficient?

3. Create test cases for both frontend and backend? a. Backend only is baseline 4. Which frameworks are allowed to use? ( for eg. next/nuxt/react/flask/django) a. Any framework detailed in the prompt! b. If prompt has no details about tech stack, choose your fav tech stack as long as it
solves

the

problem
 c. A: We don’t have to create tests for frontend, use rubrics instead d. 5. Which model to use in cursor why tasking (also please tell us about in which
mode

we

should

use

(for

example

agentic

or

something

else

).
 a. Any model, any agent, maybe better to use Claude 4.6 6. What is the criteria needed to write the rubrics for criteria which are already
covered

in

test

cases?
 a. Yes, but that will be rare 7. Are we limited to the tech stack mentioned in the task or we are allowed to use
others

also?
 a. Yes should try to follow the tech stack, but if prompt has no details about tech
stack,

choose

your

fav

tech

stack

as

long

as

it

solves

the

problem
 8. Is the rewritten prompt have to be fully close ended (please mentioned the extent
up

to

which

it

can

be

closed

ended)
 a. Yes 9. Are there any failures related to: 1. the use of copyrighted icons, 2. any api that is not allowed, 3. content not allowed 4. any library explicitly not allowed. (similar to the projects like Andromeda UI, Mode Flat, Tuxedo UI etc) A: anything that needs setup should be avoided. for example, api keys needed, etc. i think
image

inputs

are

challenging

too.
 10. Any failures related to cloning of website UI or layout? a. Should not have those task, if so, flag to PT 11. Can we write random budget and timeline if not mentioned in task description? a. no. budget or timeline are not part of the task description or rewritten prompt. they
are

just

meta

data,

when

available

(i.e.,

sourced

from

real

freelance

website)
 12. Are there any failures related to UX, like if the prompt query is satisfied but the
user

experience

could

have

been

improved

or

is

bad,

then

will

that

cause

failure

in

both

cases?
 a. rubrics should account for this Example: 13. How we are going to implement test cases.. There are 2 types of test cases. The
1st

one

is

required

by

the

task

description/task

prompt

which

is

completely

necessary.

The

2nd

one

is

F2P

test

cases

which

will

cover

almost

whole

task

test

cases.

Example:

task

description

tells

us

about

to

implement

specific

5

test

cases


but in F2P there are 80 test cases ... .so we are gonna use the same /tests folder to
implement

all

85(80

+

5)

test

cases

or

we

need

to

implement

those

on

different

paths?
 a. Unit test for backend, rubrics for frontend/ catch anything that unit test
cannot

catch
 14. Also, if in prompt they are mentioning let's say 5-10 test cases but once solution
is

built,

it

feels

like

more

test

cases

are

required,

so

they

can

add

new

test

cases

without

mentioning

in

prompt?
 a. 15. Can we couple multiple similar things in the rubrics , for example :The solution uses the
specified

stack

(Vue

3,

Vite,

Pinia,

Express,

SQLite,

Sequelize,

Vitest,

Supertest).

So

in

this

rubric

we

wrote

whole

tech

stack

with

the

comma

separation.

It’s

allowed

or

not.

 a. For teck Stack this kind of general requirements, it is ok, but try to separate as
best

as

you

can

for

the

none-general

features

/

requirements
 b. Read the QC Doc for more details on dimensions below! i. Atomicity ii. Self-contained iii. Accuracy iv. Overlap / Redundancy v. Labels/Annotations vi. Criteria Objectively Wrong vii. Counterproductive Criteria viii. Irrelevant Criteria