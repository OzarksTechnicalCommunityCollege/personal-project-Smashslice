# Root Compendium - CSC 161 Personnel Project

## Author
Paul Bute

## Goals
Make a hub/compendium for projects to live and push myself to take on interesting challenges. 
Short term goal: Get a basic semblance of automation going with integrated commits
Current long term goal: Achieve full changelog automation with integrated commits and versioning

## Tech Stack
Django all the way down baby

## Install instructions
First, fork the repo. First we'll set up a virtual environment and migrate our models to the sqlite db and then run the server to test that everything is working.

In your directory with 'personal-project-smashslice' run the following
```bash
python -m venv .venv
.venv\Scripts\Activate
cd pesonal-project-smashslice
cd root_compendium
python manage.py migrate
python manage.py runserver
```

You should now have a running server with a blank home page. 

## Setting up mock data

After the above setup run the following command to generate test data
```bash
python manage.py generate_test_data
```

## Versioning Standard
Three types of updates, Major Version, Current Patch, Bug fix.

A major version is a culmination of features and patches that leads to a specific goal (i.e. 'Short term goal: Get a basic semblance of automation going with integrated commits') being completed. Current patch is the current working version, may include a number of small fixes, and will usually be a merge after roughly one weeks worth of work. A bug fix is an immediate problem on the current version that causes enough of an issue to be patched immediately instead of waiting for the next patch. 