using System;
using Gtk;
public class ELabel : Label {
 string text = "";
 const string ellipsis = "...";
 const string en_char = "n";
 int ellipsis_width, en_width, tmp;
 int old_width;
 Pango.Layout layout;
 bool refreshed = false;
 public ELabel (string text) : base ("")
 {
  int width, height;
  GetSizeRequest (out width, out height);
  SetSizeRequest (0, height);
  SizeAllocated += new SizeAllocatedHandler (OnSizeAllocated);
  Text = text;
 }
 new public string Text
 {
  get {
   return text;
  } set {
   text = value;
   Reload ();
   Refresh ();
  }
 }
 void OnSizeAllocated (object o, SizeAllocatedArgs args)
 {
  if (refreshed) {
   refreshed = false;
   return;
  }
  if (Allocation.Width != old_width)
   Refresh ();
  old_width = Allocation.Width;
  refreshed = true;
 }
 void Reload ()
 {
  layout = Layout.Copy ();
  layout.SetText (ellipsis);
  layout.GetPixelSize (out ellipsis_width, out tmp);
  layout.SetText (en_char);
  layout.GetPixelSize (out en_width, out tmp);
 }
 void Refresh ()
 {
  string ellipsized = Ellipsize (layout, text, Allocation.Width, ellipsis_width, en_width, 0);
  if (base.Text != ellipsized)
   base.Text = ellipsized;
 }
 public static string Ellipsize (Pango.Layout layout, string newtext, int bound, int ellipsis_width, int en_width, int hAdjust)
 {
  int width, tmp;
  layout.SetText (newtext);
  layout.GetPixelSize (out width, out tmp);
  if (bound <= ellipsis_width)
   return ellipsis;
  string ellipsized = "";
  int i = 0;
  if(hAdjust !=0)
  {
   i+=hAdjust;
   while(i<newtext.Length)
   {
    ellipsized = ellipsized+newtext[i];
    layout.SetText(ellipsized);
    layout.GetPixelSize(out width, out tmp);
    if(width > bound - ellipsis_width)
     break;
    i++;
   }
   return ellipsized;
  }
  if (width < bound)
   return newtext;
  i = (bound - ellipsis_width) / (en_width);
  if (i >= newtext.Length)
   i = 0;
  ellipsized = newtext.Substring (hAdjust, i);
  while (true)
  {
   ellipsized = ellipsized + newtext[i];
   layout.SetText (ellipsized);
   layout.GetPixelSize (out width, out tmp);
   if (i == newtext.Length - 1) {
    ellipsized = "";
    i = 0;
    continue;
   }
   if (width > bound - ellipsis_width)
    break;
   i++;
  }
  ellipsized = ellipsized.Remove (ellipsized.Length - 1, 1);
  ellipsized += ellipsis;
  return ellipsized;
 }
}
