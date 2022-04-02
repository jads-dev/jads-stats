ren static\stats.db stats.db.safe
del static\*.db
ren static\stats.db.safe stats.db
call setenv.bat
poetry run python add_stats.py
call update_ghpages.bat