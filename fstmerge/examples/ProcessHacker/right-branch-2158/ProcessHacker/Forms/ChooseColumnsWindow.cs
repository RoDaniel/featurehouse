

using System;
using System.Windows.Forms;
using Aga.Controls.Tree;
using ProcessHacker.Common;

namespace ProcessHacker
{
    public partial class ChooseColumnsWindow : Form
    {
        private object _list;

        public ChooseColumnsWindow(ListView list)
            : this()
        {
            _list = list;


            foreach (ColumnHeader column in list.Columns)
            {
                listColumns.Items.Add(new ListViewItem()
                {
                    Text = column.Text,
                    Name = column.Index.ToString()
                });
            }
        }

        public ChooseColumnsWindow(TreeViewAdv tree)
            : this()
        {
            _list = tree;

            foreach (TreeColumn column in tree.Columns)
            {
                listColumns.Items.Add(new ListViewItem()
                {
                    Text = column.Header,
                    Name = column.Header,
                    Checked = column.IsVisible
                });
            }
        }

        private ChooseColumnsWindow()
        {
            InitializeComponent();
            this.AddEscapeToClose();
            this.SetTopMost();

            listColumns.SetDoubleBuffered(true);
            listColumns.SetTheme("explorer");
            columnColumn.Width = listColumns.Width - 21;
        }

        private void buttonCancel_Click(object sender, EventArgs e)
        {
            this.Close();
        }

        private void buttonOK_Click(object sender, EventArgs e)
        {
            if (_list is TreeViewAdv)
            {
                TreeViewAdv tree = _list as TreeViewAdv;

                foreach (TreeColumn column in tree.Columns)
                {
                    column.IsVisible = listColumns.Items[column.Header].Checked;
                }
            }
            else if (_list is ListView)
            {

            }

            this.Close();
        }
    }
}
