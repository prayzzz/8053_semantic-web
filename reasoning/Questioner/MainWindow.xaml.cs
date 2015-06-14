using System;
using System.Collections.Generic;
using System.Collections.ObjectModel;
using System.IO;
using System.Threading.Tasks;
using System.Windows;
using System.Windows.Controls;
using System.Windows.Data;
using System.Windows.Input;
using Newtonsoft.Json;
using VDS.RDF;
using VDS.RDF.Query;
using VDS.RDF.Storage;

namespace Questioner
{
    /// <summary>
    /// Interaktionslogik für MainWindow.xaml
    /// </summary>
    public partial class MainWindow
    {
        private const string QuestionsDir = @"./Questions/";

        private const string SettingsFile = "settings.json";

        private StardogConnector connector;

        private int columnCount;

        private readonly ObservableCollection<string> files;

        public MainWindow()
        {
            this.InitializeComponent();
            this.ExecuteButton.IsEnabled = false;

            var settings = LoadSettings();
            this.IpTextBox.Text = settings.ServerIp;
            this.DbTextBox.Text = "movies";
            this.LoginTextBox.Text = settings.Login;
            this.PasswordTextbox.Password = settings.Password;

            this.files = new ObservableCollection<string>();
            this.AvailableQuestionsListBox.ItemsSource = this.files;
            this.LoadFiles();
        }

        private void LoadFiles()
        {
            if (!Directory.Exists(QuestionsDir))
            {
                return;
            }

            this.files.Clear();
            foreach (var f in Directory.EnumerateFiles(QuestionsDir))
            {
                this.files.Add(Path.GetFileNameWithoutExtension(f));
            }
        }

        private void ConnectButton_Click(object sender, RoutedEventArgs e)
        {
            var ip = this.IpTextBox.Text;
            var db = this.DbTextBox.Text;
            var login = this.LoginTextBox.Text;
            var password = this.PasswordTextbox.Password;

            if (string.IsNullOrEmpty(ip) || string.IsNullOrEmpty(db) || string.IsNullOrEmpty(login) ||
                string.IsNullOrEmpty(password))
            {
                MessageBox.Show(this, "Missing informations!", "Error", MessageBoxButton.OK, MessageBoxImage.Error);
                return;
            }

            try
            {
                this.connector = new StardogConnector(ip, db, login, password);
                this.ExecuteButton.IsEnabled = true;
            }
            catch (Exception ex)
            {
                MessageBox.Show(this, ex.Message, "Error", MessageBoxButton.OK, MessageBoxImage.Error);
            }
        }

        private async void ExecuteButton_Click(object sender, RoutedEventArgs e)
        {
            var q = this.QuestionTextBox.Text;

            if (string.IsNullOrEmpty(q))
            {
                MessageBox.Show(this, "Missing informations!", "Error", MessageBoxButton.OK, MessageBoxImage.Error);
                return;
            }

            try
            {
                await Task.Run(() => this.ExecuteQuery(q));
            }
            catch (Exception ex)
            {
                MessageBox.Show(this, ex.Message, "Error", MessageBoxButton.OK, MessageBoxImage.Error);
            }
        }

        private void ExecuteQuery(string q)
        {
            var queryResult = this.connector.Query(q) as SparqlResultSet;

            if (queryResult == null)
            {
                throw new InvalidDataException("Query not supported");
            }

            Application.Current.Dispatcher.Invoke(() => this.AddColumns(queryResult));

            var date = new List<string[]>();
            foreach (var resultLine in queryResult.Results)
            {
                var ar = new string[this.columnCount];
                date.Add(ar);

                for (var a = 0; a < resultLine.Count; a++)
                {
                    var results = resultLine[a];
                    var d = string.Empty;

                    if (results.NodeType == NodeType.Literal)
                    {
                        d = ((LiteralNode) results).Value;
                    }

                    if (results.NodeType == NodeType.Uri)
                    {
                        d = ((UriNode) results).Uri.AbsoluteUri;
                    }

                    if (results.NodeType == NodeType.Blank)
                    {
                        d = ((BlankNode) results).ToString();
                    }

                    if (results.NodeType == NodeType.Variable)
                    {
                        d = ((VariableNode) results).ToString();
                    }

                    if (results.NodeType == NodeType.GraphLiteral)
                    {
                        d = ((GraphLiteralNode) results).ToString();
                    }

                    ar[a] = d;
                }
            }

            Application.Current.Dispatcher.Invoke(() => { this.AnswerListView.ItemsSource = date; });
        }

        private void AddColumns(SparqlResultSet queryResult)
        {
            this.columnCount = 0;

            var grid = new GridView();
            this.AnswerListView.ItemsSource = null;
            this.AnswerListView.View = grid;

            foreach (var v in queryResult.Variables)
            {
                grid.Columns.Add(new GridViewColumn
                {
                    Header = v,
                    DisplayMemberBinding = new Binding(String.Format("[{0}]", this.columnCount))
                });

                this.columnCount++;
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

        private void AvailableQuestionsListBox_OnMouseDoubleClick(object sender, MouseButtonEventArgs e)
        {
            try
            {
                var f = this.AvailableQuestionsListBox.SelectedItem as string;
                this.QuestionTextBox.Text = File.ReadAllText(QuestionsDir + f + ".rq");
            }
            catch (Exception ex)
            {
            }
        }
    }
}
