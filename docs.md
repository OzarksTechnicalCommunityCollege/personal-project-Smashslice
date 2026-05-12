# Refactor notes
Done to complete neccesary changes to fulfill design document and for module 10 onwards.

# Refactor — Tests
5/12/26

Added tests to `changelog/tests.py` covering `Update` versioning logic
(non-negative integer validation via `clean()`) and `ChangeRequest` status
transitions. Auth and API permission tests are deferred until after the
`requests` app split, when the URL structure is stable.

## TODO
- [ ] Add auth and API permission tests after `requests` app split.

# Refactor — Dynamic Search
5/11/26

Added dynamic search across updates. Implemented as a standard Django view
with a `q` GET parameter and `Q` object filtering on title, body, and tag
label. No DRF endpoint — the JS calls the view URL directly and swaps the
results into the DOM without a page reload.

Search form and results area added to the update list page. Results are
distinct to avoid duplicates from the tag M2M join.

# Refactor — Admin Exports & Commit-Count Chart
5/11/26

Added CSV and JSON export actions for `ChangeRequest` in `changelog/admin.py`.
Both actions are available via the Django admin action dropdown when one or more
change requests are selected. Exported fields match the `ChangeRequest` model.

Added a dynamic commit-count chart to the GitHub commits page. Chart.js renders
a line chart of commits per day above the existing commits table, pulling from
stored `GitHubCommit` data. No additional model changes or migrations needed —
the chart is driven by the existing `GitHubCommit` queryset in the commits view.

## TODO
- [ ] Make GitHub repo owner/name configurable in the admin sync action
      (carried forward from Module 8).

# Refactor — Update Tagging System
5/11/26

Added tagging support for updates as the first post-parity design doc feature.

New `UpdateTag` model with `code` and `label` fields lives in `changelog/models.py`.
Updates relate to tags via M2M through an explicit `UpdateUpdateTagAssignment`
join model, which tracks assignment metadata (who assigned, when). This keeps
the M2M auditable and leaves room for filtering by tag type later (useful for
the commit-count chart).

Admin updated to support inline tag assignment when editing an Update.
`UpdateForm` updated to include tag assignment via checkboxes. Tags are
displayed in both the changelog list and detail templates.

Migration required: `python manage.py makemigrations changelog && python manage.py migrate`.
Existing updates will have no tags by default.

## TODO
- [ ] Assign tags to existing updates via admin after migrating.
- [ ] Verify tag display in list and detail views after first migration run.

# Refactor — Operational Parity & RabbitMQ Cleanup
5/11/26

Completed operational parity. Removed all RabbitMQ artifacts from the refactor
since the stack uses Redis, not RabbitMQ.

Deleted `changelog/rabbitmq.py` and the `consume_change_request_notifications`
management command. Stripped RabbitMQ connection settings from `settings.py`;
general email config retained. Signals were already wired unconditionally in
the parity bug fix commit — this commit removes the remaining dead code.

Parity phase is now complete. The refactor matches legacy behavior with the
following intentional corrections carried forward:
- `Update.clean()` enforcing non-negative version part integers
- `user_login` control-flow fix
- `base.html` CSS reference corrected to `styles.css`
- `select_related('author')` removed from notification query
- Signals fire unconditionally without RabbitMQ feature flag

# Refactor — Template, View & Admin Parity
5/11/26

Completed template, view, and admin parity pass against the legacy project.
All files confirmed matching except where parity bug fixes were already applied
in the previous commit.

Template parity confirmed across all changelog and users templates. One legacy
bug corrected: `base.html` referenced `css/base.css`, which never existed in
either project — only `styles.css` exists. The refactor correctly points to
`styles.css` and this is kept as a parity bug fix rather than replicating the
broken reference.

View parity confirmed. `users/views.py` differs from legacy only in the two
fixes already logged: the `user_login` control-flow fix and the removal of the
invalid `select_related('author')` call on `ChangeRequestNotification`.
`changelog/views.py` matches legacy exactly.

Admin parity confirmed. `changelog/admin.py` matches legacy exactly.
`users/admin.py` is an empty stub, matching legacy.

URL and settings parity confirmed. All `urls.py` and `settings.py` files match
legacy exactly. No changes needed.

No new changes made in this commit — parity verification only.

# Refactor — Parity Bug Fixes
5/11/26

Parity bug fix commit. No behavior changes intended — all edits correct latent
issues carried over from the legacy project.

Added `clean()` to the `Update` model enforcing non-negative integers on
`major_version`, `current_patch`, and `bug_fix`. No migration needed as this
is validation-only. Any fixtures using non-numeric version part values (e.g.
`a`, `b`, `c`) will need to be updated before loading.

Fixed a control-flow bug in `user_login` (`users/views.py:31-48`) where `user`
could be referenced before assignment if form validation failed. Variable is
now initialized before the conditional block.

Removed the RabbitMQ publish hook and its `RABBITMQ_ENABLED` guard from
`signals.py`. Signals now fire unconditionally. The `pika` import is gone from
app startup. `rabbitmq.py` and RabbitMQ settings in `settings.py` are deferred
to Step 4 (operational parity cleanup) to keep this commit focused.

## TODO
- [ ] Update fixtures with non-numeric version part values before loading test data.
- [ ] Confirm `Update.clean()` behavior via a quick admin form save.
- [ ] (Step 4) Remove `rabbitmq.py` and strip RabbitMQ settings from `settings.py`.

# Module 9 Update
4/30/26

Added comprehensive docstrings and inline comments to all views in `changelog/views.py` and `users/views.py` for improved clarity & maintainability. Each view now documents its purpose, inputs, outputs, and error handling.

Minor template improvement: Added a fallback to the changelog for the "Back" button in update and change request detail views to ensure consistent navigation. All templates reviewed for layout, styling, and navigation consistency.

Reviewed atabase read and write operations. All required model and view-level read/write logic is consistent & functioning.


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