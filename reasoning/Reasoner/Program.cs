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
        
        private const string referenceMoviesQuery = @"Queries\01_Reference_Movies.rq";
        
        private const string TuneFindDbName = "tunefind";
        private const string ImdbDbName = "imdb";
        private const string MoviesDbName = "movies";

        private static Settings settings;

        static void Main(string[] args)
        {
            settings = LoadSettings();

            ReferenceMovies();
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

            var queryResult = tuneFindGraph.ExecuteQuery(File.ReadAllText(referenceMoviesQuery));
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
    }
}
