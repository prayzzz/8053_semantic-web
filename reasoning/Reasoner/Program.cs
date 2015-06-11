using System;
using System.Diagnostics;
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

        private const string ReferenceFilmsQuery = @"Queries\01_Reference_Films.rq";
        private const string ReferenceSongsQuery = @"Queries\02a_Reference_Songs.rq";
        private const string ReferenceArtistsQuery = @"Queries\02b_Reference_Artists.rq";
        private const string ReferenceChartsDe1Query = @"Queries\03_Reference_ChartDe.rq";

        private const string TuneFindDbName = "tunefind";
        private const string ImdbDbName = "imdb";
        private const string MoviesDbName = "movies";
        private const string LastFmDbName = "lastfm";
        private const string ChartsDeDbName = "charts_de";

        private static Settings settings;

        static void Main(string[] args)
        {
            settings = LoadSettings();

            var stopwatch = new Stopwatch();
            stopwatch.Start();

            MergeGraphs();
            AddReferenceGraph();
            //RemoveObsoleteTriples();

            stopwatch.Stop();

            Log(stopwatch.ElapsedMilliseconds / 1000.0 + "s");
            Log(stopwatch.ElapsedMilliseconds / 60000.0 + "min");
            Log("Finished...");
            Console.Read();
        }

        private static void MergeGraphs()
        {
            Log("Executing MergeGraphs()");
            Log("Connecting to Movie store...");
            var movieStore = new StardogConnector(settings.ServerIp, MoviesDbName, settings.Login, settings.Password);
            movieStore.Timeout = int.MaxValue;

            #region Tunefind
            Log("Connecting to Tunefind store...");
            var tuneFindStore = new StardogConnector(settings.ServerIp, TuneFindDbName, settings.Login, settings.Password);
            var tuneFindGraph = new Graph();
            tuneFindGraph.BaseUri = new Uri("http://imn.htwk-leipzig.de/pbachman/ontologies/tunefind#");
            tuneFindStore.LoadGraph(tuneFindGraph, string.Empty);

            Log("Uploading Graph...");
            movieStore.DeleteGraph("http://imn.htwk-leipzig.de/pbachman/ontologies/tunefind#");
            movieStore.SaveGraph(tuneFindGraph);
            #endregion

            #region IMDB
            Log("Connecting to IMDB store...");
            var imdbStore = new StardogConnector(settings.ServerIp, ImdbDbName, settings.Login, settings.Password);
            var imdbGraph = new Graph();
            imdbGraph.BaseUri = new Uri("http://imn.htwk-leipzig.de/pbachman/ontologies/imdb#");
            imdbStore.LoadGraph(imdbGraph, string.Empty);

            Log("Uploading Graph...");
            movieStore.DeleteGraph("http://imn.htwk-leipzig.de/pbachman/ontologies/imdb#");
            movieStore.SaveGraph(imdbGraph);
            #endregion

            #region LastFM
            Log("Connecting to LastFm store...");
            var lastFmStore = new StardogConnector(settings.ServerIp, LastFmDbName, settings.Login, settings.Password);
            var lastFmGraph = new Graph();
            lastFmGraph.BaseUri = new Uri("http://imn.htwk-leipzig.de/pbachman/ontologies/lastfm#");
            lastFmStore.LoadGraph(lastFmGraph, string.Empty);

            Log("Uploading Graph...");
            movieStore.DeleteGraph("http://imn.htwk-leipzig.de/pbachman/ontologies/lastfm#");
            movieStore.SaveGraph(lastFmGraph);
            #endregion

            #region Charts_de
            Log("Connecting to Chart_De store...");
            var chartsDeStore = new StardogConnector(settings.ServerIp, ChartsDeDbName, settings.Login, settings.Password);
            var chartsDeGraph = new Graph();
            chartsDeGraph.BaseUri = new Uri("http://imn.htwk-leipzig.de/pbachman/ontologies/charts_de#");
            chartsDeStore.LoadGraph(chartsDeGraph, string.Empty);

            Log("Uploading Graph...");
            movieStore.DeleteGraph("http://imn.htwk-leipzig.de/pbachman/ontologies/charts_de#");
            movieStore.SaveGraph(chartsDeGraph);
            #endregion

            Log("Merging Graphs...");
            var movieGraph = SetupMovieGraph();
            movieGraph.Merge(tuneFindGraph);
            movieGraph.Merge(imdbGraph);
            movieGraph.Merge(lastFmGraph);
            movieGraph.Merge(chartsDeGraph);

            Log("Writing Graph...");
            var writer = new CompressingTurtleWriter(TurtleSyntax.W3C);
            writer.Save(movieGraph, @"01_Movies.ttl");
        }

        private static void AddReferenceGraph()
        {
            Log("Executing AddReferenceGraph()");
            Log("Connecting to Movie store...");
            var movieStore = new StardogConnector(settings.ServerIp, MoviesDbName, settings.Login, settings.Password);
            movieStore.Timeout = int.MaxValue;
            movieStore.DeleteGraph("http://imn.htwk-leipzig.de/pbachman/ontologies/references#");

            Log("Inserting film references...");
            movieStore.Query(File.ReadAllText(ReferenceFilmsQuery));

            Log("Inserting Song references...");
            movieStore.Query(File.ReadAllText(ReferenceSongsQuery));

            Log("Inserting Artists references...");
            movieStore.Query(File.ReadAllText(ReferenceArtistsQuery));

            Log("Inserting Chart song references...");
            movieStore.Query(File.ReadAllText(ReferenceChartsDe1Query));
        }

        private static void RemoveObsoleteTriples()
        {
            Log("Connecting to Movie store...");
            var movieStore = new StardogConnector(settings.ServerIp, MoviesDbName, settings.Login, settings.Password);
            movieStore.Timeout = int.MaxValue;

            Log("Removing obsolete films...");
            movieStore.Query(File.ReadAllText(@"Queries\05a_Remove_ObsoleteFilms.rq"));

            Log("Removing obsolete TuneFind songs...");
            movieStore.Query(File.ReadAllText(@"Queries\05b_Remove_ObsoleteTunefindSongs.rq"));

            Log("Removing obsolete LastFm songs...");
            movieStore.Query(File.ReadAllText(@"Queries\05c_Remove_ObsoleteLastFmSongs.rq"));

            Log("Removing obsolete artists...");
            movieStore.Query(File.ReadAllText(@"Queries\05d_Remove_ObsoleteArtists.rq"));
        }

        private static Graph SetupMovieGraph()
        {
            var movieGraph = new Graph();
            movieGraph.BaseUri = new Uri("http://imn.htwk-leipzig.de/pbachman/ontologies/movie-soundtracks#");
            movieGraph.NamespaceMap.AddNamespace("owl", new Uri("http://www.w3.org/2002/07/owl#"));
            movieGraph.NamespaceMap.AddNamespace("dbpedia-owl", new Uri("http://dbpedia.org/property/"));
            movieGraph.NamespaceMap.AddNamespace("dbpprop", new Uri("http://dbpedia.org/ontology/"));
            movieGraph.NamespaceMap.AddNamespace("imdb", new Uri("http://imn.htwk-leipzig.de/pbachman/ontologies/imdb#"));
            movieGraph.NamespaceMap.AddNamespace("charts_de", new Uri("http://imn.htwk-leipzig.de/pbachman/ontologies/charts_de#"));
            movieGraph.NamespaceMap.AddNamespace("lastfm", new Uri("http://imn.htwk-leipzig.de/pbachman/ontologies/lastfm#"));
            movieGraph.NamespaceMap.AddNamespace("tunefind", new Uri("http://imn.htwk-leipzig.de/pbachman/ontologies/tunefind#"));
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

        private static void Log(string str)
        {
            Console.WriteLine(DateTime.Now.TimeOfDay + " " + str);
        }
    }
}
