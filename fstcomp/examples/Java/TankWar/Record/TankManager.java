
public class TankManager {
	protected Record record;
	protected int tank1Score = 0;
	protected int tank2Score = 0;
	
	public void init() {
		original();
		record = new Record();
	}
			
	public void malenkontrolle() {
		original();
		switch(status){
		case GameManager.NOTE:
			maler.note(record.readNote());
			break;
		case GameManager.NAME_VERGEBEN:
			maler.nameVergeben();
			break;
		}
	}
	
	public void addScore(int id, int type) {
		if (id == tank1.id) {
			tank1Score += type * 5;
		}
	}

	public void writeScore() {
		record.writeNote(maler.name, tank1Score);
		tank1Score = 0;
	}
	
}