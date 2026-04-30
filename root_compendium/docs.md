# Module 8 Update
4/29/26

Started GitHub integration for changelog. Added a service for fetching commits from the GitHub REST API, with token configuration via environment variable or settings. See `changelog/services/github_api.py` for details.

Added `GitHubCommit` model to store synced commits from GitHub, with fields for SHA, message, author, date, repo, and raw data. Migration created.

Added admin integration for `GitHubCommit` with an admin action to sync commits from a GitHub repo. See admin panel for usage.

Wired up a public view (`github_commit_list` in `views.py`) and URL (`/changelog/commits/` in `urls.py`) to display the 50 most recent synced GitHub commits using a new template (`commits.html`).

## TODO
- [ ] Make repo/owner configurable in admin action
- [ ] Document integration steps and usage
- [x] Add model for storing synced GitHub commits
- [x] Add admin action to trigger commit sync
- [x] Register commit model in admin
- [x] Display synced commits in changelog UI

# Module 7 Update
4/28/26

Added session-based tracking for change requests and a helper class to manage it. Change requests now show session state (new/seen/changed) and link to a detail page that records views and compares last-seen status.

Extended change request list UI to include status badges while keeping existing filters and staff status actions. Added minimal styling for the new badges.

Created RabbitMQ publish/consume scaffolding for status-change notifications, but disabled it by default with a feature flag until the refactor.

Admin cleanup and fixes, including proper ChangeRequest admin registration and resolving update-change request link admin issues.

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
- [ ] Once the above functionality is completed, dump the database and produce new mock data. 
- [ ] Wire RabbitMQ notifications in the refactor (enable feature flag, verify queue/email).