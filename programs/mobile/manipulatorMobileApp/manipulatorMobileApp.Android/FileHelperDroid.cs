using Android.Content.Res;
using System.IO;
using Xamarin.Forms;
using manipulatorMobileApp.Droid;

[assembly: Dependency(typeof(FileHelperDroid))]
namespace manipulatorMobileApp.Droid
{
    public class FileHelperDroid : IFileHelper
    {
        public string GetFilePath(string fileName)
        {
            AssetManager assetManager = Android.App.Application.Context.Assets;
            string filePath = Path.Combine(System.Environment.GetFolderPath(System.Environment.SpecialFolder.Personal), fileName);

            using (Stream inputStream = assetManager.Open(fileName))
            using (Stream outputStream = new FileStream(filePath, FileMode.Create))
            {
                inputStream.CopyTo(outputStream);
            }

            return filePath;
        }
    }
}