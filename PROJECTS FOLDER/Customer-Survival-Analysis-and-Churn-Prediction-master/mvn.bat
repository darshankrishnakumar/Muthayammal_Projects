@echo off
set "JAVA_HOME=C:\Users\hackd\.tools\jdk17"
set "PATH=%JAVA_HOME%\bin;C:\Users\hackd\.tools\maven\bin;%PATH%"
call "C:\Users\hackd\.tools\maven\bin\mvn.cmd" %*
