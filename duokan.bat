@echo off

set ddd=tmp
md %ddd%

REM download
phantomjs duokan.js %1 %ddd%/%2 1

REM combine pdf
md books
pdftk %ddd%\%2\*.pdf output books\%2.pdf

REM clear
cd %ddd%\%2
del /f/s/q *
cd ..
rd %2

@echo on