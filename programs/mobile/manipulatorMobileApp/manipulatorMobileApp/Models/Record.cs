using SQLite;
using System;

namespace manipulatorMobileApp.Models
{
    public class Record
    {
        [PrimaryKey, AutoIncrement]
        public int ID { get; set; }
        public string Title { get; set; }
        public string Text { get; set; }
        public DateTime Date { get; set; }
    }
}
