using System;
using System.IO;
using Newtonsoft.Json;
using VDS.RDF;
using VDS.RDF.Parsing;
using VDS.RDF.Query;
using VDS.RDF.Storage;
using VDS.RDF.Update;
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
            var imdb = new Graph();
            imdb.LoadFromFile(@"E:\Projects\Studium\movie-soundtrack-events\parsing\src\data\full\imdb.ttl");
            imdb.BaseUri = new Uri("http://imn.htwk-leipzig.de/pbachman/ontologies/imdb");

            var store = new TripleStore();
            store.Add(imdb);

            var parser = new SparqlUpdateParser();
            var cmds = parser.ParseFromString(File.ReadAllText(@"Queries\05_Reduce_IMDB.rq"));
            var processor = new LeviathanUpdateProcessor(store);
            processor.ProcessCommandSet(cmds);

            Console.WriteLine(DateTime.Now + " Writing Graph...");
            var writer = new CompressingTurtleWriter(TurtleSyntax.W3C);
            writer.Save(imdb, "02_ReducedMovies.ttl");
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
            Console.WriteLine(DateTime.Now + " Connecting to Tunefind store...");
            var tuneFindStore = new StardogConnector(settings.ServerIp, TuneFindDbName, settings.Login, settings.Password);
            var tuneFindGraph = new Graph();
            tuneFindStore.LoadGraph(tuneFindGraph, string.Empty);

            Console.WriteLine(DateTime.Now + " Connecting to IMDB store...");
            var imdbStore = new StardogConnector(settings.ServerIp, ImdbDbName, settings.Login, settings.Password);
            var imdbGraph = new Graph();
            imdbStore.LoadGraph(imdbGraph, string.Empty);

            Console.WriteLine(DateTime.Now + " Merging graphs...");
            tuneFindGraph.Merge(imdbGraph);

            Console.WriteLine(DateTime.Now + " Constructing new graph...");
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

            Console.WriteLine(DateTime.Now + " Writing Graph...");
            var writer = new CompressingTurtleWriter(TurtleSyntax.W3C);
            writer.Save(movieGraph, "01_Movies.ttl");

            Console.WriteLine(DateTime.Now + " Uploading Graph...");
            var movieStore = new StardogConnector(settings.ServerIp, MoviesDbName, settings.Login, settings.Password);
            movieStore.DeleteGraph("http://imn.htwk-leipzig.de/pbachman/ontologies/movie-soundtracks#");
            movieStore.SaveGraph(movieGraph);
        }

        private static void ReferenceSongsAndArtists()
        {
            Console.WriteLine(DateTime.Now + " Connecting to Movie store...");
            var movieStore = new StardogConnector(settings.ServerIp, MoviesDbName, settings.Login, settings.Password);
            var movieGraph = new Graph();
            movieStore.LoadGraph(movieGraph, "http://imn.htwk-leipzig.de/pbachman/ontologies/movie-soundtracks#");

            Console.WriteLine(DateTime.Now + " Connecting to LastFM store...");
            var lastFmStore = new StardogConnector(settings.ServerIp, LastFmDbName, settings.Login, settings.Password);
            var lastFmGraph = new Graph();
            lastFmStore.LoadGraph(lastFmGraph, string.Empty);

            Console.WriteLine(DateTime.Now + " Merging Graphs...");
            movieGraph.Merge(lastFmGraph);

            Console.WriteLine(DateTime.Now + " Constructing new Graph...");
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

            Console.WriteLine(DateTime.Now + " Writing Graph...");
            var writer = new CompressingTurtleWriter(TurtleSyntax.W3C);
            writer.Save(movieSongArtistGraph, "02_Movies_Songs.ttl");

            Console.WriteLine(DateTime.Now + " Uploading Graph...");
           // movieStore.DeleteGraph("http://imn.htwk-leipzig.de/pbachman/ontologies/movie-soundtracks#");
           // movieStore.SaveGraph(movieSongArtistGraph);
        }
    }
}
