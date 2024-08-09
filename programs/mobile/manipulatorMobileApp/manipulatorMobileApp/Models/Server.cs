using SQLite;
using System;

namespace manipulatorMobileApp.Models
{
    public class Server
    {
        [PrimaryKey, AutoIncrement]
        public int ID { get; set; }
        public string IPParam { get; set; }
        public string portParam { get; set; }
        public string name { get; set; }
        public DateTime Date { get; set; }
    }
}
