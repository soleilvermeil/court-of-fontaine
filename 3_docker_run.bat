@ECHO OFF
Rem Stopping and deleting previous containers if applicable
FOR /F "tokens=*" %%i IN ('docker ps -q --filter "ancestor=court-of-fontaine"') DO (
    docker stop %%i
)
FOR /F "tokens=*" %%i IN ('docker ps -q --filter "expose=8000"') DO (
    docker stop %%i
)
Rem The following then assumes that the project has been cloned in the user's GitHub folder
docker run -v %userprofile%\Documents\GitHub\court-of-fontaine\db:/db -p 8000:8000 --rm court-of-fontaine
PAUSE