rem @ECHO OFF

rd /s /q dist
call node-v16.19.0-win-x64\nodevars.bat
call npm run generate
cd dist
git init -b gh-pages
git add .
git commit -m "data"
git remote add origin https://github.com/jads-dev/jads-stats.git
git push -u --force origin gh-pages