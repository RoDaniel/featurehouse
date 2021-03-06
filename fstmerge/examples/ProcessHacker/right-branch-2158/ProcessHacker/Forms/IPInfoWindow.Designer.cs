namespace ProcessHacker
{
    partial class IPInfoWindow
    {



        private System.ComponentModel.IContainer components = null;





        protected override void Dispose(bool disposing)
        {
            if (disposing && (components != null))
            {
                components.Dispose();
            }
            base.Dispose(disposing);
        }







        private void InitializeComponent()
        {
            System.ComponentModel.ComponentResourceManager resources = new System.ComponentModel.ComponentResourceManager(typeof(IPInfoWindow));
            this.buttonClose = new System.Windows.Forms.Button();
            this.listInfo = new System.Windows.Forms.ListView();
            this.labelInfo = new System.Windows.Forms.Label();
            this.labelStatus = new System.Windows.Forms.Label();
            this.SuspendLayout();



            this.buttonClose.Anchor = ((System.Windows.Forms.AnchorStyles)((System.Windows.Forms.AnchorStyles.Bottom | System.Windows.Forms.AnchorStyles.Right)));
            this.buttonClose.FlatStyle = System.Windows.Forms.FlatStyle.System;
            this.buttonClose.Location = new System.Drawing.Point(376, 329);
            this.buttonClose.Name = "buttonClose";
            this.buttonClose.Size = new System.Drawing.Size(75, 23);
            this.buttonClose.TabIndex = 1;
            this.buttonClose.Text = "Close";
            this.buttonClose.UseVisualStyleBackColor = true;
            this.buttonClose.Click += new System.EventHandler(this.buttonClose_Click);



            this.listInfo.Anchor = ((System.Windows.Forms.AnchorStyles)((((System.Windows.Forms.AnchorStyles.Top | System.Windows.Forms.AnchorStyles.Bottom)
                        | System.Windows.Forms.AnchorStyles.Left)
                        | System.Windows.Forms.AnchorStyles.Right)));
            this.listInfo.FullRowSelect = true;
            this.listInfo.Location = new System.Drawing.Point(12, 31);
            this.listInfo.Name = "listInfo";
            this.listInfo.ShowItemToolTips = true;
            this.listInfo.Size = new System.Drawing.Size(439, 292);
            this.listInfo.TabIndex = 2;
            this.listInfo.UseCompatibleStateImageBehavior = false;
            this.listInfo.View = System.Windows.Forms.View.Details;



            this.labelInfo.AutoSize = true;
            this.labelInfo.Location = new System.Drawing.Point(12, 9);
            this.labelInfo.Name = "labelInfo";
            this.labelInfo.Size = new System.Drawing.Size(35, 13);
            this.labelInfo.TabIndex = 3;
            this.labelInfo.Text = "label1";



            this.labelStatus.Anchor = ((System.Windows.Forms.AnchorStyles)((System.Windows.Forms.AnchorStyles.Bottom | System.Windows.Forms.AnchorStyles.Left)));
            this.labelStatus.AutoSize = true;
            this.labelStatus.Location = new System.Drawing.Point(12, 334);
            this.labelStatus.Name = "labelStatus";
            this.labelStatus.Size = new System.Drawing.Size(56, 13);
            this.labelStatus.TabIndex = 4;
            this.labelStatus.Text = "Working...";



            this.AutoScaleDimensions = new System.Drawing.SizeF(6F, 13F);
            this.AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font;
            this.ClientSize = new System.Drawing.Size(463, 364);
            this.Controls.Add(this.listInfo);
            this.Controls.Add(this.labelStatus);
            this.Controls.Add(this.labelInfo);
            this.Controls.Add(this.buttonClose);
            this.Icon = ((System.Drawing.Icon)(resources.GetObject("$this.Icon")));
            this.MaximizeBox = false;
            this.MinimizeBox = false;
            this.MinimumSize = new System.Drawing.Size(479, 402);
            this.Name = "IPInfoWindow";
            this.ShowIcon = false;
            this.StartPosition = System.Windows.Forms.FormStartPosition.CenterParent;
            this.Text = "IP information";
            this.Load += new System.EventHandler(this.IPInfoWindow_Load);
            this.ResumeLayout(false);
            this.PerformLayout();

        }



        private System.Windows.Forms.Button buttonClose;
        private System.Windows.Forms.ListView listInfo;
        private System.Windows.Forms.Label labelInfo;
        private System.Windows.Forms.Label labelStatus;
    }
}
