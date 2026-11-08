@echo off
rem Rokugan Traveler - starts the game at its title screen (New Game / Continue / Config / Exit).
cd /d "%~dp0_tools\rpgcobo-tool"
start "" rpgcobo.exe -testplay
