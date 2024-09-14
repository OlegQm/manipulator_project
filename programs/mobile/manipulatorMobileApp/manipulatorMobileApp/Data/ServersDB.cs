using manipulatorMobileApp.Models;
using SQLite;
using System;
using System.Collections.Generic;
using System.Threading.Tasks;

namespace manipulatorMobileApp.Data
{
    public class ServersDB
    {
        readonly SQLiteAsyncConnection db;
        public ServersDB(string connectionString)
        {
            db = new SQLiteAsyncConnection(connectionString);
            db.CreateTableAsync<Server>().Wait();
        }

        public Task<List<Server>> GetServersAsync()
        {
            return db.Table<Server>().ToListAsync();
        }

        public async Task<bool> IsDatabaseNotEmpty()
        {
            try
            {
                int rowCount = await db.Table<Server>().CountAsync();
                return rowCount != 0;
            }
            catch (Exception)
            {
                return false;
            }
        }

        public async Task<Server> GetLastRecord()
        {
            try
            {
                var lastRecord = await db.Table<Server>()
                    .OrderByDescending(x => x.ID)
                    .FirstOrDefaultAsync();

                return lastRecord;
            }
            catch (Exception)
            {
                return null;
            }
        }

        public async Task<Server> FindRecordByName(string name)
        {
            Server server = await db.Table<Server>()
                                  .Where(i => i.name == name)
                                  .FirstOrDefaultAsync();
            return server;
        }

        public async Task<bool> GetServerIPAvailibiltyAsync(string IP)
        {
            var server = await db.Table<Server>()
                                  .Where(i => i.IPParam == IP)
                                  .FirstOrDefaultAsync();

            return server == null;
        }

        public Task<int> SaveServerAsync(Server server)
        {
            if (server.ID != 0)
            {
                return db.UpdateAsync(server);
            }
            return db.InsertAsync(server);
        }

        public Task<int> DeleteServerAsync(Server server)
        {
            return db.DeleteAsync(server);
        }

        public async Task DeleteAllRecords()
        {
            await db.DropTableAsync<Server>();
            await db.CreateTableAsync<Server>();
        }
    }
}
