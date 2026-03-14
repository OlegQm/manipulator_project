using Android.Content;
using Android.Text.Method;
using Android.Views;
using manipulatorMobileApp.Controls;
using manipulatorMobileApp.Droid.Renderers;
using Xamarin.Forms;
using Xamarin.Forms.Platform.Android;

[assembly: ExportRenderer(typeof(ChatInputEditor), typeof(ChatInputEditorRenderer))]

namespace manipulatorMobileApp.Droid.Renderers
{
    public class ChatInputEditorRenderer : EditorRenderer
    {
        public ChatInputEditorRenderer(Context context) : base(context)
        {
        }

        protected override void OnElementChanged(ElementChangedEventArgs<Editor> e)
        {
            base.OnElementChanged(e);
            if (Control != null)
            {
                Control.SetHorizontallyScrolling(false);
                Control.VerticalScrollBarEnabled = true;
                Control.ScrollbarFadingEnabled = true;
                Control.OverScrollMode = OverScrollMode.IfContentScrolls;
                Control.MovementMethod = new ScrollingMovementMethod();
            }
        }
    }
}
