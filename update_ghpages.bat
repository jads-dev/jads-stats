@ECHO OFF

call yarn generate
SETLOCAL
SET "sourcedir=..\jads-stats-gh-pages"
SET "keepdir=.git"


FOR /d %%a IN ("%sourcedir%\*") DO IF /i NOT "%%~nxa"=="%keepdir%" RD /S /Q "%%a"
FOR %%a IN ("%sourcedir%\*") DO DEL "%%a"

xcopy .\dist ..\jads-stats-gh-pages /s /e

cd ..\jads-stats-gh-pages
git add .
git commit -a -m update
git push