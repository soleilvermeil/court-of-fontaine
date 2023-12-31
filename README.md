# Court of Fontaine
A website that judges your artifacts.

## How to use

You can use the Docker to compile all the files into an image:
```
docker build -t court-of-fontaine .
```

You can then run the image:
```
docker run -p 8000:8000 court-of-fontaine
```

You can then access the website at http://localhost:8000 **altough the terminal may indicate another URL**.
