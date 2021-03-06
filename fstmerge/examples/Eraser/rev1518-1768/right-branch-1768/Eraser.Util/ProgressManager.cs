using System;
using System.Collections.Generic;
using System.Text;
namespace Eraser.Util
{
 public abstract class ProgressManagerBase
 {
  protected ProgressManagerBase()
  {
   StartTime = DateTime.Now;
  }
  public void Restart()
  {
   StartTime = DateTime.Now;
  }
  public abstract float Progress
  {
   get;
  }
  public abstract int Speed
  {
   get;
  }
  public abstract TimeSpan TimeLeft
  {
   get;
  }
  public DateTime StartTime
  {
   get;
   private set;
  }
 }
 public class ProgressManager : ProgressManagerBase
 {
  public void MarkComplete()
  {
   if (total == 0)
    completed = total = 1;
   else
    completed = total;
  }
  public long Completed
  {
   get
   {
    return completed;
   }
   set
   {
    if (value > Total)
     throw new ArgumentOutOfRangeException("value", value, "The Completed " +
      "property of the Progress Manager cannot exceed the total work units for " +
      "the task.");
    completed = value;
   }
  }
  public long Total
  {
   get
   {
    return total;
   }
   set
   {
    if (value < Completed)
     throw new ArgumentOutOfRangeException("value", value, "The Total property " +
      "of the Progress Manager must be greater than or equal to the completed " +
      "work units for the task.");
    total = value;
   }
  }
  public override float Progress
  {
   get
   {
    if (Total == 0)
     return 0.0f;
    return (float)((double)Completed / Total);
   }
  }
  public override int Speed
  {
   get
   {
    if (DateTime.Now == StartTime)
     return 0;
    if ((DateTime.Now - lastSpeedCalc).Seconds < 5 && lastSpeed != 0)
     return lastSpeed;
    double timeElapsed = (DateTime.Now - lastSpeedCalc).TotalSeconds;
    if (timeElapsed == 0.0)
     return 0;
    lastSpeed = (int)((Completed - lastCompleted) / timeElapsed);
    lastSpeedCalc = DateTime.Now;
    lastCompleted = Completed;
    return lastSpeed;
   }
  }
  public override TimeSpan TimeLeft
  {
   get
   {
    if (Speed == 0)
     return TimeSpan.Zero;
    return new TimeSpan(0, 0, (int)((Total - Completed) / Speed));
   }
  }
  private DateTime lastSpeedCalc;
  private long lastCompleted;
  private int lastSpeed;
  private long completed;
  private long total;
 }
 public abstract class ChainedProgressManager : ProgressManagerBase
 {
 }
 public class SteppedProgressManager : ChainedProgressManager
 {
  private class StepsList : IList<SteppedProgressManagerStep>
  {
   public StepsList(SteppedProgressManager manager)
   {
    List = new List<SteppedProgressManagerStep>();
    ListLock = manager.ListLock;
   }
   public int IndexOf(SteppedProgressManagerStep item)
   {
    lock (ListLock)
     return List.IndexOf(item);
   }
   public void Insert(int index, SteppedProgressManagerStep item)
   {
    lock (ListLock)
    {
     List.Insert(index, item);
     TotalWeights += item.Weight;
    }
   }
   public void RemoveAt(int index)
   {
    lock (ListLock)
    {
     TotalWeights -= List[index].Weight;
     List.RemoveAt(index);
    }
   }
   public SteppedProgressManagerStep this[int index]
   {
    get
    {
     lock (ListLock)
      return List[index];
    }
    set
    {
     lock (ListLock)
     {
      TotalWeights -= List[index].Weight;
      List[index] = value;
      TotalWeights += value.Weight;
     }
    }
   }
   public void Add(SteppedProgressManagerStep item)
   {
    lock (ListLock)
    {
     List.Add(item);
     TotalWeights += item.Weight;
    }
   }
   public void Clear()
   {
    lock (ListLock)
    {
     List.Clear();
     TotalWeights = 0;
    }
   }
   public bool Contains(SteppedProgressManagerStep item)
   {
    lock (ListLock)
     return List.Contains(item);
   }
   public void CopyTo(SteppedProgressManagerStep[] array, int arrayIndex)
   {
    lock (ListLock)
     List.CopyTo(array, arrayIndex);
   }
   public int Count
   {
    get
    {
     lock (ListLock)
      return List.Count;
    }
   }
   public bool IsReadOnly
   {
    get { return false; }
   }
   public bool Remove(SteppedProgressManagerStep item)
   {
    int index = List.IndexOf(item);
    if (index != -1)
     TotalWeights -= List[index].Weight;
    return List.Remove(item);
   }
   public IEnumerator<SteppedProgressManagerStep> GetEnumerator()
   {
    return List.GetEnumerator();
   }
   System.Collections.IEnumerator System.Collections.IEnumerable.GetEnumerator()
   {
    return List.GetEnumerator();
   }
   private float TotalWeights
   {
    get
    {
     return totalWeights;
    }
    set
    {
     if (value >= 1.1f || value < 0.0f)
      throw new ArgumentOutOfRangeException("value", "The total weights of " +
       "all steps in the task must be within the range [0.0, 1.0]");
     totalWeights = value;
    }
   }
   private List<SteppedProgressManagerStep> List;
   private object ListLock;
   private float totalWeights;
  }
  public SteppedProgressManager()
  {
   ListLock = new object();
   Steps = new StepsList(this);
  }
  public override float Progress
  {
   get
   {
    float result = 0.0f;
    lock (ListLock)
     foreach (SteppedProgressManagerStep step in Steps)
      result += step.Progress.Progress * step.Weight;
    return result;
   }
  }
  public override int Speed
  {
   get
   {
    if (CurrentStep == null)
     return 0;
    return CurrentStep.Progress.Speed;
   }
  }
  public override TimeSpan TimeLeft
  {
   get
   {
    long ticksElapsed = (DateTime.Now - StartTime).Ticks;
    float progressRemaining = 1.0f - Progress;
    return new TimeSpan((long)
     (progressRemaining * (ticksElapsed / (double)Progress)));
   }
  }
  public IList<SteppedProgressManagerStep> Steps
  {
   get;
   private set;
  }
  public SteppedProgressManagerStep CurrentStep
  {
   get
   {
    lock (ListLock)
    {
     if (Steps.Count == 0)
      return null;
     foreach (SteppedProgressManagerStep step in Steps)
      if (step.Progress.Progress < 1.0f)
       return step;
     return Steps[Steps.Count - 1];
    }
   }
  }
  private object ListLock;
 }
 public class SteppedProgressManagerStep
 {
  public SteppedProgressManagerStep(ProgressManagerBase progress, float weight)
   : this(progress, weight, null)
  {
  }
  public SteppedProgressManagerStep(ProgressManagerBase progress, float weight, string name)
  {
   Progress = progress;
   Weight = weight;
   Name = name;
  }
  public ProgressManagerBase Progress
  {
   get;
   set;
  }
  public float Weight
  {
   get;
   private set;
  }
  public string Name
  {
   get;
   set;
  }
 }
 public class ParallelProgressManager : ChainedProgressManager
 {
  private class SubTasksList : IList<ProgressManagerBase>
  {
   public SubTasksList(ParallelProgressManager manager)
   {
    List = new List<ProgressManagerBase>();
    ListLock = manager.TaskLock;
   }
   public int IndexOf(ProgressManagerBase item)
   {
    lock (ListLock)
     return List.IndexOf(item);
   }
   public void Insert(int index, ProgressManagerBase item)
   {
    lock (ListLock)
     List.Insert(index, item);
   }
   public void RemoveAt(int index)
   {
    lock (ListLock)
     List.RemoveAt(index);
   }
   public ProgressManagerBase this[int index]
   {
    get
    {
     lock (ListLock)
      return List[index];
    }
    set
    {
     lock (ListLock)
      List[index] = value;
    }
   }
   public void Add(ProgressManagerBase item)
   {
    lock (ListLock)
     List.Add(item);
   }
   public void Clear()
   {
    lock (ListLock)
     List.Clear();
   }
   public bool Contains(ProgressManagerBase item)
   {
    return List.Contains(item);
   }
   public void CopyTo(ProgressManagerBase[] array, int arrayIndex)
   {
    lock (ListLock)
     List.CopyTo(array, arrayIndex);
   }
   public int Count
   {
    get
    {
     lock (ListLock)
      return List.Count;
    }
   }
   public bool IsReadOnly
   {
    get { return false; }
   }
   public bool Remove(ProgressManagerBase item)
   {
    lock (ListLock)
     return List.Remove(item);
   }
   public IEnumerator<ProgressManagerBase> GetEnumerator()
   {
    return List.GetEnumerator();
   }
   System.Collections.IEnumerator System.Collections.IEnumerable.GetEnumerator()
   {
    return List.GetEnumerator();
   }
   private List<ProgressManagerBase> List;
   private object ListLock;
  }
  public ParallelProgressManager()
  {
   Tasks = new SubTasksList(this);
   TaskLock = new object();
  }
  public override float Progress
  {
   get
   {
    float result = 0.0f;
    lock (TaskLock)
     foreach (ProgressManagerBase subTask in Tasks)
      result += subTask.Progress * (1.0f / Tasks.Count);
    return result;
   }
  }
  public override int Speed
  {
   get
   {
    int maxSpeed = 0;
    lock (TaskLock)
     foreach (ProgressManagerBase subTask in Tasks)
      maxSpeed = Math.Max(subTask.Speed, maxSpeed);
    return maxSpeed;
   }
  }
  public override TimeSpan TimeLeft
  {
   get
   {
    TimeSpan maxTime = TimeSpan.MinValue;
    lock (TaskLock)
     foreach (ProgressManagerBase subTask in Tasks)
      if (maxTime < subTask.TimeLeft)
       maxTime = subTask.TimeLeft;
    return maxTime;
   }
  }
  public IList<ProgressManagerBase> Tasks
  {
   get;
   private set;
  }
  private object TaskLock;
 }
 public class ProgressChangedEventArgs : EventArgs
 {
  public ProgressChangedEventArgs(ProgressManagerBase progress, object userState)
  {
   Progress = progress;
   UserState = userState;
  }
  public ProgressManagerBase Progress { get; private set; }
  public object UserState { get; private set; }
 }
 public delegate void ProgressChangedEventHandler(object sender, ProgressChangedEventArgs e);
}
