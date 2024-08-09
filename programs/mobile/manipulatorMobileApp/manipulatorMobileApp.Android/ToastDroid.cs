using Android.Widget;
using manipulatorMobileApp.Droid;

[assembly: Xamarin.Forms.Dependency(typeof(ToastDroid))]
namespace manipulatorMobileApp.Droid
{
    public class ToastDroid : IToast
    {
        public void Show(string msg)
        {
            Android.Widget.Toast.MakeText(Android.App.Application.Context, msg, ToastLength.Short).Show();
        }
    }
}