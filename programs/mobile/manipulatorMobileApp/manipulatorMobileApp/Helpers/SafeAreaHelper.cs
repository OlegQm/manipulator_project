using Xamarin.Forms;
using Xamarin.Forms.PlatformConfiguration;
using Xamarin.Forms.PlatformConfiguration.iOSSpecific;

namespace manipulatorMobileApp.Helpers
{
    public static class SafeAreaHelper
    {
        public static void Apply(ContentPage page)
        {
            if (page == null)
            {
                return;
            }

            page.On<iOS>().SetUseSafeArea(true);
        }
    }
}
