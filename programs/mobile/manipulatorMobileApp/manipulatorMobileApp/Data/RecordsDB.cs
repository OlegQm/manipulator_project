using manipulatorMobileApp.Models;
using SQLite;
using System.Collections.Generic;
using System.Threading.Tasks;

namespace manipulatorMobileApp.Data
{
    public class RecordsDB
    {
        readonly SQLiteAsyncConnection db;
        public RecordsDB(string connectionString)
        {
            db = new SQLiteAsyncConnection(connectionString);
            db.CreateTableAsync<Record>().Wait();
        }

        public Task<List<Record>> GetNotesAsync()
        {
            return db.Table<Record>().ToListAsync();
        }

        public Task<Record> GetNoteAsync(int id)
        {
            return db.Table<Record>()
                .Where(i => i.ID == id)
                .FirstOrDefaultAsync();
        }

        public Task<int> SaveNoteAsync(Record note)
        {
            if (note.ID != 0)
                return db.UpdateAsync(note);
            else
                return db.InsertAsync(note);
        }

        public Task<int> DeleteNoteAsync(Record note)
        {
            return db.DeleteAsync(note);
        }

        public async Task DeleteAllRecords()
        {
            await db.DropTableAsync<Record>();
            await db.CreateTableAsync<Record>();
        }
    }
}
