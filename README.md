![UpTime](https://raw.githubusercontent.com/nlo-portfolio/nlo-portfolio.github.io/master/style/images/programs/uptime.png "UpTime")

## Description ##

UpTime is a utility for monitoring website uptime over an indefinite duration. It offers percentage uptime and visual alerts if the site becomes unreachable.<br>

## Dependencies ##

Ubuntu<br>
Python v3<br>
\* All required components are included in the provided Docker image.

## Usage ##

Fill out the configuration file.<br>
<br>
Ubuntu:

```
python3 uptime.py<br>
python3 -m unittest --verbose
```

Docker:

```
docker-compose build
docker-compose run <uptime | test>
```
