import javax.swing.*;   
import java.util.Arrays;      

public class RouterNode {
  private int myID;
  private GuiTextArea myGUI;
  private RouterSimulator sim;
  private int[] costs = new int[RouterSimulator.NUM_NODES];
  private int totNodes;
  private int[][] updateTable = new int[RouterSimulator.NUM_NODES][RouterSimulator.NUM_NODES];
    private int[][] neighboursTable = new int[RouterSimulator.NUM_NODES][RouterSimulator.NUM_NODES];

  //--------------------------------------------------
  public RouterNode(int ID, RouterSimulator sim, int[] costs) {
    totNodes = sim.NUM_NODES;
    myID = ID;
    this.sim = sim;
    myGUI =new GuiTextArea("  Output window for Router #"+ ID + "  ");

    System.arraycopy(costs, 0, this.costs, 0, RouterSimulator.NUM_NODES);
    
    //Initiazlize table with infinity
    for (int[] row : updateTable){
      Arrays.fill(row, RouterSimulator.INFINITY); 
    } 
    seeCostofNeighbour();
  }

  //--------------------------------------------------
  public void seeCostofNeighbour(){
    for (int i = 0; i < totNodes; i++){
      if(myID != i){
        if (costs[i] < RouterSimulator.INFINITY)
        {
          myGUI.println("Cost: "+ costs[i]);
          neighboursTable[myID][i] = costs[i];
        }
        else {
          myGUI.println("Not neighbour");
          neighboursTable[myID][i] = 999;
        } 
      }
      else{
        myGUI.println("My node");
      neighboursTable[myID][i] = 0;
      }
    }
  }

  //--------------------------------------------------
  public void recvUpdate(RouterPacket pkt) {
    myGUI.println("Receive update"+ pkt);

  }
  

  //--------------------------------------------------
  private void sendUpdate(RouterPacket pkt) {
    sim.toLayer2(pkt);
    myGUI.println("Send update");
  }
  

  //--------------------------------------------------
  public void printDistanceTable() {
	  myGUI.println("Current table for " + myID +
			"  at time " + sim.getClocktime() + "\n");

    myGUI.println("Distancetable:\n");
    printHeader();
    printDistance();
    myGUI.println("Our distance vector and routers:\n");
    printHeader();
    printCosts();

  }

  //--------------------------------------------------
  private void printHeader(){
    String header = "  dst   |   ";
    for(int i = 0; i < totNodes; i++){
      header = header + i + "      ";
    }
    myGUI.println(header);
    myGUI.println(String.format("%s", "------------------------------------------"));
  }


  //--------------------------------------------------
  private void printDistance(){
    for (int i=0; i < totNodes; i++){
      if(costs[i] != RouterSimulator.INFINITY){
        String row = "   ";
        for (int j= 0; j < totNodes; j++){
            row = row + updateTable[i][j]+ "      ";           
        }
        myGUI.println(" costs "+ i + "|" + row +"\n");
      }
    }
  }


  //--------------------------------------------------
  private void printCosts(){
    for (int i=0; i < totNodes; i++){
        String row = "   ";
        for (int j= 0; j < totNodes; j++){
            row = row + neighboursTable[i][j]+ "      ";           
        }
        myGUI.println(" nbr  "+ i + "|" + row +"\n");
    }
  }

  //--------------------------------------------------
  public void updateLinkCost(int dest, int newcost) {
  }

}
