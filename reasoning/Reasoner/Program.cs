using System;
using System.IO;
using Newtonsoft.Json;
using VDS.RDF;
using VDS.RDF.Parsing;
using VDS.RDF.Storage;
using VDS.RDF.Writing;

namespace Reasoner
{
    class Program
    {
        private const string SettingsFile = "settings.json";
        
        private const string ReferenceMoviesQuery = @"Queries\01_Reference_Movies.rq";
        private const string ReferenceSongsQuery = @"Queries\02_Reference_Songs_Artists.rq";
        private const string ReferenceChartSongsQuery = @"Queries\03_Reference_ChartSongs.rq";
        
        private const string TuneFindDbName = "tunefind";
        private const string ImdbDbName = "imdb";
        private const string MoviesDbName = "movies";
        private const string LastFmDbName = "lastfm";

        private static Settings settings;

        static void Main(string[] args)
        {
            settings = LoadSettings();

            //ReferenceMovies();
            //ReferenceSongsAndArtists();
            ReferenceChartSongs();
        }

        private static void ReferenceChartSongs()
        {
            var charts = new Graph();
            charts.LoadFromFile(@"E:\Projects\Studium\movie-soundtrack-events\data\full\imdb.ttl");

            //var tunefind = new Graph();
            //tunefind.LoadFromFile(@"E:\Projects\Studium\movie-soundtrack-events\data\full\tunefind.ttl");

            //charts.Merge(tunefind);

            var queryResult = charts.ExecuteQuery(File.ReadAllText(@"Queries\04_Get_ReleaseDates.rq"));
            if (!(queryResult is IGraph))
            {
                throw new InvalidDataException("No Construct-Query");
            }
        }

        private static Settings LoadSettings()
        {
            if (!File.Exists(SettingsFile))
            {
                throw new FileNotFoundException(SettingsFile);
            }

            using (var fileStream = File.Open(SettingsFile, FileMode.Open))
            using (var streamReader = new StreamReader(fileStream))
            using (var jsonTextReader = new JsonTextReader(streamReader))
            {
                return JsonSerializer.Create().Deserialize<Settings>(jsonTextReader);
            }
        }

        private static void ReferenceMovies()
        {
            var tuneFindStore = new StardogConnector(settings.ServerIp, TuneFindDbName, settings.Login, settings.Password);
            var tuneFindGraph = new Graph();
            tuneFindStore.LoadGraph(tuneFindGraph, string.Empty);

            var imdbStore = new StardogConnector(settings.ServerIp, ImdbDbName, settings.Login, settings.Password);
            var imdbGraph = new Graph();
            imdbStore.LoadGraph(imdbGraph, string.Empty);

            tuneFindGraph.Merge(imdbGraph);

            var queryResult = tuneFindGraph.ExecuteQuery(File.ReadAllText(ReferenceMoviesQuery));
            if (!(queryResult is IGraph))
            {
                throw new InvalidDataException("No Construct-Query");
            }

            var movieGraph = queryResult as IGraph;
            movieGraph.BaseUri = new Uri("http://imn.htwk-leipzig.de/pbachman/ontologies/movie-soundtracks#");
            movieGraph.NamespaceMap.AddNamespace("imdb", new Uri("http://imn.htwk-leipzig.de/pbachman/ontologies/imdb#"));
            movieGraph.NamespaceMap.AddNamespace("tunefind", new Uri("http://imn.htwk-leipzig.de/pbachman/ontologies/tunefind#"));
            movieGraph.Merge(tuneFindGraph);

            var writer = new CompressingTurtleWriter(TurtleSyntax.W3C);
            writer.Save(movieGraph, "01_Movies.ttl");

            var movieStore = new StardogConnector(settings.ServerIp, MoviesDbName, settings.Login, settings.Password);
            movieStore.DeleteGraph("http://imn.htwk-leipzig.de/pbachman/ontologies/movie-soundtracks#");
            movieStore.SaveGraph(movieGraph);
        }

        private static void ReferenceSongsAndArtists()
        {
            var movieStore = new StardogConnector(settings.ServerIp, MoviesDbName, settings.Login, settings.Password);
            var movieGraph = new Graph();
            movieStore.LoadGraph(movieGraph, "http://imn.htwk-leipzig.de/pbachman/ontologies/movie-soundtracks#");

            var lastFmStore = new StardogConnector(settings.ServerIp, LastFmDbName, settings.Login, settings.Password);
            var lastFmGraph = new Graph();
            lastFmStore.LoadGraph(lastFmGraph, string.Empty);

            movieGraph.Merge(lastFmGraph);

            var queryResult = movieGraph.ExecuteQuery(File.ReadAllText(ReferenceSongsQuery));
            if (!(queryResult is IGraph))
            {
                throw new InvalidDataException("No Construct-Query");
            }

            var movieSongArtistGraph = queryResult as IGraph;
            movieSongArtistGraph.BaseUri = new Uri("http://imn.htwk-leipzig.de/pbachman/ontologies/movie-soundtracks#");
            movieSongArtistGraph.NamespaceMap.AddNamespace("imdb", new Uri("http://imn.htwk-leipzig.de/pbachman/ontologies/imdb#"));
            movieSongArtistGraph.NamespaceMap.AddNamespace("lastfm", new Uri("http://imn.htwk-leipzig.de/pbachman/ontologies/lastfm#"));
            movieSongArtistGraph.NamespaceMap.AddNamespace("tunefind", new Uri("http://imn.htwk-leipzig.de/pbachman/ontologies/tunefind#"));
            movieSongArtistGraph.Merge(movieGraph);

            var writer = new CompressingTurtleWriter(TurtleSyntax.W3C);
            writer.Save(movieSongArtistGraph, "02_Movies_Songs.ttl");

            movieStore.DeleteGraph("http://imn.htwk-leipzig.de/pbachman/ontologies/movie-soundtracks#");
            movieStore.SaveGraph(movieSongArtistGraph);
        }
    }
}
