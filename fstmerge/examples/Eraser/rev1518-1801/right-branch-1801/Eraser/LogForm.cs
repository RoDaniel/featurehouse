using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Linq;
using System.Drawing;
using System.Text;
using System.Windows.Forms;
using System.Globalization;
using System.IO;
using Eraser.Manager;
using Eraser.Util;
namespace Eraser
{
 public partial class LogForm : Form, ILogTarget
 {
  public LogForm(Task task)
  {
   InitializeComponent();
   Theming.ApplyTheme(this);
   Text = string.Format(CultureInfo.InvariantCulture, "{0} - {1}", Text, task.UIText);
   foreach (LogSink sink in task.Log)
    filterSessionCombobox.Items.Add(sink.StartTime);
   if (filterSessionCombobox.Items.Count != 0)
    filterSessionCombobox.SelectedIndex = filterSessionCombobox.Items.Count - 1;
   filterFilterTypeCombobox.SelectedIndex = 0;
   filterSeverityCombobox.SelectedIndex = 0;
   Task = task;
   RefreshMessages();
   EnableButtons();
   if (Task.Log.Count > 0)
    Task.Log.Last().Chain(this);
   Task.TaskStarted += task_TaskStarted;
  }
  private void LogForm_FormClosed(object sender, FormClosedEventArgs e)
  {
   Task.TaskStarted -= task_TaskStarted;
   if (Task.Log.Count > 0)
    Task.Log.Last().Unchain(this);
  }
  private void filter_Changed(object sender, EventArgs e)
  {
   RefreshMessages();
  }
  private void task_TaskStarted(object sender, EventArgs e)
  {
   if (IsDisposed || !IsHandleCreated)
    return;
   if (InvokeRequired)
   {
    Invoke((EventHandler<EventArgs>)task_TaskStarted, sender, e);
    return;
   }
   filterSessionCombobox.Items.Add(Task.Log.Last().StartTime);
  }
  private void log_RetrieveVirtualItem(object sender, RetrieveVirtualItemEventArgs e)
  {
   LogEntry entry = EntryCache[e.ItemIndex];
   e.Item = new ListViewItem(entry.Timestamp.ToString("F", CultureInfo.CurrentCulture));
   e.Item.SubItems.Add(entry.Level.ToString());
   e.Item.SubItems.Add(entry.Message);
   switch (entry.Level)
   {
    case LogLevel.Fatal:
     e.Item.ForeColor = Color.Red;
     break;
    case LogLevel.Error:
     e.Item.ForeColor = Color.OrangeRed;
     break;
    case LogLevel.Warning:
     e.Item.ForeColor = Color.Orange;
     break;
   }
  }
  private void log_ItemSelectionChanged(object sender, ListViewItemSelectionChangedEventArgs e)
  {
   if (e.IsSelected)
   {
    SelectedEntries.Add(e.ItemIndex, EntryCache[e.ItemIndex]);
   }
   else
   {
    SelectedEntries.Remove(e.ItemIndex);
   }
  }
  private void log_VirtualItemsSelectionRangeChanged(object sender, ListViewVirtualItemsSelectionRangeChangedEventArgs e)
  {
   for (int i = e.StartIndex; i <= e.EndIndex; ++i)
   {
    if (e.IsSelected)
    {
     SelectedEntries.Add(i, EntryCache[i]);
    }
    else
    {
     SelectedEntries.Remove(i);
    }
   }
  }
  private void log_ItemActivate(object sender, EventArgs e)
  {
   if (SelectedEntries.Count < 1)
    return;
   LogEntry selectedEntry = SelectedEntries.Values[0];
   MessageBoxIcon icon = MessageBoxIcon.None;
   switch (selectedEntry.Level)
   {
    case LogLevel.Information:
     icon = MessageBoxIcon.Information;
     break;
    case LogLevel.Warning:
     icon = MessageBoxIcon.Warning;
     break;
    case LogLevel.Error:
    case LogLevel.Fatal:
     icon = MessageBoxIcon.Error;
     break;
   }
   MessageBox.Show(this, selectedEntry.Message,
    selectedEntry.Timestamp.ToString("F", CultureInfo.CurrentCulture),
    MessageBoxButtons.OK, icon, MessageBoxDefaultButton.Button1,
    Localisation.IsRightToLeft(this) ?
     MessageBoxOptions.RtlReading | MessageBoxOptions.RightAlign : 0);
  }
  private void logContextMenuStrip_Opening(object sender, CancelEventArgs e)
  {
   copySelectedEntriesToolStripMenuItem.Enabled = SelectedEntries.Count != 0;
  }
  private void copySelectedEntriesToolStripMenuItem_Click(object sender, EventArgs e)
  {
   if (SelectedEntries.Count == 0)
    return;
   StringBuilder csvText = new StringBuilder();
   StringBuilder rawText = new StringBuilder();
   DateTime sessionTime = (DateTime)filterSessionCombobox.SelectedItem;
   csvText.AppendLine(S._("Session: {0:F}", sessionTime));
   rawText.AppendLine(S._("Session: {0:F}", sessionTime));
   foreach (LogEntry entry in SelectedEntries.Values)
   {
    string timeStamp = entry.Timestamp.ToString("F", CultureInfo.CurrentCulture);
    string message = entry.Message;
    csvText.AppendFormat("\"{0}\",\"{1}\",\"{2}\"\n",
     timeStamp.Replace("\"", "\"\""), entry.Level.ToString(),
     message.Replace("\"", "\"\""));
    rawText.AppendFormat("{0}	{1}	{2}\n", timeStamp, entry.Level.ToString(),
     message);
   }
   if (csvText.Length > 0 || rawText.Length > 0)
   {
    DataObject tableText = new DataObject();
    tableText.SetText(rawText.ToString());
    byte[] bytes = Encoding.UTF8.GetBytes(csvText.ToString());
    MemoryStream tableStream = new MemoryStream(bytes);
    tableText.SetData(DataFormats.CommaSeparatedValue, tableStream);
    Clipboard.SetDataObject(tableText, true);
   }
  }
  private void clear_Click(object sender, EventArgs e)
  {
   Task.Log.Clear();
   filterSessionCombobox.Items.Clear();
   log.VirtualListSize = 0;
   SelectedEntries.Clear();
   EntryCache.Clear();
   EnableButtons();
  }
  private void close_Click(object sender, EventArgs e)
  {
   Close();
  }
  public void OnEventLogged(object sender, LogEventArgs e)
  {
   if (IsDisposed || !IsHandleCreated)
    return;
   if (InvokeRequired)
   {
    Invoke((EventHandler<LogEventArgs>)OnEventLogged, sender, e);
    return;
   }
   if (filterSessionCombobox.SelectedItem == null || !MeetsCriteria(e.LogEntry))
   {
    return;
   }
   EntryCache.Add(e.LogEntry);
   ++log.VirtualListSize;
   EnableButtons();
  }
  public void Chain(ILogTarget target)
  {
   throw new NotImplementedException();
  }
  public void Unchain(ILogTarget target)
  {
   throw new NotImplementedException();
  }
  private bool MeetsCriteria(LogEntry entry)
  {
   switch (filterFilterTypeCombobox.SelectedIndex)
   {
    case 0:
     if (entry.Level < (LogLevel)filterSeverityCombobox.SelectedIndex)
      return false;
     break;
    case 1:
     if (entry.Level != (LogLevel)filterSeverityCombobox.SelectedIndex)
      return false;
     break;
    case 2:
     if (entry.Level > (LogLevel)filterSeverityCombobox.SelectedIndex)
      return false;
     break;
   }
   return true;
  }
  private void RefreshMessages()
  {
   if (Task == null)
    return;
   if (filterSessionCombobox.SelectedIndex == -1)
    return;
   Application.UseWaitCursor = true;
   LogSink sink = Task.Log[filterSessionCombobox.SelectedIndex];
   EntryCache.Clear();
   SelectedEntries.Clear();
   EntryCache.AddRange(sink.Where(MeetsCriteria));
   log.VirtualListSize = EntryCache.Count;
   log.Refresh();
   EnableButtons();
   Application.UseWaitCursor = false;
  }
  private void EnableButtons()
  {
   clear.Enabled = Task.Log.Count > 0;
  }
  private Task Task;
  private List<LogEntry> EntryCache = new List<LogEntry>();
  private SortedList<int, LogEntry> SelectedEntries = new SortedList<int, LogEntry>();
 }
}
