using manipulatorMobileApp.Models;
using System;
using System.Collections.ObjectModel;
using System.IO;
using System.Net.Sockets;
using System.Text;
using System.Threading.Tasks;
using Xamarin.Forms;
using Xamarin.Forms.Xaml;

namespace manipulatorMobileApp.Views
{
    [XamlCompilation(XamlCompilationOptions.Compile)]
    public partial class ScreenshotPage : ContentPage
    {
        private string IP;
        private string port;
        private const string OBJECT_OPEN = "<OBJ>";
        private const string OBJECT_CLOSE = "</OBJ>";
        private const string DISCONNECT = "<DISC_ME>";
        private const string GET_IMG = "<TSC>";

        public ScreenshotPage(string IP, string port)
        {
            InitializeComponent();
            this.IP = IP;
            this.port = port;
        }

        private void closeConversation(TcpClient client)
        {
            try
            {
                if (client != null && client.Connected)
                {
                    var stream = client.GetStream();
                    if (stream != null)
                    {
                        stream.Close();
                    }
                    client.Close();
                }
            }
            catch (Exception ex)
            {
                DependencyService.Get<IToast>().Show($"An error occurred when trying to close the conversation: {ex.Message}");
            }
        }

        private async Task<int> ReadWithTimeoutAsync(NetworkStream stream, byte[] buffer, int offset, int count, int timeout)
        {
            var readTask = stream.ReadAsync(buffer, offset, count);
            if (await Task.WhenAny(readTask, Task.Delay(timeout)) == readTask)
            {
                return await readTask;
            }
            else
            {
                throw new IOException("Timeout while reading data from server");
            }
        }

        private async Task<byte[]> getDataAsync(TcpClient client)
        {
            try
            {
                NetworkStream stream = client.GetStream();
                byte[] fileSizeBytes = new byte[4];
                int bytes = await ReadWithTimeoutAsync(stream, fileSizeBytes, 0, fileSizeBytes.Length, 5000);
                if (bytes != fileSizeBytes.Length)
                {
                    throw new IOException("Failed to read file size");
                }
                int dataLength = BitConverter.ToInt32(fileSizeBytes, 0);

                byte[] data = new byte[dataLength];
                int bytesLeft = dataLength;
                int buffersize = 1024;
                int bytesRead = 0;

                while (bytesLeft > 0)
                {
                    int curDataSize = Math.Min(buffersize, bytesLeft);
                    if (client.Available < curDataSize)
                    {
                        curDataSize = client.Available;
                    }
                    bytes = await ReadWithTimeoutAsync(stream, data, bytesRead, curDataSize, 5000);
                    if (bytes == 0)
                    {
                        throw new IOException("Connection closed by server before all data was received");
                    }
                    bytesRead += curDataSize;
                    bytesLeft -= curDataSize;
                }
                return data;
            }
            catch (Exception ex)
            {
                DependencyService.Get<IToast>().Show($"Error while receiving data: {ex.Message}");
                closeConversation(client);
                return null;
            }
        }

        private async Task<bool> RequestConnectToServer(string ip, string string_port)
        {
            TcpClient client = new TcpClient();
            try
            {
                int port = Convert.ToInt32(string_port);
                await Task.Run(() => client.ConnectAsync(ip, port));
                if (client.Connected)
                {
                    Connection.Instance.client = client;
                    return true;
                }
                else
                {
                    DependencyService.Get<IToast>().Show("Connection unsuccessful\n" +
                                                         "Please, try again");
                    screenshot.IsEnabled = true;
                    return false;
                }
            }
            catch (Exception ex)
            {
                DependencyService.Get<IToast>().Show(ex.Message);
                closeConversation(client);
                screenshot.IsEnabled = true;
                return false;
            }
        }

        private bool SendMsg(TcpClient client, string msg)
        {
            try
            {
                NetworkStream stream = client.GetStream();
                string msge = msg;
                byte[] message = Encoding.ASCII.GetBytes(msge);
                stream.Write(message, 0, message.Length);
                DependencyService.Get<IToast>().Show($"Request was successfully sent to:\n{IP}:{port}");
                return true;
            }
            catch (SocketException ex)
            {
                DependencyService.Get<IToast>().Show($"Socket error while sending request\nDetails: {ex.Message}");
                closeConversation(client);
                screenshot.IsEnabled = true;
                return false;
            }
            catch (IOException ex)
            {
                DependencyService.Get<IToast>().Show($"I/O error while sending request\nDetails: {ex.Message}");
                closeConversation(client);
                screenshot.IsEnabled = true;
                return false;
            }
            catch (ObjectDisposedException ex)
            {
                DependencyService.Get<IToast>().Show($"Error: Attempted to use a closed network stream\nDetails: {ex.Message}");
                closeConversation(client);
                screenshot.IsEnabled = true;
                return false;
            }
            catch (Exception ex)
            {
                DependencyService.Get<IToast>().Show($"Request sending error\nDetails: {ex.Message}");
                closeConversation(client);
                screenshot.IsEnabled = true;
                return false;
            }
        }

        public class ItemModel
        {
            public string Word { get; set; }
        }

        private void AddWordsToCollection(string text)
        {
            availableObjects.ItemsSource = null;
            if (string.IsNullOrEmpty(text))
            {
                return;
            }

            var availableObjectsData = new ObservableCollection<ItemModel>();
            string[] words = text.Split(new[] { '\n' }, StringSplitOptions.RemoveEmptyEntries);
            foreach (string word in words)
            {
                availableObjectsData.Add(new ItemModel { Word = word });
            }
            availableObjects.ItemsSource = availableObjectsData;
        }

        private async Task ReceiveTextAsync(TcpClient client)
        {
            using (NetworkStream stream = client.GetStream())
            {
                using (StreamReader reader = new StreamReader(stream))
                {
                    try
                    {
                        char[] buffer = new char[1024];
                        int bytesRead;
                        StringBuilder sb = new StringBuilder();
                        DateTime startTime = DateTime.Now;

                        while ((bytesRead = await reader.ReadAsync(buffer, 0, buffer.Length)) > 0)
                        {
                            sb.Append(buffer, 0, bytesRead);

                            if ((DateTime.Now - startTime).TotalMilliseconds > 5000)
                            {
                                throw new IOException("Timeout while reading data from server");
                            }
                        }
                        AddWordsToCollection(sb.ToString());
                    }
                    catch (Exception ex)
                    {
                        DependencyService.Get<IToast>().Show($"Data retrieval error: {ex.Message}");
                        closeConversation(client);
                    }
                }
            }
        }

        private async void Screenshot_Clicked(object sender, EventArgs e)
        {
            screenshot.IsEnabled = false;
            screenshot.Text = "RESHOOT";
            try
            {
                bool isConnected = await RequestConnectToServer(IP, port);
                if (!isConnected)
                {
                    screenshot.IsEnabled = true;
                    return;
                }

                var client = Connection.Instance.client;
                NetworkStream stream = client.GetStream();
                string s = GET_IMG;
                bool isSended = SendMsg(client, s);
                if (!isSended)
                {
                    screenshot.IsEnabled = true;
                    return;
                }
                var data = await getDataAsync(client);
                if (data != null)
                {
                    imageView.Source = ImageSource.FromStream(() => new MemoryStream(data));
                    _ = ReceiveTextAsync(client);
                }
            }
            catch (Exception ex)
            {
                DependencyService.Get<IToast>().Show($"Error: {ex.Message}");
                if (Connection.Instance.client != null && Connection.Instance.client.Connected)
                {
                    closeConversation(Connection.Instance.client);
                }
            }
            finally
            {
                screenshot.IsEnabled = true;
            }
        }

        private async void AvailableObjects_SelectionChanged(object sender, SelectionChangedEventArgs e)
        {
            if (e.CurrentSelection == null)
            {
                return;
            }

            try
            {
                bool isConnected = await RequestConnectToServer(IP, port);
                if (!isConnected)
                {
                    return;
                }
                TcpClient client = Connection.Instance.client;
                ItemModel selectedItem = e.CurrentSelection[0] as ItemModel;
                string selectedWord = selectedItem.Word.Trim();
                string msge = OBJECT_OPEN + selectedWord + OBJECT_CLOSE + DISCONNECT;
                bool sendObj = SendMsg(client, msge);
                if (sendObj)
                {
                    await client.GetStream().FlushAsync();
                    closeConversation(client);
                }
            }
            catch (SocketException ex)
            {
                DependencyService.Get<IToast>().Show("SocketException: " + ex.Message);
                closeConversation(Connection.Instance.client);
            }
            catch (IOException ex)
            {
                DependencyService.Get<IToast>().Show("IOException: " + ex.Message);
                closeConversation(Connection.Instance.client);
            }
            catch (Exception ex)
            {
                DependencyService.Get<IToast>().Show("Exception: " + ex.Message);
                closeConversation(Connection.Instance.client);
            }
        }
    }
}