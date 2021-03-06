package com.sleepycat.je.log; 
import java.io.IOException; 
import java.nio.ByteBuffer; 
import com.sleepycat.je.DatabaseException; 
import com.sleepycat.je.dbi.EnvironmentImpl; 
import com.sleepycat.je.log.entry.LogEntry; 
import de.ovgu.cide.jakutil.*; 
public  class  PrintFileReader  extends DumpFileReader {
	 public PrintFileReader( EnvironmentImpl env, int readBufferSize, long startLsn, long finishLsn, String entryTypes, String txnIds, boolean verbose) throws IOException, DatabaseException { super(env,readBufferSize,startLsn,finishLsn,entryTypes,txnIds,verbose); }

	 protected boolean processEntry__wrappee__base( ByteBuffer entryBuffer) throws DatabaseException { LogEntryType lastEntryType=LogEntryType.findType(currentEntryTypeNum,currentEntryTypeVersion); StringBuffer sb=new StringBuffer(); sb.append("<entry lsn=\"0x").append(Long.toHexString(readBufferFileNum)); sb.append("/0x").append(Long.toHexString(currentEntryOffset)); sb.append("\" type=\"").append(lastEntryType); if (LogEntryType.isProvisional(currentEntryTypeVersion)) { sb.append("\" isProvisional=\"true"); } sb.append("\" prev=\"0x"); sb.append(Long.toHexString(currentEntryPrevOffset)); if (verbose) { sb.append("\" size=\"").append(currentEntrySize); sb.append("\" cksum=\"").append(currentEntryChecksum); } sb.append("\">"); LogEntry entry=lastEntryType.getSharedLogEntry(); entry.readEntry(entryBuffer,currentEntrySize,currentEntryTypeVersion,true); boolean dumpIt=true; if (targetTxnIds.size() > 0) { if (entry.isTransactional()) { if (!targetTxnIds.contains(new Long(entry.getTransactionId()))) { dumpIt=false; } } else { dumpIt=false; } } if (dumpIt) { entry.dumpEntry(sb,verbose); sb.append("</entry>"); System.out.println(sb.toString()); } return true; }

	 protected boolean processEntry( ByteBuffer entryBuffer) throws DatabaseException { t.in(Thread.currentThread().getStackTrace()[1].toString());	processEntry__wrappee__base(); t.out(Thread.currentThread().getStackTrace()[1].toString()); }

	private Tracer t = new Tracer();

	public Tracer getTracer(){return t;}


}
