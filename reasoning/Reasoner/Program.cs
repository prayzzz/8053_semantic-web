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
        private const string ReferenceSongsArtistsQuery = @"Queries\02_Reference_Songs_Artists.rq";
        private const string ReferenceChartSongsQuery = @"Queries\03_Reference_ChartSongs.rq";

        private const string TuneFindDbName = "tunefind";
        private const string ImdbDbName = "imdb";
        private const string MoviesDbName = "movies";
        private const string LastFmDbName = "lastfm";

        private static Settings settings;

        static void Main(string[] args)
        {
            settings = LoadSettings();

            MergeGraphs();
            ReferenceTunefindImdb();
            RemoveObsoletes();
        }

        private static void RemoveObsoletes()
        {
            Console.WriteLine(DateTime.Now + " Connecting to Movie store...");
            var movieStore = new StardogConnector(settings.ServerIp, MoviesDbName, settings.Login, settings.Password);

            Console.WriteLine(DateTime.Now + " Removing obsolete triples...");
            movieStore.Query(File.ReadAllText(@"Queries\05a_Remove_ObsoleteFilms.rq"));
            //movieStore.Query(File.ReadAllText(@"Queries\05b_Remove_ObsoleteTunefindSongs.rq"));
            //movieStore.Query(File.ReadAllText(@"Queries\05c_Remove_ObsoleteArtists.rq"));
        }

        private static void ReferenceTunefindImdb()
        {
            Console.WriteLine(DateTime.Now + " Connecting to Movie store...");
            var movieStore = new StardogConnector(settings.ServerIp, MoviesDbName, settings.Login, settings.Password);
            movieStore.DeleteGraph("http://imn.htwk-leipzig.de/pbachman/ontologies/references#");

            Console.WriteLine(DateTime.Now + " Constructing new graph...");
            movieStore.Query(File.ReadAllText(ReferenceMoviesQuery));
            movieStore.Query(File.ReadAllText(ReferenceSongsArtistsQuery));
        }

        private static void MergeGraphs()
        {
            Console.WriteLine(DateTime.Now + " Connecting to Movie store...");
            var movieStore = new StardogConnector(settings.ServerIp, MoviesDbName, settings.Login, settings.Password);
            movieStore.DeleteGraph("http://imn.htwk-leipzig.de/pbachman/ontologies/movie-soundtracks#");

            Console.WriteLine(DateTime.Now + " Connecting to Tunefind store...");
            var tuneFindStore = new StardogConnector(settings.ServerIp, TuneFindDbName, settings.Login, settings.Password);
            var tuneFindGraph = new Graph();
            tuneFindStore.LoadGraph(tuneFindGraph, string.Empty);

            Console.WriteLine(DateTime.Now + " Connecting to IMDB store...");
            var imdbStore = new StardogConnector(settings.ServerIp, ImdbDbName, settings.Login, settings.Password);
            var imdbGraph = new Graph();
            imdbStore.LoadGraph(imdbGraph, string.Empty);

            Console.WriteLine(DateTime.Now + " Connecting to LastFm store...");
            var lastFmStore = new StardogConnector(settings.ServerIp, LastFmDbName, settings.Login, settings.Password);
            var lastFmGraph = new Graph();
            lastFmStore.LoadGraph(lastFmGraph, string.Empty);

            Console.WriteLine(DateTime.Now + " Merging graphs...");
            var movieGraph = SetupMovieGraph();
            movieGraph.Merge(tuneFindGraph);
            movieGraph.Merge(imdbGraph);
            movieGraph.Merge(lastFmGraph);

            Console.WriteLine(DateTime.Now + " Uploading Graph...");
            movieStore.DeleteGraph("http://imn.htwk-leipzig.de/pbachman/ontologies/movie-soundtracks#");
            movieStore.SaveGraph(movieGraph);
        }

        private static Graph SetupMovieGraph()
        {
            var movieGraph = new Graph();
            movieGraph.BaseUri = new Uri("http://imn.htwk-leipzig.de/pbachman/ontologies/movie-soundtracks#");
            movieGraph.NamespaceMap.AddNamespace("owl", new Uri("http://www.w3.org/2002/07/owl#"));
            movieGraph.NamespaceMap.AddNamespace("dbpedia-owl", new Uri("http://dbpedia.org/property/"));
            movieGraph.NamespaceMap.AddNamespace("dbpprop", new Uri("http://dbpedia.org/ontology/"));
            movieGraph.NamespaceMap.AddNamespace("imdb", new Uri("http://imn.htwk-leipzig.de/pbachman/ontologies/imdb#"));
            movieGraph.NamespaceMap.AddNamespace("lastfm", new Uri("http://imn.htwk-leipzig.de/pbachman/ontologies/lastfm#"));
            movieGraph.NamespaceMap.AddNamespace(
                "tunefind",
                new Uri("http://imn.htwk-leipzig.de/pbachman/ontologies/tunefind#"));
            return movieGraph;
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
    }
}
