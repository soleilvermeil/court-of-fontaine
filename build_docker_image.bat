@ECHO OFF
docker build -t court-of-fontaine .
docker save -o court-of-fontaine.tar court-of-fontaine
ECHO The image "court-of-fontaine.tar" has been built with succes!
PAUSE 