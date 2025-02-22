package com.miniproject.cloudsim;


import java.io.FileWriter;
import java.io.IOException;
import java.util.*;
import org.cloudbus.cloudsim.*;
import org.cloudbus.cloudsim.core.CloudSim;
import org.cloudbus.cloudsim.provisioners.*;

public class Main {
    // Simulation Parameters
	private static final int NUM_DATACENTERS = 2;
    private static final int NUM_PMS_PER_TYPE = 10;
    private static final int VMS_PER_PM = 15;
    private static final int MAX_TASKS_PER_PM = 100;

    // Task Classification Thresholds
    private static final long SMALL_TASK_THRESHOLD = 7000;
    private static final long MEDIUM_TASK_THRESHOLD = 15000;

    private static List<Host> hostList;
    private static List<Vm> vmListSmall;
    private static List<Vm> vmListMedium;
    private static List<Vm> vmListLarge;
    private static List<Cloudlet> cloudletList;

    public static void main(String[] args) {
        try {
            int numUser = 1;
            Calendar calendar = Calendar.getInstance();
            boolean traceFlag = false;
            CloudSim.init(numUser, calendar, traceFlag);

            createHosts();
            Datacenter datacenter = createDatacenter("MainDatacenter");
            DatacenterBroker broker = createBroker("MainBroker");
            int brokerId = broker.getId();

            createVMs(brokerId);
            createCloudlets(brokerId);
            enhancedTaskClassification();

            broker.submitGuestList(getVmsForProcessing());
            broker.submitCloudletList(cloudletList);

            CloudSim.startSimulation();
            CloudSim.stopSimulation();

            List<Cloudlet> receivedCloudletList = broker.getCloudletReceivedList();
            saveResultsToCsv(receivedCloudletList, "cloudsim_results.csv");

        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    private static void createHosts() {
        hostList = new ArrayList<>();
        for (int i = 0; i < 10; i++) {
            List<Pe> peList = new ArrayList<>();
            for (int j = 0; j < 16; j++) {
                peList.add(new Pe(j, new PeProvisionerSimple(20000)));
            }

            Host host = new Host(
                i, 
                new RamProvisionerSimple(64 * 1024),
                new BwProvisionerSimple(10000),
                5 * 1024 * 1024,
                peList,
                new VmSchedulerTimeShared(peList)
            );
            hostList.add(host);
        }
    }

    private static void createVMs(int brokerId) {
        vmListSmall = new ArrayList<>();
        vmListMedium = new ArrayList<>();
        vmListLarge = new ArrayList<>();

        // Small VMs
        for (int i = 0; i < NUM_PMS_PER_TYPE * VMS_PER_PM / 3; i++) {
            vmListSmall.add(new Vm(
                i, brokerId, 7000, 1, 1024, 1000, 10000, 
                "Xen", new CloudletSchedulerTimeShared()
            ));
        }

        // Medium VMs
        for (int i = 0; i < NUM_PMS_PER_TYPE * VMS_PER_PM / 3; i++) {
            vmListMedium.add(new Vm(
                i + vmListSmall.size(), brokerId, 20000, 1, 
                4 * 1024, 1000, 10000, 
                "Xen", new CloudletSchedulerTimeShared()
            ));
        }

        // Large VMs - increased proportion
        for (int i = 0; i < NUM_PMS_PER_TYPE * VMS_PER_PM / 3; i++) {
            vmListLarge.add(new Vm(
                i + vmListSmall.size() + vmListMedium.size(), 
                brokerId, 40000, 2, 8 * 1024, 1000, 10000, 
                "Xen", new CloudletSchedulerTimeShared()
            ));
        }
    }

    private static void createCloudlets(int brokerId) {
        cloudletList = new ArrayList<>();
        Random random = new Random();
        int totalTasks = MAX_TASKS_PER_PM * NUM_PMS_PER_TYPE * 3;
        
        // Create Tasks with explicit size distribution
        for (int i = 0; i < totalTasks; i++) {
            long taskLength;
            
            // Deliberately create a mix of task sizes
            if (i < totalTasks * 0.3) {
                // Small tasks (0 - 7000)
                taskLength = random.nextInt((int)SMALL_TASK_THRESHOLD);
            } else if (i < totalTasks * 0.6) {
                // Medium tasks (7001 - 15000)
                taskLength = SMALL_TASK_THRESHOLD + 1 + 
                             random.nextInt((int)(MEDIUM_TASK_THRESHOLD - SMALL_TASK_THRESHOLD - 1));
            } else {
                // Large tasks (15001 - 50000)
                taskLength = MEDIUM_TASK_THRESHOLD + 1 + 
                             random.nextInt(50000 - (int)MEDIUM_TASK_THRESHOLD - 1);
            }

            Cloudlet cloudlet = new Cloudlet(
                i, 
                taskLength, 
                1, 300, 300,
                new UtilizationModelFull(),
                new UtilizationModelFull(),
                new UtilizationModelFull()
            );
            cloudlet.setUserId(brokerId);
            cloudletList.add(cloudlet);
        }
    }
    private static void enhancedTaskClassification() {
        Random random = new Random();
        
        for (Cloudlet cloudlet : cloudletList) {
            long length = cloudlet.getCloudletLength();
            
            if (length <= SMALL_TASK_THRESHOLD) {
                cloudlet.setGuestId(vmListSmall.get(random.nextInt(vmListSmall.size())).getId());
            } else if (length <= MEDIUM_TASK_THRESHOLD) {
                cloudlet.setGuestId(vmListMedium.get(random.nextInt(vmListMedium.size())).getId());
            } else {
                cloudlet.setGuestId(vmListLarge.get(random.nextInt(vmListLarge.size())).getId());
            }
        }
    }

    private static List<Vm> getVmsForProcessing() {
        List<Vm> allVms = new ArrayList<>();
        allVms.addAll(vmListSmall);
        allVms.addAll(vmListMedium);
        allVms.addAll(vmListLarge);
        return allVms;
    }

    private static void saveResultsToCsv(List<Cloudlet> list, String filename) {
        try (FileWriter csvWriter = new FileWriter(filename)) {
            csvWriter.append("Cloudlet ID,Status,Datacenter ID,VM ID,Actual CPU Time,Start Time,End Time,Task Size,Wait Time,Response Time,Makespan,Turnaround Time\n");
            
            for (Cloudlet cloudlet : list) {
                if (cloudlet.getStatus() == Cloudlet.CloudletStatus.SUCCESS) {
                    String taskSize;
                    long length = cloudlet.getCloudletLength();
                    
                    if (length <= SMALL_TASK_THRESHOLD) {
                        taskSize = "Small";
                    } else if (length <= MEDIUM_TASK_THRESHOLD) {
                        taskSize = "Medium";
                    } else {
                        taskSize = "Large";
                    }

                    // Calculate additional metrics: Wait Time, Response Time, Makespan, and Turnaround Time
                    double waitTime = cloudlet.getExecStartTime() - cloudlet.getSubmissionTime(); // Wait time = start time - submission time
                    double responseTime = cloudlet.getExecFinishTime() - cloudlet.getSubmissionTime(); // Response time = finish time - submission time
                    double makespan = cloudlet.getExecFinishTime() - cloudlet.getExecStartTime(); // Makespan = finish time - start time
                    double turnaroundTime = responseTime; // Turnaround time can be equivalent to response time here

                    csvWriter.append(String.format("%d,%s,%d,%d,%.2f,%.2f,%.2f,%s,%.2f,%.2f,%.2f,%.2f\n", 
                        cloudlet.getCloudletId(), 
                        "SUCCESS", 
                        cloudlet.getResourceId(), 
                        cloudlet.getGuestId(), 
                        cloudlet.getActualCPUTime(), 
                        cloudlet.getExecStartTime(), 
                        cloudlet.getExecFinishTime(),
                        taskSize,
                        waitTime,
                        responseTime,
                        makespan,
                        turnaroundTime
                    ));
                }
            }
            System.out.println("Results saved to " + filename);
        } catch (IOException e) {
            e.printStackTrace();
        }
    }

    private static Datacenter createDatacenter(String name) {
        String arch = "x86";
        String os = "Linux";
        String vmm = "Xen";
        double timeZone = 10.0;
        double cost = 3.0;
        double costPerMem = 0.05;
        double costPerStorage = 0.1;
        double costPerBw = 0.1;

        DatacenterCharacteristics characteristics = new DatacenterCharacteristics(
            arch, os, vmm, hostList, timeZone, cost, costPerMem, costPerStorage, costPerBw
        );

        try {
            return new Datacenter(name, characteristics, 
                new VmAllocationPolicySimple(hostList), 
                new LinkedList<>(), 0);
        } catch (Exception e) {
            e.printStackTrace();
            return null;
        }
    }

    private static DatacenterBroker createBroker(String name) throws Exception {
        return new DatacenterBroker(name);
    }
}