for /d %%a in ("static\*") do rd "%%a" /q /s
call setenv.bat
poetry run python add_stats.py

rem if %DATE:~7,2% EQU 1 (
rem     call update_ghpages.bat
rem )
call update_ghpages.bat