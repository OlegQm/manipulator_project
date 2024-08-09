using Foundation;
using manipulatorMobileApp.iOS;
using UIKit;

[assembly: Xamarin.Forms.Dependency(typeof(ToastIOS))]
namespace manipulatorMobileApp.iOS
{
    public class ToastIOS : IToast
    {
        const double DELAY = 2.0;
        NSTimer alertDelay;
        UIAlertController alert;

        public void Show(string msg)
        {
            ShowAlert(msg, DELAY);
        }

        void ShowAlert(string message, double seconds)
        {
            alertDelay = NSTimer.CreateScheduledTimer(seconds, (obj) =>
            {
                dismissMessage();
            });
            alert = UIAlertController.Create(null, message, UIAlertControllerStyle.Alert);
            UIApplication.SharedApplication.KeyWindow.RootViewController.PresentViewController(alert, true, null);
        }

        void dismissMessage()
        {
            if (alert != null)
            {
                alert.DismissViewController(true, null);
            }
            if (alertDelay != null)
            {
                alertDelay.Dispose();
            }
        }
    }
}