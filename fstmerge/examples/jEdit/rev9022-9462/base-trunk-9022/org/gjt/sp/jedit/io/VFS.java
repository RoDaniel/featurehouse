

package org.gjt.sp.jedit.io;


import java.awt.Color;
import java.awt.Component;
import java.io.*;
import java.util.*;

import java.util.regex.Pattern;
import java.util.regex.PatternSyntaxException;

import org.gjt.sp.jedit.msg.PropertiesChanged;
import org.gjt.sp.jedit.*;
import org.gjt.sp.jedit.bufferio.BufferLoadRequest;
import org.gjt.sp.jedit.bufferio.BufferSaveRequest;
import org.gjt.sp.jedit.bufferio.BufferInsertRequest;
import org.gjt.sp.jedit.bufferio.BufferIORequest;
import org.gjt.sp.util.Log;
import org.gjt.sp.util.ProgressObserver;
import org.gjt.sp.util.IOUtilities;
import org.gjt.sp.util.StandardUtilities;



public abstract class VFS
{
	

	
	public static final int READ_CAP = 1 << 0;

	
	public static final int WRITE_CAP = 1 << 1;

	
	public static final int BROWSE_CAP = 1 << 2;

	
	public static final int DELETE_CAP = 1 << 3;

	
	public static final int RENAME_CAP = 1 << 4;

	
	public static final int MKDIR_CAP = 1 << 5;

	
	public static final int LOW_LATENCY_CAP = 1 << 6;

	
	public static final int CASE_INSENSITIVE_CAP = 1 << 7;

	

	
	
	public static final String EA_TYPE = "type";

	
	public static final String EA_STATUS = "status";

	
	public static final String EA_SIZE = "size";

	
	public static final String EA_MODIFIED = "modified";
	

	public static int IOBUFSIZE = 32678;

	
	
	public VFS(String name)
	{
		this(name,0);
	} 

	
	
	public VFS(String name, int caps)
	{
		this.name = name;
		this.caps = caps;
		
		this.extAttrs = new String[] { EA_SIZE, EA_TYPE };
	} 

	
	
	public VFS(String name, int caps, String[] extAttrs)
	{
		this.name = name;
		this.caps = caps;
		this.extAttrs = extAttrs;
	} 

	
	
	public String getName()
	{
		return name;
	} 

	
	
	public int getCapabilities()
	{
		return caps;
	} 

	
	
	public boolean isMarkersFileSupported()
	{
		return true;
	} 

	
	
	public String[] getExtendedAttributes()
	{
		return extAttrs;
	} 

	
	
	@Deprecated
	public String showBrowseDialog(Object[] session, Component comp)
	{
		return null;
	} 

	
	
	public String getFileName(String path)
	{
		if(path.equals("/"))
			return path;

		while(path.endsWith("/") || path.endsWith(File.separator))
			path = path.substring(0,path.length() - 1);

		int index = Math.max(path.lastIndexOf('/'),
			path.lastIndexOf(File.separatorChar));
		if(index == -1)
			index = path.indexOf(':');

		
		if(index == -1 || index == path.length() - 1)
			return path;

		return path.substring(index + 1);
	} 

	
	
	public String getParentOfPath(String path)
	{
		
		
		int lastIndex = path.length() - 1;
		while(lastIndex > 0
			&& (path.charAt(lastIndex) == File.separatorChar
			|| path.charAt(lastIndex) == '/'))
		{
			lastIndex--;
		}

		int count = Math.max(0,lastIndex);
		int index = path.lastIndexOf(File.separatorChar,count);
		if(index == -1)
			index = path.lastIndexOf('/',count);
		if(index == -1)
		{
			
			
			index = path.lastIndexOf(':');
		}

		return path.substring(0,index + 1);
	} 

	
	
	public String constructPath(String parent, String path)
	{
		return parent + path;
	} 

	
	
	public char getFileSeparator()
	{
		return '/';
	} 

	
	
	public String getTwoStageSaveName(String path)
	{
		return MiscUtilities.constructPath(getParentOfPath(path),
			'#' + getFileName(path) + "#save#");
	} 

	
	
	public void reloadDirectory(String path) {} 

	
	
	public Object createVFSSession(String path, Component comp)
	{
		return new Object();
	} 

	
	
	public boolean load(View view, Buffer buffer, String path)
	{
		if((getCapabilities() & READ_CAP) == 0)
		{
			VFSManager.error(view,path,"vfs.not-supported.load",new String[] { name });
			return false;
		}

		Object session = createVFSSession(path,view);
		if(session == null)
			return false;

		if((getCapabilities() & WRITE_CAP) == 0)
			buffer.setReadOnly(true);

		BufferIORequest request = new BufferLoadRequest(
			view,buffer,session,this,path);
		if(buffer.isTemporary())
			
			request.run();
		else
			VFSManager.runInWorkThread(request);

		return true;
	} 

	
	
	public boolean save(View view, Buffer buffer, String path)
	{
		if((getCapabilities() & WRITE_CAP) == 0)
		{
			VFSManager.error(view,path,"vfs.not-supported.save",new String[] { name });
			return false;
		}

		Object session = createVFSSession(path,view);
		if(session == null)
			return false;

		
		if(!path.equals(buffer.getPath()))
			buffer.unsetProperty(Buffer.BACKED_UP);

		VFSManager.runInWorkThread(new BufferSaveRequest(
			view,buffer,session,this,path));
		return true;
	} 

	
	
	public static boolean copy(ProgressObserver progress, VFS sourceVFS, Object sourceSession,String sourcePath,
		VFS targetVFS, Object targetSession,String targetPath, Component comp, boolean canStop)
	throws IOException
	{
		if (progress != null)
			progress.setStatus("Initializing");

		InputStream in = null;
		OutputStream out = null;
		try
		{
			if (progress != null)
			{
				VFSFile sourceVFSFile = sourceVFS._getFile(sourceSession, sourcePath, comp);
				if (sourceVFSFile == null)
					throw new FileNotFoundException(sourcePath);

				progress.setMaximum(sourceVFSFile.getLength());
			}
			in = new BufferedInputStream(sourceVFS._createInputStream(sourceSession, sourcePath, false, comp));
			out = new BufferedOutputStream(targetVFS._createOutputStream(targetSession, targetPath, comp));
			boolean copyResult = IOUtilities.copyStream(IOBUFSIZE, progress, in, out, canStop);
			VFSManager.sendVFSUpdate(targetVFS, targetPath, true);
			return copyResult;
		}
		finally
		{
			IOUtilities.closeQuietly(in);
			IOUtilities.closeQuietly(out);
		}
	} 

	
	
	public static boolean copy(ProgressObserver progress, String sourcePath,String targetPath, Component comp, boolean canStop)
	throws IOException
	{
		VFS sourceVFS = VFSManager.getVFSForPath(sourcePath);
		Object sourceSession = sourceVFS.createVFSSession(sourcePath, comp);
		if (sourceSession == null)
		{
			Log.log(Log.WARNING, VFS.class, "Unable to get a valid session from " + sourceVFS + " for path " + sourcePath);
			return false;
		}
		VFS targetVFS = VFSManager.getVFSForPath(targetPath);
		Object targetSession = targetVFS.createVFSSession(targetPath, comp);
		if (targetSession == null)
		{
			Log.log(Log.WARNING, VFS.class, "Unable to get a valid session from " + targetVFS + " for path " + targetPath);
			return false;
		}
		return copy(progress, sourceVFS, sourceSession, sourcePath, targetVFS, targetSession, targetPath, comp,canStop);
	} 

	
	
	public boolean insert(View view, Buffer buffer, String path)
	{
		if((getCapabilities() & READ_CAP) == 0)
		{
			VFSManager.error(view,path,"vfs.not-supported.load",new String[] { name });
			return false;
		}

		Object session = createVFSSession(path,view);
		if(session == null)
			return false;

		VFSManager.runInWorkThread(new BufferInsertRequest(
			view,buffer,session,this,path));
		return true;
	} 

	

	
	
	public String _canonPath(Object session, String path, Component comp)
		throws IOException
	{
		return path;
	} 

	
	
	public String[] _listDirectory(Object session, String directory,
		String glob, boolean recursive, Component comp )
		throws IOException
	{
		String[] retval = null;
		retval = _listDirectory(session, directory, glob, recursive, comp, true, false);
		return retval;
	}


	
	
	public String[] _listDirectory(Object session, String directory,
		String glob, boolean recursive, Component comp,
		boolean skipBinary, boolean skipHidden)
		throws IOException
	{
		VFSFileFilter filter = new GlobVFSFileFilter(glob);
		return _listDirectory(session, directory, filter,
				      recursive, comp, skipBinary,
				      skipHidden);
	} 

	
	
	public String[] _listDirectory(Object session, String directory,
		VFSFileFilter filter, boolean recursive, Component comp,
		boolean skipBinary, boolean skipHidden)
		throws IOException
	{
		Log.log(Log.DEBUG,this,"Listing " + directory);
		List files = new ArrayList(100);

		listFiles(session,new ArrayList(),files,directory,filter,
			recursive, comp, skipBinary, skipHidden);

		String[] retVal = (String[])files.toArray(new String[files.size()]);

		Arrays.sort(retVal,new MiscUtilities.StringICaseCompare());

		return retVal;
	} 

	
	
	public VFSFile[] _listFiles(Object session, String directory,
		Component comp)
		throws IOException
	{
		return _listDirectory(session,directory,comp);
	} 

	
	
	public DirectoryEntry[] _listDirectory(Object session, String directory,
		Component comp)
		throws IOException
	{
		VFSManager.error(comp,directory,"vfs.not-supported.list",new String[] { name });
		return null;
	} 

	
	
	public VFSFile _getFile(Object session, String path,
		Component comp)
		throws IOException
	{
		return _getDirectoryEntry(session,path,comp);
	} 

	
	
	public DirectoryEntry _getDirectoryEntry(Object session, String path,
		Component comp)
		throws IOException
	{
		return null;
	} 

	
	
	public static class DirectoryEntry extends VFSFile
	{
		
		
		public DirectoryEntry()
		{
		} 

		
		public DirectoryEntry(String name, String path, String deletePath,
			int type, long length, boolean hidden)
		{
			this.name = name;
			this.path = path;
			this.deletePath = deletePath;
			this.symlinkPath = path;
			this.type = type;
			this.length = length;
			this.hidden = hidden;
			if(path != null)
			{
				
				VFS vfs = VFSManager.getVFSForPath(path);
				canRead = ((vfs.getCapabilities() & READ_CAP) != 0);
				canWrite = ((vfs.getCapabilities() & WRITE_CAP) != 0);
			}
		} 
	} 

	
	
	public boolean _delete(Object session, String path, Component comp)
		throws IOException
	{
		return false;
	} 

	
	
	public boolean _rename(Object session, String from, String to,
		Component comp) throws IOException
	{
		return false;
	} 

	
	
	public boolean _mkdir(Object session, String directory, Component comp)
		throws IOException
	{
		return false;
	} 

	
	
	public void _backup(Object session, String path, Component comp)
		throws IOException
	{
	} 

	
	
	public InputStream _createInputStream(Object session,
		String path, boolean ignoreErrors, Component comp)
		throws IOException
	{
		VFSManager.error(comp,path,"vfs.not-supported.load",new String[] { name });
		return null;
	} 

	
	
	public OutputStream _createOutputStream(Object session,
		String path, Component comp)
		throws IOException
	{
		VFSManager.error(comp,path,"vfs.not-supported.save",new String[] { name });
		return null;
	} 

	
	
	public void _saveComplete(Object session, Buffer buffer, String path,
		Component comp) throws IOException {} 

	
	
	public void _finishTwoStageSave(Object session, Buffer buffer, String path,
		Component comp) throws IOException
	{
	} 

	
	
	public void _endVFSSession(Object session, Component comp)
		throws IOException
	{
	} 

	
	
	public static Color getDefaultColorFor(String name)
	{
		synchronized(lock)
		{
			if(colors == null)
				loadColors();

			for(int i = 0; i < colors.size(); i++)
			{
				ColorEntry entry = (ColorEntry)colors.elementAt(i);
				if(entry.re.matcher(name).matches())
					return entry.color;
			}

			return null;
		}
	} 

	
	
	public static class DirectoryEntryCompare implements Comparator
	{
		private boolean sortIgnoreCase, sortMixFilesAndDirs;

		
		public DirectoryEntryCompare(boolean sortMixFilesAndDirs,
			boolean sortIgnoreCase)
		{
			this.sortMixFilesAndDirs = sortMixFilesAndDirs;
			this.sortIgnoreCase = sortIgnoreCase;
		}

		public int compare(Object obj1, Object obj2)
		{
			VFSFile file1 = (VFSFile)obj1;
			VFSFile file2 = (VFSFile)obj2;

			if(!sortMixFilesAndDirs)
			{
				if(file1.getType() != file2.getType())
					return file2.getType() - file1.getType();
			}

			return StandardUtilities.compareStrings(file1.getName(),
				file2.getName(),sortIgnoreCase);
		}
	} 

	
	private String name;
	private int caps;
	private String[] extAttrs;
	private static Vector colors;
	private static Object lock = new Object();

	
	static
	{
		EditBus.addToBus(new EBComponent()
		{
			public void handleMessage(EBMessage msg)
			{
				if(msg instanceof PropertiesChanged)
				{
					synchronized(lock)
					{
						colors = null;
					}
				}
			}
		});
	} 

	
	private void listFiles(Object session, List stack,
		List files, String directory, VFSFileFilter filter, boolean recursive,
		Component comp, boolean skipBinary, boolean skipHidden) throws IOException
	{
		if(stack.contains(directory))
		{
			Log.log(Log.ERROR,this,
				"Recursion in _listDirectory(): "
				+ directory);
			return;
		}

		stack.add(directory);

		VFSFile[] _files = _listFiles(session,directory,
			comp);
		if(_files == null || _files.length == 0)
			return;

		for(int i = 0; i < _files.length; i++)
		{
			VFSFile file = _files[i];
			if (skipHidden && (file.isHidden() || MiscUtilities.isBackup(file.getName())))
				continue;
			if(!filter.accept(file))
				continue;
			if(file.getType() == VFSFile.DIRECTORY
				|| file.getType() == VFSFile.FILESYSTEM)
			{
				if(recursive)
				{
					
					String canonPath = _canonPath(session,
						file.getPath(),comp);
					if(!MiscUtilities.isURL(canonPath))
						canonPath = MiscUtilities.resolveSymlinks(canonPath);

					listFiles(session,stack,files,
						canonPath,filter,recursive,
						comp, skipBinary, skipHidden);
				}

			}
			else 
			{
				if (skipBinary && file.isBinary(session))
					continue;

				Log.log(Log.DEBUG,this,file.getPath());
				files.add(file.getPath());
			}
		}
	} 

	
	private static void loadColors()
	{
		synchronized(lock)
		{
			colors = new Vector();

			if(!jEdit.getBooleanProperty("vfs.browser.colorize"))
				return;

			String glob;
			int i = 0;
			while((glob = jEdit.getProperty("vfs.browser.colors." + i + ".glob")) != null)
			{
				try
				{
					colors.addElement(new ColorEntry(
						Pattern.compile(StandardUtilities.globToRE(glob)),
						jEdit.getColorProperty(
						"vfs.browser.colors." + i + ".color",
						Color.black)));
				}
				catch(PatternSyntaxException e)
				{
					Log.log(Log.ERROR,VFS.class,"Invalid regular expression: "
						+ glob);
					Log.log(Log.ERROR,VFS.class,e);
				}

				i++;
			}
		}
	} 

	
	static class ColorEntry
	{
		Pattern re;
		Color color;

		ColorEntry(Pattern re, Color color)
		{
			this.re = re;
			this.color = color;
		}
	} 

	
}
