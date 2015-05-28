# movie-soundtrack-events
Semantic Web Project

## Dependencies
* TuneFind
    * OMDB
        * IMDB
    * LastFM
* Charts_de
* Charts_uk

## Common arguments
* -w:    Loading data from web
* -r:    Convert to RDF (Turtle Syntax)

## Tunefind
* fetches all movies with their songs (confidence=high) from tunefind.com
* API is limited to 1 request per second

## OMDB
* grabs the IMDB id for each movie

## IMDB
* grabs the directors, cast and release infos for each movie based on the id

## LastFM
* grabs top 5 tags for each song which is loaded from tunefind.com

## Charts_de
* grabs the charts for the given date-range

## Charts_uk
* grabs the charts for the given date-range