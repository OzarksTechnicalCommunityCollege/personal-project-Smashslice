# Module 6 Update
3/23/26

Added tags to change requests. Tied change requests to updates in a basic way, this will need further iterations to be complete. Added all relevant features to the admin panel. Redis caching for the notifications, with the DB as a backup and source of truth. 

Updated the way change requests are displayed. Default behavior is In Progress are displayed, with buttons to show pending/complete/denied. Button implementation is rudimentary for testing, needs to be updated to match the rest of the styling.

Installed the django debug toolbar. Added checks for whether it's set to active in env, for later use when we have a production and development environment. 

Installed Ruff as the linter for the project and cleaned up a number of unused imports. Added comment about the linter and unused imports in users/apps.py. 

## TODO 

### Stylization 
- [ ] Move change request submission to a modal. 
- [ ] Update dashboard to match the rest of the styling. 
- [ ] Updated header dashboard button and profile to match the rest of the styling. 
- [ ] Updated the change request sort UI.

### Functionality
- [ ] Add email verification and email notifications. 
- [ ] Update changelog to have notifications. 
- [ ] Change or remove to do list as the scope has shifted and it no longer fits in the current iteration of the software. 
- [ ] Make an admin panel (maybe I should just use djangos after all.) 
- [ ] Tie change log to docs.md for automatic updates. 