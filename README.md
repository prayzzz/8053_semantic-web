# movie-soundtrack-events
Semantic Web Project

#### Dependencies
* TuneFind
    * OMDB
        * IMDB
    * LastFM
* Charts_de

#### Common arguments
* -w:    Loading data from web
* -r:    Convert to RDF (Turtle Syntax)

#### Tunefind
* gets all movies with their songs (confidence=high) from tunefind.com
* API is limited to 1 request per second

#### OMDB
* gets the IMDB id for each movie loaded from tunefind

#### IMDB
* gets the directors, cast and release infos for each movie

#### LastFM
* gets top 5 tags for each song which is loaded from tunefind.com

#### Charts_de
* grabs the german single chart
