using System;
using System.IO;
using System.Net;
using System.Net.Sockets;
using System.Text;

namespace manipulatorServerPart
{
    class Program
    {
        private static TcpClient client;
        private static TcpListener listener;

        private const int SERVER_PORT = 1234;
        private static string ipString;
        private const string OBJECT_OPEN = "<OBJ>";
        private const string OBJECT_CLOSE = "</OBJ>";
        private const string DISCONNECT = "<DISC_ME>";
        private const string GET_IMG = "<TSC>";
        private const string LONGEST_WORD = "baseball glove";
        private const string IMG_PATH = "currentObjectsScreenshot.jpg";

        static bool isFileLocked(string filePath)
        {
            try
            {
                using (FileStream fs = File.Open(filePath, FileMode.Open,
                                       FileAccess.ReadWrite, FileShare.None))
                {
                    return false;
                }
            }
            catch (IOException)
            {
                return true;
            }
        }

        static string ExtractWordBetweenTags(string input, string startTag, string endTag)
        {
            int startIndex = input.IndexOf(startTag) + startTag.Length;
            int endIndex = input.IndexOf(endTag, startIndex);
            if (startIndex >= 0 && endIndex >= 0)
                return input.Substring(startIndex, endIndex - startIndex);
            return null;
        }

        private static bool SavingToFile(string path, string msg)
        {
            try
            {
                File.WriteAllText(path, msg);
                Console.WriteLine(msg);
                return true;
            }
            catch (Exception ex)
            {
                Console.WriteLine($"File error: {ex.Message}");
                return false;
            }
        }

        private static void SendData(byte[] data, NetworkStream stream)
        {
            int bufferSize = 1024;
            byte[] dataLength = BitConverter.GetBytes(data.Length);
            stream.Write(dataLength, 0, 4);
            int bytesSent = 0;
            int bytesLeft = data.Length;
            while (bytesLeft > 0)
            {
                int curDataSize = Math.Min(bufferSize, bytesLeft);
                stream.Write(data, bytesSent, curDataSize);
                bytesSent += curDataSize;
                bytesLeft -= curDataSize;
            }
        }

        private static void GetLocalIPAddress()
        {
            IPAddress[] localIp = Dns.GetHostAddresses(Dns.GetHostName());
            foreach (IPAddress address in localIp)
            {
                if (address.AddressFamily == AddressFamily.InterNetwork)
                {
                    ipString = address.ToString();
                }
            }
        }

        private static void ClientWaiting()
        {
            GetLocalIPAddress();
            IPEndPoint ep = new IPEndPoint(IPAddress.Parse(ipString), SERVER_PORT);
            listener.Start();
            client = listener.AcceptTcpClient();
            Console.WriteLine($"\n{DateTime.Now.ToString("HH:mm:ss")} " +
                                                         "- Connected to client!");
        }

        private static void Disconnect(string error = null)
        {
            try
            {
                if (client != null && client.Connected)
                {
                    NetworkStream stream = client.GetStream();
                    if (stream != null)
                    {
                        stream.Close();
                        stream.Dispose();
                    }

                    client.Close();
                    client.Dispose();
                }

                if (error == null)
                {
                    Console.WriteLine($"{DateTime.Now:HH:mm:ss} - " +
                        $"Disconnected from client!\n");
                }
                else
                {
                    Console.WriteLine($"{DateTime.Now:HH:mm:ss} - " +
                        $"Disconnected from client due to error: {error}\n");
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error during disconnect: {ex.Message}");
            }
        }

        private static void TryToConnect()
        {
            GetLocalIPAddress();
            IPEndPoint ep = new IPEndPoint(IPAddress.Parse(ipString), SERVER_PORT);
            listener = new TcpListener(ep);
            listener.Start();
            Console.WriteLine(@"  
                             ===================================================  
                             Started listening requests at: {0}:{1}  
                             ===================================================",
                             ep.Address, ep.Port);
            client = listener.AcceptTcpClient();
            Console.WriteLine($"\n{DateTime.Now.ToString("HH:mm:ss")} " +
                                                         "- Connected to client!");
        }

        private static void Main(string[] args)
        {
            TryToConnect();
            string maxObj = OBJECT_OPEN + LONGEST_WORD + OBJECT_CLOSE + DISCONNECT;
            while (client.Connected)
            {
                try
                {
                    int bytesize = Encoding.ASCII.GetBytes(maxObj).Length;
                    byte[] buffer = new byte[bytesize];
                    string x = client.GetStream().Read(buffer, 0, bytesize).ToString();
                    string data = ASCIIEncoding.ASCII.GetString(buffer);

                    if (data.ToUpper().Contains(OBJECT_OPEN))
                    {
                        string word = ExtractWordBetweenTags(data, OBJECT_OPEN, OBJECT_CLOSE);
                        SavingToFile("words_file.txt", word);
                    }

                    if (data.ToUpper().Contains(GET_IMG))
                    {
                        SavingToFile("screenshotRequest.txt", GET_IMG);
                        while (!File.Exists(IMG_PATH) || isFileLocked(IMG_PATH)) { }
                        using (FileStream imgStream = File.OpenRead(IMG_PATH))
                        {
                            using (MemoryStream memStream = new MemoryStream())
                            {
                                imgStream.CopyTo(memStream);
                                SendData(memStream.ToArray(), client.GetStream());
                            }
                            Console.WriteLine("Image sent to the client.");
                        }

                        using (NetworkStream stream = client.GetStream())
                        {
                            string textToSend = File.ReadAllText("currentObjects.txt");
                            byte[] textBytes = System.Text.Encoding.UTF8.GetBytes(textToSend);
                            stream.Write(textBytes, 0, textBytes.Length);
                            Console.WriteLine("Text sent to the client.");
                        }

                        //File.Delete(IMG_PATH);
                        Disconnect();
                        ClientWaiting();
                    }
                    if (data.ToUpper().Contains(DISCONNECT))
                    {
                        Disconnect();
                        ClientWaiting();
                    }
                }
                catch (Exception except)
                {
                    Disconnect(except.Message.ToString());
                }
            }
            Console.WriteLine("Disconnected from client");
        }
    }
}