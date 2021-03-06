namespace ProcessHacker.Components
{
    partial class FileNameBox
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
            this.components = new System.ComponentModel.Container();
            this.textFileName = new System.Windows.Forms.TextBox();
            this.buttonProperties = new System.Windows.Forms.Button();
            this.buttonExplore = new System.Windows.Forms.Button();
            this.toolTip = new System.Windows.Forms.ToolTip(this.components);
            this.SuspendLayout();



            this.textFileName.Anchor = ((System.Windows.Forms.AnchorStyles)((((System.Windows.Forms.AnchorStyles.Top | System.Windows.Forms.AnchorStyles.Bottom)
                        | System.Windows.Forms.AnchorStyles.Left)
                        | System.Windows.Forms.AnchorStyles.Right)));
            this.textFileName.Location = new System.Drawing.Point(0, 2);
            this.textFileName.Name = "textFileName";
            this.textFileName.Size = new System.Drawing.Size(277, 20);
            this.textFileName.TabIndex = 0;
            this.textFileName.Leave += new System.EventHandler(this.textFileName_Leave);



            this.buttonProperties.Anchor = ((System.Windows.Forms.AnchorStyles)(((System.Windows.Forms.AnchorStyles.Top | System.Windows.Forms.AnchorStyles.Bottom)
                        | System.Windows.Forms.AnchorStyles.Right)));
            this.buttonProperties.Image = global::ProcessHacker.Properties.Resources.application_form_magnify;
            this.buttonProperties.Location = new System.Drawing.Point(279, 0);
            this.buttonProperties.Name = "buttonProperties";
            this.buttonProperties.Size = new System.Drawing.Size(24, 24);
            this.buttonProperties.TabIndex = 1;
            this.toolTip.SetToolTip(this.buttonProperties, "Properties");
            this.buttonProperties.UseVisualStyleBackColor = true;
            this.buttonProperties.Click += new System.EventHandler(this.buttonProperties_Click);



            this.buttonExplore.Anchor = ((System.Windows.Forms.AnchorStyles)(((System.Windows.Forms.AnchorStyles.Top | System.Windows.Forms.AnchorStyles.Bottom)
                        | System.Windows.Forms.AnchorStyles.Right)));
            this.buttonExplore.Image = global::ProcessHacker.Properties.Resources.folder_explore;
            this.buttonExplore.Location = new System.Drawing.Point(304, 0);
            this.buttonExplore.Name = "buttonExplore";
            this.buttonExplore.Size = new System.Drawing.Size(24, 24);
            this.buttonExplore.TabIndex = 2;
            this.toolTip.SetToolTip(this.buttonExplore, "Open File Location");
            this.buttonExplore.UseVisualStyleBackColor = true;
            this.buttonExplore.Click += new System.EventHandler(this.buttonExplore_Click);



            this.AutoScaleDimensions = new System.Drawing.SizeF(6F, 13F);
            this.AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font;
            this.Controls.Add(this.buttonExplore);
            this.Controls.Add(this.buttonProperties);
            this.Controls.Add(this.textFileName);
            this.Name = "FileNameBox";
            this.Size = new System.Drawing.Size(328, 24);
            this.ResumeLayout(false);
            this.PerformLayout();

        }



        private System.Windows.Forms.TextBox textFileName;
        private System.Windows.Forms.Button buttonProperties;
        private System.Windows.Forms.Button buttonExplore;
        private System.Windows.Forms.ToolTip toolTip;
    }
}
