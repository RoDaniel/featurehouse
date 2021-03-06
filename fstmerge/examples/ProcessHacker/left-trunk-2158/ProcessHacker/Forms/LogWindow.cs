

using System;
using System.Collections.Generic;
using System.Drawing;
using System.Text;
using System.Windows.Forms;
using ProcessHacker.Common;
using ProcessHacker.UI;

namespace ProcessHacker
{
    public partial class LogWindow : Form
    {
        public LogWindow()
        {
            InitializeComponent();
            this.AddEscapeToClose();
            this.SetTopMost();

            listLog.SetDoubleBuffered(true);
            listLog.SetTheme("explorer");
            listLog.ContextMenu = listLog.GetCopyMenu(listLog_RetrieveVirtualItem);
            listLog.AddShortcuts(listLog_RetrieveVirtualItem);

            this.UpdateLog();

            if (listLog.SelectedIndices.Count == 0 && listLog.VirtualListSize > 0)
                listLog.EnsureVisible(listLog.VirtualListSize - 1);

            Program.HackerWindow.LogUpdated += new HackerWindow.LogUpdatedEventHandler(HackerWindow_LogUpdated);

            this.Size = Properties.Settings.Default.LogWindowSize;
            this.Location = Utils.FitRectangle(new Rectangle(
                Properties.Settings.Default.LogWindowLocation, this.Size), this).Location;
            checkAutoscroll.Checked = Properties.Settings.Default.LogWindowAutoScroll;
        }

        private void HackerWindow_LogUpdated(KeyValuePair<DateTime, string> value)
        {
            this.UpdateLog();
        }

        private void UpdateLog()
        {


            try
            {
                listLog.VirtualListSize = Program.HackerWindow.Log.Count;
            }
            catch
            {

            }
        }

        private void LogWindow_FormClosing(object sender, FormClosingEventArgs e)
        {
            if (this.WindowState == FormWindowState.Normal)
            {
                Properties.Settings.Default.LogWindowLocation = this.Location;
                Properties.Settings.Default.LogWindowSize = this.Size;
            }

            Properties.Settings.Default.LogWindowAutoScroll = checkAutoscroll.Checked;

            Program.HackerWindow.LogUpdated -= new HackerWindow.LogUpdatedEventHandler(HackerWindow_LogUpdated);
        }

        private void buttonClose_Click(object sender, EventArgs e)
        {
            this.Close();
        }

        private void listLog_RetrieveVirtualItem(object sender, RetrieveVirtualItemEventArgs e)
        {
            e.Item = new ListViewItem(new string[]
            {
                Program.HackerWindow.Log[e.ItemIndex].Key.ToString(),
                Program.HackerWindow.Log[e.ItemIndex].Value
            });
        }

        private void timerScroll_Tick(object sender, EventArgs e)
        {
            if (checkAutoscroll.Checked)
            {
                if (!listLog.Focused)
                    listLog.SelectedIndices.Clear();

                if (listLog.SelectedIndices.Count == 0 && listLog.VirtualListSize > 0)
                    listLog.EnsureVisible(listLog.VirtualListSize - 1);
            }
        }

        private void buttonCopy_Click(object sender, EventArgs e)
        {
            if (listLog.SelectedIndices.Count == 0)
                for (int i = 0; i < listLog.VirtualListSize; i++)
                    listLog.SelectedIndices.Add(i);

            GenericViewMenu.ListViewCopy(listLog, -1, listLog_RetrieveVirtualItem);
        }

        private void buttonSave_Click(object sender, EventArgs e)
        {
            SaveFileDialog sfd = new SaveFileDialog();

            sfd.FileName = "Process Hacker Log.txt";
            sfd.Filter = "Text Files (*.txt)|*.txt|All Files (*.*)|*.*";

            if (sfd.ShowDialog() == DialogResult.OK)
            {
                StringBuilder sb = new StringBuilder();

                foreach (var value in Program.HackerWindow.Log)
                {
                    sb.AppendLine(value.Key.ToString() + ": " + value.Value);
                }

                try
                {
                    System.IO.File.WriteAllText(sfd.FileName, sb.ToString());
                }
                catch (Exception ex)
                {
                    PhUtils.ShowException("Unable to save the log", ex);
                }
            }
        }

        private void buttonClear_Click(object sender, EventArgs e)
        {
            Program.HackerWindow.ClearLog();
        }

        private void listLog_DoubleClick(object sender, EventArgs e)
        {
            InformationBox info = new InformationBox(Program.HackerWindow.Log[listLog.SelectedIndices[0]].Value);

            info.ShowDialog();
        }
    }
}
