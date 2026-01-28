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

Coming soon