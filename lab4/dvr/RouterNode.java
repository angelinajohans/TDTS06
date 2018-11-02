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
  private boolean poisonedReverse = true;
  private boolean linkChanges = false;

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
    sendUpdate();
    
  
    
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
    //printDistanceTable();
  }

  //--------------------------------------------------
  //The implementation of Bellman-Ford equation
  public boolean updateMinCost(){
    boolean updated = false;
    for (int node = 0;  node < totNodes; node++){   
      if (node == myID) {
        continue;
      }
      int old_node = routeThrough[node];
      int old_cost = 999;
      if (linkChanges == false){
        old_cost = updateTable[myID][node];
      }
      for (int i = 0; i < totNodes; i++){
        //myGUI.println("ROUTE THROUGH!!!!!: " + routeThrough[i] +" to " + node);
        if(routeThrough[i] < 999 && i != myID){
          int cost_to_direct_neighbour = updateTable[myID][routeThrough[i]];
          int cost_from_direct_neighbour_to_node = updateTable[routeThrough[i]][node];
          int new_cost = cost_to_direct_neighbour + cost_from_direct_neighbour_to_node;

          //myGUI.println("Cost to direct neighbour : " + cost_to_direct_neighbour + " Cost from neigbour to node: " + cost_from_direct_neighbour_to_node + " Total cost: " + new_cost + "\n");

          if (new_cost < old_cost) {
            myGUI.println("Updating cost" );
            updated = true;
            //myGUI.println("Old cost: " + old_cost);
            old_cost = new_cost;
            //myGUI.println("New cost: " + old_cost);
            old_node = routeThrough[i];
        }
      }

      else{
        //myGUI.println("Routethrough is 999 and myID");
      }

    }
    updateTable[myID][node] = old_cost;
    //costs[node] = old_cost;
    routeThrough[node] = old_node;
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
    //myGUI.println("srcID " + srcID);
    for (int i = 0; i < totNodes; i++){
      updateTable[srcID][i] = minCost[i];
      myGUI.println("MinCost" + minCost[i]);
    }
    if(updateMinCost()){
      sendUpdate();
    }
  }


  //--------------------------------------------------
  // Loop through our DistanceTable and send the costs to the other nodes
  private void sendUpdate() {
    myGUI.println("send update");
    for (int dest=0; dest<totNodes ; dest++ ) {
      if(dest == myID){
        continue;
      }
      int[] tmpCosts = new int[RouterSimulator.NUM_NODES];
      if(costs[dest] != 999){
      for (int node=0;node<totNodes ;node++ ) {        
        if(poisonedReverse && routeThrough[node]==dest){
          myGUI.println("Send to node table " + dest + " that " + node +" has been Poisoned reversed");
          tmpCosts[node]=999;
        }
        else {
          tmpCosts[node] = updateTable[myID][node];
        }
      }
   
      RouterPacket packet = new RouterPacket(myID,dest,tmpCosts);
      sim.toLayer2(packet);
      myGUI.println("Send update");
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
        if (updateTable[myID][i] == 999 ){
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
  //Inte implementerat ännu!s
  public void updateLinkCost(int dest, int newcost) {
    linkChanges = true;
    myGUI.println("Update Link cost");
    myGUI.println("The destiantion is"+ dest);
    updateTable[dest][myID] = newcost;
    costs[dest] = newcost;
    sendUpdate();


    
    myGUI.println( newcost + "It is the newcost");
   
  }

}
