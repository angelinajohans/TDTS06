import javax.swing.*;
import java.util.Arrays;

public class RouterNode {
  private int myID;
  private GuiTextArea myGUI;
  private RouterSimulator sim;
  private RouterPacket packet;  
  private int[] costs = new int[RouterSimulator.NUM_NODES];
  private int totNodes;
  private int[][] updateTable = new int[RouterSimulator.NUM_NODES][RouterSimulator.NUM_NODES];
  private int[] routeThrough = new int[RouterSimulator.NUM_NODES];
  private int[] neighbour = new int[RouterSimulator.NUM_NODES];
  private boolean poisonedReverse = false;

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
    //See which nodes are neighbours
    seeCostofNeighbour();
    updateMinCost();
    updateAllNeighbours();
    
  
    
  }


  //--------------------------------------------------
  public void seeCostofNeighbour(){
    for (int i = 0; i < totNodes; i++){
      if(myID != i){
        if (costs[i] < RouterSimulator.INFINITY)
        {
          myGUI.println("Cost: "+ costs[i]);
          updateTable[myID][i] = costs[i];
          neighbour[i] = 1;
        }
        else {
          myGUI.println("Not neighbour");
          updateTable[myID][i] = 999;
          neighbour[i] = 0;
        }
      }
      else{
        myGUI.println("My node");
        updateTable[myID][i] = 0;
        neighbour[i] = 0;
      }
      if (updateTable[myID][i] < 999){
        routeThrough[i] = i;
      }
      else {
        routeThrough[i] = 999;
      }
    }
  }

  //--------------------------------------------------
  //The implementation of Bellman-Ford equation
  public boolean updateMinCost(){
    boolean updated = false;
    int bestRoute = -1;
    for (int dest = 0; dest < totNodes; ++dest) {
      if (dest == myID)
      continue;

      int minCost = RouterSimulator.INFINITY;

      for (int node = 0; node < totNodes; ++node){
        if (node == myID)
        continue;
        int cost_to_direct_neighbour = costs[node];
        int cost_from_direct_neighbour_to_node = updateTable[node][dest];
        int new_cost = cost_to_direct_neighbour  + cost_from_direct_neighbour_to_node;
        myGUI.println("From node " + dest + " to " + node + " the cost to direct neighbour is "+ cost_to_direct_neighbour + " and from neighbour to node " + cost_from_direct_neighbour_to_node );
        if (new_cost < minCost) {
          minCost = new_cost;
          bestRoute = node;
        }

      }
      if (updateTable[myID][dest] != minCost || bestRoute != routeThrough[dest])
        updated = true;

      updateTable[myID][dest] = minCost;
      routeThrough[dest] = bestRoute;
    }
    return updated;
  }

  //--------------------------------------------------
  //Update our Distance table with the other nodes costs and if this contributes
  //to an updated distance vector, send the new costs
  public void recvUpdate(RouterPacket pkt) {
    myGUI.println("Receive update");
    int srcID = pkt.sourceid;
    int[] minCost = pkt.mincost;
    for (int i = 0; i < totNodes; i++){
      updateTable[srcID][i] = minCost[i];
    }
    if(updateMinCost()){
      updateAllNeighbours();
    }
  }


  //--------------------------------------------------
  private void sendUpdate(RouterPacket pkt) {
    myGUI.println("send update");
    sim.toLayer2(pkt);
  }

  //--------------------------------------------------
  private void updateAllNeighbours(){
    for (int dest=0; dest<totNodes ; dest++ ) {
      if(dest == myID){
        continue;
      }
      int[] tmpCosts = new int[RouterSimulator.NUM_NODES];
      if(costs[dest] != RouterSimulator.INFINITY){
      for (int node=0;node<totNodes ;node++ ) {        
        if(poisonedReverse && routeThrough[node]==dest){
          myGUI.println("Send to node table " + dest + " that " + node +" has been Poisoned reversed");
          tmpCosts[node]=RouterSimulator.INFINITY;
        }
        else {
          tmpCosts[node] = updateTable[myID][node];
        }
      }
      RouterPacket packet = new RouterPacket(myID,dest,tmpCosts);
      sendUpdate(packet);
      }
    }
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
    printCostsandRoute();

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
          if( i != myID && neighbour[i]==1)
            row = row + updateTable[i][j]+ "      ";
        }
      if(i != myID && neighbour[i]==1)
        myGUI.println(" nbr "+ i + "|" + row +"\n");
      }
    }
  }


  //--------------------------------------------------
  private void printCostsandRoute(){
    String  costsrow = " costs | ";
    String routerow = " route | ";
    for (int i=0; i < totNodes; i++){
        costsrow = costsrow + updateTable[myID][i]+ "      ";
        if (updateTable[myID][i] == RouterSimulator.INFINITY  ){
          routerow = routerow + " - " + "      ";
        }
        else {
          routerow = routerow + routeThrough[i] + "      ";
        }
    }
    myGUI.println( costsrow );
    myGUI.println( routerow );
  }


  //--------------------------------------------------
  //Is running when LINKCHANGES is set to true
  public void updateLinkCost(int dest, int newcost) {
    myGUI.println("Update Link cost");
    updateTable[dest][myID] = newcost;
    myGUI.println("MyID is "+ myID + " destination is "+ dest+" and the newcost is"+ newcost);
    costs[dest] = newcost;
    updateMinCost();
    updateAllNeighbours();
  }

}
