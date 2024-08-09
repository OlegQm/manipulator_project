using Foundation;
using System.IO;
using Xamarin.Forms;
using manipulatorMobileApp.iOS;

[assembly: Dependency(typeof(FileHelperiOS))]
namespace manipulatorMobileApp.iOS
{
    public class FileHelperiOS : IFileHelper
    {
        public string GetFilePath(string fileName)
        {
            return NSBundle.MainBundle.PathForResource(Path.GetFileNameWithoutExtension(fileName), Path.GetExtension(fileName));
        }
    }
}