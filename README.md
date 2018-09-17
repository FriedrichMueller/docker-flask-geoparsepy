# docker-flask-geoparsepy

## Short description
* Geoparse demo-application with flask, geoparsepy, nltk, leaflet provided by docker 
* Inspired by [flask-docker](https://github.com/chhantyal/flask-docker)


## Local installation

### Requirements:

* Docker
* Docker-compose

### Steps

* `git clone https://gitlab.gwdg.de/FriedrichMueller/docker-flask-geoparsepy.git`
* `cd Geoparsepy`
* `docker-compose up -d`

Point your browser to [http://0.0.0.0:5000](0.0.0.0:5000)

### Info and Extension
* Current database is filled with dataset for Australia and New Zealand.
* You can add more database tar dumps from the  [geoparsepy documentation](https://pythonhosted.org/geoparsepy/readme.html) like
    * au_nz_places.tar [1 Mb]
    * north_america_places.tar [18 Mb]
    * europe_places.tar [137 Mb]
    * global_cities10.tar [4131 Mb]

    within the /app/data folder.

You can add the dump according the existing dump in [app.py](https://github.com/FriedrichMueller/docker-flask-geoparsepy/blob/master/app/app.py#L17-L25)

* you can configure the geoparsepy settings in /app/app.py like used language etc.

### Possible further tasks
* Build API for geoprocessing
* Implement solution for place name disambiguation
* Parallelize place name view with map view
* Highlight place entities

## Further information
* [Geoparsepy documentation](https://pythonhosted.org/geoparsepy/readme.html)
*  [Flask documentation](http://flask.pocoo.org/docs/1.0/)
