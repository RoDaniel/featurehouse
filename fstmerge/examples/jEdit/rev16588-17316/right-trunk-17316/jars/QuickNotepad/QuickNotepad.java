


import java.awt.BorderLayout;
import java.awt.Dimension;
import java.awt.Font;
import java.io.BufferedReader;
import java.io.File;
import java.io.FileNotFoundException;
import java.io.FileReader;
import java.io.FileWriter;
import java.io.IOException;

import javax.swing.JFileChooser;
import javax.swing.JPanel;
import javax.swing.JScrollPane;

import org.gjt.sp.jedit.EBComponent;
import org.gjt.sp.jedit.EBMessage;
import org.gjt.sp.jedit.EditBus;
import org.gjt.sp.jedit.GUIUtilities;
import org.gjt.sp.jedit.View;
import org.gjt.sp.jedit.jEdit;
import org.gjt.sp.jedit.gui.DefaultFocusComponent;
import org.gjt.sp.jedit.gui.DockableWindowManager;
import org.gjt.sp.jedit.msg.PropertiesChanged;
import org.gjt.sp.util.Log;
import org.gjt.sp.util.StandardUtilities;




public class QuickNotepad extends JPanel
    implements EBComponent, QuickNotepadActions, DefaultFocusComponent {

    
	private static final long serialVersionUID = 6412255692894321789L;

	private String filename;

	private String defaultFilename;

	private View view;

	private boolean floating;

	private QuickNotepadTextArea textArea;

	private QuickNotepadToolPanel toolPanel;
    

    
	
	public QuickNotepad(View view, String position) {
		super(new BorderLayout());
		this.view = view;
		this.floating = position.equals(DockableWindowManager.FLOATING);

		if (jEdit.getSettingsDirectory() != null) {
			this.filename = jEdit.getProperty(QuickNotepadPlugin.OPTION_PREFIX
					+ "filepath");
			if (this.filename == null || this.filename.length() == 0) {
				this.filename = new String(jEdit.getSettingsDirectory()
						+ File.separator + "qn.txt");
				jEdit.setProperty(
						QuickNotepadPlugin.OPTION_PREFIX + "filepath",
						this.filename);
			}
			this.defaultFilename = this.filename;
		}

		this.toolPanel = new QuickNotepadToolPanel(this);
		add(BorderLayout.NORTH, this.toolPanel);

		if (floating)
			this.setPreferredSize(new Dimension(500, 250));

		textArea = new QuickNotepadTextArea();
		textArea.setFont(QuickNotepadOptionPane.makeFont());

		JScrollPane pane = new JScrollPane(textArea);
		add(BorderLayout.CENTER, pane);

		readFile();
	}
    

    
    
    
	public void focusOnDefaultComponent() {
		textArea.requestFocus();
	}
    

    
	public String getFilename() {
		return filename;
	}
    

	
	
    
	public void handleMessage(EBMessage message) {
		if (message instanceof PropertiesChanged) {
			propertiesChanged();
		}
	}
    
    
    
	private void propertiesChanged() {
		String propertyFilename = jEdit
				.getProperty(QuickNotepadPlugin.OPTION_PREFIX + "filepath");
		if (!StandardUtilities.objectsEqual(defaultFilename, propertyFilename)) {
			saveFile();
			toolPanel.propertiesChanged();
			defaultFilename = propertyFilename;
			filename = defaultFilename;
			readFile();
		}
		Font newFont = QuickNotepadOptionPane.makeFont();
		if (!newFont.equals(textArea.getFont())) {
			textArea.setFont(newFont);
		}
	}
    

	
	

    
	public void addNotify() {
		super.addNotify();
		EditBus.addToBus(this);
	}
     
     
    
	public void removeNotify() {
		saveFile();
		super.removeNotify();
		EditBus.removeFromBus(this);
	}
    
    
	

    
	public void saveFile() {
		if (filename == null || filename.length() == 0)
			return;
		try {
			FileWriter out = new FileWriter(filename);
			out.write(textArea.getText());
			out.close();
		} catch (IOException ioe) {
			Log.log(Log.ERROR, QuickNotepad.class,
					"Could not write notepad text to " + filename);
		}
	}
    
    
    
	public void chooseFile() {
		String[] paths = GUIUtilities.showVFSFileDialog(view, null,
				JFileChooser.OPEN_DIALOG, false);
		if (paths != null && !paths[0].equals(filename)) {
			saveFile();
			filename = paths[0];
			toolPanel.propertiesChanged();
			readFile();
		}
	}
    

    
	public void copyToBuffer() {
		jEdit.newFile(view);
		view.getEditPane().getTextArea().setText(textArea.getText());
	}
    
    
	
	private void readFile() {
		if (filename == null || filename.length() == 0)
			return;

		BufferedReader bf = null;
		try {
			bf = new BufferedReader(new FileReader(filename));
			StringBuffer sb = new StringBuffer(2048);
			String str;
			while ((str = bf.readLine()) != null) {
				sb.append(str).append('\n');
			}
			bf.close();
			textArea.setText(sb.toString());
		} catch (FileNotFoundException fnf) {
			Log.log(Log.ERROR, QuickNotepad.class, "notepad file " + filename
					+ " does not exist");
		} catch (IOException ioe) {
			Log.log(Log.ERROR, QuickNotepad.class,
					"could not read notepad file " + filename);
		}
	}
    
    
}

