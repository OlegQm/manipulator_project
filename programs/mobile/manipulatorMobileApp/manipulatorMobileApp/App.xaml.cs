using manipulatorMobileApp.Data;
using manipulatorMobileApp.Models;
using System;
using System.IO;
using System.Net.Sockets;
using System.Text;
using Xamarin.Forms;

namespace manipulatorMobileApp
{
    public partial class App : Application
    {
        static RecordsDB notesDB;
        static ServersDB serversDB;

        public static RecordsDB RecordsDB
        {
            get
            {
                if (notesDB == null)
                {
                    notesDB = new RecordsDB(
                        Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData),
                        "notesDatabase.db3"));
                }
                return notesDB;
            }
        }

        public static ServersDB ServersDB
        {
            get
            {
                if (serversDB == null)
                {
                    serversDB = new ServersDB(
                        Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData),
                        "serversDatabase.db3"));
                }
                return serversDB;
            }
        }

        private bool SendMsg(TcpClient client, string msge)
        {
            try
            {
                NetworkStream stream = client.GetStream();
                string msg = msge;
                byte[] message = Encoding.ASCII.GetBytes(msg);
                stream.Write(message, 0, message.Length);
                return true;
            }
            catch (Exception ex)
            {
                DependencyService.Get<IToast>().Show($"Request sending error\nDetails: {ex.Message}");
                return false;
            }
        }

        public App()
        {
            InitializeComponent();
            Application.Current.UserAppTheme = OSAppTheme.Dark;
            MainPage = new NavigationPage(new MainPage());
        }

        protected override void OnStart()
        {
        }

        protected override void OnSleep()
        {
            TcpClient client = Connection.Instance.client;
            if (client != null && client.Connected)
            {
                SendMsg(client, "<DISC_ME>");
                client.GetStream().Close();
                client.Close();
            }
        }

        protected override void OnResume()
        {
        }
    }
}
